# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""SQLite state persistence (.pni/cache/workflow_state.db) for deterministic workflow execution."""

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
    RunStatus,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowOutputs,
    WorkflowRunRecord,
    WorkflowTargets,
)


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_workflow_run(row: sqlite3.Row) -> WorkflowRunRecord:
    """Deserialize a sqlite3.Row into a WorkflowRunRecord."""
    keys = set(row.keys())
    raw_cat = str(row["category"]) if "category" in keys and row["category"] else "audit"
    based_on = str(row["based_on"]) if "based_on" in keys and row["based_on"] is not None else None
    based_on_run = (
        str(row["based_on_run_id"])
        if "based_on_run_id" in keys and row["based_on_run_id"] is not None
        else None
    )
    return WorkflowRunRecord(
        run_id=str(row["run_id"]),
        workflow_id=str(row["workflow_id"]),
        category=WorkflowCategory(raw_cat),
        based_on=based_on,
        based_on_run_id=based_on_run,
        workflow_name=str(row["workflow_name"]),
        description=str(row["description"]),
        status=RunStatus(str(row["status"])),
        targets=WorkflowTargets.model_validate_json(str(row["targets_json"])),
        outputs=WorkflowOutputs.model_validate_json(str(row["outputs_json"])),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _row_to_action_run(row: sqlite3.Row) -> ActionRunRecord:
    """Deserialize a sqlite3.Row into an ActionRunRecord."""
    raw_rules = json.loads(str(row["rules_json"]))
    raw_params = json.loads(str(row["params_json"]))
    return ActionRunRecord(
        run_id=str(row["run_id"]),
        action_id=str(row["action_id"]),
        seq=int(row["seq"]),
        primitive_type=PrimitiveType(str(row["primitive_type"])),
        name=str(row["name"]),
        source_action=str(row["source_action"]) if row["source_action"] is not None else None,
        rules=raw_rules if isinstance(raw_rules, list) else [],
        params=raw_params if isinstance(raw_params, dict) else {},
        prompt=str(row["prompt"]),
        status=RunStatus(str(row["status"])),
        deterministic_output_json=(
            str(row["deterministic_output_json"]) if row["deterministic_output_json"] is not None else None
        ),
        agent_input_json=str(row["agent_input_json"]) if row["agent_input_json"] is not None else None,
        updated_at=str(row["updated_at"]),
    )


class WorkflowStateDB:
    """Encapsulates SQLite state storage in .pni/cache/workflow_state.db."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the database connection path and ensure schema exists.

        Args:
            project_root: Workspace root directory containing .pni/.
        """
        ensure_cache_dir(project_root)
        self.db_path = project_root / DEFAULT_STATE_DB_REL_PATH
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite connection configured with sqlite3.Row factory."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Create workflow_runs and action_runs tables and apply lightweight column migrations."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'audit',
                    based_on TEXT,
                    based_on_run_id TEXT,
                    workflow_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    targets_json TEXT NOT NULL,
                    outputs_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            existing_cols = {
                str(r["name"])
                for r in conn.execute("PRAGMA table_info(workflow_runs)").fetchall()
            }
            if "category" not in existing_cols:
                conn.execute("ALTER TABLE workflow_runs ADD COLUMN category TEXT NOT NULL DEFAULT 'audit'")
            if "based_on" not in existing_cols:
                conn.execute("ALTER TABLE workflow_runs ADD COLUMN based_on TEXT")
            if "based_on_run_id" not in existing_cols:
                conn.execute("ALTER TABLE workflow_runs ADD COLUMN based_on_run_id TEXT")

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_runs (
                    run_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    primitive_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    source_action TEXT,
                    rules_json TEXT NOT NULL,
                    params_json TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    status TEXT NOT NULL,
                    deterministic_output_json TEXT,
                    agent_input_json TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, action_id),
                    FOREIGN KEY (run_id) REFERENCES workflow_runs(run_id)
                )
                """
            )

    def create_run(
        self,
        workflow: WorkflowDefinition,
        primitives: list[PrimitiveStep],
        resolved_outputs: Optional[WorkflowOutputs] = None,
        based_on_run_id: Optional[str] = None,
    ) -> WorkflowRunRecord:
        """Create a new workflow run and insert all normalized primitive action steps.

        Args:
            workflow: Validated workflow definition.
            primitives: Normalized primitive action steps.
            resolved_outputs: Optional resolved effective output destinations.
            based_on_run_id: Optional completed run_id of the prerequisite audit workflow.

        Returns:
            WorkflowRunRecord: Newly created workflow run record.
        """
        now = _utc_now_iso()
        run_id = f"wf-{uuid.uuid4().hex[:8]}"
        record = WorkflowRunRecord(
            run_id=run_id,
            workflow_id=workflow.id,
            category=workflow.category,
            based_on=workflow.based_on,
            based_on_run_id=based_on_run_id,
            workflow_name=workflow.name,
            description=workflow.description,
            status=RunStatus.IN_PROGRESS,
            targets=workflow.targets,
            outputs=resolved_outputs or workflow.outputs,
            created_at=now,
            updated_at=now,
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_runs (
                    run_id, workflow_id, category, based_on, based_on_run_id,
                    workflow_name, description, status,
                    targets_json, outputs_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.run_id,
                    record.workflow_id,
                    record.category.value,
                    record.based_on,
                    record.based_on_run_id,
                    record.workflow_name,
                    record.description,
                    record.status.value,
                    record.targets.model_dump_json(),
                    record.outputs.model_dump_json(),
                    record.created_at,
                    record.updated_at,
                ),
            )
            for idx, step in enumerate(primitives, start=1):
                action_id = f"act-{idx:02d}"
                conn.execute(
                    """
                    INSERT INTO action_runs (
                        run_id, action_id, seq, primitive_type, name, source_action,
                        rules_json, params_json, prompt, status,
                        deterministic_output_json, agent_input_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        action_id,
                        idx,
                        step.type.value,
                        step.name,
                        step.source_action,
                        json.dumps(step.rules),
                        json.dumps(step.params),
                        step.prompt,
                        RunStatus.PENDING.value,
                        None,
                        None,
                        now,
                    ),
                )

        return record

    def get_run(self, run_id: str) -> WorkflowRunRecord | None:
        """Fetch a workflow run record by run_id."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
        return _row_to_workflow_run(row) if row is not None else None

    def get_latest_completed_run(self, workflow_id: str) -> WorkflowRunRecord | None:
        """Fetch the most recently completed workflow run for the given workflow_id."""
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
        """Fetch the most recent workflow run (any status) for the given workflow_id."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM workflow_runs WHERE workflow_id = ? ORDER BY created_at DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
        return _row_to_workflow_run(row) if row is not None else None

    def list_runs(self) -> list[WorkflowRunRecord]:
        """List all workflow runs ordered from most recently created to oldest."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM workflow_runs ORDER BY created_at DESC, rowid DESC"
            ).fetchall()
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

    def get_current_action(self, run_id: str) -> ActionRunRecord | None:
        """Return the earliest pending or in_progress action for an active workflow run."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM action_runs
                WHERE run_id = ? AND status IN (?, ?)
                ORDER BY seq ASC
                LIMIT 1
                """,
                (run_id, RunStatus.PENDING.value, RunStatus.IN_PROGRESS.value),
            ).fetchone()
        return _row_to_action_run(row) if row is not None else None

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
        """Cancel an unfinished workflow run and mark its remaining pending/in_progress steps cancelled.

        Args:
            run_id: Target workflow run identifier.

        Returns:
            WorkflowRunRecord | None: Updated run record, or None if run_id does not exist.

        Raises:
            ValueError: If the workflow run is already completed.
        """
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
        """Cancel all unfinished (pending/in_progress) runs for a given workflow_id."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT run_id FROM workflow_runs
                WHERE workflow_id = ? AND status IN (?, ?)
                ORDER BY created_at ASC, rowid ASC
                """,
                (workflow_id, RunStatus.PENDING.value, RunStatus.IN_PROGRESS.value),
            ).fetchall()
        cancelled: list[WorkflowRunRecord] = []
        for row in rows:
            updated = self.cancel_workflow_run(str(row["run_id"]))
            if updated is not None:
                cancelled.append(updated)
        return cancelled

    def cancel_superseded_runs(self, workflow_id: Optional[str] = None) -> list[WorkflowRunRecord]:
        """Cancel unfinished runs that have been superseded by a newer non-cancelled run of the same workflow."""
        params: tuple[str, ...]
        wf_clause = ""
        if workflow_id is not None:
            wf_clause = "AND r.workflow_id = ?"
            params = (
                RunStatus.PENDING.value,
                RunStatus.IN_PROGRESS.value,
                RunStatus.CANCELLED.value,
                workflow_id,
            )
        else:
            params = (
                RunStatus.PENDING.value,
                RunStatus.IN_PROGRESS.value,
                RunStatus.CANCELLED.value,
            )

        query = f"""
            SELECT r.run_id
            FROM workflow_runs r
            WHERE r.status IN (?, ?)
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

    def _replace_tail_actions_from_primitives(
        self,
        conn: sqlite3.Connection,
        run_id: str,
        from_seq: int,
        primitives: list[PrimitiveStep],
        now: str,
    ) -> list[str]:
        """Delete actions at `seq >= from_seq` and insert fresh pending rows from `primitives`."""
        conn.execute("DELETE FROM action_runs WHERE run_id = ? AND seq >= ?", (run_id, from_seq))
        reset_ids: list[str] = []
        for idx in range(from_seq, len(primitives) + 1):
            step = primitives[idx - 1]
            action_id = f"act-{idx:02d}"
            reset_ids.append(action_id)
            conn.execute(
                """
                INSERT INTO action_runs (
                    run_id, action_id, seq, primitive_type, name, source_action,
                    rules_json, params_json, prompt, status,
                    deterministic_output_json, agent_input_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    action_id,
                    idx,
                    step.type.value,
                    step.name,
                    step.source_action,
                    json.dumps(step.rules),
                    json.dumps(step.params),
                    step.prompt,
                    RunStatus.PENDING.value,
                    None,
                    None,
                    now,
                ),
            )
        return reset_ids

    def rewind_run_from_seq(
        self,
        run_id: str,
        from_seq: int,
        *,
        workflow_def: Optional[WorkflowDefinition] = None,
        primitives: Optional[list[PrimitiveStep]] = None,
        resolved_outputs: Optional[WorkflowOutputs] = None,
    ) -> tuple[WorkflowRunRecord, list[str], bool]:
        """Reset actions at `seq >= from_seq` to pending and optionally re-sync parameters from YAML.

        Args:
            run_id: Target workflow run identifier.
            from_seq: 1-based action sequence index to rewind back to (inclusive).
            workflow_def: Optional reloaded workflow definition from `.pni/workflows/`.
            primitives: Optional normalized primitives from the reloaded workflow YAML.
            resolved_outputs: Optional resolved outputs from the reloaded workflow YAML.

        Returns:
            tuple[WorkflowRunRecord, list[str], bool]: `(updated_run, reset_action_ids, yaml_resynced)`.

        Raises:
            ValueError: If `run_id` is missing, cancelled, or `from_seq` is out of bounds.
        """
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
                reset_ids = self._replace_tail_actions_from_primitives(conn, run_id, from_seq, primitives, now)
            else:
                conn.execute(
                    """
                    UPDATE action_runs
                    SET status = ?, deterministic_output_json = NULL, agent_input_json = NULL, updated_at = ?
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
