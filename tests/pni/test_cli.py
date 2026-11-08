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

from typer.testing import CliRunner

from pni._actions import CategoryScores, ScoreResult
from pni.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    """Test 'pni version' command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "pni501" in result.stdout
    assert "0.1.2" in result.stdout


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

        # Action 1: ast_analyze
        res_get1 = runner.invoke(app, ["workflows", "get-action", run_id])
        assert res_get1.exit_code == 0
        assert "act-01" in res_get1.stdout
        assert (tmp_path / ".pni" / "cache" / "mini" / "facts.json").exists()

        res_push1 = runner.invoke(app, ["workflows", "push-action", run_id, "act-01", '{"acknowledged": true}'])
        assert res_push1.exit_code == 0

        # Action 2: emit_score via --file
        res_get2 = runner.invoke(app, ["workflows", "get-action", run_id])
        assert res_get2.exit_code == 0
        assert "act-02" in res_get2.stdout

        score_file = tmp_path / "payload_score.json"
        score_file.write_text(
            ScoreResult(
                project_name="sample",
                workflow_id="mini",
                language="python",
                overall_score=96,
                category_scores=CategoryScores(
                    architecture=96,
                    code_quality=96,
                    typing=100,
                    testing=90,
                    dependencies=96,
                    documentation=98,
                ),
                findings=[],
                summary="All checks passed.",
            ).model_dump_json(),
            encoding="utf-8",
        )

        # Non-existent --file errors cleanly
        res_no_file = runner.invoke(app, ["workflows", "push-action", run_id, "act-02", "--file", "nope.json"])
        assert res_no_file.exit_code == 1

        res_push2 = runner.invoke(app, ["workflows", "push-action", run_id, "act-02", "--file", str(score_file)])
        assert res_push2.exit_code == 0
        assert "COMPLETED" in res_push2.stdout

        emitted = json.loads((tmp_path / "reports" / "mini_score.json").read_text(encoding="utf-8"))
        assert emitted["overall_score"] == 96

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
