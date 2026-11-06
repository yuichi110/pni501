# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit and integration tests for deterministic migration analysis, workflow engine, and blueprints."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from pni._actions import (
    CategoryScores,
    ComponentMigrationMapping,
    DecisionLogItem,
    MigrationAxis,
    MigrationOptions,
    MigrationPhaseGate,
    MigrationPlanResult,
    MigrationPrTicket,
    ScoreResult,
    TargetArchitectureDesign,
    TargetLayerSpec,
    check_migration_preflight_hints,
    resolve_migration_brief,
    resolve_migration_plan_rel_path,
    run_migration_analyze,
)
from pni._reporter import build_migration_blueprint, render_drawlib_report_guide
from pni._workflows import (
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowPrerequisiteError,
    WorkflowStepSpec,
    get_workflow_action,
    list_workflows,
    load_workflow,
    normalize_workflow_steps,
    push_workflow_action,
    start_workflow_run,
)
from pni.cli import app, init_project

REPO_ROOT = Path(__file__).resolve().parents[2]
JAVA_MESSY_DIR = REPO_ROOT / "examples" / "java" / "api_spring_messy"
PHP_MESSY_DIR = REPO_ROOT / "examples" / "php" / "legacy_shop_messy"

DETERMINISTIC_JAVA_BRIEF = """\
Target Stack & Infrastructure:
  - Runtime: Java 21 LTS + Spring Boot 3.4 (Jakarta EE 10, JUnit 5)
  - Database: PostgreSQL 16 via Spring Data JPA + Flyway
  - Cache & State: Externalize BillingManager.INVOICE_CACHE to Redis 7; make BillingController stateless
Target Design Philosophy:
  - Clean Architecture (domain / usecase / port / adapter) with pure Domain records
Compatibility & Guardrails:
  - Preserve external REST contract on POST /charge (customerId, amountCents, billedCents)
Non-Goals:
  - Do not introduce Kafka or microservice splitting in this migration wave.
"""


def test_resolve_migration_plan_rel_path_avoids_duplicate_suffix() -> None:
    """Verify resolve_migration_plan_rel_path normalizes _migration targets cleanly."""
    assert (
        resolve_migration_plan_rel_path("reports/java", "api_spring_messy_migration")
        == "reports/java/api_spring_messy_migration_plan.json"
    )
    assert (
        resolve_migration_plan_rel_path("reports/java/", "api_spring_messy")
        == "reports/java/api_spring_messy_migration_plan.json"
    )
    assert (
        resolve_migration_plan_rel_path("reports", "custom_migration_plan")
        == "reports/custom_migration_plan.json"
    )
    assert (
        resolve_migration_plan_rel_path("reports", "ignored", "reports/explicit.json")
        == "reports/explicit.json"
    )


def test_resolve_migration_brief_and_preflight_hints(tmp_path: Path) -> None:
    """Verify brief + brief_file merging, path traversal guard, and preflight readiness checks."""
    empty_opts = MigrationOptions()
    empty_hints = check_migration_preflight_hints(empty_opts, "")
    codes = {h.code for h in empty_hints}
    assert "MISSING_BRIEF" in codes
    assert "UNPINNED_STRATEGY" in codes

    vague_opts = MigrationOptions(brief="Upgrade to latest TBD")
    vague_hints = check_migration_preflight_hints(vague_opts, vague_opts.brief)
    vague_codes = {h.code for h in vague_hints}
    assert "BRIEF_TOO_TERSE" in vague_codes
    assert "VAGUE_BRIEF_TERMS" in vague_codes
    assert "UNPINNED_STRATEGY" in vague_codes
    assert "UNPINNED_CODEMOD_TOOL" in vague_codes

    brief_doc = tmp_path / "docs" / "mig_spec.md"
    brief_doc.parent.mkdir(parents=True)
    brief_doc.write_text(DETERMINISTIC_JAVA_BRIEF, encoding="utf-8")

    pinned_opts = MigrationOptions(
        brief="Confirmed Scope Addendum: Keep single Maven module.",
        brief_file="docs/mig_spec.md",
        migration_strategy="phased_pr",
        api_compatibility="strict",
        bug_handling_policy="ask_human",
        codemod_tool="openrewrite",
    )
    merged = resolve_migration_brief(tmp_path, pinned_opts)
    assert "Confirmed Scope Addendum" in merged
    assert "PostgreSQL 16" in merged
    assert check_migration_preflight_hints(pinned_opts, merged) == []

    with pytest.raises(ValueError, match="must stay within"):
        resolve_migration_brief(tmp_path, MigrationOptions(brief_file="../outside.md"))

    with pytest.raises(ValueError, match="does not exist"):
        resolve_migration_brief(tmp_path, MigrationOptions(brief_file="docs/missing.md"))


def test_run_migration_analyze_java_spring_messy(tmp_path: Path) -> None:
    """Verify 5 deterministic analyzers on examples/java/api_spring_messy."""
    target_dir = tmp_path / "examples" / "java" / "api_spring_messy"
    shutil.copytree(JAVA_MESSY_DIR, target_dir)

    opts = MigrationOptions(
        brief=DETERMINISTIC_JAVA_BRIEF,
        migration_strategy="phased_pr",
        api_compatibility="strict",
        bug_handling_policy="ask_human",
        codemod_tool="openrewrite",
    )
    facts = run_migration_analyze(
        tmp_path,
        "java_mig_test",
        target_root="examples/java/api_spring_messy",
        source_targets=["src/main/java"],
        test_targets=["src/test/java"],
        doc_targets=["README.md"],
        options=opts,
    )

    assert facts.source_language == "java"
    assert facts.transformation_mode == "architectural_restructure"
    assert facts.resolved_strategy == "phased_pr"
    assert facts.preflight_hints == []

    # 1. Waves & SCC cycle cuts (6 deduplicated canonical files across Waves 1, 2, 3, and 4)
    wave_by_basename = {
        Path(mod).name: w.wave
        for w in facts.refactoring_waves
        for mod in w.modules
    }
    assert len(wave_by_basename) == 6
    assert wave_by_basename["InvoiceRecord.java"] == 1
    assert wave_by_basename["LegacyDateHelper.java"] == 1
    assert wave_by_basename["GatewayClient.java"] == 2
    assert wave_by_basename["BillingController.java"] == 3
    assert wave_by_basename["BillingManager.java"] == 3
    assert wave_by_basename["BillingApp.java"] == 4

    assert len(facts.cycle_cuts) >= 1
    cut = facts.cycle_cuts[0]
    assert "BillingManager" in cut.recommended_cut_from
    assert "BillingController" in cut.recommended_cut_to

    # 2. Implicit contracts & env contracts
    assert any("/charge" in c.endpoint_or_file for c in facts.implicit_contracts)
    charge_contract = next(c for c in facts.implicit_contracts if "/charge" in c.endpoint_or_file)
    req_keys = {f.key for f in charge_contract.input_fields}
    resp_keys = {f.key for f in charge_contract.output_fields}
    assert {"customerId", "amountCents"} <= req_keys
    assert {"customerId", "billedCents", "controllerPing"} <= resp_keys
    assert any(e.name == "LEGACY_PAYMENT_URL" for e in facts.env_contracts)

    # 3. Boundary touchpoints
    tp_kinds = {tp.kind for tp in facts.boundary_touchpoints}
    assert tp_kinds == {"in_memory_state", "persistence_db", "external_http_rpc"}
    tp_symbols = " ".join(tp.symbol for tp in facts.boundary_touchpoints)
    assert "INVOICE_CACHE" in tp_symbols
    assert "channel" in tp_symbols
    assert "@Transactional" in tp_symbols
    assert "HttpClient" in tp_symbols

    # 4. Codemod recipes & manual blockers
    recipe_ids = {r.recipe_id for r in facts.mechanical_codemods}
    assert "org.openrewrite.java.migrate.UpgradeToJava21" in recipe_ids
    assert "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_4" in recipe_ids
    assert "org.openrewrite.java.testing.junit5.JUnit4to5Migration" in recipe_ids

    blocker_ids = {b.blocker_id for b in facts.manual_blockers}
    assert len(blocker_ids) >= 2

    # 5. Spec vs Bug candidates
    amb_behaviors = " ".join(c.observed_behavior for c in facts.spec_vs_bug_candidates)
    assert "==" in amb_behaviors
    assert "100L" in amb_behaviors or "controllerPing" in amb_behaviors


def test_run_migration_analyze_php_legacy_shop_messy(tmp_path: Path) -> None:
    """Verify cross-stack Strangler Fig detection, secret masking, and PHP contracts on legacy_shop_messy."""
    target_dir = tmp_path / "examples" / "php" / "legacy_shop_messy"
    shutil.copytree(PHP_MESSY_DIR, target_dir)

    php_brief = """\
Target Stack & Infrastructure:
  - Runtime: PHP 8.3 + Laravel 11 MVC + Eloquent/PDO prepared statements
  - Cache & Session: Redis 7 session & server-side cart replacing unserialize($_COOKIE['shop_cart'])
Target Design Philosophy:
  - Strangler Fig incremental route cutover (/login, /products, /cart, /admin/backup) with Modular Service/Action layer
Compatibility & Guardrails:
  - Preserve existing URL query parameters during Strangler Fig coexistence
Non-Goals:
  - Do not build a SPA frontend in this migration wave.
"""
    opts = MigrationOptions(
        brief=php_brief,
        migration_strategy="auto",
        api_compatibility="strict",
        bug_handling_policy="ask_human",
        codemod_tool="rector",
    )
    facts = run_migration_analyze(
        tmp_path,
        "php_mig_test",
        target_root="examples/php/legacy_shop_messy",
        source_targets=[".", "includes"],
        test_targets=["tests"],
        doc_targets=["README.md"],
        options=opts,
    )

    assert facts.source_language == "php"
    assert facts.transformation_mode == "cross_stack_replacement"
    assert facts.resolved_strategy == "strangler_fig"

    # Circular include between includes/db.php and includes/helpers.php
    assert len(facts.cycle_cuts) >= 1
    cycle_mods = {
        c.recommended_cut_from for c in facts.cycle_cuts
    } | {c.recommended_cut_to for c in facts.cycle_cuts}
    assert any("db.php" in m or "helpers.php" in m for m in cycle_mods)

    # Secret masking in env_contracts
    env_by_name = {e.name: e for e in facts.env_contracts}
    assert "DB_PASSWORD" in env_by_name
    assert env_by_name["DB_PASSWORD"].default_value == "<REDACTED>"
    assert "PARTNER_FEED_TOKEN" in env_by_name

    # Touchpoints across state/session, mysqli, curl
    tp_kinds = {tp.kind for tp in facts.boundary_touchpoints}
    assert {"in_memory_state", "persistence_db", "external_http_rpc"} <= tp_kinds

    # Rector recipes
    assert any(r.tool == "rector" for r in facts.mechanical_codemods)

    # Ambiguities (MD5 / loose == / ?debug=1)
    assert len(facts.spec_vs_bug_candidates) >= 2


def test_run_migration_analyze_python_same_lang_upgrade(tmp_path: Path) -> None:
    """Verify Python dict/env contract extraction, Ruff codemod match, and same_lang_upgrade mode."""
    src_dir = tmp_path / "src" / "app"
    src_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\nrequires-python = ">=3.9"\n',
        encoding="utf-8",
    )
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "handler.py").write_text(
        'import os\nimport requests\n\nCACHE = {}\nAPI_TOKEN = os.getenv("API_TOKEN", "dev-secret")\n'
        'TIMEOUT = os.getenv("HTTP_TIMEOUT", "5")\n\n'
        "def handle(payload: dict) -> dict:\n"
        '    user_id = payload.get("user_id", "guest")\n'
        '    resp = requests.get("https://example.com/api")\n'
        '    return {"user_id": user_id, "ok": resp.status_code == 200}\n',
        encoding="utf-8",
    )

    opts = MigrationOptions(
        brief=(
            "Upgrade Python 3.9 to Python 3.12 with strict typing and Ruff pyupgrade.\n"
            "Architecture: keep modular handler layout; preserve dict payload compatibility.\n"
            "Non-Goals: no framework change."
        ),
        migration_strategy="phased_pr",
        codemod_tool="ruff",
    )
    facts = run_migration_analyze(
        tmp_path,
        "py_mig_test",
        target_root=".",
        source_targets=["src"],
        test_targets=["tests"],
        doc_targets=["README.md"],
        options=opts,
    )
    assert facts.source_language == "python"
    assert facts.transformation_mode == "same_lang_upgrade"
    assert any(r.tool == "ruff" for r in facts.mechanical_codemods)
    env_map = {e.name: e for e in facts.env_contracts}
    assert env_map["API_TOKEN"].default_value == "<REDACTED>"
    assert env_map["HTTP_TIMEOUT"].default_value == "5"


def _build_sample_plan_payload(source_file: str = "src/app/service.py") -> MigrationPlanResult:
    """Construct a valid MigrationPlanResult payload for workflow engine and blueprint tests."""
    return MigrationPlanResult(
        project_name="demo-service",
        source_language="python",
        transformation_mode="architectural_restructure",
        migration_strategy="phased_pr",
        api_compatibility="strict",
        bug_handling_policy="ask_human",
        executive_summary="Phased migration to Clean Architecture and Python 3.12.",
        confirmed_assumptions=["Preserve external JSON keys on POST /orders."],
        non_goals=["No database engine swap in Wave 1."],
        target_axes=[
            MigrationAxis(
                category="language_runtime",
                title="Python 3.9 -> Python 3.12",
                as_is="Python 3.9",
                to_be="Python 3.12",
                migration_approach="Ruff UP codemod + CI matrix update.",
                risk_level="low",
                affected_files=[source_file],
            )
        ],
        target_architecture=TargetArchitectureDesign(
            pattern_name="Clean Architecture (domain / usecase / port / adapter)",
            summary="Isolate domain entities from HTTP and persistence adapters.",
            dependency_rules=["domain has zero framework imports."],
            target_layers=[
                TargetLayerSpec(
                    layer_name="Domain Layer",
                    package_or_dir="src/app/domain",
                    responsibility="Pure value objects and business policies.",
                    allowed_dependencies=[],
                ),
                TargetLayerSpec(
                    layer_name="Adapter Layer",
                    package_or_dir="src/app/adapter",
                    responsibility="HTTP controllers and repository implementations.",
                    allowed_dependencies=["Domain Layer"],
                ),
            ],
            component_mappings=[
                ComponentMigrationMapping(
                    source_file=source_file,
                    source_symbol="process_order",
                    target_layer="Domain Layer",
                    target_component="src/app/domain/order_policy.py",
                    port_or_adapter_role="Domain Service",
                    refactoring_note="Extract pure calculation out of stateful service.",
                )
            ],
        ),
        decision_log=[
            DecisionLogItem(
                decision_id="DEC-01",
                file_path=source_file,
                line=4,
                current_behavior="Defaults missing amount to 0.",
                impact_if_changed="Clients omitting amount receive HTTP 422.",
                recommended_option="Preserve default 0 in Phase 1 DTO.",
                stakeholder_options=["Preserve default 0", "Reject in v2 endpoint"],
            )
        ],
        phase_gates=[
            MigrationPhaseGate(
                phase_number=0,
                title="Phase 0: Characterization Tests & Build Alignment",
                objective="Lock current endpoint behavior before refactoring.",
                key_tasks=["Add golden master tests"],
                exit_criteria=["100% golden tests green"],
                rollback_or_coexistence_note="Test-only changes.",
            ),
            MigrationPhaseGate(
                phase_number=1,
                title="Phase 1: Mechanical Codemods",
                objective="Run Ruff UP rules.",
                key_tasks=["Run ruff check --select UP --fix"],
                exit_criteria=["Zero Ruff errors"],
            ),
        ],
        pr_wbs=[
            MigrationPrTicket(
                pr_id="PR-01",
                phase_number=0,
                wave=1,
                axis_category="language_runtime",
                title="Add characterization tests for process_order",
                target_files=[source_file],
                changes_summary="Pin current JSON behavior before refactoring.",
                automated_or_manual="manual",
                verification_cmd="pytest -q",
                estimated_size="S",
                depends_on_prs=[],
            )
        ],
    )


def _complete_sample_audit_workflow(project_root: Path, workflow_id: str, overall_score: int = 62) -> str:
    """Run and complete a 2-step (ast_analyze -> emit_score) audit workflow in SQLite and return run_id."""
    audit_rec = start_workflow_run(workflow_id, project_root)
    assert audit_rec is not None
    assert audit_rec.category == WorkflowCategory.AUDIT

    _, act1, _ = get_workflow_action(audit_rec.run_id, project_root)
    assert act1 is not None
    ok1, _ = push_workflow_action(audit_rec.run_id, act1.action_id, '{"acknowledged": true}', project_root)
    assert ok1 is True

    _, act2, _ = get_workflow_action(audit_rec.run_id, project_root)
    assert act2 is not None
    score_payload = ScoreResult(
        project_name="demo-service",
        workflow_id=workflow_id,
        language="python",
        overall_score=overall_score,
        category_scores=CategoryScores(
            architecture=overall_score,
            code_quality=overall_score,
            typing=70,
            testing=55,
            dependencies=75,
            documentation=60,
        ),
        findings=[],
        summary=f"Baseline audit score ({overall_score}/100) for {workflow_id}.",
    )
    ok2, msg2 = push_workflow_action(audit_rec.run_id, act2.action_id, score_payload.model_dump_json(), project_root)
    assert ok2 is True
    assert "COMPLETED" in msg2
    return audit_rec.run_id


def test_migration_blueprint_and_stateful_workflow_end_to_end(tmp_path: Path) -> None:
    """Verify full stateful workflow loop for migration_proposal + write_migration_report and CLI commands."""
    src_dir = tmp_path / "src" / "app"
    src_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo-service"\nversion = "0.1.0"\n', encoding="utf-8")
    (src_dir / "service.py").write_text(
        'STATE = {}\ndef process_order(data: dict) -> dict:\n    return {"amount": data.get("amount", 0)}\n',
        encoding="utf-8",
    )

    init_project(tmp_path, lang="python", force=True)
    audit_yaml = tmp_path / ".pni" / "workflows" / "demo_audit.yaml"
    audit_yaml.write_text(
        """\
id: demo_audit
name: Demo Service Baseline Audit
category: audit
targets:
  root: "."
  source: ["src"]
  tests: ["tests"]
  docs: ["README.md"]
steps:
  - id: s1
    action: ast_analyze
  - id: s2
    uses: emit_score
""",
        encoding="utf-8",
    )
    wf_yaml = tmp_path / ".pni" / "workflows" / "demo_migration.yaml"
    wf_yaml.write_text(
        """\
id: demo_migration
name: Demo Service Migration Plan
category: migration
based_on: demo_audit
steps:
  - id: proposal
    uses: migration_proposal
    with:
      output_dir: "reports"
      target: "demo_migration"
      migration_strategy: "phased_pr"
      api_compatibility: "strict"
      bug_handling_policy: "ask_human"
      codemod_tool: "ruff"
      brief: |
        Target Stack: Python 3.12 + Redis state externalization.
        Design Philosophy: Clean Architecture (domain / usecase / port / adapter).
        Compatibility: Preserve external JSON contract on /orders.
        Non-Goals: No database migration in Wave 1.
  - id: report
    uses: write_migration_report
    with:
      src_dir: "reports_src"
      output_dir: "reports"
      target: "demo_migration"
      lang: "ja"
""",
        encoding="utf-8",
    )

    audit_run_id = _complete_sample_audit_workflow(tmp_path, "demo_audit", overall_score=64)

    cli_runner = CliRunner()
    prev_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        show_res = cli_runner.invoke(app, ["workflows", "show", "demo_migration"])
        assert show_res.exit_code == 0
        assert "Prerequisite Audit Ready" in show_res.stdout
        assert "Migration Preflight Check" in show_res.stdout
    finally:
        os.chdir(prev_cwd)

    run_rec = start_workflow_run("demo_migration", tmp_path)
    assert run_rec is not None
    assert run_rec.category == WorkflowCategory.MIGRATION
    assert run_rec.based_on == "demo_audit"
    assert run_rec.based_on_run_id == audit_run_id

    # Step 1: migration_analyze (auto-executed on get_workflow_action, then ack)
    _, act1, guide1 = get_workflow_action(run_rec.run_id, tmp_path)
    assert act1 is not None
    assert act1.primitive_type.value == "migration_analyze"
    assert "Migration Analysis Summary" in guide1 or "migration_analyze" in guide1
    ok1, _ = push_workflow_action(run_rec.run_id, act1.action_id, '{"acknowledged": true}', tmp_path)
    assert ok1 is True

    # Step 2: ai_interpret (inherits Baseline Audit Score Summary + AST facts from SQLite)
    _, act2, guide2 = get_workflow_action(run_rec.run_id, tmp_path)
    assert act2 is not None
    assert act2.primitive_type.value == "ai_interpret"
    assert "Baseline Audit Score Summary" in guide2
    assert "64/100" in guide2
    interp_json = json.dumps(
        {
            "summary": "Extract STATE dictionary behind a state port and preserve amount default.",
            "highlights": ["Wave 1 leaf service.py"],
            "risks": ["Implicit amount=0 default"],
        }
    )
    ok2, _ = push_workflow_action(run_rec.run_id, act2.action_id, interp_json, tmp_path)
    assert ok2 is True

    # Step 3: emit_migration_plan — first test hallucinated file rejection!
    _, act3, guide3 = get_workflow_action(run_rec.run_id, tmp_path)
    assert act3 is not None
    assert act3.primitive_type.value == "emit_migration_plan"
    assert "MigrationPlanResult" in guide3

    bad_plan = _build_sample_plan_payload(source_file="src/app/nonexistent_hallucinated.py")
    ok_bad, msg_bad = push_workflow_action(
        run_rec.run_id,
        act3.action_id,
        bad_plan.model_dump_json(),
        tmp_path,
    )
    assert ok_bad is False
    assert "Unverified/hallucinated path(s)" in msg_bad

    good_plan = _build_sample_plan_payload(source_file="src/app/service.py")
    ok3, msg3 = push_workflow_action(
        run_rec.run_id,
        act3.action_id,
        good_plan.model_dump_json(),
        tmp_path,
    )
    assert ok3 is True
    assert "emit_migration_plan" in msg3

    plan_file = tmp_path / "reports" / "demo_migration_plan.json"
    assert plan_file.exists()

    # Validate via CLI command
    try:
        os.chdir(tmp_path)
        val_res = cli_runner.invoke(app, ["validate-migration-plan", str(plan_file)])
        assert val_res.exit_code == 0
        assert "Valid MigrationPlanResult" in val_res.stdout
    finally:
        os.chdir(prev_cwd)

    # Verify MigrationBlueprint in both ja and en + Drawlib guide rendering
    saved_plan = MigrationPlanResult.model_validate_json(plan_file.read_text(encoding="utf-8"))
    bp_ja = build_migration_blueprint(saved_plan, target="demo_migration", lang="ja")
    bp_en = build_migration_blueprint(saved_plan, target="demo_migration", lang="en")
    assert len(bp_ja.chapters) == 7
    assert len(bp_en.chapters) == 7
    assert bp_ja.chapters[1].filename == "01_migration_strategy_summary.md"
    assert bp_ja.chapters[6].filename == "06_pr_wbs_and_verification_gates.md"

    mig_guide = render_drawlib_report_guide(
        target="demo_migration",
        src_base_dir="reports_src",
        output_dir="reports",
        score_path="reports/demo_migration_score.json",
        facts_path=".pni/cache/demo_migration/facts.json",
        target_root=".",
        source_targets=["src"],
        doc_targets=["README.md"],
        workflow_id="demo_migration",
        lang="ja",
        report_kind="migration",
        plan_path="reports/demo_migration_plan.json",
    )
    assert "02_architecture_waves_and_contracts.md" in mig_guide
    assert "demo_migration_plan.json" in mig_guide

    # Step 4: write_drawlib_report renders blueprint-driven migration report guide
    _, act4, guide4 = get_workflow_action(run_rec.run_id, tmp_path)
    assert act4 is not None
    assert act4.primitive_type.value == "write_drawlib_report"
    assert "01_migration_strategy_summary.md" in guide4
    assert (tmp_path / ".pni" / "cache" / "demo_migration" / "migration_blueprint.json").exists()


def test_workflow_category_and_based_on_schema_validation() -> None:
    """Verify WorkflowDefinition enforces category / based_on invariants."""
    step = WorkflowStepSpec(id="s1", action="ast_analyze")

    # category='migration' requires based_on
    with pytest.raises(ValidationError, match="based_on"):
        WorkflowDefinition(
            id="bad_mig",
            name="Bad Migration",
            category=WorkflowCategory.MIGRATION,
            steps=[step],
        )

    # category='audit' forbids based_on
    with pytest.raises(ValidationError, match="based_on"):
        WorkflowDefinition(
            id="bad_audit",
            name="Bad Audit",
            category=WorkflowCategory.AUDIT,
            based_on="full_audit",
            steps=[step],
        )


def test_migration_based_on_target_inheritance_and_sqlite_enforcement(tmp_path: Path) -> None:
    """Verify targets inheritance from based_on and strict SQLite audit completion checks."""
    svc_src = tmp_path / "services" / "order" / "app"
    svc_src.mkdir(parents=True)
    (tmp_path / "services" / "order" / "pyproject.toml").write_text(
        '[project]\nname = "order-svc"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (svc_src / "handler.py").write_text(
        "CACHE = {}\ndef handle(req: dict) -> int:\n    return int(req.get('qty', 1))\n",
        encoding="utf-8",
    )

    init_project(tmp_path, lang="python", force=True)
    wf_dir = tmp_path / ".pni" / "workflows"

    (wf_dir / "order_audit.yaml").write_text(
        """\
id: order_audit
name: Order Service Audit
category: audit
targets:
  root: "services/order"
  source: ["app"]
  tests: ["spec"]
  docs: ["ARCH.md"]
steps:
  - id: s1
    action: ast_analyze
  - id: s2
    uses: emit_score
""",
        encoding="utf-8",
    )
    (wf_dir / "order_migration.yaml").write_text(
        """\
id: order_migration
name: Order Service Migration
category: migration
based_on: order_audit
steps:
  - id: proposal
    uses: migration_proposal
    with:
      target: "order_migration"
      brief: |
        Target Stack: Python 3.12 + Redis cache adapter.
        Design Philosophy: Hexagonal Architecture (domain / port / adapter).
        Compatibility: Preserve handle(req) integer return contract.
        Non-Goals: No schema split in Wave 1.
""",
        encoding="utf-8",
    )

    # 1. Automatic targets & base_audit_workflow inheritance
    loaded = load_workflow("order_migration", tmp_path)
    assert loaded is not None
    wf_info, wf_def = loaded
    assert wf_info.category == WorkflowCategory.MIGRATION
    assert wf_info.based_on == "order_audit"
    assert wf_def.targets.root == "services/order"
    assert wf_def.targets.source == ["app"]
    assert wf_def.targets.tests == ["spec"]
    assert wf_def.targets.docs == ["ARCH.md"]

    prims = normalize_workflow_steps(wf_def, tmp_path)
    mig_prim = next(p for p in prims if p.type.value == "migration_analyze")
    assert mig_prim.params["base_audit_workflow"] == "order_audit"

    mig_only = list_workflows(tmp_path, category=WorkflowCategory.MIGRATION)
    assert [w.id for w in mig_only] == ["order_migration"]

    cli_runner = CliRunner()
    prev_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)

        # 2. CLI list --category filter
        list_res = cli_runner.invoke(app, ["workflows", "list", "--category", "migration"])
        assert list_res.exit_code == 0
        assert "order_migration" in list_res.stdout
        assert "full_audit" not in list_res.stdout

        # 3. Case A: Parent audit never executed -> show displays blocking panel, start exits 1
        show_blocked = cli_runner.invoke(app, ["workflows", "show", "order_migration"])
        assert show_blocked.exit_code == 0
        assert "Blocking Prerequisite" in show_blocked.stdout

        start_blocked = cli_runner.invoke(app, ["workflows", "start", "order_migration"])
        assert start_blocked.exit_code == 1
        combined_out_a = " ".join(start_blocked.output.split())
        assert "pni workflows start order_audit" in combined_out_a

        with pytest.raises(WorkflowPrerequisiteError, match="has not been executed yet|has no completed run"):
            start_workflow_run("order_migration", tmp_path)

        # 4. Case B: Parent audit started (in_progress) -> start STILL exits 1 and points to get-action
        unfinished = start_workflow_run("order_audit", tmp_path)
        assert unfinished is not None

        start_in_prog = cli_runner.invoke(app, ["workflows", "start", "order_migration"])
        assert start_in_prog.exit_code == 1
        combined_out_b = " ".join(start_in_prog.output.split())
        assert unfinished.run_id in combined_out_b
        assert "in_progress" in combined_out_b
        assert f"pni workflows get-action {unfinished.run_id}" in combined_out_b

        # 5. Complete parent audit -> migration start now succeeds and records based_on_run_id
        completed_audit_run_id = _complete_sample_audit_workflow(tmp_path, "order_audit", overall_score=58)

        start_ok = cli_runner.invoke(app, ["workflows", "start", "order_migration"])
        assert start_ok.exit_code == 0
        assert completed_audit_run_id in start_ok.stdout

        status_res = cli_runner.invoke(app, ["workflows", "status"])
        assert status_res.exit_code == 0
        assert "migration" in status_res.stdout

        # 6. Invalid based_on target (missing workflow YAML) raises clean exit code 1
        (wf_dir / "broken_mig.yaml").write_text(
            "id: broken_mig\nname: Broken\ncategory: migration\nbased_on: missing_audit\n"
            "steps:\n  - id: s1\n    action: ast_analyze\n",
            encoding="utf-8",
        )
        broken_show = cli_runner.invoke(app, ["workflows", "show", "broken_mig"])
        assert broken_show.exit_code == 1
    finally:
        os.chdir(prev_cwd)

