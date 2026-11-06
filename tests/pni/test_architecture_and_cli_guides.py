# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for drawlib-style CLI AI Instructions, workflow authoring rules, and 3-aspect architecture recording."""

from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from pni._actions import CategoryScores, PrimitiveType, ScoreResult
from pni._workflows import (
    get_workflow_action,
    push_workflow_action,
    start_workflow_run,
)
from pni.cli import app

runner = CliRunner()


def test_cli_short_help_and_ai_instructions_epilog() -> None:
    """Verify pni -h, pni --help, and bare pni display drawlib-style AI Instructions and workflow_guide refs."""
    for args in (["-h"], ["--help"], []):
        res = runner.invoke(app, args)
        assert res.exit_code == 0
        assert "AI Instructions:" in res.stdout
        assert "common/workflow_guide" in res.stdout
        assert "<lang>/workflow_guide" in res.stdout
        assert "drawlib rules show agent-instruction" in res.stdout
        assert "drawlib rules show api" in res.stdout


def test_workflow_guide_and_nested_framework_rules_resolution(tmp_path: Path) -> None:
    """Verify pni rules show outputs raw Markdown by default and resolves nested framework rules."""
    orig = Path.cwd()
    try:
        os.chdir(tmp_path)
        for rule_id in (
            "common/agent_instruction",
            "common/workflow_guide",
            "python/workflow_guide",
            "java/workflow_guide",
            "python/modern_stack",
            "python/frameworks/fastapi",
            "java/frameworks/spring_boot",
        ):
            res = runner.invoke(app, ["rules", "show", rule_id])
            assert res.exit_code == 0, f"Failed to resolve rule {rule_id}: {res.stdout}"
            assert res.stdout.strip().startswith("#")

        agent_rule = runner.invoke(app, ["rules", "show", "common/agent_instruction"]).stdout
        assert "drawlib rules show agent-instruction" in agent_rule
        assert "drawlib rules show api" in agent_rule
        assert "drawlib rules show lib-smartarts-overview" in agent_rule

        inst_res = runner.invoke(app, ["instructions"])
        assert inst_res.exit_code == 0
        assert "drawlib -h" in inst_res.stdout
        assert "drawlib rules show agent-instruction" in inst_res.stdout
        assert "drawlib rules show api" in inst_res.stdout
        assert "drawlib rules show lib-charts-overview" in inst_res.stdout
        assert "drawlib show" in inst_res.stdout

        pretty_res = runner.invoke(app, ["rules", "show", "common/workflow_guide", "--pretty"])
        assert pretty_res.exit_code == 0
        assert "common/workflow_guide (Builtin)" in pretty_res.stdout
    finally:
        os.chdir(orig)


def test_three_aspect_record_architecture_grounding_and_persistence(tmp_path: Path) -> None:
    """Verify 3-aspect architecture_analysis rejects hallucinated paths and persists grounded ArchitectureRecord."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "mini-cli"\nversion = "0.2.0"\nrequires-python = ">=3.12"\n',
        encoding="utf-8",
    )
    src_dir = tmp_path / "src" / "mini"
    src_dir.mkdir(parents=True)
    (src_dir / "cli.py").write_text(
        '"""CLI entrypoint."""\n\nfrom mini import service\n\n'
        "def main() -> int:\n"
        '    """Run main."""\n'
        "    return service.compute(3)\n",
        encoding="utf-8",
    )
    (src_dir / "service.py").write_text(
        '"""Domain service."""\n\n'
        "def compute(x: int) -> int:\n"
        '    """Double value."""\n'
        "    return x * 2\n",
        encoding="utf-8",
    )

    wf_dir = tmp_path / ".pni" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "arch_audit.yaml").write_text(
        "id: arch_audit\n"
        "name: Grounded Architecture Audit\n"
        "targets:\n"
        "  source:\n"
        "    - src\n"
        "steps:\n"
        "  - id: inspect\n"
        "    action: project_inspect\n"
        "  - id: ast\n"
        "    action: ast_analyze\n"
        "  - id: arch\n"
        "    uses: architecture_analysis\n"
        "  - id: score\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )

    run = start_workflow_run("arch_audit", tmp_path)
    assert run is not None

    # Step 1 & 2: deterministic project_inspect & ast_analyze
    _, act1, _ = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None and act1.primitive_type == PrimitiveType.PROJECT_INSPECT
    assert push_workflow_action(run.run_id, act1.action_id, '{"acknowledged": true}', tmp_path)[0]

    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None and act2.primitive_type == PrimitiveType.AST_ANALYZE
    assert "Module Inventory (2 files)" in guide2
    assert push_workflow_action(run.run_id, act2.action_id, '{"acknowledged": true}', tmp_path)[0]

    # Step 3: Aspect 1 (purpose_and_stack)
    _, act3, guide3 = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None and act3.primitive_type == PrimitiveType.RECORD_ARCHITECTURE
    assert "purpose_and_stack" in guide3
    aspect1_json = json.dumps(
        {
            "system_purpose": "Minimal deterministic CLI calculator.",
            "domain_context": "Developer tooling",
            "runtime_types": ["cli"],
            "tech_stack": ["python", "pyproject"],
            "external_integrations": [],
        }
    )
    ok3, _ = push_workflow_action(run.run_id, act3.action_id, aspect1_json, tmp_path)
    assert ok3 is True

    # Step 4: Aspect 2 (layers_and_modules) — first test anti-hallucination rejection!
    _, act4, guide4 = get_workflow_action(run.run_id, tmp_path)
    assert act4 is not None and "layers_and_modules" in guide4

    hallucinated_smap = json.dumps(
        {
            "architecture_pattern": "layered",
            "layers": [{"name": "ghost", "responsibility": "Fake", "paths": ["src/mini/phantom_ghost.py"]}],
            "modules": [],
        }
    )
    ok_bad, err_bad = push_workflow_action(run.run_id, act4.action_id, hallucinated_smap, tmp_path)
    assert ok_bad is False
    assert "Unverified/hallucinated path(s)" in err_bad

    grounded_smap = json.dumps(
        {
            "architecture_pattern": "layered_cli",
            "layers": [
                {
                    "name": "cli",
                    "responsibility": "Command dispatch",
                    "paths": ["src/mini/cli.py"],
                    "allowed_dependencies": ["service"],
                },
                {
                    "name": "service",
                    "responsibility": "Core computation",
                    "paths": ["src/mini/service.py"],
                    "allowed_dependencies": [],
                },
            ],
            "modules": [
                {
                    "path": "src/mini/cli.py",
                    "role": "CLI entrypoint",
                    "key_symbols": ["main"],
                    "depends_on": ["src/mini/service.py"],
                }
            ],
            "boundary_assessment": "Strictly unidirectional CLI -> Service.",
        }
    )
    ok4, _ = push_workflow_action(run.run_id, act4.action_id, grounded_smap, tmp_path)
    assert ok4 is True

    # Step 5: Aspect 3 (flows_and_state) — test hallucinated entry_point rejection, then grounded success
    _, act5, _ = get_workflow_action(run.run_id, tmp_path)
    assert act5 is not None
    bad_flow = json.dumps({"entry_points": ["src/mini/missing_entry.py:main"], "execution_flows": []})
    assert push_workflow_action(run.run_id, act5.action_id, bad_flow, tmp_path)[0] is False

    grounded_flow = json.dumps(
        {
            "entry_points": ["src/mini/cli.py:main"],
            "execution_flows": [
                {
                    "name": "CLI Compute",
                    "trigger": "main()",
                    "steps": ["cli.main calls service.compute"],
                    "involved_files": ["src/mini/cli.py", "src/mini/service.py"],
                }
            ],
            "state_and_storage": ["Stateless pure functions"],
            "error_and_concurrency_model": "Synchronous single-process execution",
        }
    )
    ok5, _ = push_workflow_action(run.run_id, act5.action_id, grounded_flow, tmp_path)
    assert ok5 is True

    arch_cache = tmp_path / ".pni" / "cache" / "arch_audit" / "architecture.json"
    assert arch_cache.is_file()
    persisted = json.loads(arch_cache.read_text(encoding="utf-8"))
    assert persisted["system_profile"]["runtime_types"] == ["cli"]
    assert persisted["structure_map"]["architecture_pattern"] == "layered_cli"
    assert persisted["execution_flow_map"]["entry_points"] == ["src/mini/cli.py:main"]

    # Step 6: emit_score receives Recorded Grounded Architecture and auto-enriches architecture_overview
    _, act6, guide6 = get_workflow_action(run.run_id, tmp_path)
    assert act6 is not None and act6.primitive_type == PrimitiveType.EMIT_SCORE
    assert "Recorded Grounded Architecture" in guide6
    assert "layered_cli" in guide6

    score_payload = ScoreResult(
        project_name="mini-cli",
        workflow_id="arch_audit",
        language="python",
        overall_score=98,
        category_scores=CategoryScores(
            architecture=98,
            code_quality=98,
            typing=100,
            testing=90,
            dependencies=98,
            documentation=98,
        ),
        summary="Clean layered CLI.",
    ).model_dump_json()
    ok6, _ = push_workflow_action(run.run_id, act6.action_id, score_payload, tmp_path)
    assert ok6 is True

    score_data = json.loads((tmp_path / "reports" / "arch_audit_score.json").read_text(encoding="utf-8"))
    assert score_data["architecture_overview"]["pattern"] == "layered_cli"
    assert score_data["architecture_overview"]["entry_points"] == ["src/mini/cli.py:main"]
    assert len(score_data["architecture_overview"]["modules"]) == 1
