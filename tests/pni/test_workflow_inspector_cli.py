# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for workflow status filtering, action payload inspection, and run cancellation CLI/DB."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pni._actions import CategoryScores, PrimitiveStep, PrimitiveType, ScoreResult
from pni._workflows import (
    RunStatus,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowRunRecord,
    WorkflowStateDB,
    get_workflow_action,
    inspect_base_audit_status,
    load_workflow,
    push_workflow_action,
    query_workflow_run_summaries,
    resolve_run_actions_by_selector,
    resolve_run_by_id_or_workflow,
    start_workflow_run,
)
from pni.cli import app

runner = CliRunner()


def _extract_run_id(stdout: str) -> str:
    """Extract a `wf-xxxxxxxx` run ID from CLI stdout."""
    match = re.search(r"(wf-[0-9a-f]{8})", stdout)
    assert match is not None
    return match.group(1)


def _require_run(db: WorkflowStateDB, run_id: str) -> WorkflowRunRecord:
    """Fetch a WorkflowRunRecord from SQLite and assert it exists."""
    rec = db.get_run(run_id)
    assert rec is not None
    return rec


def _setup_inspector_project(tmp_path: Path) -> None:
    """Create a minimal Python workspace with custom composite action and workflow definitions."""
    pkg = tmp_path / "src" / "demo"
    pkg.mkdir(parents=True)
    (pkg / "calc.py").write_text(
        '"""Demo module."""\n\ndef double(x: int) -> int:\n    """Double."""\n    return x * 2\n',
        encoding="utf-8",
    )

    actions_dir = tmp_path / ".pni" / "actions"
    workflows_dir = tmp_path / ".pni" / "workflows"
    actions_dir.mkdir(parents=True)
    workflows_dir.mkdir(parents=True)

    (actions_dir / "custom_audit.yaml").write_text(
        "id: custom_audit\n"
        "name: Custom Audit Composite\n"
        "rules:\n"
        "  - common/architecture\n"
        "primitives:\n"
        "  - type: ast_analyze\n"
        "  - type: ai_interpret\n"
        "    prompt: Interpret AST findings.\n",
        encoding="utf-8",
    )

    (workflows_dir / "demo_wf.yaml").write_text(
        "id: demo_wf\n"
        "name: Demo Audit Workflow\n"
        "targets:\n"
        "  source:\n"
        "    - src\n"
        "outputs:\n"
        "  facts: .pni/cache/demo_wf/facts.json\n"
        "  score: reports/demo_wf_score.json\n"
        "steps:\n"
        "  - id: s1\n"
        "    uses: custom_audit\n"
        "  - id: s2\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )


def _complete_demo_run(project_root: Path, run_id: str) -> None:
    """Step a `demo_wf` run (ast_analyze -> ai_interpret -> emit_score) to completion."""
    get_workflow_action(run_id, project_root)
    ok1, _ = push_workflow_action(run_id, "act-01", '{"acknowledged": true}', project_root)
    assert ok1 is True

    get_workflow_action(run_id, project_root)
    interp_payload = json.dumps(
        {
            "summary": "Clean module structure.",
            "step_score": 88,
            "rule_checks": [
                {
                    "rule_id": "common/architecture",
                    "status": "pass",
                    "evidence": "src/demo/calc.py",
                    "summary": "Typed function.",
                }
            ],
            "findings": [
                {
                    "severity": "low",
                    "category": "code_quality",
                    "rule_id": "common/architecture",
                    "description": "Minor style note.",
                    "file_path": "src/demo/calc.py",
                    "evidence": "calc.py:3",
                    "recommendation": "Keep docstrings concise.",
                }
            ],
            "action_items": [],
        }
    )
    ok2, _ = push_workflow_action(run_id, "act-02", interp_payload, project_root)
    assert ok2 is True

    get_workflow_action(run_id, project_root)
    score_payload = ScoreResult(
        project_name="demo",
        workflow_id="demo_wf",
        workflow_run_id=run_id,
        language="python",
        overall_score=91,
        grade="S",
        summary="Demo executive summary.",
        category_scores=CategoryScores(
            architecture=92,
            code_quality=90,
            typing=95,
            testing=88,
            dependencies=92,
            documentation=90,
            security=94,
        ),
    ).model_dump_json()
    ok3, _ = push_workflow_action(run_id, "act-03", score_payload, project_root)
    assert ok3 is True


def test_state_db_cancellation_and_engine_guards(tmp_path: Path) -> None:
    """Test cancelling unfinished runs, guarding get/push on cancelled runs, and supersede behavior."""
    _setup_inspector_project(tmp_path)
    db = WorkflowStateDB(tmp_path)
    assert db.get_actions_map([]) == {}
    assert db.cancel_workflow_run("wf-missing0") is None

    # 1. Start run1, complete step 1, then cancel run1
    run1 = start_workflow_run("demo_wf", tmp_path)
    assert run1 is not None
    get_workflow_action(run1.run_id, tmp_path)
    ok_ack, _ = push_workflow_action(run1.run_id, "act-01", '{"acknowledged": true}', tmp_path)
    assert ok_ack is True

    cancelled = db.cancel_workflow_run(run1.run_id)
    assert cancelled is not None
    assert cancelled.status == RunStatus.CANCELLED
    # Idempotent when already cancelled
    assert db.cancel_workflow_run(run1.run_id) is not None

    actions1 = db.get_actions(run1.run_id)
    assert actions1[0].status == RunStatus.COMPLETED
    assert actions1[1].status == RunStatus.CANCELLED
    assert actions1[2].status == RunStatus.CANCELLED

    # Guard: get_workflow_action & push_workflow_action reject cancelled runs without completing them
    r_after, act_after, msg_get = get_workflow_action(run1.run_id, tmp_path)
    assert r_after is None
    assert act_after is None
    assert "cancelled" in msg_get
    assert _require_run(db, run1.run_id).status == RunStatus.CANCELLED

    ok_push, msg_push = push_workflow_action(run1.run_id, "act-02", "{}", tmp_path)
    assert ok_push is False
    assert "cancelled" in msg_push

    # Base audit status reports cancelled run clearly when no completed run exists yet
    mig_wf = WorkflowDefinition(
        id="demo_mig",
        name="Demo Migration",
        category=WorkflowCategory.MIGRATION,
        based_on="demo_wf",
        steps=[],
    )
    ready_run, err_msg = inspect_base_audit_status(mig_wf, tmp_path)
    assert ready_run is None
    assert err_msg is not None and "pni workflows start demo_wf" in err_msg

    # 2. Start run2 (left abandoned), then start run3 and complete run3
    run2 = start_workflow_run("demo_wf", tmp_path)
    run3 = start_workflow_run("demo_wf", tmp_path)
    assert run2 is not None and run3 is not None
    _complete_demo_run(tmp_path, run3.run_id)

    # Completed run cannot be cancelled
    with pytest.raises(ValueError, match="already completed"):
        db.cancel_workflow_run(run3.run_id)

    # Start run4 AFTER completed run3 -> run4 is a newer active run, NOT superseded!
    run4 = start_workflow_run("demo_wf", tmp_path)
    assert run4 is not None

    superseded = db.cancel_superseded_runs()
    superseded_ids = [r.run_id for r in superseded]
    assert run2.run_id in superseded_ids
    assert run4.run_id not in superseded_ids
    assert _require_run(db, run4.run_id).status == RunStatus.IN_PROGRESS

    # Starting run5 with supersede=True cancels run4 automatically
    run5 = start_workflow_run("demo_wf", tmp_path, supersede=True)
    assert run5 is not None
    assert _require_run(db, run4.run_id).status == RunStatus.CANCELLED

    # Cancel run5 as well; --latest should prefer completed run3 over cancelled run5
    db.cancel_workflow_run(run5.run_id)
    latest_summaries = query_workflow_run_summaries(db, latest_per_workflow=True)
    assert len(latest_summaries) == 1
    assert latest_summaries[0].run_id == run3.run_id

    resolved = resolve_run_by_id_or_workflow(db, "demo_wf")
    assert resolved is not None and resolved.run_id == run3.run_id


def test_inspector_selector_and_pentest_brief_note(tmp_path: Path) -> None:
    """Test selector edge cases and brief_note extraction for web_pentest deterministic facts."""
    _setup_inspector_project(tmp_path)
    loaded = load_workflow("demo_wf", tmp_path)
    assert loaded is not None
    _, wf_def = loaded

    db = WorkflowStateDB(tmp_path)
    prim_steps = [
        PrimitiveStep(
            id="p1",
            type=PrimitiveType.WEB_PENTEST,
            name="Web Pentest",
            source_action="common/web_penetration_audit",
        ),
        PrimitiveStep(
            id="p2",
            type=PrimitiveType.AI_INTERPRET,
            name="Interpret Pentest",
            source_action="common/web_penetration_audit",
        ),
    ]
    rec = db.create_run(wf_def, prim_steps)
    db.mark_action_in_progress(
        rec.run_id,
        "act-01",
        deterministic_output_json=json.dumps({"status": "failed", "findings": [{"id": 1}, {"id": 2}]}),
    )
    db.complete_action(rec.run_id, "act-01", '{"acknowledged": true}')
    db.complete_action(
        rec.run_id,
        "act-02",
        json.dumps({"summary": "2 findings", "step_score": 45, "findings": [{"id": 1}, {"id": 2}]}),
    )
    db.complete_workflow_run(rec.run_id)

    actions = db.get_actions(rec.run_id)
    with pytest.raises(ValueError, match="Empty action selector"):
        resolve_run_actions_by_selector(actions, "   ")

    with pytest.raises(ValueError, match="Available action IDs"):
        resolve_run_actions_by_selector(actions, "nonexistent_step")

    # Both primitives match composite leaf name 'web_penetration_audit' when unfiltered
    both = resolve_run_actions_by_selector(actions, "web_penetration_audit")
    assert len(both) == 2

    det_only = resolve_run_actions_by_selector(actions, "web_penetration_audit", prefer_deterministic=True)
    assert len(det_only) == 1 and det_only[0].primitive_type == PrimitiveType.WEB_PENTEST

    ai_only = resolve_run_actions_by_selector(actions, "web_penetration_audit", prefer_agent_input=True)
    assert len(ai_only) == 1 and ai_only[0].primitive_type == PrimitiveType.AI_INTERPRET


def test_cli_status_inspect_and_cancel_commands(tmp_path: Path) -> None:
    """Test `pni workflows status`, `inspect-action`, `cancel`, and `start --supersede` via CLI."""
    _setup_inspector_project(tmp_path)
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)

        # Empty DB state
        res_empty_json = runner.invoke(app, ["workflows", "status", "--json"])
        assert res_empty_json.exit_code == 0
        assert json.loads(res_empty_json.stdout) == []

        res_inspect_no_db = runner.invoke(app, ["workflows", "inspect-action", "demo_wf", "act-01"])
        assert res_inspect_no_db.exit_code == 1

        res_cancel_no_db = runner.invoke(app, ["workflows", "cancel", "--superseded"])
        assert res_cancel_no_db.exit_code == 0

        # Start orphaned run1, then start run2 (checks warning note about unfinished run1)
        res_s1 = runner.invoke(app, ["workflows", "start", "demo_wf"])
        assert res_s1.exit_code == 0
        run1_id = _extract_run_id(res_s1.stdout)

        res_s2 = runner.invoke(app, ["workflows", "start", "demo_wf"])
        assert res_s2.exit_code == 0
        assert "Older unfinished run(s) exist" in res_s2.stdout
        run2_id = _extract_run_id(res_s2.stdout)

        _complete_demo_run(tmp_path, run2_id)

        # Status filtering: -s in_progress finds run1
        res_in_prog = runner.invoke(app, ["workflows", "status", "-s", "in_progress", "--json"])
        assert res_in_prog.exit_code == 0
        in_prog_data = json.loads(res_in_prog.stdout)
        assert len(in_prog_data) == 1
        assert in_prog_data[0]["run_id"] == run1_id
        assert in_prog_data[0]["progress_label"] == "0/3"

        # Cancel superseded runs via CLI -> cancels run1
        res_cancel_sup = runner.invoke(app, ["workflows", "cancel", "--superseded", "-w", "demo_wf"])
        assert res_cancel_sup.exit_code == 0
        assert run1_id in res_cancel_sup.stdout

        # Re-running cancel --superseded reports nothing left
        res_cancel_sup2 = runner.invoke(app, ["workflows", "cancel", "--superseded"])
        assert res_cancel_sup2.exit_code == 0
        assert "No superseded" in res_cancel_sup2.stdout

        # Cancel CLI argument validation errors
        assert runner.invoke(app, ["workflows", "cancel"]).exit_code == 1
        assert runner.invoke(app, ["workflows", "cancel", run2_id, "--superseded"]).exit_code == 1
        assert runner.invoke(app, ["workflows", "cancel", run2_id]).exit_code == 1
        assert runner.invoke(app, ["workflows", "cancel", "wf-00000000"]).exit_code == 1

        # Status --latest (table & JSON) shows completed run2 (3/3)
        res_latest = runner.invoke(app, ["workflows", "status", "--latest"])
        assert res_latest.exit_code == 0
        assert run2_id in res_latest.stdout
        assert "3/3" in res_latest.stdout

        # Single-run detail status by workflow_id (both Rich table and --json)
        res_detail = runner.invoke(app, ["workflows", "status", "demo_wf"])
        assert res_detail.exit_code == 0
        assert "score=88, findings=1" in res_detail.stdout
        assert "overall=91/100 (S)" in res_detail.stdout

        res_detail_json = runner.invoke(app, ["workflows", "status", "demo_wf", "--json"])
        assert res_detail_json.exit_code == 0
        detail_obj = json.loads(res_detail_json.stdout)
        assert detail_obj["run"]["run_id"] == run2_id
        assert len(detail_obj["actions"]) == 3

        # inspect-action: Markdown mode, --deterministic, --agent-input, --json, and -o <file>
        res_md = runner.invoke(app, ["workflows", "inspect-action", "demo_wf", "custom_audit"])
        assert res_md.exit_code == 0
        assert "# Inspected Workflow Step(s):" in res_md.stdout
        assert "Deterministic Output JSON" in res_md.stdout
        assert "Agent Input JSON" in res_md.stdout

        res_det = runner.invoke(
            app, ["workflows", "inspect-action", "demo_wf", "custom_audit", "--deterministic"]
        )
        assert res_det.exit_code == 0
        det_json = json.loads(res_det.stdout)
        assert det_json["language"] == "python"
        assert det_json["total_files"] == 1

        out_path = tmp_path / "exported_agent_input.json"
        res_ai = runner.invoke(
            app,
            [
                "workflows",
                "inspect-action",
                run2_id,
                "custom_audit",
                "--agent-input",
                "-o",
                str(out_path),
            ],
        )
        assert res_ai.exit_code == 0
        assert out_path.exists()
        saved_ai = json.loads(out_path.read_text(encoding="utf-8"))
        assert saved_ai["step_score"] == 88

        res_json_mode = runner.invoke(
            app, ["workflows", "inspect-action", "demo_wf", "emit_score", "--json"]
        )
        assert res_json_mode.exit_code == 0
        parsed_items = json.loads(res_json_mode.stdout)
        assert len(parsed_items) == 1
        assert parsed_items[0]["agent_input"]["overall_score"] == 91

        # inspect-action error cases
        assert (
            runner.invoke(
                app,
                ["workflows", "inspect-action", "demo_wf", "act-02", "--agent-input", "--deterministic"],
            ).exit_code
            == 1
        )
        assert runner.invoke(app, ["workflows", "inspect-action", "unknown_wf", "act-01"]).exit_code == 1
        assert runner.invoke(app, ["workflows", "inspect-action", "demo_wf", "bad_step"]).exit_code == 1
        # act-02 (ai_interpret) has no deterministic_output_json
        assert (
            runner.invoke(
                app, ["workflows", "inspect-action", "demo_wf", "act-02", "--deterministic"]
            ).exit_code
            == 1
        )

        # Start run3, cancel it explicitly by run_id, then start run4 & run5 (--supersede)
        res_s3 = runner.invoke(app, ["workflows", "start", "demo_wf"])
        run3_id = _extract_run_id(res_s3.stdout)
        res_c3 = runner.invoke(app, ["workflows", "cancel", run3_id])
        assert res_c3.exit_code == 0

        res_s4 = runner.invoke(app, ["workflows", "start", "demo_wf"])
        run4_id = _extract_run_id(res_s4.stdout)
        res_s5 = runner.invoke(app, ["workflows", "start", "demo_wf", "--supersede"])
        assert res_s5.exit_code == 0
        assert "Older unfinished run(s) exist" not in res_s5.stdout
        run5_id = _extract_run_id(res_s5.stdout)

        db = WorkflowStateDB(tmp_path)
        assert _require_run(db, run4_id).status == RunStatus.CANCELLED
        assert _require_run(db, run5_id).status == RunStatus.IN_PROGRESS
    finally:
        os.chdir(original_cwd)
