# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""SQLite state persistence (.pni/cache/workflow_state.db) for Workflow v2 DAG execution."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pni._actions import PrimitiveStep, PrimitiveType
from pni._cache import DEFAULT_STATE_DB_REL_PATH, ensure_cache_dir
from pni._workflows.base_model import (
    ActionRunRecord,
    ReportMode,
    RollupComponentSpec,
    RunStatus,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowOutputs,
    WorkflowRunRecord,
    WorkflowScope,
    WorkflowTargets,
)

_TERMINAL_READY_DEP_STATUSES = {RunStatus.COMPLETED, RunStatus.SKIPPED}


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _load_json_list(raw: object) -> list[str]:
    """Safely deserialize a JSON array column into list[str]."""
    if not raw:
        return []
    parsed = json.loads(str(raw))
    return [str(x) for x in parsed] if isinstance(parsed, list) else []


def _row_to_workflow_run(row: sqlite3.Row) -> WorkflowRunRecord:
    """Deserialize a sqlite3.Row into a WorkflowRunRecord."""
    keys = set(row.keys())
    raw_cat = str(row["category"]) if "category" in keys and row["category"] else "audit"
    raw_scope = str(row["scope"]) if "scope" in keys and row["scope"] else "repo"
    scope: WorkflowScope = "component" if raw_scope == "component" else "repo"
    raw_rmode = str(row["report_mode"]) if "report_mode" in keys and row["report_mode"] else "unified"
    report_mode: ReportMode = (
        "per_component" if raw_rmode == "per_component" else "both" if raw_rmode == "both" else "unified"
    )
    raw_inc = json.loads(str(row["includes_json"])) if "includes_json" in keys and row["includes_json"] else []
    includes = [RollupComponentSpec.model_validate(item) for item in raw_inc] if isinstance(raw_inc, list) else []

    return WorkflowRunRecord(
        run_id=str(row["run_id"]),
        workflow_id=str(row["workflow_id"]),
        category=WorkflowCategory(raw_cat),
        scope=scope,
        plan_gate=bool(row["plan_gate"]) if "plan_gate" in keys and row["plan_gate"] is not None else True,
        report_mode=report_mode,
        based_on=str(row["based_on"]) if "based_on" in keys and row["based_on"] is not None else None,
        based_on_run_id=(
            str(row["based_on_run_id"])
            if "based_on_run_id" in keys and row["based_on_run_id"] is not None
            else None
        ),
        includes=includes,
        workflow_name=str(row["workflow_name"]),
        description=str(row["description"]),
        status=RunStatus(str(row["status"])),
        targets=WorkflowTargets.model_validate_json(str(row["targets_json"])),
        outputs=WorkflowOutputs.model_validate_json(str(row["outputs_json"])),
        plan_json=str(row["plan_json"]) if "plan_json" in keys and row["plan_json"] is not None else None,
        plan_approved=bool(row["plan_approved"]) if "plan_approved" in keys and row["plan_approved"] else False,
        auto_approved=bool(row["auto_approved"]) if "auto_approved" in keys and row["auto_approved"] else False,
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _row_to_action_run(row: sqlite3.Row) -> ActionRunRecord:
    """Deserialize a sqlite3.Row into an ActionRunRecord."""
    keys = set(row.keys())
    raw_params = json.loads(str(row["params_json"]))
    return ActionRunRecord(
        run_id=str(row["run_id"]),
        action_id=str(row["action_id"]),
        seq=int(row["seq"]),
        step_key=str(row["step_key"]) if "step_key" in keys and row["step_key"] else "",
        primitive_type=PrimitiveType(str(row["primitive_type"])),
        name=str(row["name"]),
        source_action=str(row["source_action"]) if row["source_action"] is not None else None,
        needs=_load_json_list(row["needs_json"]) if "needs_json" in keys else [],
        when=str(row["when_expr"]) if "when_expr" in keys and row["when_expr"] is not None else None,
        fact_views=_load_json_list(row["fact_views_json"]) if "fact_views_json" in keys else [],
        rules=_load_json_list(row["rules_json"]),
        params=raw_params if isinstance(raw_params, dict) else {},
        prompt=str(row["prompt"]),
        status=RunStatus(str(row["status"])),
        skip_reason=str(row["skip_reason"]) if "skip_reason" in keys and row["skip_reason"] is not None else None,
        deterministic_output_json=(
            str(row["deterministic_output_json"]) if row["deterministic_output_json"] is not None else None
        ),
        agent_input_json=str(row["agent_input_json"]) if row["agent_input_json"] is not None else None,
        updated_at=str(row["updated_at"]),
    )


def _ensure_columns(conn: sqlite3.Connection, table: str, column_defs: dict[str, str]) -> None:
    """Apply additive ALTER TABLE ADD COLUMN migrations for missing columns."""
    existing = {str(r["name"]) for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}  # noqa: S608
    for col, sql_type in column_defs.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {sql_type}")  # noqa: S608


class WorkflowStateDB:
    """Encapsulates SQLite state storage in .pni/cache/workflow_state.db."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the database connection path and ensure schema exists."""
        ensure_cache_dir(project_root)
        self.db_path = project_root / DEFAULT_STATE_DB_REL_PATH
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite connection configured with sqlite3.Row factory."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Create workflow_runs and action_runs tables and apply Workflow v2 column migrations."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'audit',
                    scope TEXT NOT NULL DEFAULT 'repo',
                    plan_gate INTEGER NOT NULL DEFAULT 1,
                    report_mode TEXT NOT NULL DEFAULT 'unified',
                    based_on TEXT,
                    based_on_run_id TEXT,
                    includes_json TEXT NOT NULL DEFAULT '[]',
                    workflow_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    targets_json TEXT NOT NULL,
                    outputs_json TEXT NOT NULL,
                    plan_json TEXT,
                    plan_approved INTEGER NOT NULL DEFAULT 0,
                    auto_approved INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            _ensure_columns(
                conn,
                "workflow_runs",
                {
                    "category": "TEXT NOT NULL DEFAULT 'audit'",
                    "scope": "TEXT NOT NULL DEFAULT 'repo'",
                    "plan_gate": "INTEGER NOT NULL DEFAULT 1",
                    "report_mode": "TEXT NOT NULL DEFAULT 'unified'",
                    "based_on": "TEXT",
                    "based_on_run_id": "TEXT",
                    "includes_json": "TEXT NOT NULL DEFAULT '[]'",
                    "plan_json": "TEXT",
                    "plan_approved": "INTEGER NOT NULL DEFAULT 0",
                    "auto_approved": "INTEGER NOT NULL DEFAULT 0",
                },
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_runs (
                    run_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    step_key TEXT NOT NULL DEFAULT '',
                    primitive_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    source_action TEXT,
                    needs_json TEXT NOT NULL DEFAULT '[]',
                    when_expr TEXT,
                    fact_views_json TEXT NOT NULL DEFAULT '[]',
                    rules_json TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT NOT NULL,
                    skip_reason TEXT,
                    deterministic_output_json TEXT,
                    agent_input_json TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, action_id),
                    FOREIGN KEY (run_id) REFERENCES workflow_runs(run_id)
                )
                """
            )
            _ensure_columns(
                conn,
                "action_runs",
                {
                    "step_key": "TEXT NOT NULL DEFAULT ''",
                    "needs_json": "TEXT NOT NULL DEFAULT '[]'",
                    "when_expr": "TEXT",
                    "fact_views_json": "TEXT NOT NULL DEFAULT '[]'",
                    "skip_reason": "TEXT",
                },
            )

    def _insert_action_rows(
        self,
        conn: sqlite3.Connection,
        run_id: str,
        primitives: list[PrimitiveStep],
        now: str,
        *,
        start_idx: int = 1,
    ) -> list[str]:
        """Insert normalized PrimitiveStep rows into action_runs starting at start_idx."""
        inserted_ids: list[str] = []
        for idx in range(start_idx, len(primitives) + 1):
            step = primitives[idx - 1]
            action_id = f"act-{idx:02d}"
            inserted_ids.append(action_id)
            conn.execute(
                """
                INSERT INTO action_runs (
                    run_id, action_id, seq, step_key, primitive_type, name, source_action,
                    needs_json, when_expr, fact_views_json,
                    rules_json, params_json, prompt, status, skip_reason,
                    deterministic_output_json, agent_input_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    action_id,
                    idx,
                    step.step_key or step.id,
                    step.type.value,
                    step.name,
                    step.source_action,
                    json.dumps(step.needs),
                    step.when,
                    json.dumps(step.fact_views),
                    json.dumps(step.rules),
                    json.dumps(step.params),
                    step.prompt,
                    RunStatus.PENDING.value,
                    None,
                    None,
                    None,
                    now,
                ),
            )
        return inserted_ids

    def create_run(
        self,
        workflow: WorkflowDefinition,
        primitives: list[PrimitiveStep],
        resolved_outputs: Optional[WorkflowOutputs] = None,
        based_on_run_id: Optional[str] = None,
        *,
        plan_json: Optional[str] = None,
        plan_approved: bool = False,
        auto_approved: bool = False,
    ) -> WorkflowRunRecord:
        """Create a new Workflow v2 run and persist its DAG action rows."""
        now = _utc_now_iso()
        run_id = f"wf-{uuid.uuid4().hex[:8]}"
        has_confirm = any(p.type == PrimitiveType.CONFIRM_PLAN for p in primitives)
        init_status = (
            RunStatus.AWAITING_APPROVAL
            if (has_confirm and not plan_approved and not auto_approved)
            else RunStatus.IN_PROGRESS
        )
        record = WorkflowRunRecord(
            run_id=run_id,
            workflow_id=workflow.id,
            category=workflow.category,
            scope=workflow.scope,
            plan_gate=workflow.plan_gate,
            report_mode=workflow.report_mode,
            based_on=workflow.based_on,
            based_on_run_id=based_on_run_id,
            includes=workflow.includes,
            workflow_name=workflow.name,
            description=workflow.description,
            status=init_status,
            targets=workflow.targets,
            outputs=resolved_outputs or workflow.outputs,
            plan_json=plan_json,
            plan_approved=plan_approved,
            auto_approved=auto_approved,
            created_at=now,
            updated_at=now,
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_runs (
                    run_id, workflow_id, category, scope, plan_gate, report_mode,
                    based_on, based_on_run_id, includes_json,
                    workflow_name, description, status,
                    targets_json, outputs_json, plan_json, plan_approved, auto_approved,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.run_id,
                    record.workflow_id,
                    record.category.value,
                    record.scope,
                    int(record.plan_gate),
                    record.report_mode,
                    record.based_on,
                    record.based_on_run_id,
                    json.dumps([c.model_dump() for c in record.includes]),
                    record.workflow_name,
                    record.description,
                    record.status.value,
                    record.targets.model_dump_json(),
                    record.outputs.model_dump_json(),
                    record.plan_json,
                    int(record.plan_approved),
                    int(record.auto_approved),
                    record.created_at,
                    record.updated_at,
                ),
            )
            self._insert_action_rows(conn, run_id, primitives, now, start_idx=1)

        return record

    def get_run(self, run_id: str) -> WorkflowRunRecord | None:
        """Fetch a workflow run record by run_id."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
        return _row_to_workflow_run(row) if row is not None else None

    def get_latest_completed_run(self, workflow_id: str) -> WorkflowRunRecord | None:
        """Fetch the most recently completed workflow run for workflow_id."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM workflow_runs
                WHERE workflow_id = ? AND status = ?
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
                """,
                (workflow_id, RunStatus.COMPLETED.value),
            ).fetchone()
        return _row_to_workflow_run(row) if row is not None else None

    def get_latest_run(self, workflow_id: str) -> WorkflowRunRecord | None:
        """Fetch the most recent workflow run (any status) for workflow_id."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM workflow_runs WHERE workflow_id = ? ORDER BY created_at DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
        return _row_to_workflow_run(row) if row is not None else None

    def list_runs(self) -> list[WorkflowRunRecord]:
        """List all workflow runs ordered from newest to oldest."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM workflow_runs ORDER BY created_at DESC, rowid DESC").fetchall()
        return [_row_to_workflow_run(r) for r in rows]

    def get_actions(self, run_id: str) -> list[ActionRunRecord]:
        """Fetch all action records for a workflow run in sequential order."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM action_runs WHERE run_id = ? ORDER BY seq ASC", (run_id,)).fetchall()
        return [_row_to_action_run(r) for r in rows]

    def get_actions_map(self, run_ids: list[str]) -> dict[str, list[ActionRunRecord]]:
        """Fetch ordered action records for multiple run IDs in a single SQLite query."""
        if not run_ids:
            return {}
        placeholders = ",".join("?" for _ in run_ids)
        query = f"SELECT * FROM action_runs WHERE run_id IN ({placeholders}) ORDER BY run_id ASC, seq ASC"  # noqa: S608
        grouped: dict[str, list[ActionRunRecord]] = {rid: [] for rid in run_ids}
        with self._connect() as conn:
            for row in conn.execute(query, tuple(run_ids)).fetchall():
                rec = _row_to_action_run(row)
                grouped.setdefault(rec.run_id, []).append(rec)
        return grouped

    @staticmethod
    def _deps_satisfied(
        act: ActionRunRecord,
        id_status: dict[str, RunStatus],
        key_statuses: dict[str, set[RunStatus]],
    ) -> bool:
        """Return True if every upstream dependency in `act.needs` is COMPLETED or SKIPPED."""
        for dep in act.needs:
            if dep in id_status:
                if id_status[dep] not in _TERMINAL_READY_DEP_STATUSES:
                    return False
            elif dep in key_statuses and not key_statuses[dep].issubset(_TERMINAL_READY_DEP_STATUSES):
                return False
        return True

    def get_ready_actions(self, run_id: str) -> list[ActionRunRecord]:
        """Return all pending/in_progress actions whose DAG `needs` dependencies are satisfied."""
        actions = self.get_actions(run_id)
        if not actions:
            return []

        key_statuses: dict[str, set[RunStatus]] = {}
        id_status: dict[str, RunStatus] = {}
        for act in actions:
            id_status[act.action_id] = act.status
            if act.step_key:
                key_statuses.setdefault(act.step_key, set()).add(act.status)
            if act.source_action:
                key_statuses.setdefault(act.source_action, set()).add(act.status)

        ready: list[ActionRunRecord] = []
        prior_all_done = True
        for act in actions:
            is_open = act.status in {RunStatus.PENDING, RunStatus.IN_PROGRESS}
            if is_open:
                if (act.needs and self._deps_satisfied(act, id_status, key_statuses)) or (
                    not act.needs and prior_all_done
                ):
                    ready.append(act)
            if act.status not in _TERMINAL_READY_DEP_STATUSES:
                prior_all_done = False

        if not ready:
            open_actions = [a for a in actions if a.status in {RunStatus.PENDING, RunStatus.IN_PROGRESS}]
            return [open_actions[0]] if open_actions else []
        return ready

    def get_current_action(self, run_id: str) -> ActionRunRecord | None:
        """Return the earliest ready pending/in_progress action for an active workflow run."""
        ready = self.get_ready_actions(run_id)
        return ready[0] if ready else None

    def mark_action_in_progress(
        self,
        run_id: str,
        action_id: str,
        deterministic_output_json: Optional[str] = None,
    ) -> ActionRunRecord | None:
        """Mark an action as in_progress and optionally store deterministic output JSON."""
        now = _utc_now_iso()
        with self._connect() as conn:
            if deterministic_output_json is not None:
                conn.execute(
                    """
                    UPDATE action_runs
                    SET status = ?, deterministic_output_json = ?, updated_at = ?
                    WHERE run_id = ? AND action_id = ?
                    """,
                    (RunStatus.IN_PROGRESS.value, deterministic_output_json, now, run_id, action_id),
                )
            else:
                conn.execute(
                    "UPDATE action_runs SET status = ?, updated_at = ? WHERE run_id = ? AND action_id = ?",
                    (RunStatus.IN_PROGRESS.value, now, run_id, action_id),
                )
            conn.execute("UPDATE workflow_runs SET updated_at = ? WHERE run_id = ?", (now, run_id))
            row = conn.execute(
                "SELECT * FROM action_runs WHERE run_id = ? AND action_id = ?",
                (run_id, action_id),
            ).fetchone()
        return _row_to_action_run(row) if row is not None else None

    def complete_deterministic_action(
        self,
        run_id: str,
        action_id: str,
        deterministic_output_json: str,
    ) -> ActionRunRecord | None:
        """Mark a deterministic action COMPLETED immediately (Auto-Advance without empty ACK)."""
        now = _utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE action_runs
                SET status = ?, deterministic_output_json = ?, updated_at = ?
                WHERE run_id = ? AND action_id = ?
                """,
                (RunStatus.COMPLETED.value, deterministic_output_json, now, run_id, action_id),
            )
            conn.execute("UPDATE workflow_runs SET updated_at = ? WHERE run_id = ?", (now, run_id))
            row = conn.execute(
                "SELECT * FROM action_runs WHERE run_id = ? AND action_id = ?",
                (run_id, action_id),
            ).fetchone()
        return _row_to_action_run(row) if row is not None else None

    def mark_action_skipped(self, run_id: str, action_id: str, reason: str) -> None:
        """Mark an action SKIPPED with a diagnostic skip_reason (e.g. `when:` false or plan opt-out)."""
        now = _utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE action_runs
                SET status = ?, skip_reason = ?, updated_at = ?
                WHERE run_id = ? AND action_id = ?
                """,
                (RunStatus.SKIPPED.value, reason, now, run_id, action_id),
            )
            conn.execute("UPDATE workflow_runs SET updated_at = ? WHERE run_id = ?", (now, run_id))

    def save_run_plan(
        self,
        run_id: str,
        plan_json: str,
        *,
        approved: bool,
        auto_approved: bool = False,
        updated_targets: Optional[WorkflowTargets] = None,
        report_mode: Optional[ReportMode] = None,
    ) -> WorkflowRunRecord | None:
        """Persist WorkflowExecutionPlan JSON, approval flags, and optional confirmed target overrides."""
        now = _utc_now_iso()
        new_status = RunStatus.IN_PROGRESS.value if approved else RunStatus.AWAITING_APPROVAL.value
        with self._connect() as conn:
            updates = ["plan_json = ?", "plan_approved = ?", "auto_approved = ?", "status = ?", "updated_at = ?"]
            vals: list[object] = [plan_json, int(approved), int(auto_approved), new_status, now]
            if updated_targets is not None:
                updates.append("targets_json = ?")
                vals.append(updated_targets.model_dump_json())
            if report_mode is not None:
                updates.append("report_mode = ?")
                vals.append(report_mode)
            vals.append(run_id)
            conn.execute(
                f"UPDATE workflow_runs SET {', '.join(updates)} WHERE run_id = ?",  # noqa: S608
                tuple(vals),
            )
        return self.get_run(run_id)

    def complete_action(self, run_id: str, action_id: str, agent_input_json: str) -> None:
        """Mark an action completed and record the validated agent input JSON."""
        now = _utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE action_runs
                SET status = ?, agent_input_json = ?, updated_at = ?
                WHERE run_id = ? AND action_id = ?
                """,
                (RunStatus.COMPLETED.value, agent_input_json, now, run_id, action_id),
            )
            conn.execute("UPDATE workflow_runs SET updated_at = ? WHERE run_id = ?", (now, run_id))

    def complete_workflow_run(self, run_id: str) -> None:
        """Mark the parent workflow run as completed."""
        now = _utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                "UPDATE workflow_runs SET status = ?, updated_at = ? WHERE run_id = ?",
                (RunStatus.COMPLETED.value, now, run_id),
            )

    def cancel_workflow_run(self, run_id: str) -> WorkflowRunRecord | None:
        """Cancel an unfinished workflow run and mark its remaining open steps cancelled."""
        existing = self.get_run(run_id)
        if existing is None:
            return None
        if existing.status == RunStatus.COMPLETED:
            msg = f"Workflow run '{run_id}' is already completed and cannot be cancelled."
            raise ValueError(msg)
        if existing.status == RunStatus.CANCELLED:
            return existing

        now = _utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE action_runs
                SET status = ?, updated_at = ?
                WHERE run_id = ? AND status IN (?, ?)
                """,
                (
                    RunStatus.CANCELLED.value,
                    now,
                    run_id,
                    RunStatus.PENDING.value,
                    RunStatus.IN_PROGRESS.value,
                ),
            )
            conn.execute(
                "UPDATE workflow_runs SET status = ?, updated_at = ? WHERE run_id = ?",
                (RunStatus.CANCELLED.value, now, run_id),
            )
        return self.get_run(run_id)

    def cancel_active_runs_for_workflow(self, workflow_id: str) -> list[WorkflowRunRecord]:
        """Cancel all unfinished runs for a given workflow_id."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT run_id FROM workflow_runs
                WHERE workflow_id = ? AND status IN (?, ?, ?)
                ORDER BY created_at ASC, rowid ASC
                """,
                (
                    workflow_id,
                    RunStatus.PENDING.value,
                    RunStatus.AWAITING_APPROVAL.value,
                    RunStatus.IN_PROGRESS.value,
                ),
            ).fetchall()
        cancelled: list[WorkflowRunRecord] = []
        for row in rows:
            updated = self.cancel_workflow_run(str(row["run_id"]))
            if updated is not None:
                cancelled.append(updated)
        return cancelled

    def cancel_superseded_runs(self, workflow_id: Optional[str] = None) -> list[WorkflowRunRecord]:
        """Cancel unfinished runs superseded by a newer non-cancelled run of the same workflow."""
        params: tuple[str, ...]
        wf_clause = ""
        base_params = (
            RunStatus.PENDING.value,
            RunStatus.AWAITING_APPROVAL.value,
            RunStatus.IN_PROGRESS.value,
            RunStatus.CANCELLED.value,
        )
        if workflow_id is not None:
            wf_clause = "AND r.workflow_id = ?"
            params = (*base_params, workflow_id)
        else:
            params = base_params

        query = f"""
            SELECT r.run_id
            FROM workflow_runs r
            WHERE r.status IN (?, ?, ?)
              AND EXISTS (
                  SELECT 1
                  FROM workflow_runs newer
                  WHERE newer.workflow_id = r.workflow_id
                    AND newer.run_id != r.run_id
                    AND newer.status != ?
                    AND (
                        newer.created_at > r.created_at
                        OR (newer.created_at = r.created_at AND newer.rowid > r.rowid)
                    )
              )
              {wf_clause}
            ORDER BY r.created_at ASC, r.rowid ASC
        """  # noqa: S608
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        cancelled: list[WorkflowRunRecord] = []
        for row in rows:
            updated = self.cancel_workflow_run(str(row["run_id"]))
            if updated is not None:
                cancelled.append(updated)
        return cancelled

    def rewind_run_from_seq(
        self,
        run_id: str,
        from_seq: int,
        *,
        workflow_def: Optional[WorkflowDefinition] = None,
        primitives: Optional[list[PrimitiveStep]] = None,
        resolved_outputs: Optional[WorkflowOutputs] = None,
    ) -> tuple[WorkflowRunRecord, list[str], bool]:
        """Reset actions at `seq >= from_seq` to pending and optionally re-sync parameters from YAML."""
        existing = self.get_run(run_id)
        if existing is None:
            msg = f"Workflow run '{run_id}' not found."
            raise ValueError(msg)
        if existing.status == RunStatus.CANCELLED:
            msg = f"Workflow run '{run_id}' is cancelled and cannot be rewound."
            raise ValueError(msg)

        all_actions = self.get_actions(run_id)
        if not all_actions or from_seq < 1 or from_seq > len(all_actions):
            msg = f"Invalid rewind sequence {from_seq} for run '{run_id}' (1..{len(all_actions)})."
            raise ValueError(msg)

        prior_types = [a.primitive_type for a in all_actions if a.seq < from_seq]
        can_replace_tail = (
            workflow_def is not None
            and primitives is not None
            and len(primitives) >= from_seq
            and [p.type for p in primitives[: from_seq - 1]] == prior_types
        )

        now = _utc_now_iso()
        resynced = False
        with self._connect() as conn:
            if workflow_def is not None:
                eff_out = resolved_outputs or workflow_def.outputs
                conn.execute(
                    """
                    UPDATE workflow_runs
                    SET workflow_name = ?, description = ?, status = ?,
                        targets_json = ?, outputs_json = ?, updated_at = ?
                    WHERE run_id = ?
                    """,
                    (
                        workflow_def.name,
                        workflow_def.description,
                        RunStatus.IN_PROGRESS.value,
                        workflow_def.targets.model_dump_json(),
                        eff_out.model_dump_json(),
                        now,
                        run_id,
                    ),
                )
                resynced = True
            else:
                conn.execute(
                    "UPDATE workflow_runs SET status = ?, updated_at = ? WHERE run_id = ?",
                    (RunStatus.IN_PROGRESS.value, now, run_id),
                )

            if can_replace_tail and primitives is not None:
                conn.execute("DELETE FROM action_runs WHERE run_id = ? AND seq >= ?", (run_id, from_seq))
                reset_ids = self._insert_action_rows(conn, run_id, primitives, now, start_idx=from_seq)
            else:
                conn.execute(
                    """
                    UPDATE action_runs
                    SET status = ?, skip_reason = NULL, deterministic_output_json = NULL,
                        agent_input_json = NULL, updated_at = ?
                    WHERE run_id = ? AND seq >= ?
                    """,
                    (RunStatus.PENDING.value, now, run_id, from_seq),
                )
                reset_ids = [a.action_id for a in all_actions if a.seq >= from_seq]

        updated = self.get_run(run_id)
        if updated is None:
            msg = f"Failed to reload rewound run '{run_id}'."
            raise RuntimeError(msg)
        return updated, reset_ids, resynced
