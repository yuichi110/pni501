# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test pni CLI."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pni._actions import CategoryScores, ScoreResult
from pni.cli import app

runner = CliRunner()


def test_cli_version(tmp_path: Path) -> None:
    """Test 'pni version', 'pni --version', 'pni -V', and 'pni cache clean' commands."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "pni501" in result.stdout
    assert "0.2.0" in result.stdout

    for flag in ("--version", "-V"):
        flag_res = runner.invoke(app, [flag])
        assert flag_res.exit_code == 0
        assert "pni501 0.2.0" in flag_res.stdout

    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        cache_sub = tmp_path / ".pni" / "cache" / "full_audit"
        cache_sub.mkdir(parents=True)
        (cache_sub / "facts.json").write_text("{}", encoding="utf-8")
        clean_res = runner.invoke(app, ["cache", "clean"])
        assert clean_res.exit_code == 0
        assert not cache_sub.exists()
        assert (tmp_path / ".pni" / "cache" / ".gitignore").is_file()
    finally:
        os.chdir(original_cwd)


def test_cli_default() -> None:
    """Test invoking pni without subcommands."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Project Nemesis Index" in result.stdout
    assert "pni --help" in result.stdout


def test_cli_rules_list() -> None:
    """Test 'pni rules list'."""
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    assert "common/architecture" in result.stdout
    assert "python/testing" in result.stdout


def test_cli_rules_show() -> None:
    """Test 'pni rules show' with existing and non-existing rules."""
    result = runner.invoke(app, ["rules", "show", "testing"])
    assert result.exit_code == 0
    assert "Testing Standards (Python)" in result.stdout

    result_fail = runner.invoke(app, ["rules", "show", "nonexistent"])
    assert result_fail.exit_code == 1


def test_cli_workflows_require_init(tmp_path: Path) -> None:
    """Test 'pni workflows' commands require .pni/workflows/ to be initialized."""
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        res_list_no_init = runner.invoke(app, ["workflows", "list"])
        assert res_list_no_init.exit_code == 1

        res_start_no_init = runner.invoke(app, ["workflows", "start", "full_audit"])
        assert res_start_no_init.exit_code == 1

        res_status_empty = runner.invoke(app, ["workflows", "status"])
        assert res_status_empty.exit_code == 0

        # Initialize project
        runner.invoke(app, ["init", "--lang", "python"])

        res_list = runner.invoke(app, ["workflows", "list"])
        assert res_list.exit_code == 0
        assert "full_audit" in res_list.stdout
        assert "quick_check" in res_list.stdout

        res_show = runner.invoke(app, ["workflows", "show", "full_audit"])
        assert res_show.exit_code == 0
        assert "Targets:" in res_show.stdout
        assert "Outputs:" in res_show.stdout
        assert "ast_analyze" in res_show.stdout
        assert "emit_score" in res_show.stdout
        assert "write_drawlib_report" in res_show.stdout

        res_fail = runner.invoke(app, ["workflows", "show", "unknown_wf"])
        assert res_fail.exit_code == 1
    finally:
        os.chdir(original_cwd)


def test_cli_stateful_workflow_commands(tmp_path: Path) -> None:
    """Test 'pni workflows start / get-action / push-action / status' CLI commands."""
    src_pkg = tmp_path / "src" / "sample"
    src_pkg.mkdir(parents=True)
    (src_pkg / "mod.py").write_text(
        '"""Sample module."""\n\ndef add(a: int, b: int) -> int:\n    """Add."""\n    return a + b\n',
        encoding="utf-8",
    )

    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["init", "--lang", "python"])

        # Create a compact 2-step workflow (ast_analyze -> emit_score) for CLI verification
        (tmp_path / ".pni" / "workflows" / "mini.yaml").write_text(
            "id: mini\n"
            "name: Mini Score Workflow\n"
            "steps:\n"
            "  - id: s1\n"
            "    action: ast_analyze\n"
            "  - id: s2\n"
            "    uses: emit_score\n",
            encoding="utf-8",
        )

        res_missing = runner.invoke(app, ["workflows", "start", "missing_wf"])
        assert res_missing.exit_code == 1

        res_start = runner.invoke(app, ["workflows", "start", "mini"])
        assert res_start.exit_code == 0
        match = re.search(r"(wf-[0-9a-f]{8})", res_start.stdout)
        assert match is not None
        run_id = match.group(1)

        # Unknown run ID errors cleanly
        assert runner.invoke(app, ["workflows", "get-action", "wf-00000000"]).exit_code == 1
        assert runner.invoke(app, ["workflows", "status", "wf-00000000"]).exit_code == 1

        # Action 1: confirm_plan (presents validated Mermaid DAG)
        res_get1 = runner.invoke(app, ["workflows", "get-action", run_id])
        assert res_get1.exit_code == 0
        assert "act-01" in res_get1.stdout
        assert "flowchart TD" in res_get1.stdout

        res_push1 = runner.invoke(app, ["workflows", "push-action", run_id, "act-01", '{"approved": true}'])
        assert res_push1.exit_code == 0

        # Auto-Advance runs act-02 (ast_analyze) automatically -> lands on act-03 (emit_score)
        res_get2 = runner.invoke(app, ["workflows", "get-action", run_id])
        assert res_get2.exit_code == 0
        assert "act-03" in res_get2.stdout
        assert (tmp_path / ".pni" / "cache" / "mini" / "facts.json").exists()

        score_file = tmp_path / "payload_score.json"
        score_file.write_text(
            json.dumps(
                {
                    "overall_score": 96,
                    "category_scores": {
                        "architecture": 96,
                        "code_quality": 96,
                        "typing": 100,
                        "testing": 90,
                        "dependencies": 96,
                        "security": 95,
                        "documentation": 98,
                    },
                    "summary": "All checks passed.",
                }
            ),
            encoding="utf-8",
        )

        # Non-existent --file errors cleanly
        res_no_file = runner.invoke(app, ["workflows", "push-action", run_id, "act-03", "--file", "nope.json"])
        assert res_no_file.exit_code == 1

        res_push2 = runner.invoke(app, ["workflows", "push-action", run_id, "act-03", "--file", str(score_file)])
        assert res_push2.exit_code == 0
        assert "COMPLETED" in res_push2.stdout

        emitted = json.loads((tmp_path / "pni_report" / "mini_score.json").read_text(encoding="utf-8"))
        assert emitted["overall_score"] == 96
        assert (tmp_path / "pni_report" / "mini_summary.json").is_file()
        assert (tmp_path / "pni_report" / "mini_findings.sarif").is_file()

        # Status commands
        res_status_list = runner.invoke(app, ["workflows", "status"])
        assert res_status_list.exit_code == 0
        assert run_id in res_status_list.stdout

        res_status_one = runner.invoke(app, ["workflows", "status", run_id])
        assert res_status_one.exit_code == 0
        assert "completed" in res_status_one.stdout
    finally:
        os.chdir(original_cwd)


def test_cli_instructions() -> None:
    """Test 'pni instructions' and alias 'pni instruction'."""
    res1 = runner.invoke(app, ["instructions"])
    assert res1.exit_code == 0
    assert "PNI (Project Nemesis Index) Agent Instructions" in res1.stdout

    res2 = runner.invoke(app, ["instruction"])
    assert res2.exit_code == 0
    assert "PNI (Project Nemesis Index) Agent Instructions" in res2.stdout


def test_cli_init(tmp_path: Path) -> None:
    """Test 'pni init' command execution in a directory."""
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["init", "--lang", "python"])
        assert result.exit_code == 0
        assert "Successfully initialized" in result.stdout
        assert (tmp_path / ".pni" / "rules" / "python" / "testing.md").exists()
        assert (tmp_path / ".pni" / "actions" / "python_ast_audit.yaml").exists()
        assert (tmp_path / ".pni" / "workflows" / "full_audit.yaml").exists()

        # Re-run without force
        result_again = runner.invoke(app, ["init"])
        assert "already initialized" in result_again.stdout
    finally:
        os.chdir(original_cwd)


def test_cli_validate_score(tmp_path: Path) -> None:
    """Test 'pni validate-score' on language-grouped score files and invalid files."""
    clean_score = tmp_path / "reports" / "python" / "lib_clean_score.json"
    messy_score = tmp_path / "reports" / "java" / "api_spring_messy_score.json"
    clean_score.parent.mkdir(parents=True, exist_ok=True)
    messy_score.parent.mkdir(parents=True, exist_ok=True)

    clean_score.write_text(
        ScoreResult(
            project_name="metrics-kit",
            workflow_id="py_lib_clean",
            language="python",
            overall_score=98,
            category_scores=CategoryScores(
                architecture=98,
                code_quality=98,
                typing=100,
                testing=96,
                dependencies=98,
                documentation=98,
            ),
            findings=[],
            summary="Clean Python library score.",
        ).model_dump_json(),
        encoding="utf-8",
    )
    messy_score.write_text(
        ScoreResult(
            project_name="legacy-billing-service",
            workflow_id="java_api_spring_messy",
            language="java",
            overall_score=38,
            category_scores=CategoryScores(
                architecture=35,
                code_quality=40,
                typing=45,
                testing=30,
                dependencies=38,
                documentation=40,
            ),
            findings=[],
            summary="Legacy Spring service score.",
        ).model_dump_json(),
        encoding="utf-8",
    )

    res_clean = runner.invoke(app, ["validate-score", str(clean_score)])
    assert res_clean.exit_code == 0
    assert "Valid ScoreResult" in res_clean.stdout

    res_messy = runner.invoke(app, ["validate-score", str(messy_score)])
    assert res_messy.exit_code == 0
    assert "Valid ScoreResult" in res_messy.stdout

    bad_file = tmp_path / "bad_score.json"
    bad_file.write_text('{"invalid": true}', encoding="utf-8")
    res_bad = runner.invoke(app, ["validate-score", str(bad_file)])
    assert res_bad.exit_code == 1

    res_missing = runner.invoke(app, ["validate-score", str(tmp_path / "missing.json")])
    assert res_missing.exit_code == 1


def test_auto_approval_friendly_cli_output_pull_and_next_options(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify -o/--output, start --pull, push-action --next, and rewind --pull -o avoid shell pipes/redirects."""
    src_dir = tmp_path / "src" / "mini"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text('"""Mini pkg."""\n', encoding="utf-8")
    (src_dir / "calc.py").write_text('"""Calc."""\n\n\ndef inc(x: int) -> int:\n    """Inc."""\n    return x + 1\n')
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "mini"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Mini\n\n## Usage\n\nSimple package.\n", encoding="utf-8")
    wf_dir = tmp_path / ".pni" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "pipe_free.yaml").write_text(
        """id: pipe_free
name: Pipe-Free Single Command Audit
targets:
  root: "."
  source: ["src"]
steps:
  - id: inspect
    uses: repo_structure_audit
  - id: score
    uses: emit_score
    needs: [inspect]
    with:
      target: "pipe_free"
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    # 1. rules show -o
    rule_out = tmp_path / ".pni" / "cache" / "rule.md"
    r_rule = runner.invoke(app, ["rules", "show", "common/agent_instruction", "-o", str(rule_out)])
    assert r_rule.exit_code == 0, r_rule.output
    assert "Auto-Approval Friendly CLI Discipline" in rule_out.read_text(encoding="utf-8")

    # 2. workflows plan -o
    plan_out = tmp_path / ".pni" / "cache" / "plan_preview.md"
    r_plan = runner.invoke(app, ["workflows", "plan", "pipe_free", "--no-container-probe", "-o", str(plan_out)])
    assert r_plan.exit_code == 0, r_plan.output
    assert "flowchart TD" in plan_out.read_text(encoding="utf-8")

    # 3. workflows start --pull --json -o
    start_out = tmp_path / ".pni" / "cache" / "start.json"
    r_start = runner.invoke(app, ["workflows", "start", "pipe_free", "--pull", "--json", "-o", str(start_out)])
    assert r_start.exit_code == 0, r_start.output
    started = json.loads(start_out.read_text(encoding="utf-8"))
    run_id = started["run_id"]
    assert started["next_status"] == "ready"
    assert started["next_action"]["primitive_type"] == "confirm_plan"
    assert "--file .pni/cache/pipe_free/input_act-01.json --next" in started["next_action"]["prompt_markdown"]

    # 4. get-action -o & get-actions -o
    ga_out = tmp_path / ".pni" / "cache" / "act1.md"
    r_ga = runner.invoke(app, ["workflows", "get-action", run_id, "-o", str(ga_out)])
    assert r_ga.exit_code == 0, r_ga.output
    assert "confirm_plan" in ga_out.read_text(encoding="utf-8")

    gas_out = tmp_path / ".pni" / "cache" / "ready.md"
    r_gas = runner.invoke(app, ["workflows", "get-actions", run_id, "--ready", "-o", str(gas_out)])
    assert r_gas.exit_code == 0, r_gas.output
    assert "act-01" in gas_out.read_text(encoding="utf-8")

    # 5. push-action --file ... --next --json -o (advances past project_inspect to ai_interpret!)
    p1 = tmp_path / ".pni" / "cache" / "pipe_free" / "input_act-01.json"
    p1.parent.mkdir(parents=True, exist_ok=True)
    p1.write_text(json.dumps({"approved": True}), encoding="utf-8")
    n1_out = tmp_path / ".pni" / "cache" / "next1.json"
    r_p1 = runner.invoke(
        app,
        ["workflows", "push-action", run_id, "act-01", "--file", str(p1), "--next", "--json", "-o", str(n1_out)],
    )
    assert r_p1.exit_code == 0, r_p1.output
    n1 = json.loads(n1_out.read_text(encoding="utf-8"))
    assert n1["ok"] is True
    assert n1["next_status"] == "ready"
    assert n1["next_action"]["primitive_type"] == "ai_interpret"
    ai_act_id = n1["next_action"]["action_id"]

    # 6. push-action ai_interpret --next -o (markdown mode) -> emits next emit_score prompt to file
    p2 = tmp_path / ".pni" / "cache" / "pipe_free" / f"input_{ai_act_id}.json"
    p2.write_text(json.dumps({"summary": "Manifest checked.", "step_score": 88}), encoding="utf-8")
    n2_out = tmp_path / ".pni" / "cache" / "next2.md"
    r_p2 = runner.invoke(
        app,
        ["workflows", "push-action", run_id, ai_act_id, "--file", str(p2), "--next", "-o", str(n2_out)],
    )
    assert r_p2.exit_code == 0, r_p2.output
    assert "emit_score" in n2_out.read_text(encoding="utf-8")

    # 7. rewind --pull -o
    rw_out = tmp_path / ".pni" / "cache" / "rewound.md"
    r_rw = runner.invoke(app, ["workflows", "rewind", run_id, ai_act_id, "--pull", "-o", str(rw_out)])
    assert r_rw.exit_code == 0, r_rw.output
    assert ai_act_id in rw_out.read_text(encoding="utf-8")
