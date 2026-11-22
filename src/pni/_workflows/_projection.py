# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Step-scoped fact projection and structured action payload models for Workflow v2."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from pni._actions import (
    AstFacts,
    Finding,
    PrimitiveType,
    ProjectFacts,
)
from pni._workflows.base_model import ActionRunRecord, WorkflowFactsBundle
from pni._workflows.planner import WorkflowExecutionPlan


class ActionPromptPayload(BaseModel):
    """Structured machine-readable action prompt emitted by `get-action --json` and `get-actions --ready --json`."""

    run_id: str
    workflow_id: str
    action_id: str
    step_key: str = ""
    seq: int
    total_actions: int
    primitive_type: PrimitiveType
    name: str
    source_action: Optional[str] = None
    needs: list[str] = Field(default_factory=list)
    fact_views: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    facts_path: str = ""
    expected_input_model: str = ""
    schema_skeleton: str = ""
    auto_completed_actions: list[str] = Field(default_factory=list)
    prompt_markdown: str = ""


_STATIC_FACT_VIEWS: dict[PrimitiveType, list[str]] = {
    PrimitiveType.CONFIRM_PLAN: ["plan"],
    PrimitiveType.SYNTHESIZE_ROLLUP: ["rollup"],
    PrimitiveType.WRITE_DRAWLIB_REPORT: ["report_only"],
    PrimitiveType.EMIT_SCORE: ["project_summary", "architecture"],
    PrimitiveType.EMIT_MIGRATION_PLAN: ["migration", "base_score", "architecture"],
    PrimitiveType.EMIT_PROGRESS: ["progress", "base_score"],
}
_ARCH_ASPECT_VIEWS: dict[str, list[str]] = {
    "purpose_and_stack": ["project"],
    "layers_and_modules": ["ast_structure", "architecture"],
    "flows_and_state": ["ast_structure", "architecture"],
}
_INTERPRET_HINT_RULES: tuple[tuple[tuple[str, ...], list[str]], ...] = (
    (("repo_structure", "repo_discovery"), ["project", "ast_structure", "companions", "pre_findings"]),
    (("ast_audit",), ["project_summary", "ast", "architecture", "pre_findings"]),
    (("pentest", "web_penetration"), ["pentest", "ast_security", "pre_findings"]),
    (
        ("security_vulnerability", "trivy", "security_audit"),
        ["security", "ast_security", "project_summary", "pre_findings"],
    ),
    (("runtime", "container_runtime"), ["runtime", "ast_testing", "pre_findings"]),
    (("migration",), ["migration", "base_score", "architecture"]),
    (("progress",), ["progress", "base_score"]),
    (("documentation_audit", "docs_audit"), ["project", "ast_structure", "companions", "pre_findings"]),
)


def resolve_fact_views(action: ActionRunRecord) -> list[str]:
    """Determine which fact slices should be projected into this step's prompt."""
    if action.fact_views:
        return list(action.fact_views)
    if action.primitive_type in _STATIC_FACT_VIEWS:
        return list(_STATIC_FACT_VIEWS[action.primitive_type])
    if action.primitive_type == PrimitiveType.RECORD_ARCHITECTURE:
        aspect = str(action.params.get("aspect", "all")).strip()
        return list(_ARCH_ASPECT_VIEWS.get(aspect, ["project", "ast_structure", "architecture"]))
    if action.primitive_type == PrimitiveType.AI_INTERPRET:
        return _infer_interpret_fact_views(action)
    return ["all"]


def _infer_interpret_fact_views(action: ActionRunRecord) -> list[str]:
    """Infer step-scoped fact slices for an `ai_interpret` action from source_action/step_key/rules."""
    hint = " ".join(
        [
            action.source_action or "",
            action.step_key or "",
            action.name or "",
            " ".join(action.rules),
        ]
    ).lower()
    for tokens, views in _INTERPRET_HINT_RULES:
        if any(tok in hint for tok in tokens):
            return list(views)
    return ["project_summary", "ast", "architecture", "pre_findings"]


def render_project_summary_compact(pf: ProjectFacts) -> list[str]:
    """Render a compact 4-line ProjectFacts summary for steps that don't need full repo details."""
    return [
        "\n### Project Scope Summary (`project_inspect`)",
        (
            f"- **Project**: `{pf.project_name}` (v{pf.version}, lang=`{pf.language}`, "
            f"runtime_types=`{pf.runtime_types}`, frameworks=`{pf.detected_frameworks or ['none']}`)"
        ),
        (
            f"- **Files & Dependencies**: `{pf.source_files_count}` src / `{pf.test_files_count}` test files, "
            f"`{len(pf.dependencies)}` deps (`{len(pf.unpinned_dependencies)}` unpinned), "
            f"lockfiles={pf.lockfiles_found}"
        ),
    ]


def render_ast_structure_compact(af: AstFacts) -> list[str]:
    """Render module inventory and import cycles without dumping unrelated style lists."""
    lines = [
        f"\n### AST Structural Summary (`ast_analyze`, lang=`{af.language}`)",
        (
            f"- **Size**: `{af.total_files}` files, `{af.total_loc}` LOC, "
            f"`{af.total_classes}` classes, `{af.total_functions}` functions, "
            f"circular_deps=`{len(af.circular_dependencies)}`"
        ),
    ]
    if af.module_inventory:
        inv_preview = [
            f"  - `{m.file}` ({m.loc} LOC): types={m.public_types[:4]}, callables={m.public_callables[:5]}"
            for m in af.module_inventory[:25]
        ]
        lines.append(f"- **Module Inventory ({len(af.module_inventory)} files)**:\n" + "\n".join(inv_preview))
    return lines


def render_ast_testing_compact(af: AstFacts) -> list[str]:
    """Render only test-related AST facts for runtime/testing interpretation steps."""
    tst_pct = f"{af.module_test_coverage_pct}%" if af.module_test_coverage_pct is not None else "N/A"
    lines = [
        "\n### Static Test Suite AST Summary",
        (
            f"- **Tests**: `{af.test_functions_count}` test functions, static module coverage `{tst_pct}`, "
            f"assertion-free tests=`{len(af.assertion_free_tests)}`"
        ),
    ]
    if af.test_harness_notes:
        lines.append(f"- **Test Harness Notes**: {af.test_harness_notes}")
    return lines


def render_companions_summary(bundle: WorkflowFactsBundle) -> list[str]:
    """Render companion DSL scan summary (Dockerfile/YAML/SQL/Shell/Terraform) when present."""
    if not bundle.companion_ast_facts:
        return []
    lines = ["\n### Companion Infrastructure & DSL Scan (`companion_ast_facts`)"]
    for lang_id, af in sorted(bundle.companion_ast_facts.items()):
        lines.append(
            f"- **`{lang_id}`**: `{af.total_files}` files, `{af.total_loc}` LOC, "
            f"secrets=`{len(af.hardcoded_secrets)}`, sinks=`{len(af.dangerous_sinks)}`"
        )
    return lines


def render_pre_findings_slice(pre_findings: list[Finding], views: list[str]) -> list[str]:
    """Render deterministic `det-*` pre-findings relevant to this step for AI FP triage."""
    if not pre_findings:
        return []
    if "security" in views or "pentest" in views:
        scoped = [f for f in pre_findings if f.category in {"security", "dependencies"}]
    elif "runtime" in views:
        scoped = [f for f in pre_findings if f.category == "testing"]
    else:
        scoped = pre_findings
    if not scoped:
        return []
    lines = [
        f"\n### Deterministic Pre-Findings for Triage (`det-*`, {len(scoped)} items)",
        "Use `finding_adjustments` (`waive`/`reclassify`, `reason >= 10 chars`) to triage any false positives:",
    ]
    for f in scoped[:20]:
        loc = f" (`{f.file_path}:{f.line}`)" if f.file_path else ""
        lines.append(f"- `{f.finding_id}` `[{f.severity.upper()}]` `{f.rule_id}`{loc}: {f.description}")
    return lines


def render_approved_plan_banner(plan: WorkflowExecutionPlan | None) -> list[str]:
    """Render concise approved focus areas & alignment summary from `confirm_plan`."""
    if plan is None or plan.approval is None:
        return []
    app = plan.approval
    lines: list[str] = []
    if app.focus_areas:
        lines.append(f"- **Approved Focus Areas**: `{app.focus_areas}`")
    if app.alignment_summary.strip():
        lines.append(f"- **Human Alignment Summary**: {app.alignment_summary.strip()}")
    return lines
