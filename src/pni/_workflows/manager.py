# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Workflow loading (.pni/workflows/), template copying, and step normalization."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import yaml

from pni._actions import (
    ParamValue,
    PrimitiveStep,
    PrimitiveType,
    expand_composite_action,
    resolve_migration_plan_rel_path,
    resolve_progress_result_rel_path,
)
from pni._cache import default_facts_rel_path
from pni._config import PniConfig, load_pni_config
from pni._reporter import DEFAULT_REPORT_OUTPUT_DIR, DEFAULT_REPORT_SRC_DIR
from pni._rules import detect_active_language
from pni._workflows.base_model import (
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowInfo,
    WorkflowOutputs,
    WorkflowPrerequisiteError,
    WorkflowTargets,
)

BUILTIN_WORKFLOWS_DIR = Path(__file__).resolve().parent


def _load_raw_workflow_dict(file_path: Path) -> dict[str, object] | None:
    """Read a workflow YAML file into a raw dictionary."""
    if not file_path.exists():
        return None
    raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    return raw


def _merge_inherited_targets(
    raw_child: dict[str, object],
    parent_targets: WorkflowTargets,
) -> WorkflowTargets:
    """Inherit omitted target fields from the parent audit workflow while keeping explicit overrides."""
    raw_targets = raw_child.get("targets")
    if not isinstance(raw_targets, dict):
        return parent_targets.model_copy(deep=True)
    merged = {**parent_targets.model_dump(), **raw_targets}
    return WorkflowTargets.model_validate(merged)


def _merge_pni_toml_targets(raw: dict[str, object], pni_cfg: PniConfig) -> WorkflowTargets:
    """Merge .pni/pni.toml [targets] defaults underneath explicit workflow YAML targets."""
    toml_targets = pni_cfg.targets.model_dump(exclude_none=True)
    raw_targets = raw.get("targets")
    explicit_targets = raw_targets if isinstance(raw_targets, dict) else {}
    merged = {**toml_targets, **explicit_targets}
    return WorkflowTargets.model_validate(merged)


def _load_resolved_workflow(
    file_path: Path,
    project_root: Path,
    seen: Optional[set[str]] = None,
) -> WorkflowDefinition | None:
    """Parse, validate, and resolve 'based_on' target inheritance for a workflow YAML file."""
    raw = _load_raw_workflow_dict(file_path)
    if raw is None:
        return None
    parsed = WorkflowDefinition.model_validate(raw)
    pni_cfg = load_pni_config(project_root)
    if not parsed.based_on:
        parsed.targets = _merge_pni_toml_targets(raw, pni_cfg)
        return parsed

    visited = set(seen or set())
    if parsed.id in visited:
        msg = f"Circular workflow 'based_on' reference detected involving '{parsed.id}'."
        raise WorkflowPrerequisiteError(msg)
    visited.add(parsed.id)

    parent_file = project_root / ".pni" / "workflows" / f"{parsed.based_on}.yaml"
    if not parent_file.exists():
        msg = (
            f"Workflow '{parsed.id}' references unknown base audit workflow '{parsed.based_on}' "
            f"('.pni/workflows/{parsed.based_on}.yaml' not found)."
        )
        raise WorkflowPrerequisiteError(msg)

    parent = _load_resolved_workflow(parent_file, project_root, visited)
    if parent is None:
        msg = f"Base audit workflow '{parsed.based_on}' in '{parent_file}' could not be parsed."
        raise WorkflowPrerequisiteError(msg)

    if parent.category != WorkflowCategory.AUDIT:
        msg = (
            f"Workflow '{parsed.id}' 'based_on' must reference an 'audit' workflow, "
            f"but '{parent.id}' has category='{parent.category.value}'."
        )
        raise WorkflowPrerequisiteError(msg)

    parsed.targets = _merge_inherited_targets(raw, parent.targets)
    return parsed


def _interpolate_params(params: dict[str, ParamValue], workflow_id: str) -> dict[str, ParamValue]:
    """Interpolate {workflow_id}, {target}, {output_dir}, and {src_dir} placeholders in string params."""
    raw_target = str(params.get("target") or workflow_id).replace("{workflow_id}", workflow_id)
    raw_out_dir = str(params.get("output_dir") or DEFAULT_REPORT_OUTPUT_DIR).replace("{workflow_id}", workflow_id)
    raw_src_dir = str(params.get("src_dir") or DEFAULT_REPORT_SRC_DIR).replace("{workflow_id}", workflow_id)

    tokens = {
        "{workflow_id}": workflow_id,
        "{target}": raw_target,
        "{output_dir}": raw_out_dir.rstrip("/"),
        "{src_dir}": raw_src_dir.rstrip("/"),
    }
    resolved: dict[str, ParamValue] = {}
    for key, val in params.items():
        if isinstance(val, str):
            text = val
            for token, replacement in tokens.items():
                text = text.replace(token, replacement)
            resolved[key] = text
        else:
            resolved[key] = val
    return resolved


def _build_legacy_output_overrides(outputs: WorkflowOutputs) -> dict[str, ParamValue]:
    """Extract explicit workflow-level outputs overrides when specified in YAML."""
    overrides: dict[str, ParamValue] = {}
    if outputs.facts is not None:
        overrides["facts_path"] = outputs.facts
    if outputs.score is not None:
        overrides["score_path"] = outputs.score
    if outputs.report is not None:
        overrides["output_dir"] = outputs.report
    return overrides


def _build_pni_toml_report_overrides(
    pni_cfg: PniConfig,
) -> tuple[dict[str, ParamValue], dict[str, ParamValue]]:
    """Build (path_overrides, drawlib_report_overrides) from .pni/pni.toml [report]."""
    path_overrides: dict[str, ParamValue] = {}
    if pni_cfg.report.src_dir is not None:
        path_overrides["src_dir"] = pni_cfg.report.src_dir
    if pni_cfg.report.output_dir is not None:
        path_overrides["output_dir"] = pni_cfg.report.output_dir

    report_only: dict[str, ParamValue] = {}
    if pni_cfg.report.html_output_dir is not None:
        report_only["html_output_dir"] = pni_cfg.report.html_output_dir
    if pni_cfg.report.formats is not None:
        report_only["formats"] = list(pni_cfg.report.formats)
    if pni_cfg.report.lang is not None:
        report_only["lang"] = pni_cfg.report.lang
    if pni_cfg.report.style is not None:
        report_only["style"] = pni_cfg.report.style
    return path_overrides, report_only


def _finalize_primitive_params(
    prim_params: dict[str, ParamValue],
    base_context: dict[str, ParamValue],
    workflow_id: str,
) -> dict[str, ParamValue]:
    """Merge canonical defaults, workflow target context, and action/step params, then interpolate."""
    canonical_defaults: dict[str, ParamValue] = {
        "src_dir": DEFAULT_REPORT_SRC_DIR,
        "output_dir": DEFAULT_REPORT_OUTPUT_DIR,
        "target": "{workflow_id}",
        "score_path": "{output_dir}/{target}_score.json",
    }
    merged: dict[str, ParamValue] = {**canonical_defaults, **base_context, **prim_params}
    return _interpolate_params(merged, workflow_id)


def _propagate_emitted_score(
    primitives: list[PrimitiveStep],
    explicit_report_score_steps: set[str],
) -> None:
    """Propagate resolved score_path, plan_path, or progress_path to subsequent write_drawlib_report steps."""
    emitted_score: str | None = None
    emitted_plan: str | None = None
    emitted_progress: str | None = None
    for prim in primitives:
        if prim.type == PrimitiveType.EMIT_SCORE:
            raw_score = prim.params.get("score_path")
            if isinstance(raw_score, str) and raw_score:
                emitted_score = raw_score
        elif prim.type == PrimitiveType.EMIT_MIGRATION_PLAN:
            out_dir = str(prim.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
            tgt = str(prim.params.get("target") or "")
            emitted_plan = resolve_migration_plan_rel_path(out_dir, tgt, str(prim.params.get("plan_path", "")))
            prim.params["plan_path"] = emitted_plan
        elif prim.type == PrimitiveType.EMIT_PROGRESS:
            out_dir = str(prim.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
            tgt = str(prim.params.get("target") or "")
            emitted_progress = resolve_progress_result_rel_path(out_dir, tgt, str(prim.params.get("progress_path", "")))
            prim.params["progress_path"] = emitted_progress
        elif prim.type == PrimitiveType.WRITE_DRAWLIB_REPORT:
            kind = str(prim.params.get("report_kind", "audit")).lower()
            if kind == "migration" and emitted_plan is not None and not prim.params.get("plan_path"):
                prim.params["plan_path"] = emitted_plan
            elif kind == "progress" and emitted_progress is not None and not prim.params.get("progress_path"):
                prim.params["progress_path"] = emitted_progress
            elif kind == "audit" and emitted_score is not None and prim.id not in explicit_report_score_steps:
                prim.params["score_path"] = emitted_score


def _resolve_emitted_output_from_prim(workflow_id: str, prim: PrimitiveStep) -> str | None:
    """Resolve emitted score/plan/progress path from a single primitive step if applicable."""
    if prim.type == PrimitiveType.EMIT_SCORE:
        raw_score = prim.params.get("score_path")
        return raw_score if isinstance(raw_score, str) and raw_score else None
    if prim.type == PrimitiveType.EMIT_MIGRATION_PLAN:
        out_dir = str(prim.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
        tgt = str(prim.params.get("target", workflow_id))
        return resolve_migration_plan_rel_path(out_dir, tgt, str(prim.params.get("plan_path", "")))
    if prim.type == PrimitiveType.EMIT_PROGRESS:
        out_dir = str(prim.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
        tgt = str(prim.params.get("target", workflow_id))
        return resolve_progress_result_rel_path(out_dir, tgt, str(prim.params.get("progress_path", "")))
    return None


def _resolve_report_output_from_prim(workflow_id: str, prim: PrimitiveStep) -> str:
    """Resolve output report path from a `write_drawlib_report` primitive step."""
    out_dir = str(prim.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR)).rstrip("/")
    target = str(prim.params.get("target", workflow_id))
    formats = prim.params.get("formats")
    if formats is None or (isinstance(formats, list) and "pdf" in formats):
        return f"{out_dir}/{target}.pdf"
    html_out = prim.params.get("html_output_dir")
    if isinstance(html_out, str) and html_out.strip() and isinstance(formats, list) and "html" in formats:
        return f"{html_out.rstrip('/')}/index.html"
    return out_dir


def resolve_workflow_outputs(
    workflow: WorkflowDefinition,
    primitives: list[PrimitiveStep],
) -> WorkflowOutputs:
    """Resolve effective facts, score/plan/progress JSON, and report paths from normalized primitives.

    Args:
        workflow: Parsed workflow definition.
        primitives: Normalized primitive steps for the workflow.

    Returns:
        WorkflowOutputs: Effective facts, score/plan/progress, and report output paths.
    """
    facts = workflow.outputs.facts or default_facts_rel_path(workflow.id)
    score = workflow.outputs.score
    report = workflow.outputs.report

    for prim in primitives:
        raw_facts = prim.params.get("facts_path")
        if workflow.outputs.facts is None and isinstance(raw_facts, str) and raw_facts:
            facts = raw_facts
        if workflow.outputs.score is None:
            emitted = _resolve_emitted_output_from_prim(workflow.id, prim)
            if emitted is not None:
                score = emitted
        if prim.type == PrimitiveType.WRITE_DRAWLIB_REPORT and workflow.outputs.report is None:
            report = _resolve_report_output_from_prim(workflow.id, prim)

    if score is None:
        if workflow.category == WorkflowCategory.PROGRESS:
            score = resolve_progress_result_rel_path(DEFAULT_REPORT_OUTPUT_DIR, workflow.id)
        else:
            score = f"{DEFAULT_REPORT_OUTPUT_DIR}/{workflow.id}_score.json"

    return WorkflowOutputs(facts=facts, score=score, report=report)


def normalize_workflow_steps(
    workflow: WorkflowDefinition,
    project_root: Path,
    lang: Optional[str] = None,
) -> list[PrimitiveStep]:
    """Convert workflow steps into internal PrimitiveSteps injected with targets and action-defined outputs.

    Args:
        workflow: Parsed workflow definition.
        project_root: Target project root directory.
        lang: Optional language scope override (resolved from target_root if omitted).

    Returns:
        list[PrimitiveStep]: Flat list of internal primitive steps.
    """
    pni_cfg = load_pni_config(project_root)
    target_root_dir = (project_root / workflow.targets.root).resolve()
    active_lang = lang or detect_active_language(
        target_root_dir if target_root_dir.exists() else project_root
    )

    base_context: dict[str, ParamValue] = {
        "workflow_id": workflow.id,
        "workflow_category": workflow.category.value,
        "target_root": workflow.targets.root,
        "source_targets": workflow.targets.source,
        "test_targets": workflow.targets.tests,
        "doc_targets": workflow.targets.docs,
        "exclude_targets": workflow.targets.exclude,
        "facts_path": workflow.outputs.facts or default_facts_rel_path(workflow.id),
    }
    if workflow.based_on:
        base_context["base_audit_workflow"] = workflow.based_on
    toml_path_overrides, toml_report_only = _build_pni_toml_report_overrides(pni_cfg)
    legacy_overrides = _build_legacy_output_overrides(workflow.outputs)

    normalized: list[PrimitiveStep] = []
    explicit_report_score_steps: set[str] = set()

    for step in workflow.steps:
        step_overrides: dict[str, ParamValue] = {
            **toml_path_overrides,
            **legacy_overrides,
            **step.with_params,
        }
        has_explicit_score = "score_path" in step.with_params or "target" in step.with_params
        display_name = step.name or step.uses or step.id
        step_lang_raw = step.with_params.get("lang")
        step_lang = step_lang_raw if isinstance(step_lang_raw, str) else active_lang

        if step.uses:
            expanded = expand_composite_action(
                step_id=step.id,
                step_name=display_name,
                action_id=step.uses,
                project_root=project_root,
                override_rules=step.rules,
                override_params=step_overrides,
                override_prompt=step.prompt,
                lang=step_lang,
            )
            for prim in expanded:
                merged_prim_params = (
                    {**prim.params, **toml_report_only, **step.with_params}
                    if prim.type == PrimitiveType.WRITE_DRAWLIB_REPORT
                    else prim.params
                )
                prim.params = _finalize_primitive_params(merged_prim_params, base_context, workflow.id)
                if has_explicit_score:
                    explicit_report_score_steps.add(prim.id)
            normalized.extend(expanded)
        elif step.action is not None:
            raw_direct = (
                {**toml_report_only, **step_overrides}
                if step.action == PrimitiveType.WRITE_DRAWLIB_REPORT
                else step_overrides
            )
            resolved_params = _finalize_primitive_params(raw_direct, base_context, workflow.id)
            if has_explicit_score:
                explicit_report_score_steps.add(step.id)
            normalized.append(
                PrimitiveStep(
                    id=step.id,
                    name=display_name,
                    type=step.action,
                    rules=step.rules,
                    params=resolved_params,
                    prompt=step.prompt or step.description,
                    source_action=None,
                )
            )

    _propagate_emitted_score(normalized, explicit_report_score_steps)
    return normalized


def _build_workflow_info(parsed: WorkflowDefinition, file_path: Path, project_root: Path) -> WorkflowInfo:
    """Construct WorkflowInfo with resolved effective outputs from normalized steps."""
    primitives = normalize_workflow_steps(parsed, project_root)
    resolved_outputs = resolve_workflow_outputs(parsed, primitives)
    return WorkflowInfo(
        id=parsed.id,
        category=parsed.category,
        based_on=parsed.based_on,
        name=parsed.name,
        description=parsed.description,
        path=file_path,
        step_count=len(parsed.steps),
        targets=parsed.targets,
        outputs=resolved_outputs,
    )


def list_workflows(
    project_root: Path,
    category: Optional[WorkflowCategory] = None,
) -> list[WorkflowInfo]:
    """List workflows defined in the project's .pni/workflows/ directory.

    Args:
        project_root: Target project root directory.
        category: Optional category filter ('audit' or 'migration').

    Returns:
        list[WorkflowInfo]: Sorted list of defined project workflows.
    """
    local_workflows_dir = project_root / ".pni" / "workflows"
    if not local_workflows_dir.exists():
        return []

    workflows: list[WorkflowInfo] = []
    for target_file in sorted(local_workflows_dir.glob("*.yaml")):
        parsed = _load_resolved_workflow(target_file, project_root)
        if parsed is None:
            continue
        if category is not None and parsed.category != category:
            continue
        workflows.append(_build_workflow_info(parsed, target_file, project_root))

    return workflows


def load_workflow(workflow_id: str, project_root: Path) -> tuple[WorkflowInfo, WorkflowDefinition] | None:
    """Load a workflow definition from .pni/workflows/<id>.yaml with 'based_on' inheritance resolved.

    Args:
        workflow_id: Workflow identifier (e.g. 'full_audit').
        project_root: Target project root directory.

    Returns:
        tuple[WorkflowInfo, WorkflowDefinition] | None: Metadata and validated definition.
    """
    clean_id = workflow_id.removesuffix(".yaml").strip()
    local_file = project_root / ".pni" / "workflows" / f"{clean_id}.yaml"
    if not local_file.exists():
        return None

    parsed = _load_resolved_workflow(local_file, project_root)
    if parsed is None:
        return None

    info = _build_workflow_info(parsed, local_file, project_root)
    return info, parsed


def copy_workflow_templates(
    project_root: Path,
    lang: Optional[str] = None,
    force: bool = False,
) -> list[Path]:
    """Copy built-in language-scoped workflow YAML templates to .pni/workflows/.

    Args:
        project_root: Target project directory.
        lang: Target programming language (auto-detected if omitted).
        force: If True, overwrite existing files.

    Returns:
        list[Path]: Created or overwritten file paths.
    """
    target_lang = lang or detect_active_language(project_root)
    src_dir = BUILTIN_WORKFLOWS_DIR / target_lang
    if not src_dir.is_dir():
        src_dir = BUILTIN_WORKFLOWS_DIR / "python"

    dest_dir = project_root / ".pni" / "workflows"
    dest_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for f in sorted(src_dir.glob("*.yaml")):
        dest_file = dest_dir / f.name
        if not dest_file.exists() or force:
            shutil.copy2(f, dest_file)
            created.append(dest_file)

    return created
