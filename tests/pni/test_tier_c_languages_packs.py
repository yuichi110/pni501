# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Integrity and end-to-end scaffolding tests for all 15 Tier C companion DSL rule/action/workflow packs."""

from __future__ import annotations

from pathlib import Path

import pytest

from pni._actions import PrimitiveType, list_actions, load_composite_action
from pni._languages import LANGUAGE_REGISTRY
from pni._rules import get_rule_content, list_rules
from pni._workflows import (
    load_workflow,
    normalize_workflow_steps,
    plan_workflow_run,
    validate_mermaid_static,
)
from pni.cli import init_project

TIER_C_LANGUAGES: tuple[str, ...] = tuple(
    lid for lid, spec in LANGUAGE_REGISTRY.items() if spec.tier == "companion_dsl"
)
CANONICAL_RULE_SUFFIXES: tuple[str, ...] = (
    "code_quality",
    "typing",
    "dependencies",
    "testing",
    "modern_stack",
    "workflow_guide",
)


def test_tier_c_language_count_is_fifteen() -> None:
    """Ensure all 15 Tier C (companion_dsl) languages are covered by the parametrized suite."""
    assert len(TIER_C_LANGUAGES) == 15


@pytest.mark.parametrize("lang", TIER_C_LANGUAGES)
def test_tier_c_language_pack_rules_actions_workflows_and_plan(lang: str, tmp_path: Path) -> None:
    """Verify every Tier C companion DSL has valid rules, actions, DAG workflows, and validated Mermaid plan."""
    ws = tmp_path / f"proj_{lang}"
    ws.mkdir()

    # 1. All 6 canonical rules exist in dedicated <lang> scope with H1 titles
    scoped_rules = {r.identifier for r in list_rules(ws, lang=lang)}
    for suffix in CANONICAL_RULE_SUFFIXES:
        rule_id = f"{lang}/{suffix}"
        assert rule_id in scoped_rules, f"Missing rule {rule_id}"
        loaded_rule = get_rule_content(rule_id, ws, lang=lang)
        assert loaded_rule is not None
        info, content = loaded_rule
        assert info.scope == lang
        assert content.lstrip().startswith("# ")

    # 2. Scaffold .pni/ for the language and verify bespoke actions + zero dangling rule refs
    init_project(ws, lang=lang, force=True)
    action_ids = {a.id for a in list_actions(ws, lang=lang)}
    expected_actions = (f"{lang}_ast_audit", f"{lang}_test_audit", "repo_structure_audit")
    for act_id in expected_actions:
        assert act_id in action_ids, f"Missing action {act_id} for {lang}"
        comp = load_composite_action(act_id, ws, lang=lang)
        assert comp is not None
        assert len(comp.rules) >= 1
        for rid in comp.rules:
            resolved = get_rule_content(rid, ws, lang=lang)
            assert resolved is not None, f"Dangling rule reference '{rid}' in {lang}/{act_id}"

    # 3. Both full_audit and quick_check load, normalize cleanly with confirm_plan, and build valid DAG plans
    for wf_id in ("full_audit", "quick_check"):
        loaded_wf = load_workflow(wf_id, ws)
        assert loaded_wf is not None, f"Missing workflow {wf_id} for {lang}"
        _, wf_def = loaded_wf
        steps = normalize_workflow_steps(wf_def, ws)
        assert len(steps) >= 5
        assert steps[0].type == PrimitiveType.CONFIRM_PLAN
        assert any(s.type == PrimitiveType.EMIT_SCORE for s in steps)

    planned = plan_workflow_run("full_audit", ws, probe_container_engine=False)
    assert planned is not None
    _, _, plan = planned
    mm_res = validate_mermaid_static(plan.mermaid_dag)
    assert mm_res.valid is True, f"Invalid Mermaid DAG for {lang}: {mm_res.issues}"
