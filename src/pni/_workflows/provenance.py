# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic action-level execution DAG and inspection provenance summary builders."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pni._actions.base_model import (
    AuditScopeMetadata,
    ExecutionDagSummary,
    ExecutionStageNode,
    PrimitiveType,
)
from pni._actions.progress_analyze.git_exec import inspect_git_repo_head
from pni._workflows.base_model import ActionRunRecord, RunStatus, WorkflowFactsBundle, WorkflowRunRecord
from pni._workflows.planner import DETERMINISTIC_PRIMITIVES, WorkflowExecutionPlan

if TYPE_CHECKING:
    from pni._workflows._rollup_engine import RollupFacts

StageMode = Literal["AUTO", "AI", "HYBRID", "ASK", "SKIP"]
StageStatus = Literal["completed", "skipped", "pending", "in_progress"]


def _stage_label(stage_id: str, primitives: list[ActionRunRecord]) -> str:
    """Derive a concise human-readable label (<= 52 chars) for a grouped workflow stage."""
    names = [p.name.strip() for p in primitives if p.name and p.name.strip()]
    if len(names) == 1:
        raw = names[0]
    elif names:
        prefixes = [n.split(":", 1)[0].strip() for n in names if ":" in n]
        if prefixes and len(set(prefixes)) == 1:
            raw = prefixes[0]
        else:
            src = next((p.source_action for p in primitives if p.source_action), None)
            raw = src.replace("_", " ").title() if src else stage_id.replace("_", " ").title()
    else:
        raw = stage_id.replace("_", " ").title()
    return raw if len(raw) <= 52 else raw[:49].rstrip() + "..."


def _resolve_stage_status(
    primitives: list[ActionRunRecord],
    current_action_id: str | None,
) -> StageStatus:
    """Aggregate primitive RunStatus values into a single stage execution status."""
    if current_action_id and any(p.action_id == current_action_id for p in primitives):
        return "completed"
    statuses = [p.status for p in primitives]
    if all(s == RunStatus.SKIPPED for s in statuses):
        return "skipped"
    if all(s in {RunStatus.COMPLETED, RunStatus.SKIPPED} for s in statuses):
        return "completed"
    if any(s == RunStatus.IN_PROGRESS for s in statuses):
        return "in_progress"
    return "pending"


def _resolve_stage_mode(primitives: list[ActionRunRecord], status: StageStatus) -> StageMode:
    """Classify a logical workflow stage as ASK, SKIP, AUTO, AI, or HYBRID."""
    if status == "skipped":
        return "SKIP"
    ptypes = {p.primitive_type for p in primitives}
    if PrimitiveType.CONFIRM_PLAN in ptypes:
        return "ASK"
    has_det = any(pt in DETERMINISTIC_PRIMITIVES for pt in ptypes)
    has_ai = any(pt not in DETERMINISTIC_PRIMITIVES for pt in ptypes)
    if has_det and has_ai:
        return "HYBRID"
    if has_det:
        return "AUTO"
    return "AI"


def _bundle_skip_reason(ptypes: set[PrimitiveType], bundle: WorkflowFactsBundle | None) -> str:
    """Return any deterministic runtime/security/pentest skip reason stored in bundle."""
    if bundle is None:
        return ""
    checks = (
        (PrimitiveType.RUN_CHECK, bundle.runtime_facts.skip_reason if bundle.runtime_facts else ""),
        (PrimitiveType.SECURITY_SCAN, bundle.security_facts.skip_reason if bundle.security_facts else ""),
        (PrimitiveType.WEB_PENTEST, bundle.pentest_facts.skip_reason if bundle.pentest_facts else ""),
    )
    return next((reason for pt, reason in checks if pt in ptypes and reason), "")


def _resolve_skip_reason(
    stage_id: str,
    primitives: list[ActionRunRecord],
    bundle: WorkflowFactsBundle | None,
    plan: WorkflowExecutionPlan | None,
) -> str:
    """Extract the most specific deterministic reason why a stage was skipped."""
    if plan is not None:
        if plan.approval is not None and stage_id in plan.approval.disabled_steps:
            return "Disabled during human plan approval"
        action_ids = {p.action_id for p in primitives}
        plan_reason = next(
            (
                pnode.skip_reason
                for pnode in plan.nodes
                if (pnode.action_id in action_ids or pnode.step_key == stage_id) and pnode.skip_reason
            ),
            "",
        )
        if plan_reason:
            return plan_reason

    bundle_reason = _bundle_skip_reason({p.primitive_type for p in primitives}, bundle)
    if bundle_reason:
        return bundle_reason
    when_expr = next((p.when for p in primitives if p.when), None)
    return f"Condition '{when_expr}' evaluated to false" if when_expr else "Skipped by workflow policy"


def _runtime_and_security_stage_highlights(
    ptypes: set[PrimitiveType],
    bundle: WorkflowFactsBundle,
) -> list[str]:
    """Build deterministic highlight snippets for runtime, security, and pentest primitives."""
    parts: list[str] = []
    if PrimitiveType.RUN_CHECK in ptypes and bundle.runtime_facts is not None:
        rf = bundle.runtime_facts
        if rf.status == "skipped":
            parts.append(f"runtime skipped ({rf.skip_reason or 'no harness'})")
        else:
            cov = (
                f", cov {rf.coverage.line_coverage_pct}%"
                if rf.coverage.measured and rf.coverage.line_coverage_pct is not None
                else ""
            )
            parts.append(
                f"build={rf.harness_build.status}, "
                f"tests={rf.test_execution.passed_tests}/{rf.test_execution.total_tests}{cov}"
            )
    if PrimitiveType.SECURITY_SCAN in ptypes and bundle.security_facts is not None:
        sf = bundle.security_facts
        if sf.status == "skipped":
            parts.append(f"Trivy skipped ({sf.skip_reason or 'unavailable'})")
        else:
            ac = sf.app_vuln_counts
            parts.append(f"Trivy CVEs={ac.total} (CRIT={ac.critical}, HIGH={ac.high}), secrets={len(sf.secrets)}")
    if PrimitiveType.WEB_PENTEST in ptypes and bundle.pentest_facts is not None:
        wp = bundle.pentest_facts
        if wp.status == "skipped":
            parts.append(f"pentest skipped ({wp.skip_reason or 'disabled'})")
        else:
            ps = wp.probe_summary
            parts.append(f"probes={ps.passed_probes}/{ps.total_probes}, findings={len(wp.findings)}")
    return parts


def _analysis_stage_highlights(ptypes: set[PrimitiveType], bundle: WorkflowFactsBundle) -> list[str]:
    """Build deterministic highlight snippets for project, AST, architecture, migration, progress, and emit steps."""
    parts: list[str] = []
    if PrimitiveType.PROJECT_INSPECT in ptypes and bundle.project_facts is not None:
        pf = bundle.project_facts
        parts.append(f"{pf.source_files_count} src / {pf.test_files_count} test files, {len(pf.dependencies)} deps")
    if PrimitiveType.AST_ANALYZE in ptypes and bundle.ast_facts is not None:
        af = bundle.ast_facts
        parts.append(f"{af.total_files} files, {af.total_loc:,} LOC, {len(af.dangerous_sinks)} sinks")
    parts.extend(_runtime_and_security_stage_highlights(ptypes, bundle))
    if PrimitiveType.RECORD_ARCHITECTURE in ptypes and bundle.architecture_record is not None:
        arch = bundle.architecture_record
        layers = len(arch.structure_map.layers) if arch.structure_map else 0
        flows = len(arch.execution_flow_map.execution_flows) if arch.execution_flow_map else 0
        parts.append(f"{layers} layers, {flows} flows grounded")
    if PrimitiveType.MIGRATION_ANALYZE in ptypes and bundle.migration_facts is not None:
        mf = bundle.migration_facts
        parts.append(
            f"{len(mf.refactoring_waves)} waves, {len(mf.boundary_touchpoints)} touchpoints, "
            f"{len(mf.mechanical_codemods)} codemods"
        )
    if PrimitiveType.PROGRESS_ANALYZE in ptypes and bundle.progress_facts is not None:
        prf = bundle.progress_facts
        parts.append(
            f"{len(prf.branches)} branches, {len(prf.task_evidence)} tasks, "
            f"{len(prf.policy_violations)} policy violations"
        )
    emit_labels = (
        (PrimitiveType.EMIT_SCORE, "7-axis anchored (±10pt) score + SARIF"),
        (PrimitiveType.EMIT_MIGRATION_PLAN, "Validated To-Be migration plan JSON"),
        (PrimitiveType.EMIT_PROGRESS, "Validated progress & Git health JSON"),
    )
    parts.extend(lbl for pt, lbl in emit_labels if pt in ptypes)
    return parts


def _stage_highlight(
    stage_id: str,
    primitives: list[ActionRunRecord],
    status: StageStatus,
    skip_reason: str,
    bundle: WorkflowFactsBundle | None,
    plan: WorkflowExecutionPlan | None,
    extra_highlights: dict[str, str],
) -> str:
    """Build a concise deterministic highlight string summarizing actual stage output."""
    if stage_id in extra_highlights and extra_highlights[stage_id]:
        return extra_highlights[stage_id]
    if status == "skipped":
        return skip_reason
    ptypes = {p.primitive_type for p in primitives}
    if PrimitiveType.CONFIRM_PLAN in ptypes:
        focus = (
            f" (focus: {', '.join(plan.approval.focus_areas[:2])})"
            if plan is not None and plan.approval is not None and plan.approval.focus_areas
            else ""
        )
        return f"Approved{focus}" if focus else "Plan approved"
    if PrimitiveType.WRITE_DRAWLIB_REPORT in ptypes:
        return "A4 Drawlib PDF report synthesis"
    parts = _analysis_stage_highlights(ptypes, bundle) if bundle is not None else []
    return "; ".join(parts) if parts else status


def _collect_tools_used(bundle: WorkflowFactsBundle | None, lang: str) -> list[str]:
    """Assemble deterministic list of analyzers and execution tools actually run."""
    if bundle is None:
        return []
    tools: list[str] = []
    if bundle.project_facts is not None:
        tools.append(f"project_inspect ({bundle.project_facts.language or lang or 'auto'})")
    if bundle.ast_facts is not None:
        ast_langs = [bundle.ast_facts.language, *sorted(bundle.companion_ast_facts.keys())]
        tools.append(f"tree-sitter AST ({', '.join(dict.fromkeys(x for x in ast_langs if x))})")
    elif bundle.companion_ast_facts:
        tools.append(f"tree-sitter Companion DSL ({', '.join(sorted(bundle.companion_ast_facts.keys()))})")
    if bundle.runtime_facts is not None and bundle.runtime_facts.status != "skipped":
        rf = bundle.runtime_facts
        eng = rf.container_engine or "container"
        tpl = rf.selected_dockerfile_template or "custom"
        tools.append(f"container runtime harness ({eng}: {tpl})")
    if bundle.security_facts is not None and bundle.security_facts.status != "skipped":
        sf = bundle.security_facts
        modes = [
            m
            for m, ok in (
                ("fs", sf.scanned_filesystem),
                ("image", sf.scanned_resolved_image),
            )
            if ok
        ]
        mode_lbl = "+".join(modes) if modes else "scan"
        tools.append(f"Trivy ({sf.container_engine or 'container'}: {mode_lbl})")
    if bundle.pentest_facts is not None and bundle.pentest_facts.status != "skipped":
        tools.append(f"web_pentest (httpx, {bundle.pentest_facts.probe_summary.total_probes} probes)")
    if bundle.migration_facts is not None:
        tools.append("migration_analyze (import DAG + boundary AST + codemods)")
    if bundle.progress_facts is not None:
        tools.append("progress_analyze (git merge-tree + LOC trajectory + task verifier)")
    return tools


def _build_audit_scope(
    run: WorkflowRunRecord,
    bundle: WorkflowFactsBundle | None,
    project_root: Path,
    artifact_manifest: dict[str, str],
) -> AuditScopeMetadata:
    """Construct AuditScopeMetadata with targets, languages, Git HEAD state, tools, and artifacts."""
    pf = bundle.project_facts if bundle is not None else None
    af = bundle.ast_facts if bundle is not None else None
    lang = (
        (pf.language if pf and pf.language else "")
        or (af.language if af and af.language else "")
        or (bundle.migration_facts.source_language if bundle and bundle.migration_facts else "")
    )
    companions = sorted(bundle.companion_ast_facts.keys()) if bundle is not None else []
    frameworks = list(pf.detected_frameworks) if pf is not None else []
    git_ok, branch, sha, is_dirty, _ = inspect_git_repo_head(project_root)

    return AuditScopeMetadata(
        target_root=run.targets.root,
        source_targets=list(run.targets.source),
        test_targets=list(run.targets.tests),
        doc_targets=list(run.targets.docs),
        exclude_globs=list(run.targets.exclude),
        language=lang,
        companion_languages=companions,
        detected_frameworks=frameworks,
        git_branch=branch if git_ok else "",
        git_sha=sha if git_ok else "",
        git_dirty=is_dirty if git_ok else False,
        tools_used=_collect_tools_used(bundle, lang),
        artifact_manifest=dict(artifact_manifest),
    )


def build_execution_dag_summary(
    run: WorkflowRunRecord,
    all_actions: list[ActionRunRecord],
    bundle: WorkflowFactsBundle | None,
    project_root: Path,
    *,
    plan: WorkflowExecutionPlan | None = None,
    artifact_manifest: dict[str, str] | None = None,
    current_action_id: str | None = None,
    stage_highlights: dict[str, str] | None = None,
) -> ExecutionDagSummary:
    """Collapse primitive action records into a logical action-level ExecutionDagSummary."""
    stage_order: list[str] = []
    stage_prims: dict[str, list[ActionRunRecord]] = {}
    action_to_stage: dict[str, str] = {}
    source_to_stage: dict[str, str] = {}

    for act in sorted(all_actions, key=lambda a: a.seq):
        sid = (act.step_key or act.action_id).strip() or act.action_id
        if sid not in stage_prims:
            stage_order.append(sid)
            stage_prims[sid] = []
        stage_prims[sid].append(act)
        action_to_stage[act.action_id] = sid
        if act.source_action:
            source_to_stage.setdefault(act.source_action, sid)

    has_any_explicit_needs = any(bool(act.needs) for act in all_actions)
    extra_hl = stage_highlights or {}
    nodes: list[ExecutionStageNode] = []

    for idx, sid in enumerate(stage_order):
        prims = stage_prims[sid]
        resolved_needs: list[str] = []
        for act in prims:
            for dep in act.needs:
                target_sid = dep if dep in stage_prims else action_to_stage.get(dep) or source_to_stage.get(dep)
                if target_sid and target_sid != sid and target_sid not in resolved_needs:
                    resolved_needs.append(target_sid)
        if not resolved_needs and not has_any_explicit_needs and idx > 0:
            resolved_needs.append(stage_order[idx - 1])

        status = _resolve_stage_status(prims, current_action_id)
        mode = _resolve_stage_mode(prims, status)
        skip_reason = _resolve_skip_reason(sid, prims, bundle, plan) if status == "skipped" else ""
        highlight = _stage_highlight(sid, prims, status, skip_reason, bundle, plan, extra_hl)
        rules_cnt = len({r for p in prims for r in p.rules if r.strip()})

        nodes.append(
            ExecutionStageNode(
                stage_id=sid,
                label=_stage_label(sid, prims),
                mode=mode,
                status=status,
                needs=resolved_needs,
                rules_count=rules_cnt,
                highlight=highlight,
                skip_reason=skip_reason,
            )
        )

    return ExecutionDagSummary(
        workflow_id=run.workflow_id,
        category=run.category.value,
        scope=run.scope,
        nodes=nodes,
        audit_scope=_build_audit_scope(run, bundle, project_root, artifact_manifest or {}),
    )


def build_rollup_execution_dag_summary(
    run: WorkflowRunRecord,
    all_actions: list[ActionRunRecord],
    rollup_facts: RollupFacts,
    project_root: Path,
    *,
    artifact_manifest: dict[str, str] | None = None,
) -> ExecutionDagSummary:
    """Build a multi-component Rollup ExecutionDagSummary connecting sub-audits into synthesis."""
    nodes: list[ExecutionStageNode] = []
    has_confirm = any(a.primitive_type == PrimitiveType.CONFIRM_PLAN for a in all_actions)
    if has_confirm:
        nodes.append(
            ExecutionStageNode(
                stage_id="confirm_plan",
                label="Confirm Rollup Plan & Components",
                mode="ASK",
                status="completed",
                needs=[],
                highlight=f"{len(rollup_facts.components)} component sub-audits aligned",
            )
        )

    comp_stage_ids: list[str] = []
    for comp in rollup_facts.components:
        cid = f"comp_{comp.component_id}"
        comp_stage_ids.append(cid)
        nodes.append(
            ExecutionStageNode(
                stage_id=cid,
                label=f"{comp.component_id} ({comp.language})",
                mode="HYBRID",
                status="completed",
                needs=["confirm_plan"] if has_confirm else [],
                highlight=(
                    f"{comp.overall_score}/100 ({comp.grade}), {comp.total_loc:,} LOC, "
                    f"weight={comp.weight:.2f}, crit/high={comp.critical_or_high_count}"
                ),
            )
        )

    if rollup_facts.companion_ast_facts:
        comp_langs = ", ".join(sorted(rollup_facts.companion_ast_facts.keys()))
        comp_stage_ids.append("companion_dsl_scan")
        nodes.append(
            ExecutionStageNode(
                stage_id="companion_dsl_scan",
                label="Repo Governance & Companion DSLs",
                mode="AUTO",
                status="completed",
                needs=["confirm_plan"] if has_confirm else [],
                highlight=f"tree-sitter ({comp_langs})",
            )
        )

    guard_cnt = len(rollup_facts.weakest_link_notes)
    nodes.append(
        ExecutionStageNode(
            stage_id="synthesize_rollup",
            label="Hybrid Weighted Rollup Synthesis",
            mode="HYBRID",
            status="completed",
            needs=comp_stage_ids,
            highlight=(
                f"overall={rollup_facts.weighted_overall_score}/100, "
                f"log1p(LOC) weights, guardrails={guard_cnt}"
            ),
        )
    )
    nodes.append(
        ExecutionStageNode(
            stage_id="write_drawlib_report",
            label="Unified Drawlib PDF Report",
            mode="AI",
            status="pending",
            needs=["synthesize_rollup"],
            highlight="Unified 6-chapter polyglot PDF report",
        )
    )

    git_ok, branch, sha, is_dirty, _ = inspect_git_repo_head(project_root)
    langs = sorted({c.language for c in rollup_facts.components})
    companions = sorted(rollup_facts.companion_ast_facts.keys())
    tools = [
        f"multi-audit rollup (log1p LOC + guardrails across {len(rollup_facts.components)} components)",
        "project_inspect (root governance)",
    ]
    if companions:
        tools.append(f"tree-sitter Companion DSL ({', '.join(companions)})")

    scope_meta = AuditScopeMetadata(
        target_root=".",
        source_targets=[c.root for c in rollup_facts.components],
        test_targets=[],
        doc_targets=list(run.targets.docs),
        exclude_globs=list(run.targets.exclude),
        language="+".join(langs) if langs else "multi",
        companion_languages=companions,
        detected_frameworks=list(rollup_facts.root_project_facts.detected_frameworks)
        if rollup_facts.root_project_facts
        else [],
        git_branch=branch if git_ok else "",
        git_sha=sha if git_ok else "",
        git_dirty=is_dirty if git_ok else False,
        tools_used=tools,
        artifact_manifest=dict(artifact_manifest or {}),
    )
    return ExecutionDagSummary(
        workflow_id=run.workflow_id,
        category=run.category.value,
        scope=run.scope,
        nodes=nodes,
        audit_scope=scope_meta,
    )
