# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for Executed Audit DAG provenance, baseline comparison, FP triage log, and artifact manifest in blueprints."""

from __future__ import annotations

import json
from pathlib import Path

from pni._actions import (
    AuditScopeMetadata,
    CategoryRationales,
    CategoryScores,
    ComponentScoreSummary,
    ExecutionDagSummary,
    ExecutionStageNode,
    Finding,
    FindingAdjustment,
    InterpretationInput,
    MigrationPlanResult,
    PrimitiveType,
    ProgressDimensionScores,
    ProgressResult,
    ScoreResult,
    TargetArchitectureDesign,
)
from pni._reporter.blueprint import build_report_blueprint
from pni._reporter.migration_blueprint import build_migration_blueprint
from pni._reporter.progress_blueprint import build_progress_blueprint
from pni._workflows import (
    get_workflow_action,
    push_workflow_action,
    start_workflow_run,
)


def _setup_dag_provenance_repo(tmp_path: Path) -> None:
    """Create a small Python project with a DAG workflow containing a skipped conditional stage."""
    src_dir = tmp_path / "src" / "demo"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text('"""Demo package."""\n', encoding="utf-8")
    (src_dir / "app.py").write_text(
        '"""App module."""\n\n\ndef compute(x: int) -> int:\n    """Double an int."""\n    return x * 2\n',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "dag-demo"\nversion = "0.1.0"\n'
        'requires-python = ">=3.11"\ndependencies = ["pydantic>=2.0"]\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# DAG Demo\n\n## Overview\n\nSmall test project.\n", encoding="utf-8")

    wf_dir = tmp_path / ".pni" / "workflows"
    wf_dir.mkdir(parents=True)
    (tmp_path / ".pni" / "pni.toml").write_text(
        '[report]\nsrc_dir = "docs_src/pni"\noutput_dir = "docs/pni"\n',
        encoding="utf-8",
    )
    (wf_dir / "prov_audit.yaml").write_text(
        """id: prov_audit
name: Provenance DAG Audit
targets:
  root: "."
  source: ["src"]
  tests: ["tests"]
  docs: ["README.md"]
  exclude: ["dist/**"]
steps:
  - id: structure
    uses: repo_structure_audit
  - id: ast_scan
    uses: python_ast_audit
    needs: [structure]
  - id: web_only_check
    action: ai_interpret
    name: Web API Only Gate
    needs: [structure]
    when: "has_web_api"
    prompt: "Check web routes."
  - id: score
    uses: emit_score
    needs: [ast_scan, web_only_check]
    with:
      target: "prov_audit"
  - id: report
    uses: write_drawlib_report
    needs: [score]
    with:
      target: "prov_audit"
""",
        encoding="utf-8",
    )


def test_end_to_end_execution_dag_baseline_triage_and_artifact_manifest(tmp_path: Path) -> None:
    """Verify ScoreResult captures action-level DAG, skipped stage, triage log, and renders Ch. 4 blueprint."""
    _setup_dag_provenance_repo(tmp_path)
    run = start_workflow_run("prov_audit", tmp_path, auto_approve=True)
    assert run is not None

    # 1. repo_structure_audit ai_interpret (also triage deterministic missing_lockfile pre-finding)
    _, act_struct, guide_struct = get_workflow_action(run.run_id, tmp_path)
    assert act_struct is not None and act_struct.primitive_type == PrimitiveType.AI_INTERPRET
    assert "det-" in guide_struct
    det_id = next(
        tok.strip("`")
        for tok in guide_struct.split()
        if tok.strip("`").startswith("det-")
    )
    struct_payload = InterpretationInput(
        summary="Structure checked; triaged one deterministic finding.",
        step_score=82,
        finding_adjustments=[
            FindingAdjustment(
                finding_id=det_id,
                action="reclassify",
                new_severity="low",
                reason="Library package distributes wheel metadata without app-level lockfile.",
            )
        ],
    ).model_dump_json()
    ok, msg = push_workflow_action(run.run_id, act_struct.action_id, struct_payload, tmp_path)
    assert ok is True, msg

    # 2. python_ast_audit ai_interpret (web_only_check auto-skips because has_web_api is False)
    _, act_ast, _ = get_workflow_action(run.run_id, tmp_path)
    assert act_ast is not None and act_ast.primitive_type == PrimitiveType.AI_INTERPRET
    ast_payload = InterpretationInput(
        summary="Clean typed Python module.",
        step_score=92,
        findings=[
            Finding(
                severity="low",
                category="documentation",
                rule_id="common/documentation",
                file_path="README.md",
                line=1,
                description="Add installation command example to README.",
                recommendation="Include pip/uv install snippet.",
            )
        ],
    ).model_dump_json()
    ok, msg = push_workflow_action(run.run_id, act_ast.action_id, ast_payload, tmp_path)
    assert ok is True, msg

    # 3. emit_score
    _, act_score, _ = get_workflow_action(run.run_id, tmp_path)
    assert act_score is not None and act_score.primitive_type == PrimitiveType.EMIT_SCORE
    score_payload = json.dumps(
        {
            "overall_score": 84,
            "category_scores": {
                "architecture": 95,
                "code_quality": 95,
                "typing": 98,
                "testing": 68,
                "dependencies": 75,
                "security": 95,
                "documentation": 80,
            },
            "category_rationales": {
                "dependencies": "Lockfile advisory reclassified to low for library scope.",
            },
            "summary": "Clean library baseline with transparent DAG provenance.",
        }
    )
    ok, msg = push_workflow_action(run.run_id, act_score.action_id, score_payload, tmp_path)
    assert ok is True, msg

    score_obj = ScoreResult.model_validate_json(
        (tmp_path / "docs" / "pni" / "prov_audit_score.json").read_text(encoding="utf-8")
    )
    assert score_obj.execution_dag is not None
    dag = score_obj.execution_dag
    stage_by_id = {n.stage_id: n for n in dag.nodes}
    assert {"confirm_plan", "structure", "ast_scan", "web_only_check", "score", "report"} <= set(stage_by_id)
    assert stage_by_id["structure"].mode == "HYBRID"
    assert stage_by_id["structure"].status == "completed"
    assert stage_by_id["web_only_check"].mode == "SKIP"
    assert stage_by_id["web_only_check"].status == "skipped"
    assert "has_web_api" in stage_by_id["web_only_check"].skip_reason
    assert stage_by_id["score"].status == "completed"
    assert stage_by_id["report"].status == "pending"

    assert dag.audit_scope is not None
    assert dag.audit_scope.exclude_globs == ["dist/**"]
    assert any("tree-sitter" in t for t in dag.audit_scope.tools_used)
    assert dag.audit_scope.artifact_manifest["score_json"] == "docs/pni/prov_audit_score.json"
    assert dag.audit_scope.artifact_manifest["findings_sarif"] == "docs/pni/prov_audit_findings.sarif"
    # Structured facts & plan automatically synced into custom flat report src_dir `_facts/`!
    assert dag.audit_scope.artifact_manifest["facts_json"] == "docs_src/pni/_facts/facts.json"
    assert dag.audit_scope.artifact_manifest["plan_json"] == "docs_src/pni/_facts/plan.json"
    assert (tmp_path / "docs_src" / "pni" / "_facts" / "facts.json").is_file()
    assert (tmp_path / "docs_src" / "pni" / "_facts" / "plan.json").is_file()
    assert len(score_obj.triaged_adjustments) == 1
    assert score_obj.triaged_adjustments[0].finding_id == det_id

    # 4. write_drawlib_report prompt & Chapter 4 Blueprint contents
    _, act_rep, guide_rep = get_workflow_action(run.run_id, tmp_path)
    assert act_rep is not None and act_rep.primitive_type == PrimitiveType.WRITE_DRAWLIB_REPORT
    assert (tmp_path / "docs_src" / "pni" / "_facts" / "blueprint.json").is_file()
    assert "lib-graph-overview" in guide_rep
    assert "Executed Workflow Pipeline DAG" in guide_rep
    assert "7-Axis Deterministic Baseline vs. Final Score Comparison" in guide_rep
    assert "AI False-Positive Triage Log" in guide_rep
    assert "Machine-Readable Evidence Artifacts" in guide_rep

    bp = build_report_blueprint(score_obj, target="prov_audit", lang="ja")
    ch4 = next(ch for ch in bp.chapters if ch.filename == "04_standards_and_findings.md")
    ch4_text = "\n".join(ch4.sorted_data_markdown)
    assert "DAG" in ch4.title
    assert "web_only_check" in ch4_text
    assert "[SKIP | SKIPPED]" in ch4_text
    assert "Finding Source Split" in ch4_text
    assert det_id in ch4_text
    assert "docs/pni/prov_audit_findings.sarif" in ch4_text
    assert "docs_src/pni/_facts/facts.json" in ch4_text


def test_rollup_migration_and_progress_blueprints_include_dag_and_artifacts() -> None:
    """Verify Rollup, Migration, and Progress blueprints surface Executed DAG and Artifact Manifest pointers."""
    cats = CategoryScores(
        architecture=85,
        code_quality=82,
        typing=80,
        testing=75,
        dependencies=88,
        security=90,
        documentation=78,
    )
    rollup_dag = ExecutionDagSummary(
        workflow_id="repo_rollup",
        category="rollup",
        scope="repo",
        nodes=[
            ExecutionStageNode(
                stage_id="comp_backend",
                label="backend (python)",
                mode="HYBRID",
                status="completed",
                highlight="88/100 (A), 4,200 LOC, weight=0.60",
            ),
            ExecutionStageNode(
                stage_id="comp_frontend",
                label="frontend (typescript)",
                mode="HYBRID",
                status="completed",
                highlight="79/100 (B), 2,100 LOC, weight=0.40",
            ),
            ExecutionStageNode(
                stage_id="synthesize_rollup",
                label="Hybrid Weighted Rollup Synthesis",
                mode="HYBRID",
                status="completed",
                needs=["comp_backend", "comp_frontend"],
                highlight="overall=84/100, log1p(LOC) weights",
            ),
        ],
        audit_scope=AuditScopeMetadata(
            target_root=".",
            source_targets=["backend", "frontend"],
            language="python+typescript",
            companion_languages=["dockerfile", "yaml"],
            tools_used=["multi-audit rollup (log1p LOC + guardrails across 2 components)"],
            artifact_manifest={
                "score_json": "reports/repo_rollup_score.json",
                "findings_sarif": "reports/repo_rollup_findings.sarif",
            },
        ),
    )
    rollup_score = ScoreResult(
        project_name="poly-repo",
        workflow_id="repo_rollup",
        language="python+typescript",
        overall_score=84,
        grade="A",
        category_scores=cats,
        category_rationales=CategoryRationales(architecture="Clean REST contract."),
        components=[
            ComponentScoreSummary(
                component_id="backend",
                language="python",
                root="backend",
                weight=0.6,
                total_loc=4200,
                overall_score=88,
                grade="A",
                category_scores=cats,
                score_file="reports/backend_score.json",
            ),
            ComponentScoreSummary(
                component_id="frontend",
                language="typescript",
                root="frontend",
                weight=0.4,
                total_loc=2100,
                overall_score=79,
                grade="B",
                category_scores=cats,
                score_file="reports/frontend_score.json",
            ),
        ],
        execution_dag=rollup_dag,
        summary="Unified polyglot summary.",
    )
    rollup_bp = build_report_blueprint(rollup_score, target="repo_rollup", lang="en")
    ch4_rollup = next(c for c in rollup_bp.chapters if c.filename == "04_governance_and_companions.md")
    rollup_txt = "\n".join(ch4_rollup.sorted_data_markdown)
    assert "comp_backend" in rollup_txt
    assert "synthesize_rollup" in rollup_txt
    assert "reports/repo_rollup_findings.sarif" in rollup_txt

    mig_plan = MigrationPlanResult(
        project_name="legacy-app",
        workflow_id="mig_plan",
        source_language="python",
        executive_summary="Phased migration plan.",
        target_architecture=TargetArchitectureDesign(pattern_name="Clean Architecture"),
        execution_dag=ExecutionDagSummary(
            workflow_id="mig_plan",
            category="migration",
            nodes=[
                ExecutionStageNode(stage_id="analyze", label="Migration Analyze", mode="HYBRID", status="completed"),
            ],
            audit_scope=AuditScopeMetadata(
                artifact_manifest={"migration_plan_json": "reports/mig_plan_migration_plan.json"}
            ),
        ),
    )
    mig_bp = build_migration_blueprint(mig_plan, target="mig_plan", lang="en")
    ch6_mig = next(c for c in mig_bp.chapters if c.filename == "06_pr_wbs_and_verification_gates.md")
    assert "reports/mig_plan_migration_plan.json" in "\n".join(ch6_mig.sorted_data_markdown)

    prog_res = ProgressResult(
        project_name="active-app",
        workflow_id="prog_check",
        delivery_status="on_track",
        overall_health_score=86,
        dimension_scores=ProgressDimensionScores(
            schedule_adherence=90,
            git_and_merge_hygiene=85,
            momentum_and_churn=82,
            test_and_quality_trajectory=87,
        ),
        executive_summary="On track.",
        plan_file=".pni/progress/prog_check.yaml",
        execution_dag=ExecutionDagSummary(
            workflow_id="prog_check",
            category="progress",
            nodes=[
                ExecutionStageNode(stage_id="progress", label="Progress Analyze", mode="HYBRID", status="completed"),
            ],
            audit_scope=AuditScopeMetadata(
                artifact_manifest={"progress_json": "reports/prog_check_progress.json"}
            ),
        ),
    )
    prog_bp = build_progress_blueprint(prog_res, target="prog_check", lang="en")
    ch4_prog = next(c for c in prog_bp.chapters if c.filename == "04_risks_and_next_actions.md")
    assert "reports/prog_check_progress.json" in "\n".join(ch4_prog.sorted_data_markdown)
