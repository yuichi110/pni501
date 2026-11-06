# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Stateless ad-hoc single-action workflow runner (`pni workflows run-action`)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from pni._actions import (
    AstFacts,
    ParamValue,
    PentestFacts,
    PentestOptions,
    PrimitiveStep,
    PrimitiveType,
    ProjectFacts,
    RuntimeFacts,
    SecurityFacts,
    get_expected_input_schema_json,
    render_action_task_body,
    run_ast_analyze,
    run_migration_analyze,
    run_progress_analyze,
    run_project_inspect,
    run_runtime_check,
    run_security_scan,
    run_web_pentest,
)
from pni._workflows._migration_engine import parse_migration_options
from pni._workflows._progress_engine import parse_progress_options
from pni._workflows.base_model import WorkflowDefinition, WorkflowFactsBundle
from pni._workflows.engine import (
    _parse_pentest_options,
    _parse_runtime_check_options,
    _parse_security_scan_options,
    _render_active_rules,
    _render_bundle_facts,
)
from pni._workflows.manager import load_workflow, normalize_workflow_steps, resolve_workflow_outputs

_DETERMINISTIC_PRIMITIVES: frozenset[PrimitiveType] = frozenset(
    {
        PrimitiveType.PROJECT_INSPECT,
        PrimitiveType.AST_ANALYZE,
        PrimitiveType.RUN_CHECK,
        PrimitiveType.SECURITY_SCAN,
        PrimitiveType.WEB_PENTEST,
        PrimitiveType.MIGRATION_ANALYZE,
        PrimitiveType.PROGRESS_ANALYZE,
    }
)


class AdhocActionOutcome(BaseModel):
    """Structured result of executing one workflow step or action without SQLite run state."""

    workflow_id: str
    selector: str
    matched_step_ids: list[str] = Field(default_factory=list)
    executed_primitives: list[str] = Field(default_factory=list)
    has_error: bool = False
    has_findings: bool = False
    error_message: str = ""
    bundle: WorkflowFactsBundle
    rendered_markdown: str = ""


def _parse_step_index_selector(selector: str, total: int) -> int | None:
    """Parse 'act-07' or '7' into a validated 0-based index when in bounds."""
    raw = selector.removeprefix("act-") if selector.startswith("act-") else selector
    if not raw.isdigit():
        return None
    idx = int(raw)
    return idx - 1 if 1 <= idx <= total else None


def _available_selectors_hint(primitives: list[PrimitiveStep]) -> str:
    """Build a concise diagnostic string listing valid selectors in the workflow."""
    step_ids = list(dict.fromkeys(p.id.split("__", maxsplit=1)[0] for p in primitives))
    uses_ids = list(
        dict.fromkeys(p.source_action.split("/", maxsplit=1)[-1] for p in primitives if p.source_action)
    )
    prim_types = list(dict.fromkeys(p.type.value for p in primitives))
    return (
        f"Available step IDs: {step_ids}; "
        f"composite actions (`uses`): {uses_ids}; "
        f"primitive types: {prim_types}"
    )


def select_workflow_primitives(primitives: list[PrimitiveStep], selector: str) -> list[PrimitiveStep]:
    """Select one or more expanded PrimitiveStep entries matching a step ID, `uses` name, or primitive type.

    Args:
        primitives: Normalized workflow primitives from `normalize_workflow_steps`.
        selector: User-supplied step ID, composite action name, primitive type, or `act-XX` index.

    Returns:
        list[PrimitiveStep]: Ordered non-empty list of matching primitive steps.

    Raises:
        ValueError: If `selector` does not match any step or primitive in the workflow.
    """
    q = selector.strip()
    if not q:
        msg = f"Empty action selector. {_available_selectors_hint(primitives)}"
        raise ValueError(msg)

    idx = _parse_step_index_selector(q, len(primitives))
    if idx is not None:
        return [primitives[idx]]

    exact_id = [p for p in primitives if p.id == q]
    if exact_id:
        return exact_id

    by_step_id = [p for p in primitives if p.id.split("__", maxsplit=1)[0] == q]
    if by_step_id:
        return by_step_id

    by_source = [
        p
        for p in primitives
        if p.source_action and (p.source_action == q or p.source_action.split("/", maxsplit=1)[-1] == q)
    ]
    if by_source:
        return by_source

    by_type = [p for p in primitives if p.type.value == q]
    if by_type:
        return by_type

    msg = f"No action matching '{q}' found in workflow. {_available_selectors_hint(primitives)}"
    raise ValueError(msg)


def _ensure_project_facts(
    bundle: WorkflowFactsBundle,
    wf_def: WorkflowDefinition,
    project_root: Path,
    step_lang: str | None,
) -> ProjectFacts:
    """Lazily compute ProjectFacts in memory when required by a downstream primitive."""
    if bundle.project_facts is None:
        t_dir = (project_root / wf_def.targets.root).resolve()
        bundle.project_facts = run_project_inspect(
            t_dir,
            source_dirs=wf_def.targets.source,
            test_dirs=wf_def.targets.tests,
            doc_files=wf_def.targets.docs,
            lang=step_lang,
            exclude_globs=wf_def.targets.exclude,
        )
    return bundle.project_facts


def _ensure_ast_facts(
    bundle: WorkflowFactsBundle,
    wf_def: WorkflowDefinition,
    project_root: Path,
    params: dict[str, ParamValue],
    step_lang: str | None,
) -> AstFacts:
    """Lazily compute AstFacts in memory when required by a downstream primitive."""
    if bundle.ast_facts is None:
        pf = _ensure_project_facts(bundle, wf_def, project_root, step_lang)
        t_dir = (project_root / wf_def.targets.root).resolve()
        raw_targets = params.get("targets") or params.get("source_targets")
        targets = raw_targets if isinstance(raw_targets, list) else wf_def.targets.source
        raw_tests = params.get("test_targets")
        test_targets = raw_tests if isinstance(raw_tests, list) else wf_def.targets.tests
        raw_ex = params.get("exclude_globs") or params.get("exclude_targets")
        exclude_globs = raw_ex if isinstance(raw_ex, list) else wf_def.targets.exclude
        bundle.ast_facts = run_ast_analyze(
            t_dir,
            targets=targets,
            display_root=project_root.resolve(),
            lang=step_lang or pf.language,
            test_targets=test_targets,
            exclude_globs=exclude_globs,
            detected_frameworks=pf.detected_frameworks,
            declared_lang_version=pf.language_version_constraint,
        )
    return bundle.ast_facts


def _run_web_pentest_adhoc(
    prim: PrimitiveStep,
    wf_def: WorkflowDefinition,
    project_root: Path,
    bundle: WorkflowFactsBundle,
    step_lang: str | None,
    *,
    base_url: str,
    force_pentests: bool,
) -> PentestFacts:
    """Execute ad-hoc web_pentest primitive with optional CLI overrides."""
    pf = _ensure_project_facts(bundle, wf_def, project_root, step_lang)
    af = _ensure_ast_facts(bundle, wf_def, project_root, prim.params, step_lang)
    opts: PentestOptions = _parse_pentest_options(prim.params)
    updates: dict[str, str | bool] = {}
    if base_url.strip():
        updates["base_url"] = base_url.strip()
    if force_pentests:
        updates["force_regenerate_pentests"] = True
    if updates:
        opts = opts.model_copy(update=updates)
    return run_web_pentest(
        project_root,
        wf_def.id,
        target_root=wf_def.targets.root,
        source_targets=wf_def.targets.source,
        test_targets=wf_def.targets.tests,
        lang=step_lang,
        project_facts=pf,
        ast_facts=af,
        options=opts,
    )


def _execute_single_adhoc_primitive(
    prim: PrimitiveStep,
    wf_def: WorkflowDefinition,
    project_root: Path,
    bundle: WorkflowFactsBundle,
    *,
    base_url: str,
    force_pentests: bool,
) -> None:
    """Execute one deterministic primitive directly in memory and populate `bundle`."""
    raw_lang = prim.params.get("lang")
    step_lang = raw_lang if isinstance(raw_lang, str) else None
    t_dir = (project_root / wf_def.targets.root).resolve()

    if prim.type == PrimitiveType.PROJECT_INSPECT:
        bundle.project_facts = run_project_inspect(
            t_dir,
            source_dirs=wf_def.targets.source,
            test_dirs=wf_def.targets.tests,
            doc_files=wf_def.targets.docs,
            lang=step_lang,
            exclude_globs=wf_def.targets.exclude,
        )
    elif prim.type == PrimitiveType.AST_ANALYZE:
        bundle.ast_facts = None
        _ensure_ast_facts(bundle, wf_def, project_root, prim.params, step_lang)
    elif prim.type == PrimitiveType.RUN_CHECK:
        pf = _ensure_project_facts(bundle, wf_def, project_root, step_lang)
        bundle.runtime_facts = run_runtime_check(
            project_root,
            wf_def.id,
            target_root=wf_def.targets.root,
            source_targets=wf_def.targets.source,
            test_targets=wf_def.targets.tests,
            lang=step_lang,
            project_facts=pf,
            options=_parse_runtime_check_options(prim.params),
        )
    elif prim.type == PrimitiveType.SECURITY_SCAN:
        pf = _ensure_project_facts(bundle, wf_def, project_root, step_lang)
        bundle.security_facts = run_security_scan(
            project_root,
            wf_def.id,
            target_root=wf_def.targets.root,
            source_targets=wf_def.targets.source,
            test_targets=wf_def.targets.tests,
            lang=step_lang,
            project_facts=pf,
            options=_parse_security_scan_options(prim.params),
        )
    elif prim.type == PrimitiveType.WEB_PENTEST:
        bundle.pentest_facts = _run_web_pentest_adhoc(
            prim,
            wf_def,
            project_root,
            bundle,
            step_lang,
            base_url=base_url,
            force_pentests=force_pentests,
        )
    elif prim.type == PrimitiveType.MIGRATION_ANALYZE:
        pf = _ensure_project_facts(bundle, wf_def, project_root, step_lang)
        af = _ensure_ast_facts(bundle, wf_def, project_root, prim.params, step_lang)
        bundle.migration_facts = run_migration_analyze(
            project_root,
            wf_def.id,
            target_root=wf_def.targets.root,
            source_targets=wf_def.targets.source,
            test_targets=wf_def.targets.tests,
            doc_targets=wf_def.targets.docs,
            exclude_globs=wf_def.targets.exclude,
            lang=step_lang,
            project_facts=pf,
            ast_facts=af,
            runtime_facts=bundle.runtime_facts,
            options=parse_migration_options(prim.params),
        )
    elif prim.type == PrimitiveType.PROGRESS_ANALYZE:
        p_opts = parse_progress_options(prim.params)
        if not p_opts.base_audit_workflow and wf_def.based_on:
            p_opts = p_opts.model_copy(update={"base_audit_workflow": wf_def.based_on})
        bundle.progress_facts = run_progress_analyze(
            project_root,
            wf_def.id,
            target_root=wf_def.targets.root,
            source_targets=wf_def.targets.source,
            test_targets=wf_def.targets.tests,
            doc_targets=wf_def.targets.docs,
            options=p_opts,
        )


def _has_progress_findings(bundle: WorkflowFactsBundle, executed_types: set[PrimitiveType]) -> bool:
    """Return True if executed progress_analyze facts report policy violations or conflicts."""
    if PrimitiveType.PROGRESS_ANALYZE not in executed_types or bundle.progress_facts is None:
        return False
    prgf = bundle.progress_facts
    return bool(prgf.policy_violations or any(b.has_conflict for b in prgf.branches))


def _evaluate_bundle_health(
    bundle: WorkflowFactsBundle,
    executed_types: set[PrimitiveType],
) -> tuple[bool, bool, str]:
    """Classify `(has_error, has_findings, error_message)` across executed deterministic steps."""
    errors: list[str] = []
    has_findings = _has_progress_findings(bundle, executed_types)

    rf: RuntimeFacts | None = bundle.runtime_facts if PrimitiveType.RUN_CHECK in executed_types else None
    if rf is not None:
        if rf.status == "error":
            errors.append(rf.skip_reason or "Container runtime verification failed with status='error'.")
        elif rf.status == "failed":
            has_findings = True

    sf: SecurityFacts | None = bundle.security_facts if PrimitiveType.SECURITY_SCAN in executed_types else None
    if sf is not None:
        if sf.status == "error":
            errors.append(sf.skip_reason or "Container security scan failed with status='error'.")
        elif sf.vulnerabilities or sf.misconfigurations or sf.secrets:
            has_findings = True

    pf: PentestFacts | None = bundle.pentest_facts if PrimitiveType.WEB_PENTEST in executed_types else None
    if pf is not None:
        if pf.status in {"error", "timeout"}:
            errors.append(pf.boot_failure_reason or pf.skip_reason or f"Web pentest ended with status='{pf.status}'.")
        elif pf.status == "failed" or pf.findings:
            has_findings = True

    return bool(errors), has_findings, "\n".join(errors)


def _render_adhoc_markdown(
    wf_def: WorkflowDefinition,
    selector: str,
    matched: list[PrimitiveStep],
    display_bundle: WorkflowFactsBundle,
    project_root: Path,
) -> str:
    """Format stateless ad-hoc action output and AI instructions into Markdown."""
    lines: list[str] = [
        f"# PNI Ad-Hoc Workflow Action: `{wf_def.id}` -> `{selector}`",
        "- **Mode**: Stateless Ad-Hoc Execution (no `workflow_state.db` run required)",
        f"- **Target Root**: `{wf_def.targets.root}` (sources={wf_def.targets.source})",
        f"- **Matched Steps ({len(matched)})**: {', '.join(f'`{m.id}` (`{m.type.value}`)' for m in matched)}",
    ]
    lines.extend(_render_bundle_facts(display_bundle))

    seen_rules: list[str] = []
    for prim in matched:
        for rid in prim.rules:
            if rid not in seen_rules:
                seen_rules.append(rid)
        if prim.type not in _DETERMINISTIC_PRIMITIVES:
            effective_params: dict[str, ParamValue] = {"workflow_id": wf_def.id, **prim.params}
            schema_str = get_expected_input_schema_json(prim.type, prim.params)
            lines.extend(
                [
                    f"\n## Paired Step Guidance: `{prim.id}` (`{prim.type.value}`)",
                    render_action_task_body(
                        prim.type,
                        effective_params,
                        prim.prompt,
                        rules=prim.rules,
                        source_action=prim.source_action,
                        project_root=project_root,
                    ),
                    f"\n### Expected Output Schema (`{prim.type.value}`):\n```json\n{schema_str}\n```",
                ]
            )

    lines.extend(_render_active_rules(seen_rules, project_root))
    return "\n".join(lines) + "\n"


def _filter_display_bundle(
    full_bundle: WorkflowFactsBundle,
    executed_types: set[PrimitiveType],
) -> WorkflowFactsBundle:
    """Keep only facts produced by explicitly matched steps (suppressing silent prerequisite helpers)."""
    if not executed_types:
        return full_bundle
    return WorkflowFactsBundle(
        workflow_id=full_bundle.workflow_id,
        targets=full_bundle.targets,
        outputs=full_bundle.outputs,
        project_facts=full_bundle.project_facts if PrimitiveType.PROJECT_INSPECT in executed_types else None,
        ast_facts=full_bundle.ast_facts if PrimitiveType.AST_ANALYZE in executed_types else None,
        runtime_facts=full_bundle.runtime_facts if PrimitiveType.RUN_CHECK in executed_types else None,
        security_facts=full_bundle.security_facts if PrimitiveType.SECURITY_SCAN in executed_types else None,
        pentest_facts=full_bundle.pentest_facts if PrimitiveType.WEB_PENTEST in executed_types else None,
        migration_facts=full_bundle.migration_facts if PrimitiveType.MIGRATION_ANALYZE in executed_types else None,
        progress_facts=full_bundle.progress_facts if PrimitiveType.PROGRESS_ANALYZE in executed_types else None,
    )


def run_workflow_action_adhoc(
    workflow_id: str,
    selector: str,
    project_root: Path,
    *,
    base_url: str = "",
    force_pentests: bool = False,
) -> AdhocActionOutcome | None:
    """Execute a specific step or action inside a workflow YAML directly without prior preparation.

    Does not create or require a run in `.pni/cache/workflow_state.db` and bypasses workflow-wide
    `based_on` / prerequisite gates unless the invoked action itself requires them.

    Args:
        workflow_id: Workflow identifier under `.pni/workflows/`.
        selector: Step ID (e.g. `web_pentest`), composite `uses` ID (`web_penetration_audit`),
            primitive type (`run_check`, `ast_analyze`), or `act-XX` index.
        project_root: Workspace root directory.
        base_url: Optional live loopback URL override for `web_pentest`.
        force_pentests: Optional flag to regenerate `.pni/pentests/<target>/` before `web_pentest`.

    Returns:
        AdhocActionOutcome | None: Execution outcome, or None if `workflow_id` does not exist.
    """
    loaded = load_workflow(workflow_id, project_root)
    if loaded is None:
        return None

    _, wf_def = loaded
    primitives = normalize_workflow_steps(wf_def, project_root)
    matched = select_workflow_primitives(primitives, selector)

    bundle = WorkflowFactsBundle(
        workflow_id=wf_def.id,
        targets=wf_def.targets,
        outputs=resolve_workflow_outputs(wf_def, primitives),
    )
    executed_types: set[PrimitiveType] = set()
    executed_names: list[str] = []
    for prim in matched:
        if prim.type in _DETERMINISTIC_PRIMITIVES:
            _execute_single_adhoc_primitive(
                prim,
                wf_def,
                project_root,
                bundle,
                base_url=base_url,
                force_pentests=force_pentests,
            )
            executed_types.add(prim.type)
            executed_names.append(f"{prim.id} ({prim.type.value})")

    has_error, has_findings, err_msg = _evaluate_bundle_health(bundle, executed_types)
    display_bundle = _filter_display_bundle(bundle, executed_types)
    rendered = _render_adhoc_markdown(wf_def, selector, matched, display_bundle, project_root)
    return AdhocActionOutcome(
        workflow_id=wf_def.id,
        selector=selector,
        matched_step_ids=[m.id for m in matched],
        executed_primitives=executed_names,
        has_error=has_error,
        has_findings=has_findings,
        error_message=err_msg,
        bundle=display_bundle,
        rendered_markdown=rendered,
    )
