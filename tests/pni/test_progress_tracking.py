# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit and E2E tests for Project Progress & Git Governance Tracking (`progress_analyze`, `emit_progress`, CLI)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from pni._actions import (
    BranchIntegrationAssessment,
    CategoryScores,
    HealthGrade,
    InterpretationInput,
    ProgressActionItem,
    ProgressDimensionScores,
    ProgressOptions,
    ProgressPlanDefinition,
    ProgressResult,
    ReportCompletionInput,
    RuleCheckResult,
    ScoreResult,
    TaskProgressAssessment,
    load_and_validate_progress_plan,
    read_audit_history,
    read_progress_history,
    record_audit_history_from_score,
    resolve_progress_result_rel_path,
    run_progress_analyze,
    scaffold_progress_plan,
)
from pni._actions.progress_analyze.git_exec import validate_safe_git_ref
from pni._actions.progress_analyze.plan_loader import resolve_bounded_plan_path
from pni._reporter import build_progress_blueprint, render_drawlib_report_guide
from pni._workflows import (
    RunStatus,
    WorkflowCategory,
    WorkflowPrerequisiteError,
    get_workflow_action,
    list_workflows,
    push_workflow_action,
    run_workflow_action_adhoc,
    start_workflow_run,
)
from pni.cli import app


def _git(repo: Path, *args: str, date_iso: str = "2026-04-01T10:00:00+00:00") -> str:
    """Run a deterministic local git command inside `repo` for test fixture construction."""
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test Dev",
        "GIT_AUTHOR_EMAIL": "dev@example.com",
        "GIT_COMMITTER_NAME": "Test Dev",
        "GIT_COMMITTER_EMAIL": "dev@example.com",
        "GIT_AUTHOR_DATE": date_iso,
        "GIT_COMMITTER_DATE": date_iso,
        "LC_ALL": "C",
    }
    git_bin = shutil.which("git")
    assert git_bin is not None
    completed = subprocess.run(  # noqa: S603
        [git_bin, *args],
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _create_git_progress_fixture(tmp_path: Path) -> Path:
    """Build a multi-branch Git repository with clean, conflicting, overlapping, and non-compliant commits."""
    repo = tmp_path / "sample_repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "commit.gpgsign", "false")

    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "docs").mkdir()
    (repo / "src" / "auth.py").write_text(
        "def verify_token(tok: str) -> bool:\n    # TODO: add revocation check\n    return bool(tok)\n",
        encoding="utf-8",
    )
    (repo / "src" / "shared.py").write_text("VERSION = '1.0'\n", encoding="utf-8")
    (repo / "tests" / "test_auth.py").write_text(
        "def test_verify_token_non_empty() -> None:\n    assert True\n",
        encoding="utf-8",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\nInitial documentation.\n", encoding="utf-8")
    (repo / "uv.lock").write_text("\n".join(f"pkg-{i} = '1.0.0'" for i in range(200)) + "\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: bootstrap auth module", date_iso="2026-04-01T09:00:00+00:00")

    # 1. Clean feature branch (`feat/*` compliant) modifying shared.py + adding a second test
    _git(repo, "checkout", "-b", "feat/clean-api")
    (repo / "src" / "api.py").write_text("def health() -> str:\n    return 'ok'\n", encoding="utf-8")
    (repo / "src" / "shared.py").write_text("VERSION = '1.1-api'\n", encoding="utf-8")
    (repo / "tests" / "test_auth.py").write_text(
        "def test_verify_token_non_empty() -> None:\n    assert True\n\n"
        "def test_health_endpoint() -> None:\n    assert True\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: add health endpoint", date_iso="2026-04-08T10:00:00+00:00")

    # 2. Conflicting + improperly named branch touching auth.py AND shared.py (cross-branch overlap)
    _git(repo, "checkout", "main")
    _git(repo, "checkout", "-b", "bad_conflict_branch")
    (repo / "src" / "auth.py").write_text(
        "def verify_token(tok: str) -> bool:\n    return tok.startswith('branch-v2:')\n",
        encoding="utf-8",
    )
    (repo / "src" / "shared.py").write_text("VERSION = '1.1-conflict'\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "feat: rewrite token check on branch", date_iso="2026-04-09T10:00:00+00:00")

    # 3. Advance main on the same lines of auth.py + record a WIP commit and a --no-ff foxtrot merge commit
    _git(repo, "checkout", "main")
    (repo / "src" / "auth.py").write_text(
        "def verify_token(tok: str) -> bool:\n    # TODO: check expiry\n    return tok.startswith('main-v2:')\n",
        encoding="utf-8",
    )
    _git(repo, "add", "src/auth.py")
    _git(repo, "commit", "-m", "WIP: update auth prefix on main", date_iso="2026-04-12T10:00:00+00:00")

    _git(repo, "checkout", "-b", "fix/minor-doc")
    (repo / "docs" / "guide.md").write_text("# Guide\nUpdated docs.\n", encoding="utf-8")
    _git(repo, "add", "docs/guide.md")
    _git(repo, "commit", "-m", "docs: clarify guide", date_iso="2026-04-13T10:00:00+00:00")

    _git(repo, "checkout", "main")
    _git(
        repo,
        "merge",
        "--no-ff",
        "fix/minor-doc",
        "-m",
        "Merge branch 'main' into feat/foxtrot-sim",
        date_iso="2026-04-14T10:00:00+00:00",
    )
    return repo


def _sample_score_result(score: int, grade: HealthGrade = "B") -> ScoreResult:
    """Create a minimal valid `ScoreResult` for audit JSONL ledger tests."""
    return ScoreResult(
        project_name="sample_repo",
        workflow_id="core_audit",
        evaluated_at="2026-04-14T12:00:00+00:00",
        language="python",
        overall_score=score,
        grade=grade,
        category_scores=CategoryScores(
            architecture=score,
            code_quality=score,
            typing=score,
            testing=score,
            dependencies=score,
            security=score,
            documentation=score,
        ),
        summary="Deterministic test audit score.",
    )


def _sample_progress_result() -> ProgressResult:
    """Build a valid `ProgressResult` matching `scaffold_progress_plan` defaults (`T-01`, `T-02`)."""
    return ProgressResult(
        project_name="sample_repo",
        delivery_status="at_risk",
        overall_health_score=64,
        dimension_scores=ProgressDimensionScores(
            schedule_adherence=70,
            git_and_merge_hygiene=52,
            momentum_and_churn=68,
            test_and_quality_trajectory=66,
        ),
        executive_summary="Core implementation is 55% complete; one branch has merge conflicts against main.",
        audit_status_note="Linked audit `core_audit` improved from 75 to 82 (+7).",
        task_assessments=[
            TaskProgressAssessment(
                task_id="T-01",
                name="Core Module & Unit Tests",
                declared_progress=50,
                verified_progress=60,
                status_verdict="on_track",
                evidence_summary="Implemented in `src/auth.py` and `src/api.py`; 1 TODO marker remains.",
            ),
            TaskProgressAssessment(
                task_id="T-02",
                name="End-to-End Verification & Release Readiness",
                declared_progress=0,
                verified_progress=20,
                status_verdict="at_risk",
                evidence_summary="Blocked by unmerged conflict in `bad_conflict_branch`.",
                risk_note="Merge conflict on `src/auth.py` delays integration.",
            ),
        ],
        branch_assessments=[
            BranchIntegrationAssessment(
                branch_name="bad_conflict_branch",
                integration_risk="high",
                merge_recommendation="Rename to `feat/...` and rebase onto `main` resolving `src/auth.py`.",
                conflicting_files=["src/auth.py"],
            )
        ],
        bottlenecks_and_risks=[
            "Branch `bad_conflict_branch` conflicts with `main` in `src/auth.py`.",
            "Concurrent modifications to `src/shared.py` across two active branches.",
        ],
        next_actions=[
            ProgressActionItem(
                priority="P0",
                category="conflict_resolution",
                title="Resolve conflict and rename bad_conflict_branch",
                description="Rebase onto `main`, unify token prefix validation, and rename to `feat/*`.",
                target_files=["src/auth.py"],
                target_branches=["bad_conflict_branch"],
                expected_impact="Unblocks T-02 integration and restores linear trunk hygiene.",
            )
        ],
    )


def test_resolve_progress_result_rel_path_normalization() -> None:
    """Verify `resolve_progress_result_rel_path` avoids duplicate `_progress` suffixes."""
    assert resolve_progress_result_rel_path("reports", "app_progress") == "reports/app_progress.json"
    assert resolve_progress_result_rel_path("reports/", "app") == "reports/app_progress.json"
    assert (
        resolve_progress_result_rel_path("reports", "ignored", "reports/custom_prog.json")
        == "reports/custom_prog.json"
    )


def test_progress_plan_schema_and_security_guards(tmp_path: Path) -> None:
    """Verify date ordering, milestone refs, DAG cycle detection, path containment, and git ref safety."""
    with pytest.raises(ValueError, match="Parent traversal"):
        resolve_bounded_plan_path(tmp_path, "../../etc/passwd")
    with pytest.raises(ValueError, match="escapes workspace root"):
        resolve_bounded_plan_path(tmp_path, "../../outside.yaml")

    with pytest.raises(ValueError, match="Unsafe or malformed Git reference"):
        validate_safe_git_ref("--upload-pack=evil")
    with pytest.raises(ValueError, match="Unsafe or malformed Git reference"):
        validate_safe_git_ref("main..origin/main")

    # Reversed task dates must fail validation
    with pytest.raises(ValidationError, match="planned_start"):
        ProgressPlanDefinition.model_validate(
            {
                "id": "demo",
                "name": "Demo Plan",
                "start_date": "2026-04-01",
                "target_date": "2026-05-01",
                "milestones": [{"id": "M1", "name": "Milestone 1", "due_date": "2026-04-30"}],
                "tasks": [
                    {
                        "id": "T-01",
                        "milestone": "M1",
                        "name": "Bad Dates",
                        "planned_start": "2026-04-20",
                        "planned_end": "2026-04-10",
                    }
                ],
            }
        )

    # Unknown milestone reference must fail validation
    with pytest.raises(ValidationError, match="unknown milestone"):
        ProgressPlanDefinition.model_validate(
            {
                "id": "demo",
                "name": "Demo Plan",
                "start_date": "2026-04-01",
                "target_date": "2026-05-01",
                "milestones": [{"id": "M1", "name": "Milestone 1", "due_date": "2026-04-30"}],
                "tasks": [
                    {
                        "id": "T-01",
                        "milestone": "M99",
                        "name": "Orphan Task",
                        "planned_start": "2026-04-01",
                        "planned_end": "2026-04-10",
                    }
                ],
            }
        )

    # Circular task dependencies must fail validation
    with pytest.raises(ValidationError, match="Circular task dependency"):
        ProgressPlanDefinition.model_validate(
            {
                "id": "demo",
                "name": "Demo Plan",
                "start_date": "2026-04-01",
                "target_date": "2026-05-01",
                "milestones": [{"id": "M1", "name": "Milestone 1", "due_date": "2026-04-30"}],
                "tasks": [
                    {
                        "id": "T-01",
                        "milestone": "M1",
                        "name": "A",
                        "planned_start": "2026-04-01",
                        "planned_end": "2026-04-15",
                        "depends_on": ["T-02"],
                    },
                    {
                        "id": "T-02",
                        "milestone": "M1",
                        "name": "B",
                        "planned_start": "2026-04-10",
                        "planned_end": "2026-04-25",
                        "depends_on": ["T-01"],
                    },
                ],
            }
        )


def test_run_progress_analyze_detects_conflicts_overlaps_violations_and_trajectories(tmp_path: Path) -> None:
    """Verify non-destructive `git merge-tree` conflicts, overlaps, policy checks, and LOC/test history."""
    repo = _create_git_progress_fixture(tmp_path)
    _, rel_plan, _ = scaffold_progress_plan(repo, "dev_progress", source_dir="src", test_dir="tests")
    assert rel_plan == ".pni/progress/dev_progress.yaml"
    _git(repo, "add", ".pni/progress/dev_progress.yaml")
    _git(repo, "commit", "-m", "chore: add progress plan", date_iso="2026-04-15T09:00:00+00:00")

    assert _git(repo, "status", "--porcelain") == ""

    facts = run_progress_analyze(
        repo,
        "dev_progress",
        source_targets=["src"],
        test_targets=["tests"],
        doc_targets=["docs"],
        options=ProgressOptions(lookback_weeks=6, as_of_date="2026-04-15"),
    )

    # Working tree and index MUST remain completely untouched after merge simulation
    assert _git(repo, "status", "--porcelain") == ""

    by_branch = {b.branch_name: b for b in facts.branches}
    assert "feat/clean-api" in by_branch
    assert by_branch["feat/clean-api"].has_conflict is False
    assert by_branch["feat/clean-api"].naming_compliant is True

    assert "bad_conflict_branch" in by_branch
    conflict_br = by_branch["bad_conflict_branch"]
    assert conflict_br.has_conflict is True
    assert "src/auth.py" in conflict_br.conflicting_files
    assert conflict_br.naming_compliant is False

    # Both feat/clean-api and bad_conflict_branch touch src/shared.py
    overlap_map = {ov.file_path: set(ov.branches) for ov in facts.overlapping_file_hotspots}
    assert "src/shared.py" in overlap_map
    assert {"feat/clean-api", "bad_conflict_branch"}.issubset(overlap_map["src/shared.py"])

    # Git governance policy violations: naming, conflict, squash_only merge commit, foxtrot merge, WIP commit
    violation_codes = {v.code for v in facts.policy_violations}
    assert "branch_naming_violation" in violation_codes
    assert "branch_merge_conflict" in violation_codes
    assert "unexpected_merge_commit_on_linear_trunk" in violation_codes
    assert "foxtrot_merge_detected" in violation_codes
    assert "wip_commit_on_trunk" in violation_codes

    # Historical LOC trajectory must exclude 200-line uv.lock and count static test functions
    assert len(facts.trajectory) >= 1
    latest_pt = facts.trajectory[-1]
    assert 0 < latest_pt.source_loc < 50
    assert latest_pt.test_loc > 0
    assert latest_pt.docs_loc > 0
    assert latest_pt.static_test_cases >= 1

    # Task deterministic evidence should detect TODO marker in src/auth.py and matched branch
    t01_ev = next(te for te in facts.task_evidence if te.task_id == "T-01")
    assert t01_ev.stub_todo_count >= 1
    assert t01_ev.has_tests is True
    assert "feat/clean-api" in t01_ev.matched_branches


def test_jsonl_history_ledgers_upsert_same_sha_and_append_on_new_commit(tmp_path: Path) -> None:
    """Verify `.pni/history/audit/*.jsonl` upserts on identical `git_sha` and appends when `HEAD` advances."""
    repo = _create_git_progress_fixture(tmp_path)

    record_audit_history_from_score(repo, "core_audit", _sample_score_result(72, "B"))
    record_audit_history_from_score(repo, "core_audit", _sample_score_result(78, "B"))
    entries_same_sha = read_audit_history(repo, "core_audit")
    assert len(entries_same_sha) == 1
    assert entries_same_sha[0].overall_score == 78

    # Advance HEAD commit and record again -> must append a 2nd entry
    (repo / "docs" / "guide.md").write_text("# Guide\nVersion 3\n", encoding="utf-8")
    _git(repo, "add", "docs/guide.md")
    _git(repo, "commit", "-m", "docs: bump guide v3", date_iso="2026-04-16T10:00:00+00:00")

    record_audit_history_from_score(repo, "core_audit", _sample_score_result(86, "A"))
    entries_two_commits = read_audit_history(repo, "core_audit")
    assert len(entries_two_commits) == 2
    assert [e.overall_score for e in entries_two_commits] == [78, 86]


def test_cli_progress_commands_and_full_stateful_workflow_e2e(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify CLI `progress init/validate`, fail-closed plan immutability (`PRG-02`), and 5-file blueprint."""
    repo = _create_git_progress_fixture(tmp_path)
    monkeypatch.chdir(repo)
    runner = CliRunner()

    # Seed Git-tracked audit history (without SQLite workflow_state.db) to verify non-blocking `based_on`
    record_audit_history_from_score(repo, "core_audit", _sample_score_result(75, "B"))
    (repo / "docs" / "guide.md").write_text("# Guide\nAudit step 2\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "chore: record initial audit ledger", date_iso="2026-04-16T12:00:00+00:00")
    record_audit_history_from_score(repo, "core_audit", _sample_score_result(82, "A"))

    wf_dir = repo / ".pni" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / "core_audit.yaml").write_text(
        "id: core_audit\n"
        "name: Core Software Audit\n"
        "category: audit\n"
        "targets:\n"
        "  root: .\n"
        "  source: [src]\n"
        "  tests: [tests]\n"
        "  docs: [docs]\n"
        "steps:\n"
        "  - id: s1\n"
        "    action: ast_analyze\n"
        "  - id: s2\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )
    wf_yaml = wf_dir / "dev_progress.yaml"
    wf_yaml.write_text(
        "id: dev_progress\n"
        "name: Dev Progress & Git Governance\n"
        "category: progress\n"
        "based_on: core_audit\n"
        "targets:\n"
        "  root: .\n"
        "  source: [src]\n"
        "  tests: [tests]\n"
        "  docs: [docs]\n"
        "steps:\n"
        "  - id: assess\n"
        "    uses: common/progress_assessment\n"
        "    with:\n"
        "      target: dev_progress\n"
        "  - id: report\n"
        "    uses: common/write_progress_report\n"
        "    with:\n"
        "      target: dev_progress\n"
        "      formats: [html]\n",
        encoding="utf-8",
    )

    # 1. Fail-closed before `.pni/progress/dev_progress.yaml` exists
    with pytest.raises(WorkflowPrerequisiteError, match="pni progress init"):
        start_workflow_run("dev_progress", repo)

    # 2. Scaffold & validate via CLI
    res_init = runner.invoke(app, ["progress", "init", "dev_progress"])
    assert res_init.exit_code == 0, res_init.output
    res_val = runner.invoke(app, ["progress", "validate", "dev_progress"])
    assert res_val.exit_code == 0, res_val.output

    # Verify workflow discovery and `workflows show` preflight panel
    discovered = list_workflows(repo, category=WorkflowCategory.PROGRESS)
    assert [w.id for w in discovered] == ["dev_progress"]
    res_list = runner.invoke(app, ["workflows", "list", "-c", "progress"])
    assert res_list.exit_code == 0
    assert "dev_progress" in res_list.output
    res_show = runner.invoke(app, ["workflows", "show", "dev_progress"])
    assert res_show.exit_code == 0
    assert "Progress & Git Governance" in res_show.output

    # Verify stateless ad-hoc execution works as well
    adhoc_res = run_workflow_action_adhoc("dev_progress", "progress_analyze", repo)
    assert adhoc_res is not None
    assert not adhoc_res.has_error
    assert adhoc_res.has_findings is True
    assert "Progress & Git" in adhoc_res.rendered_markdown

    # 3. Start stateful workflow run (succeeds even though SQLite has no `core_audit` run!)
    run_rec = start_workflow_run("dev_progress", repo)
    assert run_rec is not None
    assert run_rec.category == WorkflowCategory.PROGRESS

    # Act-01: progress_analyze
    _, a1, p1 = get_workflow_action(run_rec.run_id, repo)
    assert a1 is not None and a1.action_id == "act-01"
    assert "core_audit" in p1
    ok1, msg1 = push_workflow_action(run_rec.run_id, "act-01", '{"acknowledged": true}', repo)
    assert ok1, msg1

    # Act-02: ai_interpret (evaluates PRG-* and GIT-* rules)
    _, a2, _ = get_workflow_action(run_rec.run_id, repo)
    assert a2 is not None and a2.action_id == "act-02"
    interp = InterpretationInput(
        summary="Assessed schedule and Git governance facts.",
        step_score=64,
        rule_checks=[
            RuleCheckResult(rule_id=rid, status="pass", summary="Verified against Git facts.")
            for rid in a2.rules
        ],
    )
    ok2, msg2 = push_workflow_action(run_rec.run_id, "act-02", interp.model_dump_json(), repo)
    assert ok2, msg2

    # Act-03: emit_progress — verify mid-run `.pni/progress/dev_progress.yaml` mutation is REJECTED (PRG-02)
    _, a3, _ = get_workflow_action(run_rec.run_id, repo)
    assert a3 is not None and a3.action_id == "act-03"
    plan_path = repo / ".pni" / "progress" / "dev_progress.yaml"
    original_plan_bytes = plan_path.read_bytes()
    plan_path.write_text(
        original_plan_bytes.decode("utf-8").replace('status: "todo"', 'status: "done"'),
        encoding="utf-8",
    )

    prog_payload = _sample_progress_result().model_dump_json()
    ok_mutated, msg_mutated = push_workflow_action(run_rec.run_id, "act-03", prog_payload, repo)
    assert not ok_mutated
    assert "modified" in msg_mutated.lower() or "sha-256" in msg_mutated.lower()

    # Restore baseline YAML and re-submit `emit_progress` -> succeeds and writes JSON + JSONL ledger
    plan_path.write_bytes(original_plan_bytes)
    ok3, msg3 = push_workflow_action(run_rec.run_id, "act-03", prog_payload, repo)
    assert ok3, msg3

    emitted_file = repo / "reports" / "dev_progress.json"
    assert emitted_file.is_file()
    res_val_prog = runner.invoke(app, ["validate-progress", str(emitted_file)])
    assert res_val_prog.exit_code == 0, res_val_prog.output

    prog_ledger = read_progress_history(repo, "dev_progress")
    assert len(prog_ledger) == 1
    assert prog_ledger[0].overall_health_score == 64
    assert prog_ledger[0].verified_completion_pct == 40.0

    # Act-04: write_drawlib_report -> materializes 5-chapter `ProgressBlueprint`
    _, a4, p4 = get_workflow_action(run_rec.run_id, repo)
    assert a4 is not None and a4.action_id == "act-04"
    assert "01_schedule_and_milestones.md" in p4
    assert "02_git_methodology_and_conflicts.md" in p4
    assert "03_code_and_test_trajectories.md" in p4
    assert "04_risks_and_next_actions.md" in p4

    bp_files = list((repo / ".pni" / "cache").rglob("*progress_blueprint.json"))
    assert len(bp_files) == 1
    bp_data = json.loads(bp_files[0].read_text(encoding="utf-8"))
    assert len(bp_data["chapters"]) == 5

    # Also test direct blueprint & guide helper APIs
    _, _, _, _ = load_and_validate_progress_plan(repo, "dev_progress")
    persisted_prog = ProgressResult.model_validate_json(emitted_file.read_text(encoding="utf-8"))
    direct_bp = build_progress_blueprint(persisted_prog, target="dev_progress", lang="ja")
    assert len(direct_bp.chapters) == 5
    guide_ja = render_drawlib_report_guide(
        target="dev_progress",
        src_base_dir="reports_src",
        output_dir="reports",
        score_path="reports/dev_progress_score.json",
        facts_path=".pni/cache/dev_progress/facts.json",
        target_root=".",
        source_targets=["src"],
        doc_targets=["docs"],
        workflow_id="dev_progress",
        lang="ja",
        report_kind="progress",
        progress_path="reports/dev_progress.json",
        project_root=repo,
    )
    assert "01_schedule_and_milestones.md" in guide_ja

    # Simulate rendered HTML output and complete Act-04
    html_dir = repo / "reports" / "dev_progress_html"
    html_dir.mkdir(parents=True, exist_ok=True)
    html_index = html_dir / "index.html"
    html_index.write_text("<html><body>Progress Report</body></html>\n", encoding="utf-8")

    rep_done = ReportCompletionInput(
        summary="Generated 5-chapter progress report.",
        generated_files=["reports/dev_progress_html/index.html"],
    )
    ok4, msg4 = push_workflow_action(run_rec.run_id, "act-04", rep_done.model_dump_json(), repo)
    assert ok4, msg4
    assert RunStatus.COMPLETED.value in msg4 or "completed" in msg4.lower()
