# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Migration action execution, Markdown rendering, and MigrationPlanResult persistence helpers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from pni._actions import (
    AstFacts,
    MigrationFacts,
    MigrationOptions,
    MigrationPlanResult,
    ParamValue,
    resolve_migration_plan_rel_path,
    run_migration_analyze,
)
from pni._cache import default_migration_facts_rel_path
from pni._reporter import DEFAULT_REPORT_OUTPUT_DIR
from pni._workflows.base_model import (
    ActionRunRecord,
    WorkflowFactsBundle,
    WorkflowRunRecord,
)


def parse_migration_options(params: dict[str, ParamValue]) -> MigrationOptions:
    """Construct validated MigrationOptions from workflow action parameters."""
    known = set(MigrationOptions.model_fields.keys())
    filtered = {k: v for k, v in params.items() if k in known}
    return MigrationOptions.model_validate(filtered)


def execute_migration_analyze_json(
    prior_bundle: WorkflowFactsBundle,
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    workspace_root: Path,
    step_lang: str | None,
) -> str:
    """Execute deterministic migration_analyze and return serialized MigrationFacts JSON."""
    mf = run_migration_analyze(
        workspace_root,
        run.workflow_id,
        target_root=run.targets.root,
        source_targets=run.targets.source,
        test_targets=run.targets.tests,
        doc_targets=run.targets.docs,
        exclude_globs=run.targets.exclude,
        lang=step_lang,
        project_facts=prior_bundle.project_facts,
        ast_facts=prior_bundle.ast_facts,
        runtime_facts=prior_bundle.runtime_facts,
        options=parse_migration_options(action.params),
    )
    return mf.model_dump_json(indent=2)


def _render_waves_and_touchpoints(mf: MigrationFacts) -> list[str]:
    """Render refactoring waves, cycle cuts, and boundary touchpoints into Markdown."""
    lines: list[str] = []
    if mf.refactoring_waves:
        lines.append(f"- **Topological Refactoring Waves ({len(mf.refactoring_waves)})**:")
        for w in mf.refactoring_waves:
            lines.append(f"  - **{w.label}**: {w.modules} — {w.rationale}")
    if mf.cycle_cuts:
        lines.append(f"- **Cycle-Cut Suggestions ({len(mf.cycle_cuts)})**:")
        for cut in mf.cycle_cuts:
            lines.append(f"  - `{cut.recommended_cut_from} -> {cut.recommended_cut_to}`: {cut.rationale}")
    if mf.boundary_touchpoints:
        lines.append(f"- **Boundary Touchpoints (State / DB / HTTP, {len(mf.boundary_touchpoints)})**:")
        for tp in mf.boundary_touchpoints[:15]:
            lines.append(
                f"  - `[{tp.kind}]` `{tp.file}:{tp.line}` (`{tp.symbol}`): "
                f"{tp.current_coupling} -> {tp.recommended_port_hint}"
            )
    return lines


def _render_contracts_codemods_and_decisions(mf: MigrationFacts) -> list[str]:
    """Render implicit I/O contracts, env contracts, codemods, blockers, and spec-vs-bug items."""
    lines: list[str] = []
    if mf.implicit_contracts:
        lines.append(f"- **Implicit Endpoint / Script Contracts ({len(mf.implicit_contracts)})**:")
        for ic in mf.implicit_contracts[:10]:
            ins = [f"{f.key}:{f.inferred_type}(def={f.default_value})" for f in ic.input_fields]
            outs = [f"{f.key}:{f.inferred_type}" for f in ic.output_fields]
            lines.append(f"  - `{ic.http_method} {ic.endpoint_or_file}`: inputs={ins}, outputs={outs}")
    if mf.env_contracts:
        envs = [f"{e.name}(def={e.default_value}, {e.file}:{e.line})" for e in mf.env_contracts[:12]]
        lines.append(f"- **Environment & Config Contracts ({len(mf.env_contracts)})**: {envs}")
    if mf.manual_blockers:
        lines.append(f"- **Structural / Build Blockers ({len(mf.manual_blockers)})**:")
        for blk in mf.manual_blockers:
            lines.append(f"  - `[{blk.severity.upper()}]` `{blk.blocker_id}`: {blk.description}")
    if mf.mechanical_codemods:
        cms = [f"{c.tool}:{c.recipe_id}" for c in mf.mechanical_codemods]
        lines.append(f"- **Matched Codemod Recipes ({len(mf.mechanical_codemods)})**: {cms}")
    if mf.spec_vs_bug_candidates:
        lines.append(f"- **Spec vs. Bug Candidates ({len(mf.spec_vs_bug_candidates)})**:")
        for cand in mf.spec_vs_bug_candidates[:12]:
            lines.append(f"  - `{cand.candidate_id}` (`{cand.file}:{cand.line}`): {cand.observed_behavior}")
    return lines


def render_migration_facts(mf: MigrationFacts) -> list[str]:
    """Render deterministic MigrationFacts into concise Markdown instructions for AI steps."""
    lines = [
        f"\n### Deterministic Migration Intelligence (`migration_analyze`, lang=`{mf.source_language}`)",
        (
            f"- **Transformation Mode**: `{mf.transformation_mode}` | "
            f"**Resolved Strategy**: `{mf.resolved_strategy}` | "
            f"**API Compatibility**: `{mf.effective_options.api_compatibility}` | "
            f"**Bug Policy**: `{mf.effective_options.bug_handling_policy}`"
        ),
    ]
    if mf.resolved_brief:
        lines.append(f"- **Confirmed Multi-Line Migration Brief**:\n```markdown\n{mf.resolved_brief}\n```")
    if mf.preflight_hints:
        lines.append(f"- **Preflight Readiness Hints ({len(mf.preflight_hints)})**:")
        for h in mf.preflight_hints:
            lines.append(f"  - `[{h.code}]` {h.message}")
    lines.extend(_render_waves_and_touchpoints(mf))
    lines.extend(_render_contracts_codemods_and_decisions(mf))
    return lines


def _verify_safe_relative_paths(paths: list[str], field_name: str) -> None:
    """Ensure PR WBS paths are workspace-relative without absolute prefixes or '..' traversal."""
    invalid = [
        p
        for p in paths
        if p.strip().startswith("/") or ".." in [seg for seg in p.replace("\\", "/").split("/") if seg]
    ]
    if invalid:
        msg = f"Invalid non-relative path(s) in '{field_name}': {invalid}."
        raise ValueError(msg)


def validate_and_persist_migration_plan(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    bundle: WorkflowFactsBundle,
    raw_input: str,
    project_root: Path,
    verify_grounded_fn: Callable[[list[str], str, Path, Path, AstFacts | None], None],
) -> str:
    """Validate MigrationPlanResult, verify As-Is path grounding, attach MigrationFacts, and write JSON."""
    plan_obj = MigrationPlanResult.model_validate_json(raw_input)
    target_root = (project_root / run.targets.root).resolve()

    axis_files = [f for ax in plan_obj.target_axes for f in ax.affected_files if f.strip()]
    mapping_files = [m.source_file for m in plan_obj.target_architecture.component_mappings if m.source_file.strip()]
    dec_files = [d.file_path for d in plan_obj.decision_log if d.file_path.strip()]
    pr_files = [f for pr in plan_obj.pr_wbs for f in pr.target_files if f.strip()]

    if axis_files:
        verify_grounded_fn(axis_files, "target_axes[].affected_files", project_root, target_root, bundle.ast_facts)
    if mapping_files:
        verify_grounded_fn(
            mapping_files,
            "target_architecture.component_mappings[].source_file",
            project_root,
            target_root,
            bundle.ast_facts,
        )
    if dec_files:
        verify_grounded_fn(dec_files, "decision_log[].file_path", project_root, target_root, bundle.ast_facts)
    if pr_files:
        _verify_safe_relative_paths(pr_files, "pr_wbs[].target_files")

    plan_obj.workflow_id = run.workflow_id
    plan_obj.workflow_run_id = run.run_id
    if not plan_obj.generated_at:
        plan_obj.generated_at = datetime.now(timezone.utc).isoformat()
    plan_obj.target_root = run.targets.root
    plan_obj.migration_facts_file = default_migration_facts_rel_path(run.workflow_id)
    if bundle.migration_facts is not None:
        plan_obj.migration_facts = bundle.migration_facts

    out_dir = str(action.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
    tgt = str(action.params.get("target") or run.workflow_id)
    plan_rel = resolve_migration_plan_rel_path(out_dir, tgt, str(action.params.get("plan_path", "")))
    plan_file = project_root / plan_rel
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    canonical = plan_obj.model_dump_json(indent=2)
    plan_file.write_text(canonical + "\n", encoding="utf-8")
    return canonical
