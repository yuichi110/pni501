# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for deterministic AST/project actions, composite normalization, and SQLite workflows."""

from __future__ import annotations

import json
from pathlib import Path

from pni._actions import (
    CategoryScores,
    PrimitiveType,
    ScoreResult,
    list_actions,
    load_composite_action,
    run_ast_analyze,
    run_project_inspect,
)
from pni._workflows import (
    RunStatus,
    WorkflowStateDB,
    copy_workflow_templates,
    get_workflow_action,
    list_workflows,
    load_workflow,
    normalize_workflow_steps,
    push_workflow_action,
    start_workflow_run,
)


def test_ast_analyze_deterministic(tmp_path: Path) -> None:
    """Test deterministic AST extraction of typing, docstrings, Any usage, and imports."""
    pkg = tmp_path / "src" / "demo"
    pkg.mkdir(parents=True)

    (pkg / "good.py").write_text(
        '"""Good module."""\n\n'
        "def greet(name: str) -> str:\n"
        '    """Return greeting."""\n'
        "    return f'Hello {name}'\n",
        encoding="utf-8",
    )
    (pkg / "bad.py").write_text(
        "from typing import Any\n"
        "from . import good\n\n"
        "mutable_cache = []\n\n"
        "def untyped(x, y: Any):\n"
        "    global mutable_cache\n"
        "    if x == 1:\n"
        "        pass\n"
        "    elif x == 2:\n"
        "        pass\n"
        "    elif x == 3:\n"
        "        pass\n"
        "    elif x == 4:\n"
        "        pass\n"
        "    elif x == 5:\n"
        "        pass\n"
        "    elif x == 6:\n"
        "        pass\n"
        "    elif x == 7:\n"
        "        pass\n"
        "    elif x == 8:\n"
        "        pass\n"
        "    return x\n",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["src"])
    assert facts.language == "python"
    assert facts.total_files == 2
    assert facts.total_functions == 2
    assert facts.type_safety_coverage_pct == 50.0
    assert len(facts.type_safety_issues) == 1
    assert facts.type_safety_issues[0].symbol == "untyped"
    assert len(facts.weak_type_usages) == 1
    assert facts.weak_type_usages[0].symbol == "untyped"
    assert len(facts.missing_docstrings) >= 2
    assert any(c.symbol == "untyped" for c in facts.complex_functions)
    assert len(facts.global_state_usages) == 1
    assert "demo.good" in facts.internal_import_graph.get("demo.bad", [])


def test_project_inspect_deterministic(tmp_path: Path) -> None:
    """Test deterministic project metadata and lockfile inspection."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-proj"\nversion = "1.2.3"\ndependencies = ["pydantic>=2.0.0", "unpinned-pkg"]\n',
        encoding="utf-8",
    )
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    facts = run_project_inspect(tmp_path)
    assert facts.project_name == "demo-proj"
    assert facts.version == "1.2.3"
    assert facts.language == "python"
    assert facts.build_system == "uv"
    assert "pyproject.toml" in facts.manifest_files
    assert "uv.lock" in facts.lockfiles_found
    assert "pydantic>=2.0.0" in facts.dependencies
    assert "unpinned-pkg" in facts.unpinned_dependencies
    assert facts.has_readme is True


def test_composite_action_normalization(tmp_path: Path) -> None:
    """Test loading composite actions and normalizing workflow steps into primitives."""
    actions = list_actions(tmp_path)
    action_ids = {a.id for a in actions}
    assert "python_ast_audit" in action_ids
    assert "emit_score" in action_ids
    assert "write_drawlib_report" in action_ids

    comp = load_composite_action("python_ast_audit", tmp_path)
    assert comp is not None
    assert len(comp.primitives) == 2

    # Before copying workflow templates, list_workflows returns empty
    assert list_workflows(tmp_path) == []

    # Copy templates to .pni/workflows/
    copy_workflow_templates(tmp_path)
    workflows = list_workflows(tmp_path)
    wf_ids = {w.id for w in workflows}
    assert "full_audit" in wf_ids
    assert "quick_check" in wf_ids

    loaded = load_workflow("full_audit", tmp_path)
    assert loaded is not None
    wf_info, wf_def = loaded
    assert wf_def.targets.source == ["src"]
    assert wf_info.outputs.facts == ".pni/cache/full_audit/facts.json"
    assert wf_info.outputs.score == "reports/full_audit_score.json"
    assert wf_info.outputs.report == "reports/full_audit.pdf"

    primitives = normalize_workflow_steps(wf_def, tmp_path)
    prim_types = [p.type for p in primitives]
    assert PrimitiveType.PROJECT_INSPECT in prim_types
    assert PrimitiveType.AST_ANALYZE in prim_types
    assert PrimitiveType.AI_INTERPRET in prim_types
    assert PrimitiveType.EMIT_SCORE in prim_types
    assert primitives[-1].type == PrimitiveType.WRITE_DRAWLIB_REPORT
    assert primitives[-1].params["src_dir"] == "reports_src"
    assert primitives[-1].params["output_dir"] == "reports"
    assert primitives[-1].params["score_path"] == "reports/full_audit_score.json"


def test_stateful_workflow_pull_push_lifecycle(tmp_path: Path) -> None:
    """Test full start -> get-action -> push-action SQLite state machine lifecycle."""
    (tmp_path / "app").mkdir(parents=True)
    (tmp_path / "app" / "core.py").write_text(
        '"""Core module."""\n\ndef calc(x: int) -> int:\n    """Calc."""\n    return x * 2\n',
        encoding="utf-8",
    )

    actions_dir = tmp_path / ".pni" / "actions"
    workflows_dir = tmp_path / ".pni" / "workflows"
    actions_dir.mkdir(parents=True)
    workflows_dir.mkdir(parents=True)

    (actions_dir / "custom_check.yaml").write_text(
        "id: custom_check\n"
        "name: Custom Check Action\n"
        "rules:\n"
        "  - common/architecture\n"
        "primitives:\n"
        "  - type: ast_analyze\n"
        "  - type: ai_interpret\n"
        "    prompt: Custom interpretation prompt.\n",
        encoding="utf-8",
    )

    (workflows_dir / "custom_wf.yaml").write_text(
        "id: custom_wf\n"
        "name: Custom Workflow\n"
        "targets:\n"
        "  source:\n"
        "    - app\n"
        "  tests:\n"
        "    - spec\n"
        "  docs:\n"
        "    - docs/ARCH.md\n"
        "outputs:\n"
        "  facts: .pni/cache/custom_facts.json\n"
        "  score: .pni/custom_score.json\n"
        "  report: docs/pni_report\n"
        "steps:\n"
        "  - id: step1\n"
        "    uses: custom_check\n"
        "  - id: step2\n"
        "    uses: emit_score\n"
        "  - id: step3\n"
        "    uses: write_drawlib_report\n",
        encoding="utf-8",
    )

    assert start_workflow_run("nonexistent_wf", tmp_path) is None
    run = start_workflow_run("custom_wf", tmp_path)
    assert run is not None
    assert (tmp_path / ".pni" / "cache" / "workflow_state.db").exists()
    assert (tmp_path / ".pni" / "cache" / ".gitignore").is_file()
    assert (tmp_path / ".pni" / "cache" / "CACHEDIR.TAG").is_file()

    # Step 1 (act-01): ast_analyze
    _, act1, guide1 = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None
    assert act1.action_id == "act-01"
    assert act1.primitive_type == PrimitiveType.AST_ANALYZE
    assert "Deterministic AST Facts" in guide1
    assert (tmp_path / ".pni" / "cache" / "custom_facts.json").exists()

    # Out-of-order push must be rejected
    ok_wrong, msg_wrong = push_workflow_action(run.run_id, "act-02", "{}", tmp_path)
    assert ok_wrong is False
    assert "Action mismatch" in msg_wrong

    ok1, _ = push_workflow_action(run.run_id, "act-01", '{"acknowledged": true}', tmp_path)
    assert ok1 is True

    # Step 2 (act-02): ai_interpret
    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None
    assert act2.action_id == "act-02"
    assert "Custom interpretation prompt." in guide2

    # Invalid JSON schema must be rejected
    ok_bad_interp, _ = push_workflow_action(run.run_id, "act-02", '{"wrong": 1}', tmp_path)
    assert ok_bad_interp is False

    interp_payload = json.dumps(
        {
            "summary": "Clean architecture verified.",
            "findings": [],
            "suggested_scores": {"architecture": 95},
        }
    )
    ok2, _ = push_workflow_action(run.run_id, "act-02", interp_payload, tmp_path)
    assert ok2 is True

    # Step 3 (act-03): emit_score
    _, act3, guide3 = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None
    assert act3.action_id == "act-03"
    assert "Clean architecture verified." in guide3

    score_payload = ScoreResult(
        project_name="demo",
        workflow_id="custom_wf",
        language="python",
        overall_score=95,
        category_scores=CategoryScores(
            architecture=95,
            code_quality=95,
            typing=100,
            testing=90,
            dependencies=95,
            documentation=95,
        ),
        findings=[],
        summary="Strong project health.",
    ).model_dump_json()
    ok3, _ = push_workflow_action(run.run_id, "act-03", score_payload, tmp_path)
    assert ok3 is True
    assert (tmp_path / ".pni" / "custom_score.json").exists()

    # Step 4 (act-04): write_drawlib_report
    _, act4, guide4 = get_workflow_action(run.run_id, tmp_path)
    assert act4 is not None
    assert act4.action_id == "act-04"
    assert "READ Score" in guide4
    assert "WRITE or INCREMENTALLY UPDATE drawlib Report" in guide4

    # Missing report file must be rejected
    bad_rep = json.dumps({"generated_files": ["docs/pni_report/missing.png"], "summary": "Done"})
    ok_bad_rep, _ = push_workflow_action(run.run_id, "act-04", bad_rep, tmp_path)
    assert ok_bad_rep is False

    report_dir = tmp_path / "docs" / "pni_report"
    report_dir.mkdir(parents=True)
    (report_dir / "overview.png").write_bytes(b"PNGDATA")
    good_rep = json.dumps({"generated_files": ["docs/pni_report/overview.png"], "summary": "Generated chart"})
    ok4, msg4 = push_workflow_action(run.run_id, "act-04", good_rep, tmp_path)
    assert ok4 is True
    assert "COMPLETED" in msg4

    # Subsequent get-action shows COMPLETED
    _, act_done, done_guide = get_workflow_action(run.run_id, tmp_path)
    assert act_done is None
    assert "COMPLETED" in done_guide

    db = WorkflowStateDB(tmp_path)
    final_run = db.get_run(run.run_id)
    assert final_run is not None
    assert final_run.status == RunStatus.COMPLETED


def test_action_with_target_interpolation_and_score_propagation(tmp_path: Path) -> None:
    """Test Action YAML placeholder interpolation and score_path propagation without workflow outputs."""
    workflows_dir = tmp_path / ".pni" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "example_clean.yaml").write_text(
        "id: example_clean\n"
        "name: Example Clean\n"
        "steps:\n"
        "  - id: output_score\n"
        "    uses: emit_score\n"
        "    with:\n"
        "      target: python_clean\n"
        "  - id: create_report\n"
        "    uses: write_drawlib_report\n"
        "    with:\n"
        "      lang: ja\n",
        encoding="utf-8",
    )

    loaded = load_workflow("example_clean", tmp_path)
    assert loaded is not None
    wf_info, wf_def = loaded
    prims = normalize_workflow_steps(wf_def, tmp_path)
    assert len(prims) == 2
    assert prims[0].params["score_path"] == "reports/python_clean_score.json"
    # Even though create_report omitted target, emitted score_path propagated forward
    assert prims[1].params["score_path"] == "reports/python_clean_score.json"
    assert wf_info.outputs.score == "reports/python_clean_score.json"
    assert wf_info.outputs.report == "reports/example_clean.pdf"
