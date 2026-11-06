# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for programmatic audit aggregation, deterministic sorting, and 5-chapter ReportBlueprint."""

from __future__ import annotations

import json
from pathlib import Path

from pni._actions import (
    ActionItem,
    AstFacts,
    CategoryScores,
    CodeLocation,
    Finding,
    InterpretationInput,
    ModuleAstSummary,
    PrimitiveType,
    RuleCheckResult,
    ScoreResult,
)
from pni._reporter.blueprint import build_report_blueprint, load_or_build_blueprint
from pni._workflows import (
    get_workflow_action,
    push_workflow_action,
    start_workflow_run,
)
from pni._workflows.aggregator import (
    compute_module_hotspots,
    deduplicate_and_sort_actions,
    deduplicate_and_sort_findings,
    merge_and_sort_rule_compliance,
    score_to_grade,
)


def test_score_to_grade_boundaries() -> None:
    """Verify deterministic score_to_grade conversion boundaries."""
    assert score_to_grade(95) == "S"
    assert score_to_grade(90) == "S"
    assert score_to_grade(85) == "A"
    assert score_to_grade(75) == "B"
    assert score_to_grade(60) == "C"
    assert score_to_grade(59) == "D"


def test_deterministic_sorting_and_deduplication() -> None:
    """Verify FAIL->WARN->PASS, CRITICAL->INFO, and P0->P2 canonical sorting and deduplication."""
    raw_rules = [
        RuleCheckResult(rule_id="general/readme_hygiene", status="pass", evidence="Diataxis headings present"),
        RuleCheckResult(rule_id="general/twelve_factor_app", status="warn", evidence="1 scattered env read"),
        RuleCheckResult(rule_id="general/security_owasp_asvs", status="pass", evidence="Initial check"),
        RuleCheckResult(rule_id="general/security_owasp_asvs", status="fail", evidence="Hardcoded API key at L12"),
        RuleCheckResult(rule_id="general/container_hygiene", status="not_applicable", evidence="Library package"),
    ]
    sorted_rules = merge_and_sort_rule_compliance(raw_rules)
    assert [r.rule_id for r in sorted_rules] == [
        "general/security_owasp_asvs",
        "general/twelve_factor_app",
        "general/readme_hygiene",
        "general/container_hygiene",
    ]
    assert sorted_rules[0].status == "fail"
    assert "Hardcoded API key at L12" in sorted_rules[0].evidence

    raw_findings = [
        Finding(
            severity="low",
            category="docs",
            rule_id="general/readme_hygiene",
            description="Minor heading typo",
            recommendation="Fix heading",
        ),
        Finding(
            severity="medium",
            category="security",
            rule_id="general/security_owasp_asvs",
            file_path="src/app.py",
            line=12,
            symbol="API_KEY",
            description="Duplicate lower severity",
            recommendation="Use env",
        ),
        Finding(
            severity="critical",
            category="security",
            rule_id="general/security_owasp_asvs",
            file_path="src/app.py",
            line=12,
            symbol="API_KEY",
            description="Hardcoded secret key",
            recommendation="Use secret manager",
        ),
        Finding(
            severity="high",
            category="ops",
            rule_id="general/sre_production_readiness",
            file_path="src/app.py",
            line=30,
            description="Missing HTTP timeout",
            recommendation="Pass timeout=5.0",
        ),
    ]
    sorted_findings = deduplicate_and_sort_findings(raw_findings)
    assert [f.severity for f in sorted_findings] == ["critical", "high", "low"]
    assert sorted_findings[0].description == "Hardcoded secret key"

    raw_actions = [
        ActionItem(
            priority="P2",
            title="Polish README",
            category="documentation",
            action="Add examples",
            expected_impact="Clearer onboarding",
        ),
        ActionItem(
            priority="P0",
            title="Remove hardcoded secret",
            category="security",
            action="Move to env",
            expected_impact="Eliminate credential leak",
        ),
        ActionItem(
            priority="P0",
            title="remove hardcoded secret",
            category="security",
            action="Duplicate",
            expected_impact="Duplicate",
        ),
        ActionItem(
            priority="P1",
            title="Add request timeouts",
            category="reliability",
            action="Set timeout=5.0",
            expected_impact="Prevent hung workers",
        ),
    ]
    sorted_actions = deduplicate_and_sort_actions(raw_actions)
    assert [a.priority for a in sorted_actions] == ["P0", "P1", "P2"]
    assert len(sorted_actions) == 3


def test_compute_module_hotspots_combines_findings_and_ast_bonuses() -> None:
    """Verify module_hotspots ranks risky files ahead of clean inventory files."""
    ast_facts = AstFacts(
        language="python",
        total_files=2,
        total_loc=120,
        module_inventory=[
            ModuleAstSummary(file="src/clean.py", loc=40),
            ModuleAstSummary(file="src/risky.py", loc=80),
        ],
        complex_functions=[CodeLocation(file="src/risky.py", line=10, symbol="god_fn", detail="85 LOC")],
        global_state_usages=[CodeLocation(file="src/risky.py", line=4, symbol="CACHE", detail="mutable dict")],
        hardcoded_secrets=[CodeLocation(file="src/risky.py", line=5, symbol="SECRET", detail="hardcoded token")],
    )
    findings = [
        Finding(
            severity="critical",
            category="security",
            rule_id="general/security_owasp_asvs",
            file_path="src/risky.py",
            line=5,
            description="Hardcoded token",
            recommendation="Remove hardcoded secret",
        )
    ]
    hotspots = compute_module_hotspots(findings, ast_facts)
    assert len(hotspots) == 2
    assert hotspots[0].file_path == "src/risky.py"
    assert hotspots[0].risk_score >= 0.9
    assert hotspots[1].file_path == "src/clean.py"
    assert hotspots[1].risk_score == 0.06


def _setup_demo_repo(tmp_path: Path) -> None:
    """Create a tiny Python package and workflow definition inside tmp_path."""
    src_dir = tmp_path / "src" / "pkg"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text('"""Demo package."""\n', encoding="utf-8")
    (src_dir / "core.py").write_text(
        '"""Core module."""\n\n\ndef add(a: int, b: int) -> int:\n    """Add ints."""\n    return a + b\n',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# Demo\n\n## Usage\n", encoding="utf-8")

    wf_dir = tmp_path / ".pni" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "bp_test.yaml").write_text(
        """id: bp_test
name: Blueprint Map-Reduce Test
targets:
  root: "."
  source: ["src"]
steps:
  - id: inspect
    uses: repo_structure_audit
  - id: ast
    uses: python_ast_audit
  - id: arch
    uses: architecture_analysis
    with:
      target: "bp_test"
  - id: score
    uses: emit_score
    with:
      target: "bp_test"
  - id: report
    uses: write_drawlib_report
    with:
      target: "bp_test"
      src_dir: "reports_src"
      output_dir: "reports"
""",
        encoding="utf-8",
    )


def _push_three_aspect_architecture(run_id: str, tmp_path: Path) -> None:
    """Push 3-aspect grounded architecture records for the demo repo."""
    payloads = [
        {
            "system_purpose": "Demo math library",
            "runtime_types": ["library"],
            "tech_stack": ["Python 3.11+"],
        },
        {
            "architecture_pattern": "pure_library",
            "layers": [{"name": "core", "responsibility": "Arithmetic", "paths": ["src/pkg/core.py"]}],
            "modules": [{"path": "src/pkg/core.py", "role": "Arithmetic helpers"}],
            "boundary_assessment": "Acyclic clean boundary.",
        },
        {
            "entry_points": ["src/pkg/core.py:add"],
            "execution_flows": [
                {
                    "name": "Addition Call",
                    "trigger": "add(a, b)",
                    "steps": ["Caller invokes add", "Returns integer sum"],
                    "involved_files": ["src/pkg/core.py"],
                }
            ],
            "state_and_storage": ["Pure stateless functions"],
            "error_and_concurrency_model": "Thread-safe pure functions",
        },
    ]
    for payload in payloads:
        _, act, _ = get_workflow_action(run_id, tmp_path)
        assert act is not None and act.primitive_type == PrimitiveType.RECORD_ARCHITECTURE
        ok, msg = push_workflow_action(run_id, act.action_id, json.dumps(payload), tmp_path)
        assert ok is True, msg


def test_workflow_map_reduce_and_five_chapter_blueprint(tmp_path: Path) -> None:
    """Verify end-to-end step submission, path grounding, auto-sorting into ScoreResult, and 5-chapter Blueprint."""
    _setup_demo_repo(tmp_path)
    run = start_workflow_run("bp_test", tmp_path)
    assert run is not None

    _, act1, _ = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None and act1.primitive_type == PrimitiveType.PROJECT_INSPECT
    assert push_workflow_action(run.run_id, act1.action_id, '{"acknowledged": true}', tmp_path)[0] is True

    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None and act2.primitive_type == PrimitiveType.AI_INTERPRET
    assert "Required Structured Deliverables in `push-action`" in guide2

    bad_payload = InterpretationInput(
        summary="Hallucinated file test",
        step_score=70,
        findings=[
            Finding(
                severity="medium",
                category="dependencies",
                rule_id="general/dependency_management",
                file_path="src/pkg/does_not_exist.py",
                line=1,
                description="Fake file",
                recommendation="None",
            )
        ],
    ).model_dump_json()
    ok_bad, err_bad = push_workflow_action(run.run_id, act2.action_id, bad_payload, tmp_path)
    assert ok_bad is False
    assert "does_not_exist.py" in err_bad

    good_act2 = InterpretationInput(
        summary="Manifest inspected; lockfile missing.",
        step_score=72,
        rule_checks=[
            RuleCheckResult(
                rule_id="general/dependency_management",
                status="warn",
                evidence="pyproject.toml present, uv.lock missing",
                summary="Missing lockfile.",
            )
        ],
        findings=[
            Finding(
                severity="medium",
                category="dependencies",
                rule_id="general/dependency_management",
                file_path="pyproject.toml",
                line=1,
                description="Missing lockfile for reproducible installs.",
                recommendation="Commit uv.lock",
            )
        ],
        action_items=[
            ActionItem(
                priority="P1",
                title="Commit uv.lock",
                category="dependencies",
                target_files=["pyproject.toml"],
                action="Generate and commit uv.lock.",
                expected_impact="Deterministic builds",
            )
        ],
    ).model_dump_json()
    assert push_workflow_action(run.run_id, act2.action_id, good_act2, tmp_path)[0] is True

    _, act3, _ = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None and act3.primitive_type == PrimitiveType.AST_ANALYZE
    assert push_workflow_action(run.run_id, act3.action_id, '{"acknowledged": true}', tmp_path)[0] is True

    _, act4, _ = get_workflow_action(run.run_id, tmp_path)
    assert act4 is not None and act4.primitive_type == PrimitiveType.AI_INTERPRET
    good_act4 = InterpretationInput(
        summary="Clean typed AST with 100% annotations and docstrings.",
        step_score=96,
        strengths=["100% type annotations and docstrings across src/pkg"],
    ).model_dump_json()
    assert push_workflow_action(run.run_id, act4.action_id, good_act4, tmp_path)[0] is True

    _push_three_aspect_architecture(run.run_id, tmp_path)

    _, act8, guide8 = get_workflow_action(run.run_id, tmp_path)
    assert act8 is not None and act8.primitive_type == PrimitiveType.EMIT_SCORE
    assert "Pre-Sorted Programmatic Audit Digest" in guide8

    score_in = ScoreResult(
        project_name="demo-pkg",
        workflow_id="bp_test",
        language="python",
        overall_score=86,
        category_scores=CategoryScores(
            architecture=95,
            code_quality=95,
            typing=100,
            testing=70,
            dependencies=72,
            documentation=84,
        ),
        summary="Clean library with missing lockfile.",
    ).model_dump_json()
    assert push_workflow_action(run.run_id, act8.action_id, score_in, tmp_path)[0] is True

    persisted_score = ScoreResult.model_validate_json(
        (tmp_path / "reports" / "bp_test_score.json").read_text(encoding="utf-8")
    )
    assert persisted_score.grade == "A"
    assert persisted_score.architecture_record is not None
    assert persisted_score.architecture_record.system_profile is not None
    assert [d.score for d in persisted_score.audit_dimensions] == [72, 96]
    assert persisted_score.rule_compliance[0].status == "warn"
    assert persisted_score.rule_compliance[0].rule_id == "general/dependency_management"
    assert len(persisted_score.findings) == 1
    assert len(persisted_score.action_plan) == 1
    assert len(persisted_score.module_hotspots) >= 2

    _, act9, guide9 = get_workflow_action(run.run_id, tmp_path)
    assert act9 is not None and act9.primitive_type == PrimitiveType.WRITE_DRAWLIB_REPORT
    assert "Deterministic 6-Chapter Report Blueprint" in guide9
    assert "01_executive_summary.md" in guide9
    assert "03_remediation_roadmap.md" in guide9
    assert "04_standards_and_findings.md" in guide9
    assert "06_security_and_supply_chain.md" in guide9
    assert (tmp_path / ".pni" / "cache" / "bp_test" / "blueprint.json").is_file()

    bp = build_report_blueprint(persisted_score, lang="ja", target="bp_test")
    assert [c.filename for c in bp.chapters] == [
        "00_cover.md",
        "01_executive_summary.md",
        "02_architecture_and_structure.md",
        "03_remediation_roadmap.md",
        "04_standards_and_findings.md",
        "05_code_and_runtime_analysis.md",
        "06_security_and_supply_chain.md",
    ]
    assert load_or_build_blueprint(tmp_path, "../../etc/passwd", target="bp_test", lang="ja") == (None, "")
