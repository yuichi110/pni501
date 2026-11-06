# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Stateful workflow execution engine backed by SQLite (.pni/cache/workflow_state.db)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pni._actions import (
    ActionItem,
    ArchitectureRecord,
    AstFacts,
    CategoryRationales,
    CodeLocation,
    DeterministicAckInput,
    ExecutionFlowMap,
    Finding,
    InterpretationInput,
    MetricScalar,
    MigrationFacts,
    ParamValue,
    PentestFacts,
    PentestOptions,
    PrimitiveStep,
    PrimitiveType,
    ProgressFacts,
    ProjectFacts,
    ReportCompletionInput,
    RuntimeCheckOptions,
    RuntimeFacts,
    ScoreResult,
    SecurityFacts,
    SecurityScanOptions,
    StructureMap,
    SystemProfile,
    extract_verbatim_error_excerpt,
    get_expected_input_schema_json,
    record_audit_history_from_score,
    render_action_task_body,
    run_ast_analyze,
    run_project_inspect,
    run_runtime_check,
    run_security_scan,
    run_web_pentest,
)
from pni._cache import (
    DEFAULT_STATE_DB_REL_PATH,
    default_architecture_rel_path,
    default_facts_rel_path,
    ensure_cache_parent,
)
from pni._config import OptOutEntry, PniConfig, load_pni_config
from pni._pentests import inspect_target_pentests_status
from pni._reporter import DEFAULT_REPORT_OUTPUT_DIR
from pni._rules import get_rule_content
from pni._workflows._migration_engine import (
    execute_migration_analyze_json,
    render_migration_facts,
    validate_and_persist_migration_plan,
)
from pni._workflows._progress_engine import (
    execute_progress_analyze_json,
    inspect_progress_plan_prerequisite,
    render_progress_facts,
    validate_and_persist_progress_result,
)
from pni._workflows.aggregator import (
    compile_workflow_digest,
    normalize_step_rule_checks,
    render_pre_score_digest_markdown,
    score_to_grade,
)
from pni._workflows.base_model import (
    ActionRunRecord,
    RunStatus,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowFactsBundle,
    WorkflowPrerequisiteError,
    WorkflowRunRecord,
)
from pni._workflows.manager import (
    load_workflow,
    normalize_workflow_steps,
    resolve_workflow_outputs,
)
from pni._workflows.state_db import WorkflowStateDB


def inspect_base_audit_status(
    workflow_def: WorkflowDefinition,
    project_root: Path,
) -> tuple[WorkflowRunRecord | None, str | None]:
    """Check SQLite state DB for a completed prerequisite audit run when 'based_on' is declared.

    Note: `category: progress` workflows treat `based_on` as an optional Git-tracked history link
    (`.pni/history/audit/<based_on>.jsonl` / `reports/<based_on>_score.json`) rather than requiring
    `.gitignore`'d `.pni/cache/workflow_state.db`.
    """
    db_file = project_root / DEFAULT_STATE_DB_REL_PATH
    if not workflow_def.based_on or (not db_file.exists() and workflow_def.category == WorkflowCategory.PROGRESS):
        return None, None

    if not db_file.exists():
        err = (
            f"Prerequisite audit workflow '{workflow_def.based_on}' has not been executed yet "
            f"('{DEFAULT_STATE_DB_REL_PATH}' does not exist). "
            f"Run 'pni workflows start {workflow_def.based_on}' and complete all audit actions "
            f"before starting '{workflow_def.id}'."
        )
        return None, err

    db = WorkflowStateDB(project_root)
    completed = db.get_latest_completed_run(workflow_def.based_on)
    if completed is not None or workflow_def.category == WorkflowCategory.PROGRESS:
        return completed, None

    latest = db.get_latest_run(workflow_def.based_on)
    if latest is not None and latest.status == RunStatus.IN_PROGRESS:
        err = (
            f"Prerequisite audit workflow '{workflow_def.based_on}' has an unfinished run "
            f"'{latest.run_id}' (status='{latest.status.value}') in '{DEFAULT_STATE_DB_REL_PATH}'. "
            f"Resume and complete it first with 'pni workflows get-action {latest.run_id}', "
            f"then retry 'pni workflows start {workflow_def.id}'."
        )
        return None, err

    err = (
        f"Prerequisite audit workflow '{workflow_def.based_on}' has no completed run in "
        f"'{DEFAULT_STATE_DB_REL_PATH}'. Run 'pni workflows start {workflow_def.based_on}' "
        f"and complete all audit actions before starting '{workflow_def.id}'."
    )
    return None, err


def inspect_pentests_prerequisite(
    workflow_def: WorkflowDefinition,
    primitives: list[PrimitiveStep],
    project_root: Path,
) -> tuple[Path | None, list[str], str | None]:
    """Check that `.pni/pentests/<target>/` exists whenever a workflow includes `web_pentest`."""
    pentest_steps = [p for p in primitives if p.type == PrimitiveType.WEB_PENTEST]
    if not pentest_steps:
        return None, [], None
    if all(_param_bool(p.params, "force_regenerate_pentests", False) for p in pentest_steps):
        return None, [], None
    return inspect_target_pentests_status(
        project_root,
        workflow_def.targets.root,
        workflow_id=workflow_def.id,
    )


def start_workflow_run(
    workflow_id: str,
    project_root: Path,
    *,
    supersede: bool = False,
) -> WorkflowRunRecord | None:
    """Create a stateful workflow run in .pni/cache/workflow_state.db.

    Args:
        workflow_id: Target workflow identifier in .pni/workflows/.
        project_root: Workspace root directory.
        supersede: When True, automatically cancel any unfinished runs for workflow_id first.

    Returns:
        WorkflowRunRecord | None: Newly created run record, or None if workflow not found.

    Raises:
        WorkflowPrerequisiteError: If 'based_on' audit run, '.pni/progress/' plan, or '.pni/pentests/' is missing.
    """
    loaded = load_workflow(workflow_id, project_root)
    if loaded is None:
        return None

    _, workflow_def = loaded
    parent_run, err_msg = inspect_base_audit_status(workflow_def, project_root)
    if err_msg is not None:
        raise WorkflowPrerequisiteError(err_msg)

    primitives = normalize_workflow_steps(workflow_def, project_root)
    _, _, pentest_err = inspect_pentests_prerequisite(workflow_def, primitives, project_root)
    if pentest_err is not None:
        raise WorkflowPrerequisiteError(pentest_err)

    _, _, prog_err = inspect_progress_plan_prerequisite(workflow_def, primitives, project_root)
    if prog_err is not None:
        raise WorkflowPrerequisiteError(prog_err)

    resolved_outputs = resolve_workflow_outputs(workflow_def, primitives)
    db = WorkflowStateDB(project_root)
    if supersede:
        db.cancel_active_runs_for_workflow(workflow_def.id)
    return db.create_run(
        workflow_def,
        primitives,
        resolved_outputs=resolved_outputs,
        based_on_run_id=parent_run.run_id if parent_run is not None else None,
    )


def _resolve_facts_rel_path(run: WorkflowRunRecord, action: ActionRunRecord | None = None) -> str:
    """Resolve the workspace-relative facts JSON file path for a workflow run or action."""
    if action is not None:
        raw = action.params.get("facts_path")
        if isinstance(raw, str) and raw:
            return raw
    return run.outputs.facts or default_facts_rel_path(run.workflow_id)


def _resolve_arch_rel_path(run: WorkflowRunRecord, action: ActionRunRecord | None = None) -> str:
    """Resolve the workspace-relative architecture record JSON path (.pni/cache/<workflow_id>/architecture.json)."""
    if action is not None:
        raw = action.params.get("architecture_path")
        if isinstance(raw, str) and raw:
            return raw
    return default_architecture_rel_path(run.workflow_id)


def _resolve_score_rel_path(run: WorkflowRunRecord, action: ActionRunRecord | None = None) -> str:
    """Resolve the workspace-relative score JSON file path for a workflow run or action."""
    if action is not None:
        raw = action.params.get("score_path")
        if isinstance(raw, str) and raw:
            return raw
    return run.outputs.score or f"{DEFAULT_REPORT_OUTPUT_DIR}/{run.workflow_id}_score.json"


def _merge_arch_action(record: ArchitectureRecord, act: ActionRunRecord) -> None:
    """Merge a single completed record_architecture action's JSON payload into ArchitectureRecord."""
    if act.agent_input_json is None:
        return
    aspect = str(act.params.get("aspect", "all")).strip()
    if aspect == "purpose_and_stack":
        record.system_profile = SystemProfile.model_validate_json(act.agent_input_json)
    elif aspect == "layers_and_modules":
        record.structure_map = StructureMap.model_validate_json(act.agent_input_json)
    elif aspect == "flows_and_state":
        record.execution_flow_map = ExecutionFlowMap.model_validate_json(act.agent_input_json)
    else:
        full = ArchitectureRecord.model_validate_json(act.agent_input_json)
        record.system_profile = full.system_profile or record.system_profile
        record.structure_map = full.structure_map or record.structure_map
        record.execution_flow_map = full.execution_flow_map or record.execution_flow_map


def _extract_deterministic_facts(bundle: WorkflowFactsBundle, actions: list[ActionRunRecord]) -> None:
    """Populate deterministic facts (project, AST, runtime, security, migration, progress) from actions."""
    for act in actions:
        raw = act.deterministic_output_json
        if raw is None:
            continue
        if act.primitive_type == PrimitiveType.PROJECT_INSPECT and bundle.project_facts is None:
            bundle.project_facts = ProjectFacts.model_validate_json(raw)
        elif act.primitive_type == PrimitiveType.AST_ANALYZE and bundle.ast_facts is None:
            bundle.ast_facts = AstFacts.model_validate_json(raw)
        elif act.primitive_type == PrimitiveType.RUN_CHECK and bundle.runtime_facts is None:
            bundle.runtime_facts = RuntimeFacts.model_validate_json(raw)
        elif act.primitive_type == PrimitiveType.SECURITY_SCAN and bundle.security_facts is None:
            bundle.security_facts = SecurityFacts.model_validate_json(raw)
        elif act.primitive_type == PrimitiveType.WEB_PENTEST and bundle.pentest_facts is None:
            bundle.pentest_facts = PentestFacts.model_validate_json(raw)
        elif act.primitive_type == PrimitiveType.MIGRATION_ANALYZE and bundle.migration_facts is None:
            bundle.migration_facts = MigrationFacts.model_validate_json(raw)
        elif act.primitive_type == PrimitiveType.PROGRESS_ANALYZE and bundle.progress_facts is None:
            bundle.progress_facts = ProgressFacts.model_validate_json(raw)


def _extract_arch_record_from_actions(
    workflow_id: str,
    run_id: str,
    target_root: str,
    actions: list[ActionRunRecord],
) -> ArchitectureRecord | None:
    """Reconstruct an ArchitectureRecord from completed record_architecture actions if present."""
    arch_actions = [
        a for a in actions if a.primitive_type == PrimitiveType.RECORD_ARCHITECTURE and a.agent_input_json is not None
    ]
    if not arch_actions:
        return None
    arch = ArchitectureRecord(
        workflow_id=workflow_id,
        workflow_run_id=run_id,
        recorded_at=arch_actions[-1].updated_at,
        target_root=target_root,
    )
    for act in arch_actions:
        _merge_arch_action(arch, act)
    return arch


def _extract_score_from_actions(actions: list[ActionRunRecord]) -> ScoreResult | None:
    """Extract the most recent persisted ScoreResult from completed emit_score actions."""
    score_actions = [
        a for a in actions if a.primitive_type == PrimitiveType.EMIT_SCORE and a.agent_input_json is not None
    ]
    if not score_actions:
        return None
    return ScoreResult.model_validate_json(score_actions[-1].agent_input_json or "{}")


def _assemble_facts_bundle(
    run: WorkflowRunRecord,
    actions: list[ActionRunRecord],
    db: WorkflowStateDB | None = None,
) -> WorkflowFactsBundle:
    """Reconstruct WorkflowFactsBundle from current run actions plus any 'based_on_run_id' SQLite audit run."""
    bundle = WorkflowFactsBundle(
        workflow_id=run.workflow_id,
        targets=run.targets,
        outputs=run.outputs,
    )
    _extract_deterministic_facts(bundle, actions)
    bundle.architecture_record = _extract_arch_record_from_actions(
        run.workflow_id,
        run.run_id,
        run.targets.root,
        actions,
    )
    if db is not None and run.based_on_run_id:
        parent_actions = db.get_actions(run.based_on_run_id)
        _extract_deterministic_facts(bundle, parent_actions)
        if bundle.architecture_record is None:
            bundle.architecture_record = _extract_arch_record_from_actions(
                run.based_on or run.workflow_id,
                run.based_on_run_id,
                run.targets.root,
                parent_actions,
            )
        bundle.base_score_result = _extract_score_from_actions(parent_actions)
    return bundle


def _param_str(params: dict[str, ParamValue], key: str, default: str) -> str:
    """Read a string action parameter with fallback."""
    val = params.get(key)
    return val if isinstance(val, str) and val.strip() else default


def _param_bool(params: dict[str, ParamValue], key: str, default: bool) -> bool:
    """Read a boolean action parameter with fallback."""
    val = params.get(key)
    return val if isinstance(val, bool) else default


def _param_float(params: dict[str, ParamValue], key: str, default: float) -> float:
    """Read a numeric action parameter as float with fallback."""
    val = params.get(key)
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return float(val)
    return default


def _param_str_tuple(params: dict[str, ParamValue], key: str) -> tuple[str, ...]:
    """Read a string or list[str] action parameter into a tuple of non-empty strings."""
    val = params.get(key)
    if isinstance(val, list):
        return tuple(str(x).strip() for x in val if str(x).strip())
    if isinstance(val, str) and val.strip():
        return tuple(val.split())
    return ()


def _parse_runtime_check_options(params: dict[str, ParamValue]) -> RuntimeCheckOptions:
    """Construct RuntimeCheckOptions from action parameters."""
    raw_port = params.get("smoke_port")
    smoke_port = raw_port if isinstance(raw_port, int) and not isinstance(raw_port, bool) else 18080
    return RuntimeCheckOptions(
        container_engine=_param_str(params, "container_engine", "auto"),
        on_missing_runtime=_param_str(params, "on_missing_runtime", "skip"),
        dockerfile=_param_str(params, "dockerfile", ""),
        force_regenerate_dockerfile=_param_bool(params, "force_regenerate_dockerfile", False),
        extra_apt_packages=_param_str(params, "extra_apt_packages", ""),
        test_cmd=_param_str(params, "test_cmd", ""),
        pytest_extra_args=_param_str_tuple(params, "pytest_extra_args"),
        pre_test_cmd=_param_str(params, "pre_test_cmd", ""),
        smoke_cmd=_param_str(params, "smoke_cmd", ""),
        smoke_port=smoke_port,
        allow_test_network=_param_bool(params, "allow_test_network", False),
        cleanup_images=_param_bool(params, "cleanup_images", True),
        build_timeout_sec=_param_float(params, "build_timeout_sec", 240.0),
        test_timeout_sec=_param_float(params, "test_timeout_sec", 120.0),
        smoke_timeout_sec=_param_float(params, "smoke_timeout_sec", 30.0),
    )


def _execute_run_check_json(
    db: WorkflowStateDB,
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    workspace_root: Path,
    step_lang: str | None,
) -> str:
    """Execute containerized dynamic verification for a RUN_CHECK action and return JSON."""
    prior_bundle = _assemble_facts_bundle(run, db.get_actions(run.run_id), db=db)
    rf = run_runtime_check(
        workspace_root,
        run.workflow_id,
        target_root=run.targets.root,
        source_targets=run.targets.source,
        test_targets=run.targets.tests,
        lang=step_lang,
        project_facts=prior_bundle.project_facts,
        options=_parse_runtime_check_options(action.params),
    )
    return rf.model_dump_json(indent=2)


def _parse_security_scan_options(params: dict[str, ParamValue]) -> SecurityScanOptions:
    """Construct SecurityScanOptions from workflow action parameters."""
    known = set(SecurityScanOptions.model_fields.keys())
    filtered = {k: v for k, v in params.items() if k in known}
    return SecurityScanOptions.model_validate(filtered)


def _execute_security_scan_json(
    db: WorkflowStateDB,
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    workspace_root: Path,
    step_lang: str | None,
) -> str:
    """Execute containerized Trivy security scan for a SECURITY_SCAN action and return JSON."""
    prior_bundle = _assemble_facts_bundle(run, db.get_actions(run.run_id), db=db)
    sf = run_security_scan(
        workspace_root,
        run.workflow_id,
        target_root=run.targets.root,
        source_targets=run.targets.source,
        test_targets=run.targets.tests,
        lang=step_lang,
        project_facts=prior_bundle.project_facts,
        options=_parse_security_scan_options(action.params),
    )
    return sf.model_dump_json(indent=2)


def _parse_pentest_options(params: dict[str, ParamValue]) -> PentestOptions:
    """Construct PentestOptions from workflow action parameters."""
    known = set(PentestOptions.model_fields.keys())
    filtered = {k: v for k, v in params.items() if k in known}
    return PentestOptions.model_validate(filtered)


def _execute_web_pentest_json(
    db: WorkflowStateDB,
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    workspace_root: Path,
    step_lang: str | None,
) -> str:
    """Materialize `.pni/pentests/` and execute isolated loopback `httpx` pentest probes."""
    prior_bundle = _assemble_facts_bundle(run, db.get_actions(run.run_id), db=db)
    pf = run_web_pentest(
        workspace_root,
        run.workflow_id,
        target_root=run.targets.root,
        source_targets=run.targets.source,
        test_targets=run.targets.tests,
        lang=step_lang,
        project_facts=prior_bundle.project_facts,
        ast_facts=prior_bundle.ast_facts,
        options=_parse_pentest_options(action.params),
    )
    return pf.model_dump_json(indent=2)


def _execute_deterministic_step_if_needed(
    db: WorkflowStateDB,
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    workspace_root: Path,
) -> ActionRunRecord:
    """Execute programmatic analyzer on first visit, store output in SQLite, and write facts.json."""
    if action.deterministic_output_json is not None:
        return action

    target_root = (workspace_root / run.targets.root).resolve()
    det_json: str | None = None
    raw_lang = action.params.get("lang")
    step_lang = raw_lang if isinstance(raw_lang, str) else None

    if action.primitive_type == PrimitiveType.PROJECT_INSPECT:
        pf = run_project_inspect(
            target_root,
            source_dirs=run.targets.source,
            test_dirs=run.targets.tests,
            doc_files=run.targets.docs,
            lang=step_lang,
            exclude_globs=run.targets.exclude,
        )
        det_json = pf.model_dump_json(indent=2)
    elif action.primitive_type == PrimitiveType.AST_ANALYZE:
        prior_pf = _assemble_facts_bundle(run, db.get_actions(run.run_id), db=db).project_facts
        raw_targets = action.params.get("targets") or action.params.get("source_targets")
        targets = raw_targets if isinstance(raw_targets, list) else run.targets.source
        raw_tests = action.params.get("test_targets")
        test_targets = raw_tests if isinstance(raw_tests, list) else run.targets.tests
        raw_ex = action.params.get("exclude_globs") or action.params.get("exclude_targets")
        exclude_globs = raw_ex if isinstance(raw_ex, list) else run.targets.exclude
        af = run_ast_analyze(
            target_root,
            targets=targets,
            display_root=workspace_root.resolve(),
            lang=step_lang,
            test_targets=test_targets,
            exclude_globs=exclude_globs,
            detected_frameworks=prior_pf.detected_frameworks if prior_pf is not None else None,
            declared_lang_version=prior_pf.language_version_constraint if prior_pf is not None else None,
        )
        det_json = af.model_dump_json(indent=2)
    elif action.primitive_type == PrimitiveType.RUN_CHECK:
        det_json = _execute_run_check_json(db, run, action, workspace_root, step_lang)
    elif action.primitive_type == PrimitiveType.SECURITY_SCAN:
        det_json = _execute_security_scan_json(db, run, action, workspace_root, step_lang)
    elif action.primitive_type == PrimitiveType.WEB_PENTEST:
        det_json = _execute_web_pentest_json(db, run, action, workspace_root, step_lang)
    elif action.primitive_type == PrimitiveType.MIGRATION_ANALYZE:
        prior_bundle = _assemble_facts_bundle(run, db.get_actions(run.run_id), db=db)
        det_json = execute_migration_analyze_json(prior_bundle, run, action, workspace_root, step_lang)
    elif action.primitive_type == PrimitiveType.PROGRESS_ANALYZE:
        det_json = execute_progress_analyze_json(run, action, workspace_root)

    updated = db.mark_action_in_progress(run.run_id, action.action_id, deterministic_output_json=det_json)
    if det_json is not None:
        all_actions = db.get_actions(run.run_id)
        bundle = _assemble_facts_bundle(run, all_actions, db=db)
        facts_file = workspace_root / _resolve_facts_rel_path(run, action)
        ensure_cache_parent(workspace_root, facts_file)
        facts_file.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")

    return updated or action


def _format_location_list(title: str, locations: list[CodeLocation]) -> list[str]:
    """Format up to 10 CodeLocation entries into Markdown bullet items."""
    if not locations:
        return []
    lines = [f"- **{title} ({len(locations)})**:"]
    for loc in locations[:10]:
        lines.append(f"  - `{loc.file}:{loc.line}` (`{loc.symbol}`): {loc.detail}")
    return lines


def _render_project_facts(pf: ProjectFacts) -> list[str]:
    """Render deterministic ProjectFacts into Markdown bullet lines."""
    lines = [
        "\n### Deterministic Project Facts (`project_inspect`)",
        (
            f"- **Project**: `{pf.project_name}` (v{pf.version}, "
            f"language: `{pf.language}`, runtime_types: `{pf.runtime_types}`, "
            f"build_system: `{pf.build_system}`, "
            f"version_constraint: `{pf.language_version_constraint or 'unset'}`, "
            f"type_marker: `{pf.has_type_marker}`)"
        ),
        f"- **Detected Frameworks**: {pf.detected_frameworks or 'None'}",
        f"- **Manifests & Lockfiles**: manifests={pf.manifest_files}, lockfiles={pf.lockfiles_found}",
        f"- **Dependencies ({len(pf.dependencies)})**: {', '.join(pf.dependencies) or 'None'}",
        f"- **Unpinned Dependencies ({len(pf.unpinned_dependencies)})**: {pf.unpinned_dependencies}",
        f"- **Source / Test Files**: `{pf.source_files_count}` source, `{pf.test_files_count}` test files",
        (
            f"- **Governance & Supply Chain**: `LICENSE`={pf.has_license}, "
            f"`SECURITY.md`={pf.has_security_policy}, "
            f"`dependency_automation`={pf.has_dependency_automation}, "
            f"`ci_workflows`={pf.ci_workflows_found}"
        ),
        (
            f"- **Documentation & Git**: `README`={pf.has_readme} ({pf.readme_line_count} lines), "
            f"`.gitignore`={pf.has_gitignore}, `docs_inventory`={pf.docs_inventory}"
        ),
    ]
    if pf.readme_headings:
        lines.append(f"- **README Headings ({len(pf.readme_headings)})**: {pf.readme_headings}")
    for label, items in (
        ("CI Supply-Chain Issues", pf.ci_supply_chain_issues),
        ("Committed Secret / Key Files", pf.committed_secret_files),
        ("Container / Dockerfile Hygiene Issues", pf.container_hygiene_issues),
        ("Legacy Language Findings", pf.legacy_language_findings),
        ("Tooling Modernization Issues", pf.tooling_modernization_issues),
    ):
        if items:
            lines.append(f"- **{label} ({len(items)})**: {items}")
    return lines


def _render_internal_import_graph(graph: dict[str, list[str]]) -> list[str]:
    """Render internal import graph JSON, capping large graphs (> 60 modules) by fan-out."""
    if not graph:
        return []
    if len(graph) <= 60:
        graph_json = json.dumps(graph, indent=2)
        return [f"- **Internal Import Graph**:\n```json\n{graph_json}\n```"]
    top_keys = sorted(graph, key=lambda k: len(graph[k]), reverse=True)[:40]
    sample = {k: graph[k][:15] for k in top_keys}
    graph_json = json.dumps(sample, indent=2)
    return [
        f"- **Internal Import Graph (Top 40 of {len(graph)} modules by fan-out; full graph in facts.json)**:\n"
        f"```json\n{graph_json}\n```"
    ]


def _render_ast_facts(af: AstFacts) -> list[str]:
    """Render deterministic AstFacts including module inventory and all 8 checker dimensions."""
    imp_pct = f"{af.import_hygiene_coverage_pct}%" if af.import_hygiene_coverage_pct is not None else "N/A"
    typ_pct = f"{af.type_safety_coverage_pct}%" if af.type_safety_coverage_pct is not None else "N/A"
    doc_pct = f"{af.docstring_coverage_pct}%" if af.docstring_coverage_pct is not None else "N/A"
    tst_pct = f"{af.module_test_coverage_pct}%" if af.module_test_coverage_pct is not None else "N/A"
    lines = [
        f"\n### Deterministic AST Facts (`ast_analyze`, language=`{af.language}`)",
        (
            f"- **Codebase Size**: `{af.total_files}` files, `{af.total_loc}` LOC, "
            f"`{af.total_classes}` classes, `{af.total_functions}` functions"
        ),
        f"- **Import Hygiene Coverage**: `{imp_pct}`",
        f"- **Type Safety Coverage**: `{typ_pct}`",
        f"- **Docstring / Javadoc Coverage**: `{doc_pct}`",
        f"- **Test Suite AST**: `{af.test_functions_count}` tests, module coverage `{tst_pct}`",
        (
            f"- **Circular Dependencies**: `{len(af.circular_dependencies)}` "
            f"(type-checking-only cycles: `{len(af.type_checking_cycles)}`)"
        ),
    ]
    if af.type_checking_cycles:
        lines.append(
            f"- **Type-Checking-Only Import Cycles ({len(af.type_checking_cycles)}, zero runtime impact)**: "
            f"{af.type_checking_cycles[:5]}"
        )
    if af.test_harness_notes:
        lines.append(f"- **Test Harness Notes ({len(af.test_harness_notes)})**: {af.test_harness_notes}")
    if af.unused_dependencies:
        lines.append(f"- **Unused Declared Dependencies ({len(af.unused_dependencies)})**: {af.unused_dependencies}")
    for title, locs in (
        ("Unsorted / Misgrouped Imports", af.unsorted_imports),
        ("Wildcard Imports", af.wildcard_imports),
        ("Late (In-Function) Imports", af.late_imports),
        ("Type Safety Issues", af.type_safety_issues),
        ("Weak / Suppressed Type Usages", af.weak_type_usages),
        ("Unscoped Type Ignores", af.unscoped_type_ignores),
        ("Missing Docstrings / Javadocs", af.missing_docstrings),
        ("Empty / Stub Docstrings", af.empty_docstrings),
        ("Docstring Signature Mismatches", af.doc_signature_mismatches),
        ("Complex / Long Functions", af.complex_functions),
        ("Excessive Parameters (> 6, SIG Unit Interfacing)", af.excessive_parameters),
        ("Mutable Global / Static State Usages", af.global_state_usages),
        ("Bug-Risk & Dangerous Idioms", af.bug_risk_idioms),
        ("Undeclared / Dev-in-Prod Imports", af.undeclared_dependencies),
        ("Architectural Boundary Violations", af.boundary_violations),
        ("Assertion-Free Tests", af.assertion_free_tests),
        ("Framework Best-Practice Issues", af.framework_issues),
        ("Modernization Hints", af.modernization_hints),
        ("Language-Version API / Syntax Mismatches", af.language_version_mismatches),
        ("Missing External I/O Timeouts (SRE PRR)", af.missing_io_timeouts),
        ("Scattered Direct Env Access (12-Factor III)", af.scattered_env_access),
        ("Unstructured Console Logging (12-Factor XI)", af.unstructured_logging),
        ("Hardcoded Secrets / Credentials (OWASP ASVS)", af.hardcoded_secrets),
    ):
        lines.extend(_format_location_list(title, locs))
    lines.extend(_render_ast_security_section(af))
    if af.module_inventory:
        inv_preview = [
            f"  - `{m.file}` ({m.loc} LOC): types={m.public_types}, callables={m.public_callables[:6]}"
            for m in af.module_inventory[:25]
        ]
        lines.append(f"- **Module Inventory ({len(af.module_inventory)} files)**:\n" + "\n".join(inv_preview))
    lines.extend(_render_internal_import_graph(af.internal_import_graph))
    return lines


def _render_ast_security_section(af: AstFacts) -> list[str]:
    """Render AST-extracted CWE dangerous sinks and API endpoint attack surface."""
    lines: list[str] = []
    if af.dangerous_sinks:
        lines.append(f"- **Dangerous Code Sinks (CWE SAST, {len(af.dangerous_sinks)})**:")
        for sink in af.dangerous_sinks[:12]:
            sym = f" (`{sink.symbol}`)" if sink.symbol else ""
            lines.append(
                f"  - `[{sink.severity.upper()}]` `{sink.cwe_id}` `{sink.category}` "
                f"`{sink.file}:{sink.line}`{sym}: {sink.detail}"
            )
    if af.api_endpoints:
        unauth = sum(1 for ep in af.api_endpoints if not ep.has_auth_hint)
        lines.append(
            f"- **Extracted API Endpoints (Attack Surface, total={len(af.api_endpoints)}, "
            f"without_auth_hint={unauth})**:"
        )
        for ep in af.api_endpoints[:15]:
            auth_lbl = f"auth={ep.auth_mechanisms}" if ep.has_auth_hint else "auth_hint=NONE"
            lines.append(
                f"  - `{ep.http_method} {ep.path}` -> `{ep.handler}` (`{ep.file}:{ep.line}`, {auth_lbl})"
            )
    return lines


def _render_runtime_failures_and_coverage(rf: RuntimeFacts) -> list[str]:
    """Render verbatim build/smoke compiler diagnostics, test failures, and lowest-covered modules."""
    lines: list[str] = []
    if rf.project_dockerfile_build is not None and rf.project_dockerfile_build.error_tail:
        proj_excerpt = extract_verbatim_error_excerpt(rf.project_dockerfile_build.error_tail, max_lines=4)
        if proj_excerpt:
            lines.append("- **Project Dockerfile Verbatim Error Excerpt**:")
            lines.extend(f"  - `{ln}`" for ln in proj_excerpt)
    if rf.harness_build.error_tail:
        harness_excerpt = extract_verbatim_error_excerpt(rf.harness_build.error_tail, max_lines=5)
        lines.append("- **Harness Build Verbatim Error Excerpt**:")
        lines.extend(f"  - `{ln}`" for ln in harness_excerpt)
    if rf.test_execution.failures:
        lines.append(f"- **Failed / Error Test Cases ({len(rf.test_execution.failures)})**:")
        for fc in rf.test_execution.failures[:10]:
            lines.append(f"  - `[{fc.kind.upper()}]` `{fc.classname}.{fc.name}`: {fc.message[:200]}")
    if rf.coverage.lowest_covered_modules:
        lines.append("- **Lowest-Covered Modules (Measured Ascending)**:")
        for item in rf.coverage.lowest_covered_modules[:8]:
            br = f", branch={item.branch_coverage_pct}%" if item.branch_coverage_pct is not None else ""
            lines.append(
                f"  - `{item.file_path}`: line=`{item.line_coverage_pct}%`{br} "
                f"(`{item.covered_lines}/{item.total_statements}` stmts, missing={item.missing_lines_preview[:10]})"
            )
    if rf.smoke_check.log_tail:
        smoke_excerpt = extract_verbatim_error_excerpt(rf.smoke_check.log_tail, max_lines=4)
        lines.append(f"- **Smoke Check Failure Excerpt**: {smoke_excerpt}")
    return lines


def _render_runtime_facts(rf: RuntimeFacts) -> list[str]:
    """Render deterministic RuntimeFacts into Markdown bullet lines."""
    lines = [
        f"\n### Containerized Runtime Verification (`run_check`, status=`{rf.status}`)",
        (
            f"- **Container Engine**: `{rf.container_engine or 'unavailable'}` "
            f"(available=`{rf.engine_available}`, skip_reason=`{rf.skip_reason or 'none'}`)"
        ),
        (
            f"- **Harness Dockerfile**: `{rf.harness_dockerfile_path}` "
            f"(template=`{rf.selected_dockerfile_template}`, build_args={rf.build_args})"
        ),
    ]
    if rf.project_dockerfile_build is not None:
        pb = rf.project_dockerfile_build
        lines.append(
            f"- **Project Dockerfile Build**: status=`{pb.status}`, "
            f"file=`{pb.dockerfile_used}`, duration=`{pb.duration_sec}s`"
        )
    hb = rf.harness_build
    te = rf.test_execution
    cv = rf.coverage
    sm = rf.smoke_check
    lines.extend(
        [
            f"- **Harness Image Build**: status=`{hb.status}`, duration=`{hb.duration_sec}s`",
            (
                f"- **Offline Unit Tests (`--network=none`)**: status=`{te.status}`, "
                f"total=`{te.total_tests}`, passed=`{te.passed_tests}`, failed=`{te.failed_tests}`, "
                f"errors=`{te.error_tests}`, skipped=`{te.skipped_tests}`, duration=`{te.duration_sec}s`"
            ),
            (
                f"- **Measured Coverage (`{cv.tool or 'none'}`)**: measured=`{cv.measured}`, "
                f"line=`{cv.line_coverage_pct}%`, branch=`{cv.branch_coverage_pct}%` "
                f"(`{cv.covered_lines}/{cv.total_statements}` statements)"
            ),
            (
                f"- **Startup Smoke Check (`{sm.archetype}`)**: status=`{sm.status}`, "
                f"failure_kind=`{sm.failure_kind}`, detail=`{sm.detail or 'ok'}`"
            ),
            *_render_runtime_failures_and_coverage(rf),
        ]
    )
    return lines


def _render_security_facts(sf: SecurityFacts) -> list[str]:
    """Render deterministic SecurityFacts (Trivy CVEs, IaC misconfigs, redacted secrets) into Markdown."""
    ac = sf.app_vuln_counts
    oc = sf.os_vuln_counts
    lines = [
        f"\n### Containerized Security & Supply-Chain Scan (`security_scan`, status=`{sf.status}`)",
        (
            f"- **Scanner & Runtime**: `{sf.scanner}` (`{sf.trivy_image}`), engine=`{sf.container_engine}`, "
            f"fs_scanned=`{sf.scanned_filesystem}`, image_scanned=`{sf.scanned_resolved_image}` "
            f"(source=`{sf.resolved_image_source or 'none'}`, skip_reason=`{sf.skip_reason or 'none'}`)"
        ),
        (
            f"- **Application Dependency CVEs**: total=`{ac.total}` "
            f"(CRITICAL=`{ac.critical}`, HIGH=`{ac.high}`, MEDIUM=`{ac.medium}`, LOW=`{ac.low}`)"
        ),
        (
            f"- **Container OS Layer CVEs**: total=`{oc.total}` "
            f"(CRITICAL=`{oc.critical}`, HIGH=`{oc.high}`, MEDIUM=`{oc.medium}`, LOW=`{oc.low}`)"
        ),
    ]
    if sf.vulnerabilities:
        lines.append(f"- **Top Deduplicated Vulnerabilities ({len(sf.vulnerabilities)} shown)**:")
        for v in sf.vulnerabilities[:12]:
            fix_lbl = f" -> fix=`{v.fixed_version}`" if v.fixed_version else " (no upstream fix)"
            unpinned_lbl = (
                f" [UNPINNED RANGE MATCH: {v.version_resolution_note}]" if v.is_unpinned_specifier else ""
            )
            lines.append(
                f"  - `[{v.severity}]` `{v.vuln_id}` in `{v.pkg_name}@{v.installed_version}` "
                f"(`{v.pkg_type}`){fix_lbl}{unpinned_lbl}: {v.title[:100]}"
            )
    if sf.misconfigurations:
        lines.append(f"- **Container / IaC Misconfigurations ({len(sf.misconfigurations)})**:")
        for m in sf.misconfigurations[:10]:
            ln = f":{m.start_line}" if m.start_line else ""
            lines.append(f"  - `[{m.severity}]` `{m.check_id}` (`{m.file_path}{ln}`): {m.title}")
    if sf.secrets:
        lines.append(f"- **Detected Secrets (Redacted, {len(sf.secrets)})**:")
        for s in sf.secrets[:10]:
            ln = f":{s.start_line}" if s.start_line else ""
            lines.append(
                f"  - `[{s.severity}]` `{s.rule_id}` (`{s.file_path}{ln}`): {s.title} (`{s.redacted_match}`)"
            )
    return lines


def _render_base_score_summary(sr: ScoreResult) -> list[str]:
    """Render concise baseline audit score and top findings inherited from a completed SQLite audit run."""
    cs = sr.category_scores
    lines = [
        f"\n### Baseline Audit Score Summary (Inherited from SQLite Audit Run `{sr.workflow_run_id or '-'}`)",
        (
            f"- **Overall Score**: `{sr.overall_score}/100` (Grade `{sr.grade}`) | "
            f"arch=`{cs.architecture}`, code=`{cs.code_quality}`, typing=`{cs.typing}`, "
            f"test=`{cs.testing}`, deps=`{cs.dependencies}`, sec=`{cs.security}`, docs=`{cs.documentation}`"
        ),
        f"- **Audit Summary**: {sr.summary}",
    ]
    if sr.findings:
        lines.append(f"- **Top Inherited Audit Findings ({len(sr.findings)} total)**:")
        for f in sr.findings[:8]:
            loc = f" (`{f.file_path}:{f.line}`)" if f.file_path else ""
            lines.append(f"  - `[{f.severity.upper()}]` `{f.rule_id}`{loc}: {f.description}")
    return lines


def _render_pentest_facts(pf: PentestFacts) -> list[str]:
    """Render deterministic PentestFacts (live HTTP probes & CWE findings) into Markdown."""
    ps = pf.probe_summary
    lines = [
        f"\n### Dynamic Web Penetration Test (`web_pentest`, status=`{pf.status}`)",
        (
            f"- **Suite & Target**: suite=`{pf.pentests_dir or '.pni/pentests'}`, "
            f"engine=`{pf.container_engine}`, booted=`{pf.server_booted}`, "
            f"base_url=`{pf.target_base_url or '-'}`, skip_reason=`{pf.skip_reason or 'none'}`"
        ),
        (
            f"- **Probe Summary**: total=`{ps.total_probes}`, passed=`{ps.passed_probes}`, "
            f"failed=`{ps.failed_probes}`, skipped=`{ps.skipped_probes}`, errors=`{ps.error_probes}`"
        ),
    ]
    if pf.boot_failure_reason:
        lines.append(f"- **Boot / Execution Failure**: `{pf.boot_failure_reason}`")
    if pf.materialized_files:
        lines.append(f"- **Materialized Test Files**: {', '.join(f'`{f}`' for f in pf.materialized_files)}")
    if pf.findings:
        lines.append(f"- **Live Penetration Findings ({len(pf.findings)})**:")
        for item in pf.findings[:15]:
            lines.append(
                f"  - `[{item.severity.upper()}]` `{item.cwe_id}` on `{item.endpoint}` "
                f"(`{item.test_file}`): {item.title} — `{item.evidence}`"
            )
    return lines


def _render_bundle_facts(bundle: WorkflowFactsBundle) -> list[str]:
    """Render accumulated ProjectFacts, AstFacts, RuntimeFacts, SecurityFacts, PentestFacts, and Architecture."""
    lines: list[str] = []
    if bundle.base_score_result is not None:
        lines.extend(_render_base_score_summary(bundle.base_score_result))
    if bundle.project_facts is not None:
        lines.extend(_render_project_facts(bundle.project_facts))
    if bundle.ast_facts is not None:
        lines.extend(_render_ast_facts(bundle.ast_facts))
    if bundle.runtime_facts is not None:
        lines.extend(_render_runtime_facts(bundle.runtime_facts))
    if bundle.security_facts is not None:
        lines.extend(_render_security_facts(bundle.security_facts))
    if bundle.pentest_facts is not None:
        lines.extend(_render_pentest_facts(bundle.pentest_facts))
    if bundle.migration_facts is not None:
        lines.extend(render_migration_facts(bundle.migration_facts))
    if bundle.progress_facts is not None:
        lines.extend(render_progress_facts(bundle.progress_facts))
    if bundle.architecture_record is not None:
        arch_json = bundle.architecture_record.model_dump_json(indent=2, exclude_none=True)
        lines.append(f"\n### Recorded Grounded Architecture (`record_architecture`)\n```json\n{arch_json}\n```")
    return lines


def _render_active_opt_outs(opt_outs: list[OptOutEntry]) -> list[str]:
    """Render configured [[opt_out]] design waivers from .pni/pni.toml."""
    if not opt_outs:
        return []
    lines = [
        "\n### Active Design Waivers (`.pni/pni.toml` `[[opt_out]]`)",
        "The following rules/checks have been explicitly opted out with documented engineering rationale.",
        "Do NOT emit findings, action items, or score penalties for items covered by these waivers:",
    ]
    for entry in opt_outs:
        scope_str = ", ".join(entry.scope) if entry.scope else "repo-wide"
        lines.append(f"- `{entry.id}` (scope: `{scope_str}`) — {entry.reason}")
    return lines


def _render_active_rules(rule_ids: list[str], project_root: Path) -> list[str]:
    """Load and render full Markdown standards for the action's target rules."""
    if not rule_ids:
        return []
    lines = ["\n## Active Engineering Rules for This Action"]
    for rid in rule_ids:
        res = get_rule_content(rid, project_root)
        if res is not None:
            info, content = res
            lines.append(f"\n### Rule `{info.identifier}`\n{content.strip()}")
    return lines


def _render_single_interpretation(act: ActionRunRecord, parsed: InterpretationInput) -> list[str]:
    """Render one completed ai_interpret record into Markdown lines."""
    lines = [f"\n### From `{act.action_id}` ({act.name})", f"- **Summary**: {parsed.summary}"]
    if parsed.step_score is not None:
        lines.append(f"- **Step Score**: `{parsed.step_score}/100`")
    if parsed.suggested_scores:
        lines.append(f"- **Suggested Category Scores**: `{parsed.suggested_scores}`")
    if parsed.category_rationales:
        lines.append(f"- **Category Rationales**: `{parsed.category_rationales}`")
    if parsed.rule_checks:
        statuses = [f"{rc.rule_id}={rc.status}" for rc in parsed.rule_checks]
        lines.append(f"- **Rule Checks ({len(parsed.rule_checks)})**: {statuses}")
    if parsed.strengths:
        lines.append(f"- **Strengths ({len(parsed.strengths)})**: {parsed.strengths}")
    if parsed.modules:
        mod_paths = [f"{m.path} ({m.role})" for m in parsed.modules]
        lines.append(f"- **Mapped Modules ({len(parsed.modules)})**: {mod_paths}")
    if parsed.findings:
        lines.append(f"- **Findings ({len(parsed.findings)})**:")
        for f in parsed.findings:
            loc = f" (`{f.file_path}:{f.line}`)" if f.file_path else ""
            lines.append(f"  - [{f.severity.upper()}] `{f.rule_id}`{loc}: {f.description}")
    return lines


def _render_prior_interpretations(actions: list[ActionRunRecord]) -> list[str]:
    """Render accumulated findings and suggested scores from completed ai_interpret steps."""
    prior = [
        a for a in actions if a.primitive_type == PrimitiveType.AI_INTERPRET and a.agent_input_json is not None
    ]
    if not prior:
        return []

    lines = ["\n## Prior AI Interpretation Results (Stored in `workflow_state.db`)"]
    for act in prior:
        if act.agent_input_json is not None:
            parsed = InterpretationInput.model_validate_json(act.agent_input_json)
            lines.extend(_render_single_interpretation(act, parsed))
    return lines


def _format_action_guide(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    all_actions: list[ActionRunRecord],
    project_root: Path,
    db: WorkflowStateDB | None = None,
) -> str:
    """Format the complete deterministic prompt for a single stateful action step."""
    pni_cfg = load_pni_config(project_root)
    bundle = _assemble_facts_bundle(run, all_actions, db=db)
    origin = f" (from `{action.source_action}`)" if action.source_action else ""
    effective_params: dict[str, ParamValue] = {
        "workflow_id": run.workflow_id,
        "facts_path": _resolve_facts_rel_path(run, action),
        "architecture_path": _resolve_arch_rel_path(run, action),
        "score_path": _resolve_score_rel_path(run, action),
        **action.params,
    }
    base_line = (
        [f"- **Based On Audit**: `{run.based_on}` (SQLite run: `{run.based_on_run_id or '-'}`)"]
        if run.based_on
        else []
    )
    lines: list[str] = [
        f"# PNI Workflow Action: `{action.action_id}` ({action.seq}/{len(all_actions)})",
        f"- **Workflow Run ID**: `{run.run_id}` (`{run.workflow_id}`, category=`{run.category.value}`)",
        *base_line,
        f"- **Action ID**: `{action.action_id}`",
        f"- **Primitive Type**: `{action.primitive_type.value}`{origin}",
        f"- **Step Name**: {action.name}\n",
        "## Action Instructions",
        render_action_task_body(
            action.primitive_type,
            effective_params,
            action.prompt,
            rules=action.rules,
            source_action=action.source_action,
            project_root=project_root,
        ),
    ]

    lines.extend(_render_bundle_facts(bundle))
    lines.extend(_render_active_opt_outs(pni_cfg.opt_out))
    lines.extend(_render_active_rules(action.rules, project_root))

    if action.primitive_type in (
        PrimitiveType.EMIT_SCORE,
        PrimitiveType.EMIT_MIGRATION_PLAN,
        PrimitiveType.EMIT_PROGRESS,
        PrimitiveType.WRITE_DRAWLIB_REPORT,
    ):
        lines.extend(_render_prior_interpretations(all_actions))
    if action.primitive_type == PrimitiveType.EMIT_SCORE:
        lines.extend(
            render_pre_score_digest_markdown(
                compile_workflow_digest(all_actions, bundle, opt_outs=pni_cfg.opt_out)
            )
        )

    schema_str = get_expected_input_schema_json(action.primitive_type, action.params)
    lines.extend(
        [
            "\n## Submit Action Result (`push-action`)",
            "After completing the work above, submit your JSON payload to advance the workflow state:",
            "```bash",
            f"pni workflows push-action {run.run_id} {action.action_id} '<JSON_INPUT>'",
            f"# Or from a JSON file: pni workflows push-action {run.run_id} {action.action_id} --file <path.json>",
            "```",
            "\n### Required `INPUT` JSON Schema:",
            f"```json\n{schema_str}\n```",
        ]
    )
    return "\n".join(lines) + "\n"


def get_workflow_action(
    run_id: str,
    project_root: Path,
) -> tuple[WorkflowRunRecord | None, ActionRunRecord | None, str]:
    """Fetch and prepare the current pending/active action for a workflow run.

    Args:
        run_id: Workflow run identifier (e.g. 'wf-1a2b3c4d').
        project_root: Workspace root directory.

    Returns:
        tuple[WorkflowRunRecord | None, ActionRunRecord | None, str]:
            Run record, current action record (None if workflow finished), and Markdown output.
    """
    db = WorkflowStateDB(project_root)
    run = db.get_run(run_id)
    if run is None:
        return None, None, f"Error: Workflow run '{run_id}' not found in .pni/cache/workflow_state.db."
    if run.status == RunStatus.CANCELLED:
        msg = (
            f"Error: Workflow run '{run_id}' ({run.workflow_id}) was cancelled. "
            f"Start a new run with 'pni workflows start {run.workflow_id}'."
        )
        return None, None, msg

    current = db.get_current_action(run_id)
    if current is None:
        db.complete_workflow_run(run_id)
        facts_out = _resolve_facts_rel_path(run)
        score_out = _resolve_score_rel_path(run)
        report_out = run.outputs.report or "-"
        done_msg = (
            f"# PNI Workflow Completed (`{run.run_id}`)\n"
            f"- **Workflow**: {run.workflow_name} (`{run.workflow_id}`)\n"
            f"- **Status**: `COMPLETED`\n"
            f"- **Facts Output**: `{facts_out}`\n"
            f"- **Score Output**: `{score_out}`\n"
            f"- **Report Output**: `{report_out}`\n"
        )
        return run, None, done_msg

    if (
        current.primitive_type == PrimitiveType.WEB_PENTEST
        and current.deterministic_output_json is None
        and not _param_bool(current.params, "force_regenerate_pentests", False)
    ):
        _, _, pentest_err = inspect_target_pentests_status(
            project_root,
            run.targets.root,
            workflow_id=run.workflow_id,
        )
        if pentest_err is not None:
            raise WorkflowPrerequisiteError(pentest_err)

    current = _execute_deterministic_step_if_needed(db, run, current, project_root)
    all_actions = db.get_actions(run_id)
    guide = _format_action_guide(run, current, all_actions, project_root, db=db)
    return run, current, guide


def _set_opt_metric(metrics: dict[str, MetricScalar], key: str, val: float | None) -> None:
    """Assign an optional float metric into metrics dict only when non-None."""
    if val is not None:
        metrics[key] = val


def _build_deterministic_metrics(bundle: WorkflowFactsBundle) -> dict[str, MetricScalar]:
    """Build canonical deterministic metrics snapshot from ProjectFacts and AstFacts."""
    metrics: dict[str, MetricScalar] = {}
    if bundle.project_facts is not None:
        pf = bundle.project_facts
        metrics["language"] = pf.language
        metrics["runtime_types"] = [str(rt) for rt in pf.runtime_types]
        metrics["build_system"] = pf.build_system
        metrics["has_manifest"] = len(pf.manifest_files) > 0
        metrics["has_lockfile"] = len(pf.lockfiles_found) > 0
        metrics["has_license"] = pf.has_license
        metrics["has_security_policy"] = pf.has_security_policy
        metrics["has_dependency_automation"] = pf.has_dependency_automation
        if pf.has_type_marker is not None:
            metrics["has_type_marker"] = pf.has_type_marker
        metrics["dependencies_count"] = len(pf.dependencies)
        metrics["unpinned_dependencies_count"] = len(pf.unpinned_dependencies)
        metrics["source_files_count"] = pf.source_files_count
        metrics["test_files_count"] = pf.test_files_count
        metrics["readme_line_count"] = pf.readme_line_count
        metrics["ci_supply_chain_issues_count"] = len(pf.ci_supply_chain_issues)
        metrics["committed_secret_files_count"] = len(pf.committed_secret_files)
        metrics["container_hygiene_issues_count"] = len(pf.container_hygiene_issues)
        metrics["legacy_language_findings_count"] = len(pf.legacy_language_findings)
    if bundle.ast_facts is not None:
        af = bundle.ast_facts
        metrics["total_files"] = af.total_files
        metrics["total_loc"] = af.total_loc
        metrics["total_classes"] = af.total_classes
        metrics["total_functions"] = af.total_functions
        _set_opt_metric(metrics, "import_hygiene_coverage_pct", af.import_hygiene_coverage_pct)
        _set_opt_metric(metrics, "type_safety_coverage_pct", af.type_safety_coverage_pct)
        _set_opt_metric(metrics, "docstring_coverage_pct", af.docstring_coverage_pct)
        _set_opt_metric(metrics, "module_test_coverage_pct", af.module_test_coverage_pct)
        metrics["unsorted_imports_count"] = len(af.unsorted_imports)
        metrics["wildcard_imports_count"] = len(af.wildcard_imports)
        metrics["type_safety_issues_count"] = len(af.type_safety_issues)
        metrics["weak_type_usages_count"] = len(af.weak_type_usages)
        metrics["empty_docstrings_count"] = len(af.empty_docstrings)
        metrics["doc_signature_mismatches_count"] = len(af.doc_signature_mismatches)
        metrics["complex_functions_count"] = len(af.complex_functions)
        metrics["excessive_parameters_count"] = len(af.excessive_parameters)
        metrics["global_state_usages_count"] = len(af.global_state_usages)
        metrics["bug_risk_idioms_count"] = len(af.bug_risk_idioms)
        metrics["circular_dependencies_count"] = len(af.circular_dependencies)
        metrics["type_checking_cycles_count"] = len(af.type_checking_cycles)
        metrics["unused_dependencies_count"] = len(af.unused_dependencies)
        metrics["undeclared_dependencies_count"] = len(af.undeclared_dependencies)
        metrics["test_functions_count"] = af.test_functions_count
        metrics["assertion_free_tests_count"] = len(af.assertion_free_tests)
        metrics["has_conftest_assertion_hook"] = len(af.test_harness_notes) > 0
        metrics["framework_issues_count"] = len(af.framework_issues)
        metrics["modernization_hints_count"] = len(af.modernization_hints)
        metrics["language_version_mismatches_count"] = len(af.language_version_mismatches)
        metrics["missing_io_timeouts_count"] = len(af.missing_io_timeouts)
        metrics["scattered_env_access_count"] = len(af.scattered_env_access)
        metrics["unstructured_logging_count"] = len(af.unstructured_logging)
        metrics["hardcoded_secrets_count"] = len(af.hardcoded_secrets)
        metrics["ast_dangerous_sinks_count"] = len(af.dangerous_sinks)
        metrics["api_endpoints_count"] = len(af.api_endpoints)
    if bundle.runtime_facts is not None:
        _populate_runtime_metrics(metrics, bundle.runtime_facts)
    if bundle.security_facts is not None:
        _populate_security_metrics(metrics, bundle.security_facts)
    if bundle.pentest_facts is not None:
        _populate_pentest_metrics(metrics, bundle.pentest_facts)
    return metrics


def _populate_runtime_metrics(metrics: dict[str, MetricScalar], rf: RuntimeFacts) -> None:
    """Populate deterministic container runtime, test, coverage, and smoke metrics."""
    metrics["runtime_status"] = rf.status
    metrics["harness_build_status"] = rf.harness_build.status
    metrics["tests_status"] = rf.test_execution.status
    metrics["tests_total"] = rf.test_execution.total_tests
    metrics["tests_passed"] = rf.test_execution.passed_tests
    metrics["tests_failed"] = rf.test_execution.failed_tests + rf.test_execution.error_tests
    _set_opt_metric(metrics, "measured_line_coverage_pct", rf.coverage.line_coverage_pct)
    _set_opt_metric(metrics, "measured_branch_coverage_pct", rf.coverage.branch_coverage_pct)
    metrics["smoke_check_status"] = rf.smoke_check.status


def _populate_security_metrics(metrics: dict[str, MetricScalar], sf: SecurityFacts) -> None:
    """Populate deterministic Trivy CVE, misconfiguration, and secret metrics."""
    metrics["security_scan_status"] = sf.status
    metrics["app_vuln_critical"] = sf.app_vuln_counts.critical
    metrics["app_vuln_high"] = sf.app_vuln_counts.high
    metrics["app_vuln_total"] = sf.app_vuln_counts.total
    metrics["app_vuln_unpinned_range_matches"] = sum(1 for v in sf.vulnerabilities if v.is_unpinned_specifier)
    metrics["os_vuln_high_or_crit"] = sf.os_vuln_counts.critical + sf.os_vuln_counts.high
    metrics["misconfig_count"] = len(sf.misconfigurations)
    metrics["secret_leak_count"] = len(sf.secrets)


def _populate_pentest_metrics(metrics: dict[str, MetricScalar], pf: PentestFacts) -> None:
    """Populate deterministic dynamic HTTP penetration probe metrics."""
    metrics["pentest_status"] = pf.status
    metrics["pentest_probes_total"] = pf.probe_summary.total_probes
    metrics["pentest_probes_passed"] = pf.probe_summary.passed_probes
    metrics["pentest_probes_failed"] = pf.probe_summary.failed_probes + pf.probe_summary.error_probes
    metrics["pentest_findings_count"] = len(pf.findings)
    metrics["pentest_high_or_crit_count"] = sum(1 for f in pf.findings if f.severity in {"critical", "high"})


def _enrich_architecture_overview(score_obj: ScoreResult, arch: ArchitectureRecord) -> None:
    """Populate legacy architecture_overview fields from grounded ArchitectureRecord when empty."""
    if arch.structure_map is not None:
        if not score_obj.architecture_overview.pattern:
            score_obj.architecture_overview.pattern = arch.structure_map.architecture_pattern
        if not score_obj.architecture_overview.modules:
            score_obj.architecture_overview.modules = arch.structure_map.modules
        if not score_obj.architecture_overview.dependency_notes:
            score_obj.architecture_overview.dependency_notes = arch.structure_map.boundary_assessment
    if arch.execution_flow_map is not None and not score_obj.architecture_overview.entry_points:
        score_obj.architecture_overview.entry_points = arch.execution_flow_map.entry_points


def _merge_category_rationales(target: CategoryRationales, fallback: dict[str, str]) -> CategoryRationales:
    """Backfill empty CategoryRationales fields from prior step rationales."""
    existing = target.model_dump()
    allowed = set(CategoryRationales.model_fields.keys())
    updates = {k: v for k, v in fallback.items() if k in allowed and not existing.get(k)}
    return target.model_copy(update=updates) if updates else target


def _attach_bundle_artifacts(score_obj: ScoreResult, bundle: WorkflowFactsBundle) -> None:
    """Attach deterministic runtime, security, pentest, AST, and architecture artifacts onto ScoreResult."""
    if bundle.runtime_facts is not None:
        score_obj.runtime_facts = bundle.runtime_facts
    if bundle.security_facts is not None:
        score_obj.security_facts = bundle.security_facts
    if bundle.pentest_facts is not None:
        score_obj.pentest_facts = bundle.pentest_facts
    if bundle.ast_facts is not None:
        score_obj.module_inventory = bundle.ast_facts.module_inventory
        score_obj.dangerous_sinks = bundle.ast_facts.dangerous_sinks
        score_obj.api_endpoints = bundle.ast_facts.api_endpoints
        score_obj.language_version_mismatches = bundle.ast_facts.language_version_mismatches
    if bundle.architecture_record is not None:
        score_obj.architecture_record = bundle.architecture_record
        _enrich_architecture_overview(score_obj, bundle.architecture_record)


def _enrich_score_result(
    score_obj: ScoreResult,
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    all_actions: list[ActionRunRecord],
    db: WorkflowStateDB | None = None,
    project_root: Path | None = None,
) -> ScoreResult:
    """Stamp provenance metadata, pre-sorted audit digest, architecture, and metrics onto ScoreResult."""
    pni_cfg = load_pni_config(project_root) if project_root is not None else PniConfig()
    bundle = _assemble_facts_bundle(run, all_actions, db=db)
    digest = compile_workflow_digest(
        all_actions,
        bundle,
        extra_findings=score_obj.findings,
        extra_actions=score_obj.action_plan,
        extra_strengths=score_obj.strengths,
        opt_outs=pni_cfg.opt_out,
    )
    det_metrics = _build_deterministic_metrics(bundle)
    _attach_bundle_artifacts(score_obj, bundle)
    if not score_obj.architecture_overview.modules and digest.modules:
        score_obj.architecture_overview.modules = digest.modules

    score_obj.grade = score_to_grade(score_obj.overall_score)
    score_obj.workflow_id = run.workflow_id
    score_obj.workflow_run_id = run.run_id
    if not score_obj.evaluated_at:
        score_obj.evaluated_at = datetime.now(timezone.utc).isoformat()
    score_obj.target_root = run.targets.root
    score_obj.facts_file = _resolve_facts_rel_path(run, action)
    score_obj.metrics_snapshot = {**score_obj.metrics_snapshot, **det_metrics}
    score_obj.category_rationales = _merge_category_rationales(
        score_obj.category_rationales,
        digest.category_rationales,
    )
    score_obj.audit_dimensions = digest.audit_dimensions
    score_obj.rule_compliance = digest.rule_compliance
    score_obj.module_hotspots = digest.module_hotspots
    score_obj.findings = digest.findings
    score_obj.consolidated_findings = digest.consolidated_findings
    score_obj.action_plan = digest.action_plan
    score_obj.strengths = digest.strengths
    score_obj.opt_outs = digest.opt_outs
    return score_obj


def _is_grounded_repo_path(
    raw_ref: str,
    project_root: Path,
    target_root: Path,
    inventory_paths: set[str],
) -> bool:
    """Return True if raw_ref ('path' or 'path:symbol') resolves to an existing repo path or AST inventory entry."""
    clean = raw_ref.split(":", maxsplit=1)[0].split("#", maxsplit=1)[0].strip().rstrip("/")
    if not clean:
        return False
    if clean in {".", "*"} or clean in inventory_paths:
        return True
    if any(inv == clean or inv.startswith(f"{clean}/") for inv in inventory_paths):
        return True
    resolved_proj = project_root.resolve()
    resolved_tgt = target_root.resolve()
    cand_proj = (project_root / clean).resolve()
    cand_tgt = (target_root / clean).resolve()
    in_proj = cand_proj.is_relative_to(resolved_proj) and cand_proj.exists()
    in_tgt = cand_tgt.is_relative_to(resolved_tgt) and cand_tgt.exists()
    return in_proj or in_tgt


def _verify_grounded_paths(
    paths: list[str],
    field_name: str,
    project_root: Path,
    target_root: Path,
    ast_facts: AstFacts | None,
) -> None:
    """Raise ValueError if any path in paths does not exist in AST module_inventory or repository."""
    inv = {m.file.rstrip("/") for m in ast_facts.module_inventory} if ast_facts is not None else set()
    missing = [p for p in paths if not _is_grounded_repo_path(p, project_root, target_root, inv)]
    if missing:
        msg = (
            f"Unverified/hallucinated path(s) in '{field_name}': {missing}. "
            "Every path must exist in the repository or AstFacts.module_inventory."
        )
        raise ValueError(msg)


def _validate_findings_and_actions_paths(
    findings: list[Finding],
    action_items: list[ActionItem],
    project_root: Path,
    target_root: Path,
    ast_facts: AstFacts | None,
) -> None:
    """Verify all non-empty file_path and target_files references in findings and action items."""
    finding_paths = [f.file_path for f in findings if f.file_path and f.file_path.strip()]
    action_paths = [p for item in action_items for p in item.target_files if p.strip()]
    if finding_paths:
        _verify_grounded_paths(finding_paths, "findings[].file_path", project_root, target_root, ast_facts)
    if action_paths:
        _verify_grounded_paths(action_paths, "action_items[].target_files", project_root, target_root, ast_facts)


def _validate_structure_map(
    smap: StructureMap,
    project_root: Path,
    target_root: Path,
    ast_facts: AstFacts | None,
) -> None:
    """Verify all layer paths and module paths in StructureMap exist in repository or AST inventory."""
    layer_paths = [p for layer in smap.layers for p in layer.paths]
    mod_paths = [m.path for m in smap.modules]
    _verify_grounded_paths(layer_paths, "layers[].paths", project_root, target_root, ast_facts)
    _verify_grounded_paths(mod_paths, "modules[].path", project_root, target_root, ast_facts)


def _validate_flow_map(
    fmap: ExecutionFlowMap,
    project_root: Path,
    target_root: Path,
    ast_facts: AstFacts | None,
) -> None:
    """Verify all entry_points and involved_files in ExecutionFlowMap exist in repository or AST inventory."""
    flow_files = [f for flow in fmap.execution_flows for f in flow.involved_files]
    _verify_grounded_paths(fmap.entry_points, "entry_points", project_root, target_root, ast_facts)
    _verify_grounded_paths(flow_files, "execution_flows[].involved_files", project_root, target_root, ast_facts)


def _validate_and_persist_architecture(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    all_actions: list[ActionRunRecord],
    raw_input: str,
    project_root: Path,
    db: WorkflowStateDB | None = None,
) -> str:
    """Validate an aspect or full ArchitectureRecord, verify path grounding, and persist JSON."""
    bundle = _assemble_facts_bundle(run, all_actions, db=db)
    target_root = (project_root / run.targets.root).resolve()
    aspect = str(action.params.get("aspect", "all")).strip()

    if aspect == "purpose_and_stack":
        validated_json = SystemProfile.model_validate_json(raw_input).model_dump_json(indent=2)
    elif aspect == "layers_and_modules":
        smap = StructureMap.model_validate_json(raw_input)
        _validate_structure_map(smap, project_root, target_root, bundle.ast_facts)
        validated_json = smap.model_dump_json(indent=2)
    elif aspect == "flows_and_state":
        fmap = ExecutionFlowMap.model_validate_json(raw_input)
        _validate_flow_map(fmap, project_root, target_root, bundle.ast_facts)
        validated_json = fmap.model_dump_json(indent=2)
    else:
        full = ArchitectureRecord.model_validate_json(raw_input)
        if full.structure_map is not None:
            _validate_structure_map(full.structure_map, project_root, target_root, bundle.ast_facts)
        if full.execution_flow_map is not None:
            _validate_flow_map(full.execution_flow_map, project_root, target_root, bundle.ast_facts)
        validated_json = full.model_dump_json(indent=2)

    preview_action = action.model_copy(
        update={
            "agent_input_json": validated_json,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    updated_actions = [preview_action if a.action_id == action.action_id else a for a in all_actions]
    merged_bundle = _assemble_facts_bundle(run, updated_actions, db=db)
    if merged_bundle.architecture_record is not None:
        arch_file = project_root / _resolve_arch_rel_path(run, action)
        ensure_cache_parent(project_root, arch_file)
        arch_file.write_text(merged_bundle.architecture_record.model_dump_json(indent=2) + "\n", encoding="utf-8")
        facts_file = project_root / _resolve_facts_rel_path(run, action)
        ensure_cache_parent(project_root, facts_file)
        facts_file.write_text(merged_bundle.model_dump_json(indent=2), encoding="utf-8")

    return validated_json


def _validate_report_completion(raw_input: str, project_root: Path) -> str:
    """Validate ReportCompletionInput and verify generated report deliverables exist and are non-empty."""
    rep_obj = ReportCompletionInput.model_validate_json(raw_input)
    resolved_root = project_root.resolve()
    for rel_file in rep_obj.generated_files:
        candidate = (project_root / rel_file).resolve()
        if not candidate.is_relative_to(resolved_root) or not candidate.is_file() or candidate.stat().st_size == 0:
            msg = f"Generated report file '{rel_file}' does not exist or is empty."
            raise ValueError(msg)
    return rep_obj.model_dump_json(indent=2)


def _persist_emitted_score(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    all_actions: list[ActionRunRecord],
    bundle: WorkflowFactsBundle,
    raw_input: str,
    project_root: Path,
    target_root: Path,
    db: WorkflowStateDB | None,
) -> str:
    """Validate, enrich, persist `ScoreResult`, and append/upsert `.pni/history/audit/<id>.jsonl`."""
    score_obj = ScoreResult.model_validate_json(raw_input)
    _validate_findings_and_actions_paths(
        score_obj.findings,
        score_obj.action_plan,
        project_root,
        target_root,
        bundle.ast_facts,
    )
    score_obj = _enrich_score_result(score_obj, run, action, all_actions, db=db, project_root=project_root)
    canonical = score_obj.model_dump_json(indent=2)
    score_file = project_root / _resolve_score_rel_path(run, action)
    score_file.parent.mkdir(parents=True, exist_ok=True)
    score_file.write_text(canonical + "\n", encoding="utf-8")
    record_audit_history_from_score(project_root, run.workflow_id, score_obj)
    return canonical


def _persist_emitted_output(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    all_actions: list[ActionRunRecord],
    bundle: WorkflowFactsBundle,
    raw_input: str,
    project_root: Path,
    target_root: Path,
    db: WorkflowStateDB | None,
) -> str:
    """Dispatch `emit_score`, `emit_migration_plan`, or `emit_progress` persistence."""
    if action.primitive_type == PrimitiveType.EMIT_SCORE:
        return _persist_emitted_score(run, action, all_actions, bundle, raw_input, project_root, target_root, db)
    if action.primitive_type == PrimitiveType.EMIT_MIGRATION_PLAN:
        return validate_and_persist_migration_plan(
            run, action, bundle, raw_input, project_root, _verify_grounded_paths
        )
    return validate_and_persist_progress_result(run, action, bundle, raw_input, project_root)


def _validate_and_apply_push_payload(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    all_actions: list[ActionRunRecord],
    raw_input: str,
    project_root: Path,
    db: WorkflowStateDB | None = None,
) -> str:
    """Validate raw_input against the action's Pydantic schema and execute deterministic side effects."""
    ptype = action.primitive_type
    if ptype == PrimitiveType.RECORD_ARCHITECTURE:
        return _validate_and_persist_architecture(run, action, all_actions, raw_input, project_root, db=db)
    if ptype == PrimitiveType.WRITE_DRAWLIB_REPORT:
        return _validate_report_completion(raw_input, project_root)

    bundle = _assemble_facts_bundle(run, all_actions, db=db)
    target_root = (project_root / run.targets.root).resolve()

    if ptype == PrimitiveType.AI_INTERPRET:
        parsed = InterpretationInput.model_validate_json(raw_input)
        _validate_findings_and_actions_paths(
            parsed.findings,
            parsed.action_items,
            project_root,
            target_root,
            bundle.ast_facts,
        )
        pni_cfg = load_pni_config(project_root)
        parsed.rule_checks = normalize_step_rule_checks(action, parsed, pni_cfg.opt_out)
        return parsed.model_dump_json(indent=2)

    if ptype in {PrimitiveType.EMIT_SCORE, PrimitiveType.EMIT_MIGRATION_PLAN, PrimitiveType.EMIT_PROGRESS}:
        return _persist_emitted_output(run, action, all_actions, bundle, raw_input, project_root, target_root, db)

    payload = raw_input.strip() or '{"acknowledged": true}'
    return DeterministicAckInput.model_validate_json(payload).model_dump_json(indent=2)


def push_workflow_action(
    run_id: str,
    action_id: str,
    raw_input: str,
    project_root: Path,
) -> tuple[bool, str]:
    """Validate and record the agent's input for the active action and advance the state machine.

    Args:
        run_id: Workflow run identifier.
        action_id: Expected current action identifier (e.g. 'act-01').
        raw_input: JSON string submitted by the agent.
        project_root: Workspace root directory.

    Returns:
        tuple[bool, str]: (success flag, status or error message).
    """
    db = WorkflowStateDB(project_root)
    run = db.get_run(run_id)
    if run is None:
        return False, f"Workflow run '{run_id}' not found."
    if run.status == RunStatus.CANCELLED:
        return False, f"Workflow run '{run_id}' was cancelled and cannot accept actions."

    current = db.get_current_action(run_id)
    if current is None:
        return False, f"Workflow run '{run_id}' is already completed."

    if current.action_id != action_id:
        return (
            False,
            f"Action mismatch: expected active action '{current.action_id}', but received '{action_id}'. "
            f"Run 'pni workflows get-action {run_id}' first.",
        )

    if current.primitive_type in (
        PrimitiveType.PROJECT_INSPECT,
        PrimitiveType.AST_ANALYZE,
        PrimitiveType.RUN_CHECK,
        PrimitiveType.SECURITY_SCAN,
        PrimitiveType.WEB_PENTEST,
        PrimitiveType.MIGRATION_ANALYZE,
        PrimitiveType.PROGRESS_ANALYZE,
    ):
        current = _execute_deterministic_step_if_needed(db, run, current, project_root)

    all_actions = db.get_actions(run_id)
    try:
        canonical_json = _validate_and_apply_push_payload(run, current, all_actions, raw_input, project_root, db=db)
    except Exception as exc:
        return False, f"Validation failed for action '{action_id}' ({current.primitive_type.value}):\n{exc}"

    db.complete_action(run_id, action_id, canonical_json)
    next_act = db.get_current_action(run_id)
    if next_act is None:
        db.complete_workflow_run(run_id)
        done_msg = (
            f"✓ Action '{action_id}' completed.\n"
            f"★ All actions finished! Workflow '{run_id}' ({run.workflow_id}) is COMPLETED."
        )
    else:
        done_msg = (
            f"✓ Action '{action_id}' ({current.primitive_type.value}) completed.\n"
            f"Next action: '{next_act.action_id}' ({next_act.primitive_type.value} - {next_act.name}).\n"
            f"Run: pni workflows get-action {run_id}"
        )
    return True, done_msg

