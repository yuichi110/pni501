# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Comprehensive test suite for PNI501 Clean-Break Workflow v2 features."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pni._actions import (
    CategoryScores,
    Finding,
    PlanApprovalInput,
    PrimitiveType,
    RollupSynthesisInput,
    ScoreResult,
    ScoreSubmissionInput,
    ScoreSummary,
)
from pni._reporter import build_report_blueprint
from pni._workflows import (
    RunStatus,
    WorkflowCategory,
    WorkflowPrerequisiteError,
    WorkflowStateDB,
    compute_baseline_evaluation,
    evaluate_when_expr,
    extract_mermaid_blocks,
    get_ready_workflow_actions,
    get_workflow_action,
    plan_workflow_run,
    push_workflow_action,
    start_workflow_run,
    validate_mermaid_static,
)
from pni.cli import app, init_project

runner = CliRunner()


def test_safe_when_evaluator_and_injection_rejection() -> None:
    """Verify safe AST `when:` predicates evaluate cleanly and reject unsafe syntax."""
    ctx: dict[str, object] = {
        "lang": "rust",
        "has_runtime_harness": True,
        "is_component_scope": False,
        "runtime_types": ["cli", "library"],
    }
    assert evaluate_when_expr("has_runtime_harness", ctx) == (True, "")
    assert evaluate_when_expr("not is_component_scope and lang in ['python', 'rust']", ctx) == (True, "")
    ok_false, reason = evaluate_when_expr("'web_api' in runtime_types", ctx)
    assert ok_false is False
    assert "evaluated to false" in reason

    for unsafe in ("__import__('os').system('echo pwn')", "1 + 2", "lang.upper() == 'RUST'"):
        with pytest.raises(ValueError, match="Unsupported"):
            evaluate_when_expr(unsafe, ctx)


def test_mermaid_static_validator_and_cli(tmp_path: Path) -> None:
    """Verify Layer 1 static Mermaid validation catches common AI syntax bugs and passes valid graphs."""
    good_dag = (
        "flowchart TD\n"
        '    act_01["[ASK] Confirm Plan"]\n'
        '    act_02["[AUTO] AST Analysis (Python)"]\n'
        "    act_01 --> act_02\n"
    )
    res_good = validate_mermaid_static(good_dag)
    assert res_good.valid is True
    assert res_good.diagram_type == "flowchart"

    # Unquoted parentheses inside brackets, reserved 'end' node ID, unclosed subgraph, raw HTML
    bad_dag = (
        "flowchart TD\n"
        "    subgraph S1\n"
        "    A[Run (fast)] --> end\n"
        '    B["<b>bold</b>"]\n'
    )
    res_bad = validate_mermaid_static(bad_dag)
    assert res_bad.valid is False
    codes = {i.code for i in res_bad.issues}
    assert "MM-UNQUOTED-SPECIAL" in codes
    assert "MM-RESERVED-ID" in codes
    assert "MM-UNCLOSED-SUBGRAPH" in codes
    assert "MM-HTML" in codes

    # Markdown fence extraction + CLI `pni validate-mermaid`
    md_file = tmp_path / "plan.md"
    md_file.write_text(f"# Plan\n```mermaid\n{good_dag}```\n", encoding="utf-8")
    assert len(extract_mermaid_blocks(md_file.read_text(encoding="utf-8"))) == 1

    res_cli_ok = runner.invoke(app, ["validate-mermaid", str(md_file), "--json"])
    assert res_cli_ok.exit_code == 0, res_cli_ok.stdout
    assert json.loads(res_cli_ok.stdout)["valid"] is True

    bad_file = tmp_path / "broken.mmd"
    bad_file.write_text(bad_dag, encoding="utf-8")
    res_cli_bad = runner.invoke(app, ["validate-mermaid", str(bad_file)])
    assert res_cli_bad.exit_code == 1


def test_phase0_recon_plan_gate_interactive_and_auto_approve(tmp_path: Path) -> None:
    """Verify Phase 0 Recon, Mermaid DAG plan CLI, interactive confirm_plan, disabled_steps, and --auto-approve."""
    # Multi-language repo: backend (Python) + frontend (TypeScript) + Dockerfile companion
    be = tmp_path / "backend"
    fe = tmp_path / "frontend"
    (be / "src").mkdir(parents=True)
    (fe / "src").mkdir(parents=True)
    (be / "pyproject.toml").write_text('[project]\nname = "be"\nversion = "0.1.0"\n', encoding="utf-8")
    (be / "src" / "app.py").write_text(
        '"""App."""\ndef run() -> int:\n    """Run."""\n    return 1\n',
        encoding="utf-8",
    )
    (fe / "package.json").write_text('{"name": "fe", "version": "1.0.0"}\n', encoding="utf-8")
    (fe / "src" / "index.ts").write_text("export const x: number = 1;\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\nUSER app\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "mono"\nversion = "0.1.0"\n', encoding="utf-8")

    init_project(tmp_path, lang="python", force=True)
    (tmp_path / ".pni" / "workflows" / "plan_demo.yaml").write_text(
        "id: plan_demo\n"
        "name: Plan Gate Demo\n"
        "targets:\n"
        '  root: "."\n'
        '  source: ["backend/src"]\n'
        "steps:\n"
        "  - id: repo_step\n"
        "    uses: repo_structure_audit\n"
        "  - id: optional_sec\n"
        "    uses: security_vulnerability_audit\n"
        "    needs: [repo_step]\n"
        "  - id: final_score\n"
        "    uses: emit_score\n"
        "    needs: [optional_sec]\n",
        encoding="utf-8",
    )

    planned = plan_workflow_run("plan_demo", tmp_path, probe_container_engine=False)
    assert planned is not None
    _, _, plan = planned
    assert validate_mermaid_static(plan.mermaid_dag).valid is True
    assert len(plan.components) >= 2
    assert "dockerfile" in plan.companion_languages
    assert len(plan.alignment_questions) >= 2
    assert (tmp_path / ".pni" / "cache" / "plan_demo" / "plan.json").is_file()

    orig = Path.cwd()
    try:
        os.chdir(tmp_path)
        plan_cli = runner.invoke(app, ["workflows", "plan", "plan_demo", "--mermaid", "--no-container-probe"])
        assert plan_cli.exit_code == 0
        assert "flowchart TD" in plan_cli.stdout
        assert validate_mermaid_static(plan_cli.stdout).valid is True
    finally:
        os.chdir(orig)

    # Interactive start pauses at AWAITING_APPROVAL -> confirm_plan
    run = start_workflow_run("plan_demo", tmp_path, probe_container_engine=False)
    assert run is not None
    assert run.status == RunStatus.AWAITING_APPROVAL
    _, act1, guide1 = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None and act1.primitive_type == PrimitiveType.CONFIRM_PLAN
    assert "```mermaid" in guide1

    # Rejection keeps run awaiting approval
    ok_rej, _ = push_workflow_action(run.run_id, act1.action_id, '{"approved": false}', tmp_path)
    assert ok_rej is False

    # Approval disables optional_sec and injects focus_areas
    approval = PlanApprovalInput(
        approved=True,
        disabled_steps=["optional_sec"],
        focus_areas=["API authorization", "Input validation"],
        alignment_summary="Skip Trivy scan; focus on auth.",
    )
    ok_app, _ = push_workflow_action(run.run_id, act1.action_id, approval.model_dump_json(), tmp_path)
    assert ok_app is True

    db = WorkflowStateDB(tmp_path)
    actions = db.get_actions(run.run_id)
    sec_actions = [a for a in actions if a.step_key == "optional_sec"]
    assert sec_actions and all(a.status == RunStatus.SKIPPED for a in sec_actions)

    # Auto-Advance runs project_inspect -> lands on repo_step ai_interpret with approved focus banner
    _, act_repo, guide_repo = get_workflow_action(run.run_id, tmp_path)
    assert act_repo is not None and act_repo.primitive_type == PrimitiveType.AI_INTERPRET
    assert "API authorization" in guide_repo
    assert "Skip Trivy scan; focus on auth." in guide_repo

    # Batch --auto-approve skips confirm_plan immediately
    batch_run = start_workflow_run("plan_demo", tmp_path, auto_approve=True, probe_container_engine=False)
    assert batch_run is not None
    assert batch_run.status == RunStatus.IN_PROGRESS
    assert batch_run.plan_approved is True


def test_parallel_dag_auto_advance_ready_actions_and_step_projection(tmp_path: Path) -> None:
    """Verify parallel deterministic Auto-Advance, `get-actions --ready`, out-of-order push, and fact projection."""
    src_dir = tmp_path / "src" / "pkg"
    src_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "dag-demo"\nversion = "0.1.0"\n', encoding="utf-8")
    (src_dir / "mod.py").write_text(
        '"""Mod."""\ndef f(x: int) -> int:\n    """F."""\n    return x + 1\n',
        encoding="utf-8",
    )

    init_project(tmp_path, lang="python", force=True)
    (tmp_path / ".pni" / "workflows" / "parallel_dag.yaml").write_text(
        "id: parallel_dag\n"
        "name: Parallel DAG Demo\n"
        "targets:\n"
        '  source: ["src"]\n'
        "steps:\n"
        "  - id: branch_ast\n"
        "    uses: python_ast_audit\n"
        "    needs: [confirm_plan]\n"
        "    fact_views: [ast]\n"
        "  - id: branch_repo\n"
        "    uses: repo_structure_audit\n"
        "    needs: [confirm_plan]\n"
        "    fact_views: [project]\n"
        "  - id: join_score\n"
        "    uses: emit_score\n"
        "    needs: [branch_ast, branch_repo]\n",
        encoding="utf-8",
    )

    run = start_workflow_run("parallel_dag", tmp_path, auto_approve=True, probe_container_engine=False)
    assert run is not None

    # Single call auto-executes BOTH ast_analyze AND project_inspect in parallel -> returns BOTH ai_interpret actions!
    _, payloads, _ = get_ready_workflow_actions(run.run_id, tmp_path)
    assert len(payloads) == 2
    by_key = {p.step_key: p for p in payloads}
    assert set(by_key.keys()) == {"branch_ast", "branch_repo"}
    assert "Deterministic AST Facts" in by_key["branch_ast"].prompt_markdown
    assert "Deterministic Project Facts" not in by_key["branch_ast"].prompt_markdown
    assert "Deterministic Project Facts" in by_key["branch_repo"].prompt_markdown
    assert "Deterministic AST Facts" not in by_key["branch_repo"].prompt_markdown

    # CLI `get-actions --ready --json` and out-of-order parallel push (push branch_repo FIRST, branch_ast SECOND)
    orig = Path.cwd()
    try:
        os.chdir(tmp_path)
        res_ready = runner.invoke(app, ["workflows", "get-actions", run.run_id, "--ready", "--json"])
        assert res_ready.exit_code == 0
        ready_arr = json.loads(res_ready.stdout)
        assert len(ready_arr) == 2

        ok_b, _ = push_workflow_action(
            run.run_id, by_key["branch_repo"].action_id, json.dumps({"summary": "Repo ok."}), tmp_path
        )
        assert ok_b is True

        # join_score is NOT ready yet while branch_ast is still pending
        _, mid_payloads, _ = get_ready_workflow_actions(run.run_id, tmp_path)
        assert [p.step_key for p in mid_payloads] == ["branch_ast"]

        res_push_a = runner.invoke(
            app,
            [
                "workflows",
                "push-action",
                run.run_id,
                by_key["branch_ast"].action_id,
                '{"summary": "AST ok."}',
                "--json",
            ],
        )
        assert res_push_a.exit_code == 0
        assert json.loads(res_push_a.stdout)["ok"] is True

        # Now join_score unlocks; verify compact vs --full-schema
        res_compact = runner.invoke(app, ["workflows", "get-action", run.run_id, "--json"])
        assert res_compact.exit_code == 0
        compact_obj = json.loads(res_compact.stdout)
        assert compact_obj["step_key"] == "join_score"
        assert compact_obj["expected_input_model"] == "ScoreSubmissionInput"
        assert '"$defs"' not in compact_obj["schema_skeleton"]

        res_full = runner.invoke(app, ["workflows", "get-action", run.run_id, "--full-schema", "--json"])
        assert res_full.exit_code == 0
        assert '"properties"' in json.loads(res_full.stdout)["schema_skeleton"]
    finally:
        os.chdir(orig)


def test_baseline_anchoring_finding_adjustments_and_sarif_summary_outputs(tmp_path: Path) -> None:
    """Verify deterministic pre-findings, FP waiver adjustments, delta bounds, and Score + Summary + SARIF outputs."""
    src_dir = tmp_path / "src" / "app"
    src_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "sec-demo"\nversion = "0.1.0"\ndependencies = ["requests>=2.0"]\n',
        encoding="utf-8",
    )
    (src_dir / "runner.py").write_text(
        '"""Script runner."""\n\ndef run_expr(expr: str) -> object:\n    """Eval."""\n    return eval(expr)\n',
        encoding="utf-8",
    )

    init_project(tmp_path, lang="python", force=True)
    (tmp_path / ".pni" / "workflows" / "baseline_wf.yaml").write_text(
        "id: baseline_wf\n"
        "name: Baseline & SARIF Test\n"
        "targets:\n"
        '  source: ["src"]\n'
        "steps:\n"
        "  - id: repo\n"
        "    uses: repo_structure_audit\n"
        "  - id: ast\n"
        "    uses: python_ast_audit\n"
        "  - id: score\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )

    run = start_workflow_run("baseline_wf", tmp_path, auto_approve=True, probe_container_engine=False)
    assert run is not None

    _, act_repo, _ = get_workflow_action(run.run_id, tmp_path)
    assert act_repo is not None
    # Out-of-bounds baseline_delta (> 10) must be rejected by Pydantic validator
    ok_bad_delta, msg_bad_delta = push_workflow_action(
        run.run_id,
        act_repo.action_id,
        json.dumps({"summary": "Too large delta.", "baseline_delta": {"security": 15}}),
        tmp_path,
    )
    assert ok_bad_delta is False
    assert "[-10, +10]" in msg_bad_delta

    assert push_workflow_action(
        run.run_id,
        act_repo.action_id,
        json.dumps({"summary": "Repo checked.", "baseline_delta": {"dependencies": -5}}),
        tmp_path,
    )[0]

    _, act_ast, guide_ast = get_workflow_action(run.run_id, tmp_path)
    assert act_ast is not None
    assert "Deterministic Pre-Findings for Triage" in guide_ast
    assert "det-" in guide_ast

    # Compute deterministic pre-findings to get exact det-* ID for eval() CWE-94 sink
    db = WorkflowStateDB(tmp_path)
    from pni._workflows.base_model import WorkflowFactsBundle  # noqa: PLC0415

    cached_bundle = WorkflowFactsBundle.model_validate_json(
        (tmp_path / ".pni" / "cache" / "baseline_wf" / "facts.json").read_text(encoding="utf-8")
    )
    beval = compute_baseline_evaluation(cached_bundle)
    cwe94 = next(f for f in beval.pre_findings if f.rule_id == "CWE-94")
    assert cwe94.finding_id.startswith("det-")

    # Waive CWE-94 with grounded rationale >= 10 chars
    ok_ast, _ = push_workflow_action(
        run.run_id,
        act_ast.action_id,
        json.dumps(
            {
                "summary": "Waived intentional DSL evaluator.",
                "finding_adjustments": [
                    {
                        "finding_id": cwe94.finding_id,
                        "action": "waive",
                        "reason": "Intentional sandboxed expression evaluator documented in architecture spec.",
                    }
                ],
            }
        ),
        tmp_path,
    )
    assert ok_ast is True

    _, act_score, guide_score = get_workflow_action(run.run_id, tmp_path)
    assert act_score is not None and act_score.primitive_type == PrimitiveType.EMIT_SCORE
    assert "Deterministic 7-Axis Baseline Scores" in guide_score

    sub = ScoreSubmissionInput(
        overall_score=84,
        category_scores=CategoryScores(
            architecture=90,
            code_quality=88,
            typing=95,
            testing=70,
            dependencies=75,
            security=85,
            documentation=85,
        ),
        summary="Clean service after triaging intentional evaluator.",
    )
    ok_score, msg_score = push_workflow_action(run.run_id, act_score.action_id, sub.model_dump_json(), tmp_path)
    assert ok_score is True and "COMPLETED" in msg_score

    score_path = tmp_path / "reports" / "baseline_wf_score.json"
    summary_path = tmp_path / "reports" / "baseline_wf_summary.json"
    sarif_path = tmp_path / "reports" / "baseline_wf_findings.sarif"
    assert score_path.is_file()
    assert summary_path.is_file()
    assert sarif_path.is_file()

    saved_score = ScoreResult.model_validate_json(score_path.read_text(encoding="utf-8"))
    assert saved_score.schema_version == "2.0"
    assert saved_score.baseline_scores is not None
    # Waived CWE-94 pre-finding must not appear in final findings
    assert all(f.finding_id != cwe94.finding_id for f in saved_score.findings)

    saved_summary = ScoreSummary.model_validate_json(summary_path.read_text(encoding="utf-8"))
    assert saved_summary.overall_score == 84
    assert saved_summary.sarif_file == "reports/baseline_wf_findings.sarif"

    sarif_doc = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert sarif_doc["version"] == "2.1.0"
    assert sarif_doc["runs"][0]["tool"]["driver"]["name"] == "PNI501"
    assert isinstance(sarif_doc["runs"][0]["results"], list)
    assert len(sarif_doc["runs"][0]["results"]) == len(saved_score.findings)
    assert db.get_run(run.run_id) is not None


def test_polyglot_monorepo_rollup_e2e_weighted_guardrail_and_unified_blueprint(tmp_path: Path) -> None:
    """Verify multi-language Rollup: prerequisites, log1p weights, weakest-link guardrail, path norm, and blueprint."""
    (tmp_path / "README.md").write_text("# Polyglot Monorepo\n\nFull stack system.\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\nUSER app\n", encoding="utf-8")
    (tmp_path / "backend" / "src").mkdir(parents=True)
    (tmp_path / "frontend" / "src").mkdir(parents=True)
    (tmp_path / "native" / "src").mkdir(parents=True)

    init_project(tmp_path, lang="python", force=True)
    wf_dir = tmp_path / ".pni" / "workflows"
    (wf_dir / "monorepo_rollup.yaml").write_text(
        "id: monorepo_rollup\n"
        "category: rollup\n"
        "name: Polyglot Monorepo Unified Audit\n"
        "report_mode: unified\n"
        "includes:\n"
        "  - id: backend\n"
        "    workflow_id: audit_backend\n"
        "    root: backend\n"
        "    lang: python\n"
        "    primary: true\n"
        "  - id: frontend\n"
        "    workflow_id: audit_frontend\n"
        "    root: frontend\n"
        "    lang: typescript\n"
        "    primary: true\n"
        "  - id: native\n"
        "    workflow_id: audit_native\n"
        "    root: native\n"
        "    lang: rust\n"
        "    primary: false\n",
        encoding="utf-8",
    )

    # 1. Missing component scores fails closed before starting rollup
    with pytest.raises(WorkflowPrerequisiteError, match="missing completed sub-audit score"):
        start_workflow_run("monorepo_rollup", tmp_path, auto_approve=True, probe_container_engine=False)

    # 2. Emit 3 component sub-audit ScoreResults (backend has weak security=35 to trigger weakest-link guardrail!)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True)

    backend_score = ScoreResult(
        project_name="backend",
        workflow_id="audit_backend",
        language="python",
        target_root="backend",
        overall_score=68,
        grade="C",
        category_scores=CategoryScores(
            architecture=80,
            code_quality=75,
            typing=85,
            testing=70,
            dependencies=70,
            security=35,
            documentation=65,
        ),
        metrics_snapshot={"total_loc": 2000, "measured_line_coverage_pct": 72.0},
        findings=[
            Finding(
                severity="critical",
                category="security",
                rule_id="CWE-89",
                file_path="src/db.py",
                line=42,
                description="Unsanitized SQL query.",
                recommendation="Use parameterized query.",
            )
        ],
        summary="Python API backend has a critical SQLi.",
    )
    frontend_score = ScoreResult(
        project_name="frontend",
        workflow_id="audit_frontend",
        language="typescript",
        target_root="frontend",
        overall_score=90,
        grade="S",
        category_scores=CategoryScores(
            architecture=90,
            code_quality=92,
            typing=95,
            testing=88,
            dependencies=90,
            security=92,
            documentation=86,
        ),
        metrics_snapshot={"total_loc": 3000, "measured_line_coverage_pct": 85.0},
        findings=[
            Finding(
                severity="low",
                category="code_quality",
                rule_id="ts/style",
                file_path="src/App.tsx",
                line=10,
                description="Unused helper.",
                recommendation="Remove unused helper.",
            )
        ],
        summary="Clean TypeScript React SPA.",
    )
    native_score = ScoreResult(
        project_name="native",
        workflow_id="audit_native",
        language="rust",
        target_root="native",
        overall_score=88,
        grade="A",
        category_scores=CategoryScores(
            architecture=90,
            code_quality=90,
            typing=95,
            testing=85,
            dependencies=90,
            security=88,
            documentation=80,
        ),
        metrics_snapshot={"total_loc": 800},
        summary="Safe Rust CLI helper.",
    )

    (reports_dir / "audit_backend_score.json").write_text(backend_score.model_dump_json(indent=2), encoding="utf-8")
    (reports_dir / "audit_frontend_score.json").write_text(frontend_score.model_dump_json(indent=2), encoding="utf-8")
    (reports_dir / "audit_native_score.json").write_text(native_score.model_dump_json(indent=2), encoding="utf-8")

    # 3. Start rollup workflow -> lands on SYNTHESIZE_ROLLUP with RollupFacts table & weakest-link guardrail
    run = start_workflow_run("monorepo_rollup", tmp_path, auto_approve=True, probe_container_engine=False)
    assert run is not None
    assert run.category == WorkflowCategory.ROLLUP

    _, act_synth, guide_synth = get_workflow_action(run.run_id, tmp_path)
    assert act_synth is not None and act_synth.primitive_type == PrimitiveType.SYNTHESIZE_ROLLUP
    assert "Weakest-Link Guardrails Applied" in guide_synth
    assert "`backend`" in guide_synth and "`frontend`" in guide_synth and "`native`" in guide_synth
    assert "dockerfile" in guide_synth

    synth_input = RollupSynthesisInput(
        summary="Unified polyglot health constrained by Python backend SQLi.",
        cross_component_architecture="React TS frontend calls Python FastAPI backend; Rust helper builds assets.",
        strengths=["Strong TypeScript typing and Rust memory safety"],
    )
    ok_synth, _ = push_workflow_action(run.run_id, act_synth.action_id, synth_input.model_dump_json(), tmp_path)
    assert ok_synth is True

    # 4. Verify unified ScoreResult, Summary, SARIF, path normalization, weakest-link cap, and unified Blueprint!
    unified_score_file = reports_dir / "monorepo_rollup_score.json"
    assert unified_score_file.is_file()
    assert (reports_dir / "monorepo_rollup_summary.json").is_file()
    assert (reports_dir / "monorepo_rollup_findings.sarif").is_file()

    unified = ScoreResult.model_validate_json(unified_score_file.read_text(encoding="utf-8"))
    assert unified.language == "python+rust+typescript"
    assert len(unified.components) == 3
    # Security capped at min_primary (35) + 15 = 50!
    assert unified.category_scores.security == 50
    # Component findings normalized to repo-root relative paths with component tags
    paths_by_comp = {(f.component, f.file_path) for f in unified.findings}
    assert ("backend", "backend/src/db.py") in paths_by_comp
    assert ("frontend", "frontend/src/App.tsx") in paths_by_comp

    # build_report_blueprint automatically delegates to 6-chapter unified rollup blueprint
    bp = build_report_blueprint(unified, target="monorepo_rollup", lang="ja")
    assert [ch.filename for ch in bp.chapters] == [
        "00_cover.md",
        "01_executive_summary.md",
        "02_cross_component_architecture.md",
        "03_remediation_roadmap.md",
        "04_governance_and_companions.md",
        "05_component_deep_dives.md",
    ]
