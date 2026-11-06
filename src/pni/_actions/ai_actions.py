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

from pni._actions.base_model import (
    ArchitectureRecord,
    DeterministicAckInput,
    ExecutionFlowMap,
    InterpretationInput,
    ParamValue,
    PrimitiveType,
    ReportCompletionInput,
    ScoreResult,
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


def get_expected_input_schema_json(
    primitive_type: PrimitiveType,
    params: dict[str, ParamValue] | None = None,
) -> str:
    """Return the formatted JSON Schema expected by push-action for a primitive type."""
    if primitive_type == PrimitiveType.RECORD_ARCHITECTURE:
        aspect = str((params or {}).get("aspect", "all")).strip()
        arch_cls = _ARCH_ASPECT_MODELS.get(aspect, ArchitectureRecord)
        return json.dumps(arch_cls.model_json_schema(), indent=2)
    model_map = {
        PrimitiveType.AI_INTERPRET: InterpretationInput,
        PrimitiveType.EMIT_SCORE: ScoreResult,
        PrimitiveType.EMIT_MIGRATION_PLAN: MigrationPlanResult,
        PrimitiveType.EMIT_PROGRESS: ProgressResult,
        PrimitiveType.WRITE_DRAWLIB_REPORT: ReportCompletionInput,
    }
    schema_cls = model_map.get(primitive_type, DeterministicAckInput)
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
            "PNI will deterministically deduplicate and sort them."
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
    rt_facts_path = default_runtime_facts_rel_path(cache_key)
    sec_facts_path = default_security_facts_rel_path(cache_key)
    pentest_facts_path = default_pentest_facts_rel_path(cache_key)
    mig_facts_path = default_migration_facts_rel_path(cache_key)
    prog_facts_path = default_progress_facts_rel_path(cache_key)
    arch_path = str(params.get("architecture_path", default_architecture_rel_path(cache_key)))
    score_path = str(params.get("score_path", f"{output_dir.rstrip('/')}/{target}_score.json"))
    plan_path = resolve_migration_plan_rel_path(output_dir, target, str(params.get("plan_path", "")))
    prog_path = resolve_progress_result_rel_path(output_dir, target, str(params.get("progress_path", "")))

    if primitive_type in (
        PrimitiveType.PROJECT_INSPECT,
        PrimitiveType.AST_ANALYZE,
        PrimitiveType.RUN_CHECK,
        PrimitiveType.SECURITY_SCAN,
        PrimitiveType.WEB_PENTEST,
        PrimitiveType.MIGRATION_ANALYZE,
        PrimitiveType.PROGRESS_ANALYZE,
    ):
        lines.extend(
            _render_deterministic_task_lines(
                primitive_type,
                facts_path,
                rt_facts_path,
                sec_facts_path,
                mig_facts_path,
                pentest_facts_path,
                prog_facts_path,
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
    elif primitive_type == PrimitiveType.EMIT_SCORE:
        lines.append(
            f"- **Agent Task (Score Emission)**: Review the Pre-Sorted Programmatic Audit Digest below and "
            f"submit 7-axis `ScoreResult` JSON (`architecture`, `code_quality`, `typing`, `testing`, "
            f"`dependencies`, `security`, `documentation`). PNI automatically merges & deterministically sorts "
            f"all prior `findings`, `rule_compliance`, `audit_dimensions`, `module_hotspots`, `action_plan`, "
            f"`runtime_facts`, `security_facts`, `pentest_facts`, `module_inventory`, `dangerous_sinks`, "
            f"`api_endpoints`, and `architecture_record` into `{score_path}`."
        )
    elif primitive_type == PrimitiveType.EMIT_MIGRATION_PLAN:
        lines.append(
            f"- **Agent Task (`emit_migration_plan`)**: Synthesize all deterministic `MigrationFacts` and the "
            f"confirmed `brief` into a validated `MigrationPlanResult` JSON (`confirmed_assumptions`, `non_goals`, "
            f"dynamic `target_axes`, `target_architecture` with Port/Adapter `component_mappings`, `decision_log`, "
            f"5-stage `phase_gates`, and topologically ordered `pr_wbs`). Every As-Is file in `affected_files`, "
            f"`component_mappings[].source_file`, and `decision_log[].file_path` MUST exist in the repository. "
            f"PNI attaches `migration_facts` and writes `{plan_path}`."
        )
    elif primitive_type == PrimitiveType.EMIT_PROGRESS:
        lines.append(
            f"- **Agent Task (`emit_progress`)**: Synthesize deterministic `ProgressFacts` and target code "
            f"inspection into a validated `ProgressResult` JSON (`delivery_status`, `overall_health_score`, "
            f"4-axis `dimension_scores`, per-task `task_assessments` matching exact `task_id`s from `.pni/progress/`, "
            f"`branch_assessments`, `bottlenecks_and_risks`, and prioritized `next_actions`). Do NOT modify "
            f"`.pni/progress/*.yaml` during measurement. PNI verifies baseline plan hash & paths, writes "
            f"`{prog_path}`, and updates `.pni/history/progress/`."
        )
    elif primitive_type == PrimitiveType.WRITE_DRAWLIB_REPORT:
        lines.append(_render_report_directive(params, arch_path, project_root))

    if prompt.strip():
        lines.append(f"\n{prompt.strip()}")

    return "\n".join(lines)
