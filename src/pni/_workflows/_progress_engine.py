# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Progress action execution, Markdown rendering, baseline immutability check, and persistence."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from pni._actions import (
    ParamValue,
    PrimitiveStep,
    PrimitiveType,
    ProgressFacts,
    ProgressOptions,
    ProgressPreflightHint,
    ProgressResult,
    load_and_validate_progress_plan,
    record_progress_history_from_result,
    resolve_progress_result_rel_path,
    run_progress_analyze,
)
from pni._cache import default_progress_facts_rel_path
from pni._reporter import DEFAULT_REPORT_OUTPUT_DIR
from pni._workflows.base_model import (
    ActionRunRecord,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowFactsBundle,
    WorkflowRunRecord,
)


def parse_progress_options(params: dict[str, ParamValue]) -> ProgressOptions:
    """Construct validated ProgressOptions from workflow action parameters."""
    known = set(ProgressOptions.model_fields.keys())
    filtered = {k: v for k, v in params.items() if k in known}
    return ProgressOptions.model_validate(filtered)


def inspect_progress_plan_prerequisite(
    workflow_def: WorkflowDefinition,
    primitives: list[PrimitiveStep],
    project_root: Path,
) -> tuple[str | None, list[ProgressPreflightHint], str | None]:
    """Validate `.pni/progress/<target>.yaml` before starting a progress workflow.

    Returns:
        tuple[str | None, list[ProgressPreflightHint], str | None]:
            `(resolved_plan_rel_path, preflight_hints, actionable_error_message)`.
    """
    prog_steps = [p for p in primitives if p.type == PrimitiveType.PROGRESS_ANALYZE]
    if workflow_def.category != WorkflowCategory.PROGRESS and not prog_steps:
        return None, [], None

    plan_arg = ""
    if prog_steps:
        p0 = prog_steps[0].params
        raw_pf = p0.get("plan_file")
        raw_tgt = p0.get("target")
        if isinstance(raw_pf, str) and raw_pf.strip():
            plan_arg = raw_pf.strip()
        elif isinstance(raw_tgt, str) and raw_tgt.strip():
            plan_arg = raw_tgt.strip()
    if not plan_arg:
        plan_arg = workflow_def.id

    try:
        _, plan_rel, _, hints = load_and_validate_progress_plan(
            project_root,
            plan_arg,
            fallback_id=workflow_def.id,
        )
    except Exception as exc:
        return None, [], str(exc)

    return plan_rel, hints, None


def execute_progress_analyze_json(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    workspace_root: Path,
) -> str:
    """Execute deterministic `progress_analyze` and return serialized `ProgressFacts` JSON."""
    opts = parse_progress_options(action.params)
    if not opts.base_audit_workflow and run.based_on:
        opts = opts.model_copy(update={"base_audit_workflow": run.based_on})
    pf = run_progress_analyze(
        workspace_root,
        run.workflow_id,
        target_root=run.targets.root,
        source_targets=run.targets.source,
        test_targets=run.targets.tests,
        doc_targets=run.targets.docs,
        options=opts,
    )
    return pf.model_dump_json(indent=2)


def _render_git_and_conflict_section(pf: ProgressFacts) -> list[str]:
    """Render Git methodology, working-tree conflicts, branch merge-tree status, and overlaps."""
    gp = pf.plan.git_policy
    lines: list[str] = [
        (
            f"- **Git Governance Policy**: methodology=`{gp.methodology}`, "
            f"trunk=`{pf.resolved_base_branch}`, merge_strategy=`{gp.merge_strategy}`, "
            f"forbid_foxtrot=`{gp.forbid_foxtrot_merges}`, convention=`{gp.commit_convention}` "
            f"(ratio=`{pf.conventional_commit_ratio:.0%}`)"
        ),
        (
            f"- **Repository State**: git_available=`{pf.git_available}`, branch=`{pf.current_branch or '-'}`, "
            f"head=`{pf.head_sha[:8] if pf.head_sha else '-'}`, dirty=`{pf.git_dirty}`, "
            f"trunk_merges=`{pf.trunk_merge_commits_count}`, foxtrot_merges=`{pf.foxtrot_merges_count}`, "
            f"wip_on_trunk=`{pf.wip_commits_on_trunk}`"
        ),
    ]
    wt = pf.working_tree_conflicts
    if wt.unmerged_index_files or wt.in_progress_operations or wt.committed_conflict_markers:
        lines.append(
            f"- **Working-Tree / Committed Conflicts**: unmerged_index={wt.unmerged_index_files}, "
            f"ops_in_progress={wt.in_progress_operations}, committed_markers={wt.committed_conflict_markers}"
        )
    if pf.branches:
        unmerged = [b for b in pf.branches if not b.is_merged]
        conflicts = [b for b in unmerged if b.has_conflict]
        stale = [b for b in unmerged if b.is_stale]
        lines.append(
            f"- **Tracked Branches ({len(pf.branches)} total, {len(unmerged)} unmerged, "
            f"{len(conflicts)} conflicting, {len(stale)} stale)**:"
        )
        for br in pf.branches[:20]:
            c_lbl = f" CONFLICT={br.conflicting_files}" if br.has_conflict else ""
            s_lbl = " [STALE]" if br.is_stale else ""
            m_lbl = " [MERGED]" if br.is_merged else ""
            lines.append(
                f"  - `{br.branch_name}`{m_lbl}{s_lbl}: ahead=`+{br.ahead_commits}` / "
                f"behind=`-{br.behind_commits}`, lines=`{br.changed_lines}`, age=`{br.age_days}d`{c_lbl}"
            )
    if pf.overlapping_file_hotspots:
        lines.append(f"- **Cross-Branch Overlapping Files ({len(pf.overlapping_file_hotspots)})**:")
        for ov in pf.overlapping_file_hotspots[:12]:
            lines.append(f"  - `{ov.file_path}` touched by branches: {ov.branches}")
    if pf.policy_violations:
        lines.append(f"- **Git Policy Violations ({len(pf.policy_violations)})**:")
        for v in pf.policy_violations[:15]:
            lines.append(f"  - `[{v.severity.upper()}]` `{v.code}` (`{v.branch_or_sha}`): {v.detail}")
    return lines


def _render_trajectory_and_tasks_section(pf: ProgressFacts) -> list[str]:
    """Render weekly LOC/test trajectory, churn hotspots, task evidence, and linked audit history."""
    lines: list[str] = []
    if pf.trajectory:
        lines.append(f"- **Historical Velocity & LOC/Test Trajectory ({len(pf.trajectory)} periods)**:")
        for pt in pf.trajectory[-8:]:
            lines.append(
                f"  - `{pt.period_label}` (`{pt.period_end_date}`): commits=`{pt.commits_count}`, "
                f"`+{pt.lines_added}/-{pt.lines_deleted}`, src_loc=`{pt.source_loc}`, "
                f"test_loc=`{pt.test_loc}` (ratio=`{pt.test_to_code_ratio:.2f}`), "
                f"static_tests=`{pt.static_test_cases}`"
            )
    if pf.churn_hotspots:
        lines.append(f"- **Rework / Churn Hotspots ({len(pf.churn_hotspots)})**:")
        for ch in pf.churn_hotspots[:10]:
            lines.append(
                f"  - `{ch.file_path}`: commits=`{ch.commits_count}`, "
                f"`+{ch.lines_added}/-{ch.lines_deleted}` (rework=`{ch.rework_ratio:.2f}`)"
            )
    if pf.task_evidence:
        lines.append(f"- **Planned Task Deterministic Evidence ({len(pf.task_evidence)})**:")
        for ev in pf.task_evidence:
            lines.append(
                f"  - `{ev.task_id}` ({ev.milestone_id} - {ev.name}, `{ev.planned_start}..{ev.planned_end}`): "
                f"declared=`{ev.declared_status}` (`{ev.declared_progress}%`), state=`{ev.schedule_state}` "
                f"(delta=`{ev.days_delta}d`), branches={ev.matched_branches}, "
                f"conflict=`{ev.branch_has_conflict}`, missing_paths={ev.missing_paths}, "
                f"recent_commits=`{ev.recent_commits_count}`, stubs=`{ev.stub_todo_count}`, tests=`{ev.has_tests}`"
            )
    if pf.audit_summary is not None:
        aus = pf.audit_summary
        delta_s = f" (delta `{aus.score_delta:+d}`)" if aus.score_delta is not None else ""
        lines.append(
            f"- **Linked Audit Summary (`{aus.base_workflow_id}`)**: "
            f"latest=`{aus.latest_score if aus.latest_score is not None else 'N/A'}` "
            f"(`{aus.latest_grade or '-'}`){delta_s}, critical=`{aus.critical_findings}`, "
            f"high=`{aus.high_findings}`, ledger_entries=`{len(aus.history_points)}`"
        )
    if pf.progress_history:
        last_p = pf.progress_history[-1]
        lines.append(
            f"- **Prior Progress Ledger (`{len(pf.progress_history)}` entries)**: "
            f"latest=`{last_p.delivery_status}` (score=`{last_p.overall_health_score}`, "
            f"verified=`{last_p.verified_completion_pct}%` at `{last_p.git_sha[:8]}`)"
        )
    return lines


def render_progress_facts(pf: ProgressFacts) -> list[str]:
    """Render deterministic `ProgressFacts` into concise Markdown instructions for AI steps."""
    lines = [
        f"\n### Deterministic Project Progress & Git Governance Facts (`progress_analyze`, as_of=`{pf.as_of_date}`)",
        (
            f"- **Baseline Plan**: `{pf.plan_file}` (`{pf.project_name}`, "
            f"`{pf.plan.start_date}..{pf.plan.target_date}`, sha256=`{pf.plan_sha256[:12]}...`, READ-ONLY)"
        ),
    ]
    if pf.preflight_hints:
        lines.append(f"- **Preflight Advisories ({len(pf.preflight_hints)})**:")
        for h in pf.preflight_hints:
            lines.append(f"  - `[{h.code}]` {h.message}")
    lines.extend(_render_git_and_conflict_section(pf))
    lines.extend(_render_trajectory_and_tasks_section(pf))
    return lines


def _verify_safe_relative_paths(paths: list[str], field_name: str) -> None:
    """Reject absolute paths or '..' parent traversal in emitted progress references."""
    invalid = [
        p
        for p in paths
        if p.strip().startswith("/") or ".." in [seg for seg in p.replace("\\", "/").split("/") if seg]
    ]
    if invalid:
        msg = f"Invalid non-relative path(s) in '{field_name}': {invalid}."
        raise ValueError(msg)


def _verify_baseline_plan_unchanged(pf: ProgressFacts, project_root: Path) -> None:
    """Enforce PRG-02: reject `emit_progress` if `.pni/progress/<target>.yaml` was mutated mid-run."""
    root_res = project_root.resolve()
    plan_file = (root_res / pf.plan_file).resolve()
    if not plan_file.is_relative_to(root_res) or not plan_file.is_file():
        msg = f"Baseline progress plan '{pf.plan_file}' is missing or outside workspace root."
        raise ValueError(msg)
    current_sha = hashlib.sha256(plan_file.read_bytes()).hexdigest()
    if current_sha != pf.plan_sha256:
        msg = (
            f"Baseline progress plan '{pf.plan_file}' was modified during workflow execution "
            f"(expected sha256={pf.plan_sha256[:12]}..., found {current_sha[:12]}...). "
            "Progress plan files are strictly read-only during measurement runs."
        )
        raise ValueError(msg)


def validate_and_persist_progress_result(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    bundle: WorkflowFactsBundle,
    raw_input: str,
    project_root: Path,
) -> str:
    """Validate `ProgressResult`, enforce plan immutability, persist JSON, and update JSONL history."""
    prog_obj = ProgressResult.model_validate_json(raw_input)
    pf = bundle.progress_facts

    if pf is not None:
        _verify_baseline_plan_unchanged(pf, project_root)
        known_task_ids = {t.id for t in pf.plan.tasks}
        unknown_ids = [ta.task_id for ta in prog_obj.task_assessments if ta.task_id not in known_task_ids]
        if unknown_ids:
            msg = (
                f"Unknown task_id(s) in 'task_assessments': {unknown_ids} "
                f"(expected subset of {sorted(known_task_ids)})."
            )
            raise ValueError(msg)

    action_files = [f for item in prog_obj.next_actions for f in item.target_files if f.strip()]
    conflict_files = [f for br in prog_obj.branch_assessments for f in br.conflicting_files if f.strip()]
    if action_files:
        _verify_safe_relative_paths(action_files, "next_actions[].target_files")
    if conflict_files:
        _verify_safe_relative_paths(conflict_files, "branch_assessments[].conflicting_files")

    prog_obj.workflow_id = run.workflow_id
    prog_obj.workflow_run_id = run.run_id
    if not prog_obj.generated_at:
        prog_obj.generated_at = datetime.now(timezone.utc).isoformat()
    prog_obj.target_root = run.targets.root
    prog_obj.progress_facts_file = default_progress_facts_rel_path(run.workflow_id)
    if pf is not None:
        prog_obj.as_of_date = pf.as_of_date
        prog_obj.plan_file = pf.plan_file
        prog_obj.plan_sha256 = pf.plan_sha256
        prog_obj.progress_facts = pf

    out_dir = str(action.params.get("output_dir", DEFAULT_REPORT_OUTPUT_DIR))
    tgt = str(action.params.get("target") or run.workflow_id)
    prog_rel = resolve_progress_result_rel_path(out_dir, tgt, str(action.params.get("progress_path", "")))
    root_res = project_root.resolve()
    prog_file = (root_res / prog_rel).resolve()
    if prog_file == root_res or not prog_file.is_relative_to(root_res):
        msg = f"Resolved progress output path escapes workspace root: {prog_rel!r}"
        raise ValueError(msg)

    prog_file.parent.mkdir(parents=True, exist_ok=True)
    canonical = prog_obj.model_dump_json(indent=2)
    prog_file.write_text(canonical + "\n", encoding="utf-8")

    record_progress_history_from_result(project_root, run.workflow_id, prog_obj)
    return canonical
