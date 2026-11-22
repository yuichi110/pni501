# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Prompt builders and schema selectors for stateful workflow action steps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pydantic import BaseModel

from pni._actions.base_model import (
    ArchitectureRecord,
    DeterministicAckInput,
    ExecutionFlowMap,
    InterpretationInput,
    ParamValue,
    PlanApprovalInput,
    PrimitiveType,
    ReportCompletionInput,
    RollupSynthesisInput,
    ScoreSubmissionInput,
    StructureMap,
    SystemProfile,
)
from pni._actions.migration_analyze.models import (
    MigrationPlanResult,
    resolve_migration_plan_rel_path,
)
from pni._actions.progress_analyze.models import (
    ProgressResult,
    resolve_progress_result_rel_path,
)
from pni._cache import (
    default_architecture_rel_path,
    default_facts_rel_path,
    default_migration_facts_rel_path,
    default_pentest_facts_rel_path,
    default_progress_facts_rel_path,
    default_runtime_facts_rel_path,
    default_security_facts_rel_path,
)
from pni._reporter import (
    DEFAULT_REPORT_OUTPUT_DIR,
    DEFAULT_REPORT_SRC_DIR,
    render_drawlib_report_guide,
)

_ASPECT_GUIDES: Final[dict[str, str]] = {
    "purpose_and_stack": (
        "- **Agent Task (`record_architecture` — Aspect 1: `purpose_and_stack`)**: "
        "Synthesize the system purpose, domain context, runtime type, tech stack, and external "
        "integrations strictly from `ProjectFacts`, `README`, and manifests. Do NOT speculate."
    ),
    "layers_and_modules": (
        "- **Agent Task (`record_architecture` — Aspect 2: `layers_and_modules`)**: "
        "Map architectural layers, module responsibilities, and dependency boundaries strictly grounded "
        "in `AstFacts.module_inventory` and `internal_import_graph`. Every `paths` and `modules[].path` "
        "entry MUST exist in the repository or `push-action` will reject hallucinated paths."
    ),
    "flows_and_state": (
        "- **Agent Task (`record_architecture` — Aspect 3: `flows_and_state`)**: "
        "Trace concrete entry points, runtime execution flows, state/storage mechanisms, and error/concurrency "
        "handling by reading entry-point files. Every path in `entry_points` and `involved_files` MUST "
        "reference a real repository file (`path` or `path:symbol`)."
    ),
}


_ARCH_ASPECT_MODELS: Final[dict[str, type[SystemProfile | StructureMap | ExecutionFlowMap]]] = {
    "purpose_and_stack": SystemProfile,
    "layers_and_modules": StructureMap,
    "flows_and_state": ExecutionFlowMap,
}


def get_expected_input_model(
    primitive_type: PrimitiveType,
    params: dict[str, ParamValue] | None = None,
) -> type[BaseModel]:
    """Return the Pydantic input model expected by push-action for a primitive type."""
    if primitive_type == PrimitiveType.RECORD_ARCHITECTURE:
        aspect = str((params or {}).get("aspect", "all")).strip()
        return _ARCH_ASPECT_MODELS.get(aspect, ArchitectureRecord)
    model_map: dict[PrimitiveType, type[BaseModel]] = {
        PrimitiveType.CONFIRM_PLAN: PlanApprovalInput,
        PrimitiveType.AI_INTERPRET: InterpretationInput,
        PrimitiveType.EMIT_SCORE: ScoreSubmissionInput,
        PrimitiveType.SYNTHESIZE_ROLLUP: RollupSynthesisInput,
        PrimitiveType.EMIT_MIGRATION_PLAN: MigrationPlanResult,
        PrimitiveType.EMIT_PROGRESS: ProgressResult,
        PrimitiveType.WRITE_DRAWLIB_REPORT: ReportCompletionInput,
    }
    return model_map.get(primitive_type, DeterministicAckInput)


def _compact_scalar_type(prop: dict[str, object]) -> object:
    """Render a compact scalar placeholder string for primitive JSON Schema types."""
    ptype = prop.get("type")
    if ptype == "integer":
        lo, hi = prop.get("minimum"), prop.get("maximum")
        return f"int({lo}..{hi})" if lo is not None or hi is not None else "int"
    if ptype == "string":
        min_len = prop.get("minLength")
        return f"string(min_len={min_len})" if min_len else "string"
    return {"number": "float", "boolean": "bool"}.get(str(ptype), "any")


def _compact_object_node(
    prop: dict[str, object],
    defs: dict[str, dict[str, object]],
    depth: int,
) -> object:
    """Render a compact object skeleton from JSON Schema properties or additionalProperties."""
    props = prop.get("properties")
    if isinstance(props, dict) and depth < 3:
        raw_req = prop.get("required")
        req = set(raw_req) if isinstance(raw_req, list) else set()
        return {
            (k if k in req else f"{k}?"): _compact_schema_node(sub, defs, depth + 1)
            for k, sub in props.items()
            if isinstance(sub, dict)
        }
    add_props = prop.get("additionalProperties")
    if isinstance(add_props, dict):
        return {"<key>": _compact_schema_node(add_props, defs, depth + 1)}
    return "{}"


def _compact_schema_node(
    prop: dict[str, object],
    defs: dict[str, dict[str, object]],
    depth: int = 0,
) -> object:
    """Recursively render a concise human/LLM-friendly JSON skeleton from JSON Schema."""
    ref = prop.get("$ref")
    if isinstance(ref, str):
        ref_name = ref.rsplit("/", maxsplit=1)[-1]
        return (
            _compact_schema_node(defs[ref_name], defs, depth + 1)
            if ref_name in defs and depth < 3
            else f"<{ref_name}>"
        )
    any_of = prop.get("anyOf")
    if isinstance(any_of, list):
        non_null = [p for p in any_of if isinstance(p, dict) and p.get("type") != "null"]
        return (
            _compact_schema_node(non_null[0], defs, depth)
            if len(non_null) == 1
            else " | ".join(str(_compact_schema_node(p, defs, depth + 1)) for p in non_null[:3])
        )
    enum_vals = prop.get("enum")
    if isinstance(enum_vals, list):
        return " | ".join(repr(v) for v in enum_vals)
    ptype = prop.get("type")
    if ptype == "object":
        return _compact_object_node(prop, defs, depth)
    if ptype == "array":
        items = prop.get("items")
        return [_compact_schema_node(items, defs, depth + 1)] if isinstance(items, dict) else ["..."]
    return _compact_scalar_type(prop)


def render_compact_schema(model_cls: type[BaseModel]) -> str:
    """Render a compact JSON skeleton with inline type hints (`key?` denotes optional fields)."""
    raw = model_cls.model_json_schema()
    raw_defs = raw.get("$defs")
    defs = {k: v for k, v in raw_defs.items() if isinstance(v, dict)} if isinstance(raw_defs, dict) else {}
    skeleton = _compact_schema_node(raw, defs, depth=0)
    return json.dumps(skeleton, indent=2)


def get_expected_input_schema_json(
    primitive_type: PrimitiveType,
    params: dict[str, ParamValue] | None = None,
    *,
    compact: bool = False,
) -> str:
    """Return the formatted JSON Schema (or compact skeleton) expected by push-action."""
    schema_cls = get_expected_input_model(primitive_type, params)
    if compact:
        return render_compact_schema(schema_cls)
    return json.dumps(schema_cls.model_json_schema(), indent=2)


def _to_str_list(raw: ParamValue | None, fallback: list[str]) -> list[str]:
    """Normalize a ParamValue into a list of strings."""
    if isinstance(raw, list):
        return [str(item) for item in raw]
    if isinstance(raw, str):
        return [s.strip() for s in raw.split(",") if s.strip()] or fallback
    return fallback


def _render_report_directive(
    params: dict[str, ParamValue],
    arch_path: str,
    project_root: Path | None,
) -> str:
    """Render the Drawlib report authoring directive and pre-sorted ReportBlueprint."""
    workflow_id = str(params.get("workflow_id") or "")
    target = str(params.get("target") or workflow_id or "full_audit")
    cache_key = workflow_id or target
    output_dir = str(params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
    src_base_dir = str(params.get("src_dir", DEFAULT_REPORT_SRC_DIR))
    report_kind = str(params.get("report_kind", "audit")).strip().lower()
    default_score = f"{output_dir.rstrip('/')}/{target}_score.json"
    plan_path = (
        resolve_migration_plan_rel_path(output_dir, target, str(params.get("plan_path", "")))
        if report_kind == "migration"
        else ""
    )
    progress_path = (
        resolve_progress_result_rel_path(output_dir, target, str(params.get("progress_path", "")))
        if report_kind == "progress"
        else ""
    )
    raw_html_out = params.get("html_output_dir")
    html_out = str(raw_html_out).strip() if isinstance(raw_html_out, str) and raw_html_out.strip() else None
    return render_drawlib_report_guide(
        target=target,
        src_base_dir=src_base_dir,
        output_dir=output_dir,
        html_output_dir=html_out,
        formats=_to_str_list(params.get("formats"), ["pdf"]),
        score_path=str(params.get("score_path", default_score)),
        facts_path=str(params.get("facts_path", default_facts_rel_path(cache_key))),
        target_root=str(params.get("target_root", ".")),
        source_targets=_to_str_list(params.get("source_targets"), ["src"]),
        doc_targets=_to_str_list(params.get("doc_targets"), ["README.md"]),
        lang=str(params.get("lang", "en")),
        style=str(params.get("style", "google")),
        architecture_path=arch_path,
        workflow_id=workflow_id,
        project_root=project_root,
        report_kind=report_kind,
        plan_path=plan_path,
        progress_path=progress_path,
    )


def _render_ai_interpret_checklist(rules: list[str], source_action: str | None) -> list[str]:
    """Render explicit structured submission instructions for an ai_interpret step."""
    audit_label = f"`{source_action}`" if source_action else "this audit step"
    rule_list = ", ".join(f"`{r}`" for r in rules) if rules else "active rules"
    return [
        f"- **Agent Task (`ai_interpret` — {audit_label})**: "
        "Evaluate the deterministic facts and target source files against the active rules below.",
        "- **Required Structured Deliverables in `push-action` (`InterpretationInput`)**:",
        f"  1. **`step_score` (`0..100`) & `summary`**: Overall score and concise synthesis for {audit_label}.",
        (
            f"  2. **`rule_checks` (Mandatory Per-Rule Verdicts)**: Submit one `RuleCheckResult` "
            f"(`status`: `pass` | `warn` | `fail` | `not_applicable` + exact `evidence` from facts/code) "
            f"for **each** rule in [{rule_list}]. Even `pass` checks MUST be recorded so compliance "
            "appears in the final report!"
        ),
        (
            "  3. **`findings` & `action_items`**: Submit grounded violations (`file_path` MUST exist in repo) "
            "and prioritized fixes (`P0` | `P1` | `P2`, populating `related_rules` with rule IDs / CVE IDs). "
            "Use `finding_adjustments` (`waive` / `reclassify` with `reason >= 10 chars`) to triage deterministic "
            "`det-*` pre-findings, and optional `baseline_delta` (`-10..+10`) for qualitative adjustments."
        ),
    ]


def _render_deterministic_task_lines(
    primitive_type: PrimitiveType,
    facts_path: str,
    runtime_facts_path: str,
    security_facts_path: str,
    migration_facts_path: str = "",
    pentest_facts_path: str = "",
    progress_facts_path: str = "",
) -> list[str]:
    """Render deterministic step instructions for programmatic analyzer primitives."""
    if primitive_type == PrimitiveType.RUN_CHECK:
        return [
            (
                f"- **Deterministic Container Verification Completed**: PNI executed `{primitive_type.value}`, "
                f"saved detailed artifacts to `{runtime_facts_path}`, and updated `{facts_path}`."
            ),
            (
                "- **Agent Task**: Review the container build, offline unit test, measured coverage, and startup "
                "smoke results below, then push acknowledgment to proceed."
            ),
        ]
    if primitive_type == PrimitiveType.SECURITY_SCAN:
        return [
            (
                f"- **Deterministic Security & Supply-Chain Scan Completed**: PNI executed `{primitive_type.value}`, "
                f"saved normalized Trivy artifacts to `{security_facts_path}`, and updated `{facts_path}`."
            ),
            (
                "- **Agent Task**: Review the application vs OS CVEs, Dockerfile misconfigurations, redacted secrets, "
                "and AST dangerous sinks / API endpoints below, then push acknowledgment to proceed."
            ),
        ]
    if primitive_type == PrimitiveType.WEB_PENTEST:
        return [
            (
                f"- **Deterministic Web Penetration Test Completed**: PNI materialized `httpx` probes in "
                f"`.pni/pentests/`, executed `{primitive_type.value}`, saved `PentestFacts` to "
                f"`{pentest_facts_path}`, and updated `{facts_path}`."
            ),
            (
                "- **Agent Task**: Review the live HTTP probe summary and CWE-mapped penetration findings below "
                "(customizing `.pni/pentests/<target>/` if needed), then push acknowledgment to proceed."
            ),
        ]
    if primitive_type == PrimitiveType.MIGRATION_ANALYZE:
        return [
            (
                f"- **Deterministic Migration Intelligence Completed**: PNI executed `{primitive_type.value}`, "
                f"saved `MigrationFacts` to `{migration_facts_path}`, and updated `{facts_path}`."
            ),
            (
                "- **Agent Task**: Review the resolved multi-line `brief`, topological Waves 1..4, cycle-cut "
                "recommendations, implicit I/O & env contracts, stateful/DB/HTTP `boundary_touchpoints`, codemod "
                "recipes, and `spec_vs_bug_candidates` below, then push acknowledgment to proceed."
            ),
        ]
    if primitive_type == PrimitiveType.PROGRESS_ANALYZE:
        return [
            (
                f"- **Deterministic Progress & Git Governance Analysis Completed**: PNI executed "
                f"`{primitive_type.value}`, saved `ProgressFacts` to `{progress_facts_path}`, "
                f"and updated `{facts_path}`."
            ),
            (
                "- **Agent Task**: Review the planned milestones/tasks, `git merge-tree` branch conflict simulations, "
                "Git policy compliance, LOC/test trajectories, and linked audit history below without modifying "
                "`.pni/progress/*.yaml`, then push acknowledgment to proceed."
            ),
        ]
    return [
        (
            f"- **Deterministic Execution Completed**: PNI has executed `{primitive_type.value}` "
            f"and updated `{facts_path}`."
        ),
        (
            "- **Agent Task**: Review the deterministic facts below, verify target scope accuracy, "
            "and push acknowledgment to proceed to the next action."
        ),
    ]


_DETERMINISTIC_TASK_TYPES: Final[frozenset[PrimitiveType]] = frozenset(
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


def _render_emit_and_report_lines(
    primitive_type: PrimitiveType,
    params: dict[str, ParamValue],
    arch_path: str,
    score_path: str,
    plan_path: str,
    prog_path: str,
    project_root: Path | None,
) -> list[str]:
    """Render directive lines for emission, rollup synthesis, and Drawlib report primitives."""
    if primitive_type == PrimitiveType.EMIT_SCORE:
        return [
            f"- **Agent Task (`emit_score` — v2 Clean Score Submission)**: Review the Deterministic 7-Axis "
            f"Baseline Scores and Pre-Sorted Programmatic Audit Digest below, then submit the compact "
            f"`ScoreSubmissionInput` DTO (`overall_score`, `category_scores`, `category_rationales`, `summary`, "
            f"optional `finding_adjustments` / `extra_findings` / `extra_action_items` / `report_hints`). "
            f"PNI automatically merges deterministic pre-findings, prior `ai_interpret` evidence, runtime/security/"
            f"pentest facts, and writes `{score_path}`, `*_summary.json`, and `*_findings.sarif` (SARIF 2.1.0)."
        ]
    if primitive_type == PrimitiveType.SYNTHESIZE_ROLLUP:
        return [
            f"- **Agent Task (`synthesize_rollup` — Multi-Component Executive Synthesis)**: Review the "
            f"Deterministic Multi-Component Rollup Summary (component weights, 7-axis rolled-up scores, "
            f"weakest-link guardrails, root governance, and companion DSLs) below and submit `RollupSynthesisInput` "
            f"(`summary`, `cross_component_architecture`, `boundary_findings`, `unified_action_plan`, `strengths`, "
            f"`report_hints`). PNI writes unified `{score_path}`, `*_summary.json`, and `*_findings.sarif`."
        ]
    if primitive_type == PrimitiveType.EMIT_MIGRATION_PLAN:
        return [
            f"- **Agent Task (`emit_migration_plan`)**: Synthesize all deterministic `MigrationFacts` and the "
            f"confirmed `brief` into a validated `MigrationPlanResult` JSON (`confirmed_assumptions`, `non_goals`, "
            f"dynamic `target_axes`, `target_architecture` with Port/Adapter `component_mappings`, `decision_log`, "
            f"5-stage `phase_gates`, and topologically ordered `pr_wbs`). Every As-Is file in `affected_files`, "
            f"`component_mappings[].source_file`, and `decision_log[].file_path` MUST exist in the repository. "
            f"PNI attaches `migration_facts` and writes `{plan_path}`."
        ]
    if primitive_type == PrimitiveType.EMIT_PROGRESS:
        return [
            f"- **Agent Task (`emit_progress`)**: Synthesize deterministic `ProgressFacts` and target code "
            f"inspection into a validated `ProgressResult` JSON (`delivery_status`, `overall_health_score`, "
            f"4-axis `dimension_scores`, per-task `task_assessments` matching exact `task_id`s from `.pni/progress/`, "
            f"`branch_assessments`, `bottlenecks_and_risks`, and prioritized `next_actions`). Do NOT modify "
            f"`.pni/progress/*.yaml` during measurement. PNI verifies baseline plan hash & paths, writes "
            f"`{prog_path}`, and updates `.pni/history/progress/`."
        ]
    if primitive_type == PrimitiveType.WRITE_DRAWLIB_REPORT:
        return [_render_report_directive(params, arch_path, project_root)]
    return []


def render_action_task_body(
    primitive_type: PrimitiveType,
    params: dict[str, ParamValue],
    prompt: str,
    *,
    rules: list[str] | None = None,
    source_action: str | None = None,
    project_root: Path | None = None,
) -> str:
    """Render the task-specific directive body for an action step."""
    lines: list[str] = []
    workflow_id = str(params.get("workflow_id") or "")
    target = str(params.get("target") or workflow_id or "full_audit")
    cache_key = workflow_id or target
    output_dir = str(params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
    facts_path = str(params.get("facts_path", default_facts_rel_path(cache_key)))
    arch_path = str(params.get("architecture_path", default_architecture_rel_path(cache_key)))
    score_path = str(params.get("score_path", f"{output_dir.rstrip('/')}/{target}_score.json"))
    plan_path = resolve_migration_plan_rel_path(output_dir, target, str(params.get("plan_path", "")))
    prog_path = resolve_progress_result_rel_path(output_dir, target, str(params.get("progress_path", "")))

    if primitive_type == PrimitiveType.CONFIRM_PLAN:
        lines.extend(
            [
                "- **Agent Task (`confirm_plan` — Human-in-the-Loop DAG Alignment Gate)**: "
                "Present the validated Mermaid Execution DAG, detected scope/language/harness summary, and "
                "Alignment Questions below to the user BEFORE executing heavy audit stages.",
                "- **After User Alignment**: Submit `PlanApprovalInput` (`approved: true`, plus any agreed "
                "`confirmed_targets`, `disabled_steps`, `focus_areas`, `extra_opt_outs`, `report_lang`, "
                "`report_formats`, `report_mode`, and `alignment_summary`).",
            ]
        )
    elif primitive_type in _DETERMINISTIC_TASK_TYPES:
        lines.extend(
            _render_deterministic_task_lines(
                primitive_type,
                facts_path,
                default_runtime_facts_rel_path(cache_key),
                default_security_facts_rel_path(cache_key),
                default_migration_facts_rel_path(cache_key),
                default_pentest_facts_rel_path(cache_key),
                default_progress_facts_rel_path(cache_key),
            )
        )
    elif primitive_type == PrimitiveType.LOAD_RULES:
        lines.append("- **Agent Task**: Load and review the engineering standards included below.")
    elif primitive_type == PrimitiveType.RECORD_ARCHITECTURE:
        aspect = str(params.get("aspect", "all")).strip()
        default_guide = (
            "- **Agent Task (`record_architecture`)**: Record grounded architecture metadata verified against AST."
        )
        lines.append(_ASPECT_GUIDES.get(aspect, default_guide))
        lines.append(f"- **Persistence Target**: PNI validates paths and updates `{arch_path}`.")
    elif primitive_type == PrimitiveType.AI_INTERPRET:
        lines.extend(_render_ai_interpret_checklist(rules or [], source_action))
    else:
        lines.extend(
            _render_emit_and_report_lines(
                primitive_type,
                params,
                arch_path,
                score_path,
                plan_path,
                prog_path,
                project_root,
            )
        )

    if prompt.strip():
        lines.append(f"\n{prompt.strip()}")

    return "\n".join(lines)
