# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Structured SQLite workflow run progress summaries and step payload inspection helpers."""

from __future__ import annotations

import contextlib
import json
from typing import Optional

from pydantic import BaseModel, Field

from pni._actions import PrimitiveType
from pni._workflows.base_model import (
    ActionRunRecord,
    RunStatus,
    WorkflowCategory,
    WorkflowRunRecord,
)
from pni._workflows.state_db import WorkflowStateDB


class WorkflowRunSummary(BaseModel):
    """Progress and active-step summary for a recorded workflow run."""

    run_id: str
    workflow_id: str
    workflow_name: str
    category: WorkflowCategory
    based_on: Optional[str] = None
    based_on_run_id: Optional[str] = None
    status: RunStatus
    completed_actions: int
    total_actions: int
    progress_label: str
    current_action_id: Optional[str] = None
    current_primitive: Optional[str] = None
    current_source_action: Optional[str] = None
    current_step_label: str = "-"
    created_at: str
    updated_at: str


class ActionStepSummary(BaseModel):
    """Step-level execution status and brief diagnostic summary for a workflow run."""

    action_id: str
    seq: int
    primitive_type: PrimitiveType
    name: str
    source_action: Optional[str] = None
    status: RunStatus
    has_deterministic_output: bool = False
    has_agent_input: bool = False
    brief_note: str = ""
    updated_at: str = ""


class WorkflowRunDetail(BaseModel):
    """Detailed progress view combining run summary and ordered action step summaries."""

    run: WorkflowRunSummary
    actions: list[ActionStepSummary] = Field(default_factory=list)


class InspectedActionItem(BaseModel):
    """Extracted metadata and JSON payloads for a single inspected workflow action step."""

    run_id: str
    workflow_id: str
    action_id: str
    seq: int
    primitive_type: PrimitiveType
    name: str
    source_action: Optional[str] = None
    status: RunStatus
    updated_at: str
    deterministic_output_json: Optional[str] = None
    agent_input_json: Optional[str] = None


def _short_source_action(source_action: str | None) -> str:
    """Return the leaf identifier of a composite source_action (e.g. 'common/x' -> 'x')."""
    if not source_action:
        return ""
    return source_action.rsplit("/", maxsplit=1)[-1]


def _extract_agent_brief_note(ptype: PrimitiveType, data: dict[str, object]) -> str:
    """Format a brief CLI summary string from a validated agent_input_json dictionary."""
    if ptype == PrimitiveType.AI_INTERPRET:
        score = data.get("step_score")
        findings = data.get("findings")
        f_cnt = len(findings) if isinstance(findings, list) else 0
        score_part = f"score={score}" if score is not None else "score=auto"
        return f"{score_part}, findings={f_cnt}"
    if ptype == PrimitiveType.EMIT_SCORE:
        ov = data.get("overall_score")
        gr = data.get("grade")
        return f"overall={ov}/100 ({gr or '-'})" if ov is not None else ""
    if ptype == PrimitiveType.EMIT_MIGRATION_PLAN:
        mode = data.get("migration_mode", "-")
        prs = data.get("pr_wbs") or data.get("pr_breakdown")
        pr_cnt = len(prs) if isinstance(prs, list) else 0
        return f"mode={mode}, prs={pr_cnt}"
    if ptype == PrimitiveType.EMIT_PROGRESS:
        ds = data.get("delivery_status", "-")
        hs = data.get("overall_health_score")
        return f"status={ds}, score={hs}/100" if hs is not None else f"status={ds}"
    if ptype == PrimitiveType.WRITE_DRAWLIB_REPORT:
        pdf = data.get("pdf_path", "")
        return f"pdf={pdf}" if pdf else "report completed"
    return ""


def _extract_deterministic_brief_note(ptype: PrimitiveType, det: dict[str, object]) -> str:
    """Format a brief CLI summary string from a deterministic_output_json dictionary."""
    if ptype == PrimitiveType.PROGRESS_ANALYZE:
        brs = det.get("branches")
        viols = det.get("policy_violations")
        b_cnt = len(brs) if isinstance(brs, list) else 0
        v_cnt = len(viols) if isinstance(viols, list) else 0
        return f"branches={b_cnt}, violations={v_cnt}"
    st = det.get("status")
    if ptype == PrimitiveType.WEB_PENTEST:
        findings = det.get("findings")
        f_cnt = len(findings) if isinstance(findings, list) else 0
        return f"status={st}, findings={f_cnt}"
    return f"status={st}" if st is not None else ""


def _extract_brief_note(act: ActionRunRecord) -> str:
    """Summarize key metrics from deterministic_output_json or agent_input_json for CLI display."""
    if act.agent_input_json:
        with contextlib.suppress(Exception):
            data = json.loads(act.agent_input_json)
            if isinstance(data, dict):
                note = _extract_agent_brief_note(act.primitive_type, data)
                if note:
                    return note

    if act.deterministic_output_json:
        with contextlib.suppress(Exception):
            det = json.loads(act.deterministic_output_json)
            if isinstance(det, dict):
                return _extract_deterministic_brief_note(act.primitive_type, det)
    return ""


def build_workflow_run_summary(
    run: WorkflowRunRecord,
    actions: list[ActionRunRecord],
) -> WorkflowRunSummary:
    """Construct a WorkflowRunSummary from a run record and its ordered action records."""
    total = len(actions)
    done = sum(1 for a in actions if a.status == RunStatus.COMPLETED)
    progress_lbl = f"{done}/{total}"

    cur_act: ActionRunRecord | None = None
    if run.status == RunStatus.IN_PROGRESS:
        cur_act = next(
            (a for a in actions if a.status in {RunStatus.IN_PROGRESS, RunStatus.PENDING}),
            None,
        )

    cur_id = cur_act.action_id if cur_act is not None else None
    cur_prim = cur_act.primitive_type.value if cur_act is not None else None
    cur_src = _short_source_action(cur_act.source_action) if cur_act is not None else None
    if cur_act is not None:
        src_suffix = f" ({cur_src})" if cur_src and cur_src != cur_prim else ""
        cur_lbl = f"{cur_act.action_id}: {cur_prim}{src_suffix}"
    else:
        cur_lbl = "-"

    return WorkflowRunSummary(
        run_id=run.run_id,
        workflow_id=run.workflow_id,
        workflow_name=run.workflow_name,
        category=run.category,
        based_on=run.based_on,
        based_on_run_id=run.based_on_run_id,
        status=run.status,
        completed_actions=done,
        total_actions=total,
        progress_label=progress_lbl,
        current_action_id=cur_id,
        current_primitive=cur_prim,
        current_source_action=cur_src or None,
        current_step_label=cur_lbl,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def query_workflow_run_summaries(
    db: WorkflowStateDB,
    *,
    workflow_id: Optional[str] = None,
    status_filter: Optional[RunStatus] = None,
    latest_per_workflow: bool = False,
    limit: Optional[int] = None,
) -> list[WorkflowRunSummary]:
    """Query, filter, and summarize workflow runs from SQLite in a single batched pass.

    Args:
        db: Initialized WorkflowStateDB instance.
        workflow_id: Optional workflow_id filter.
        status_filter: Optional RunStatus filter.
        latest_per_workflow: When True, keep only the most recent matching run per workflow_id.
        limit: Optional maximum number of summaries to return (<=0 means unlimited).

    Returns:
        list[WorkflowRunSummary]: Filtered run summaries ordered newest first.
    """
    runs = db.list_runs()
    if workflow_id:
        clean_wf = workflow_id.strip().removesuffix(".yaml")
        runs = [r for r in runs if r.workflow_id == clean_wf]
    if status_filter is not None:
        runs = [r for r in runs if r.status == status_filter]
    if latest_per_workflow:
        non_cancelled_wfs = {r.workflow_id for r in runs if r.status != RunStatus.CANCELLED}
        seen_wfs: set[str] = set()
        deduped: list[WorkflowRunRecord] = []
        for r in runs:
            if r.workflow_id in seen_wfs:
                continue
            if (
                status_filter != RunStatus.CANCELLED
                and r.status == RunStatus.CANCELLED
                and r.workflow_id in non_cancelled_wfs
            ):
                continue
            seen_wfs.add(r.workflow_id)
            deduped.append(r)
        runs = deduped
    if limit is not None and limit > 0:
        runs = runs[:limit]

    actions_map = db.get_actions_map([r.run_id for r in runs])
    return [build_workflow_run_summary(r, actions_map.get(r.run_id, [])) for r in runs]


def resolve_run_by_id_or_workflow(
    db: WorkflowStateDB,
    run_or_workflow: str,
    *,
    prefer_completed: bool = False,
) -> WorkflowRunRecord | None:
    """Resolve either an explicit 'wf-xxxxxxxx' run_id or a workflow_id to a WorkflowRunRecord.

    Args:
        db: Initialized WorkflowStateDB instance.
        run_or_workflow: Run identifier ('wf-...') or workflow identifier ('php_legacy_shop_messy').
        prefer_completed: When resolving by workflow_id, prefer the latest completed run if one exists.

    Returns:
        WorkflowRunRecord | None: Matching run record or None if not found.
    """
    target = run_or_workflow.strip()
    direct = db.get_run(target)
    if direct is not None:
        return direct

    clean_wf = target.removesuffix(".yaml")
    if prefer_completed:
        completed = db.get_latest_completed_run(clean_wf)
        if completed is not None:
            return completed

    wf_runs = [r for r in db.list_runs() if r.workflow_id == clean_wf]
    active_or_done = [r for r in wf_runs if r.status != RunStatus.CANCELLED]
    chosen = active_or_done or wf_runs
    return chosen[0] if chosen else None


def build_workflow_run_detail(
    db: WorkflowStateDB,
    run: WorkflowRunRecord,
) -> WorkflowRunDetail:
    """Build detailed action-by-action progress and diagnostic summaries for a single workflow run."""
    actions = db.get_actions(run.run_id)
    summary = build_workflow_run_summary(run, actions)
    step_summaries = [
        ActionStepSummary(
            action_id=a.action_id,
            seq=a.seq,
            primitive_type=a.primitive_type,
            name=a.name,
            source_action=_short_source_action(a.source_action) or None,
            status=a.status,
            has_deterministic_output=a.deterministic_output_json is not None,
            has_agent_input=a.agent_input_json is not None,
            brief_note=_extract_brief_note(a),
            updated_at=a.updated_at,
        )
        for a in actions
    ]
    return WorkflowRunDetail(run=summary, actions=step_summaries)


def _available_run_selectors_hint(actions: list[ActionRunRecord]) -> str:
    """Build a diagnostic hint listing valid action IDs, source actions, and primitives in a run."""
    act_ids = [a.action_id for a in actions]
    src_ids = list(dict.fromkeys(_short_source_action(a.source_action) for a in actions if a.source_action))
    prims = list(dict.fromkeys(a.primitive_type.value for a in actions))
    return f"Available action IDs: {act_ids}; source actions: {src_ids}; primitives: {prims}"


def resolve_run_actions_by_selector(
    actions: list[ActionRunRecord],
    selector: str,
    *,
    prefer_agent_input: bool = False,
    prefer_deterministic: bool = False,
) -> list[ActionRunRecord]:
    """Match one or more recorded ActionRunRecords by action_id, index, source_action, name, or primitive.

    Args:
        actions: Ordered action records belonging to a workflow run.
        selector: User-supplied selector ('act-16', '16', 'web_penetration_audit', 'emit_score', etc.).
        prefer_agent_input: Narrow multi-step composite matches to steps carrying agent_input_json.
        prefer_deterministic: Narrow multi-step composite matches to steps carrying deterministic_output_json.

    Returns:
        list[ActionRunRecord]: Non-empty list of matched action records.

    Raises:
        ValueError: If selector matches zero recorded actions.
    """
    needle = selector.strip()
    if not needle:
        msg = f"Empty action selector. {_available_run_selectors_hint(actions)}"
        raise ValueError(msg)

    raw_num = needle.removeprefix("act-") if needle.startswith("act-") else needle
    if raw_num.isdigit():
        seq_num = int(raw_num)
        by_seq = [a for a in actions if a.seq == seq_num]
        if by_seq:
            return by_seq

    exact_id = [a for a in actions if a.action_id == needle]
    if exact_id:
        return exact_id

    by_source = [
        a
        for a in actions
        if needle in {a.source_action, _short_source_action(a.source_action)}
    ]
    matched = by_source or [
        a for a in actions if needle in {a.primitive_type.value, a.name, a.name.split(" (", maxsplit=1)[0]}
    ]
    if not matched:
        msg = f"Action selector '{needle}' did not match any step in run. {_available_run_selectors_hint(actions)}"
        raise ValueError(msg)

    if len(matched) > 1 and prefer_agent_input:
        non_ack = [
            a
            for a in matched
            if a.agent_input_json is not None
            and a.primitive_type
            in {
                PrimitiveType.AI_INTERPRET,
                PrimitiveType.RECORD_ARCHITECTURE,
                PrimitiveType.EMIT_SCORE,
                PrimitiveType.EMIT_MIGRATION_PLAN,
                PrimitiveType.EMIT_PROGRESS,
                PrimitiveType.WRITE_DRAWLIB_REPORT,
            }
        ]
        if non_ack:
            return non_ack

    if len(matched) > 1 and prefer_deterministic:
        det_only = [a for a in matched if a.deterministic_output_json is not None]
        if det_only:
            return det_only

    return matched


def inspect_workflow_run_actions(
    db: WorkflowStateDB,
    run: WorkflowRunRecord,
    selector: str,
    *,
    prefer_agent_input: bool = False,
    prefer_deterministic: bool = False,
) -> list[InspectedActionItem]:
    """Extract matched action records and stored JSON payloads for `pni workflows inspect-action`."""
    all_actions = db.get_actions(run.run_id)
    matched = resolve_run_actions_by_selector(
        all_actions,
        selector,
        prefer_agent_input=prefer_agent_input,
        prefer_deterministic=prefer_deterministic,
    )
    return [
        InspectedActionItem(
            run_id=run.run_id,
            workflow_id=run.workflow_id,
            action_id=a.action_id,
            seq=a.seq,
            primitive_type=a.primitive_type,
            name=a.name,
            source_action=_short_source_action(a.source_action) or None,
            status=a.status,
            updated_at=a.updated_at,
            deterministic_output_json=a.deterministic_output_json,
            agent_input_json=a.agent_input_json,
        )
        for a in matched
    ]
