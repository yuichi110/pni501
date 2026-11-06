# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Git-tracked JSON Lines (.jsonl) time-series ledger for audit and progress histories."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from pni._actions.base_model import MetricScalar, ScoreResult
from pni._actions.progress_analyze.git_exec import inspect_git_repo_head
from pni._actions.progress_analyze.models import (
    AuditHistoryEntry,
    AuditLocSummary,
    AuditTestSummary,
    ProgressHistoryEntry,
    ProgressResult,
)
from pni._cache import default_audit_history_rel_path, default_progress_history_rel_path

_EntryT = TypeVar("_EntryT", AuditHistoryEntry, ProgressHistoryEntry)


def _resolve_bounded_ledger_path(project_root: Path, rel_path: str) -> Path:
    """Resolve `rel_path` strictly inside `project_root` to prevent directory traversal."""
    root_resolved = project_root.resolve()
    candidate = (root_resolved / rel_path).resolve()
    if candidate == root_resolved or not candidate.is_relative_to(root_resolved):
        msg = f"Ledger path escapes workspace boundary: {rel_path!r}"
        raise ValueError(msg)
    return candidate


def _read_jsonl_entries(file_path: Path, model_cls: type[_EntryT]) -> list[_EntryT]:
    """Parse valid JSONL records from `file_path`, ignoring blank lines."""
    if not file_path.is_file():
        return []
    entries: list[_EntryT] = []
    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        entries.append(model_cls.model_validate_json(stripped))
    return entries


def _upsert_jsonl_entry(file_path: Path, entries: list[_EntryT], new_entry: _EntryT) -> None:
    """Upsert `new_entry` when the trailing entry shares the same non-empty `git_sha`, else append."""
    updated = list(entries)
    if updated and new_entry.git_sha and updated[-1].git_sha == new_entry.git_sha:
        updated[-1] = new_entry
    else:
        updated.append(new_entry)

    file_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = "\n".join(item.model_dump_json() for item in updated) + "\n"
    file_path.write_text(serialized, encoding="utf-8")


def read_audit_history(project_root: Path, workflow_id: str) -> list[AuditHistoryEntry]:
    """Load chronological `AuditHistoryEntry` records from `.pni/history/audit/<workflow_id>.jsonl`."""
    rel = default_audit_history_rel_path(workflow_id)
    ledger_file = _resolve_bounded_ledger_path(project_root, rel)
    return _read_jsonl_entries(ledger_file, AuditHistoryEntry)


def read_progress_history(project_root: Path, workflow_id: str) -> list[ProgressHistoryEntry]:
    """Load chronological `ProgressHistoryEntry` records from `.pni/history/progress/<workflow_id>.jsonl`."""
    rel = default_progress_history_rel_path(workflow_id)
    ledger_file = _resolve_bounded_ledger_path(project_root, rel)
    return _read_jsonl_entries(ledger_file, ProgressHistoryEntry)


def _extract_int_metric(metrics: dict[str, MetricScalar], keys: tuple[str, ...]) -> int:
    """Extract the first matching integer metric from `ScoreResult.metrics_snapshot`."""
    for key in keys:
        val = metrics.get(key)
        if isinstance(val, int) and not isinstance(val, bool):
            return val
    return 0


def record_audit_history_from_score(
    project_root: Path,
    workflow_id: str,
    score_result: ScoreResult,
) -> AuditHistoryEntry:
    """Build and upsert an `AuditHistoryEntry` into `.pni/history/audit/<workflow_id>.jsonl`."""
    rel = default_audit_history_rel_path(workflow_id)
    ledger_file = _resolve_bounded_ledger_path(project_root, rel)
    _, branch, head_sha, is_dirty, _ = inspect_git_repo_head(project_root)

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in score_result.findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    source_loc = sum(m.loc for m in score_result.module_inventory)
    if source_loc == 0:
        source_loc = _extract_int_metric(
            score_result.metrics_snapshot,
            ("total_source_lines", "source_lines", "source_loc"),
        )
    test_loc = _extract_int_metric(score_result.metrics_snapshot, ("total_test_lines", "test_lines", "test_loc"))
    docs_loc = _extract_int_metric(score_result.metrics_snapshot, ("readme_line_count", "docs_loc"))

    test_summary = AuditTestSummary()
    if score_result.runtime_facts is not None:
        te = score_result.runtime_facts.test_execution
        test_summary.passed = te.passed_tests
        test_summary.failed = te.failed_tests + te.error_tests
        test_summary.skipped = te.skipped_tests
        if score_result.runtime_facts.coverage.measured:
            test_summary.coverage_pct = score_result.runtime_facts.coverage.line_coverage_pct

    vuln_count = 0
    if score_result.security_facts is not None:
        vuln_count = len(score_result.security_facts.vulnerabilities)

    ts = score_result.evaluated_at or datetime.now(timezone.utc).isoformat()
    cat_dump: BaseModel = score_result.category_scores
    entry = AuditHistoryEntry(
        timestamp=ts,
        workflow_id=workflow_id,
        git_sha=head_sha or "untracked",
        git_branch=branch,
        git_dirty=is_dirty,
        overall_score=score_result.overall_score,
        health_grade=score_result.grade,
        category_scores={k: int(v) for k, v in cat_dump.model_dump().items()},
        finding_counts=counts,
        loc=AuditLocSummary(source=source_loc, tests=test_loc, docs=docs_loc),
        test_execution=test_summary,
        vuln_count=vuln_count,
    )
    existing = _read_jsonl_entries(ledger_file, AuditHistoryEntry)
    _upsert_jsonl_entry(ledger_file, existing, entry)
    return entry


def record_progress_history_from_result(
    project_root: Path,
    workflow_id: str,
    result: ProgressResult,
) -> ProgressHistoryEntry:
    """Build and upsert a `ProgressHistoryEntry` into `.pni/history/progress/<workflow_id>.jsonl`."""
    rel = default_progress_history_rel_path(workflow_id)
    ledger_file = _resolve_bounded_ledger_path(project_root, rel)
    _, branch, head_sha, is_dirty, _ = inspect_git_repo_head(project_root)

    verified_avg = (
        round(sum(t.verified_progress for t in result.task_assessments) / len(result.task_assessments), 1)
        if result.task_assessments
        else 0.0
    )

    commits_recent = 0
    net_src = 0
    net_tst = 0
    static_cases = 0
    active_br = 0
    stale_br = 0
    conflict_br = 0
    violations = 0
    if result.progress_facts is not None:
        pf = result.progress_facts
        head_sha = pf.head_sha or head_sha
        branch = pf.current_branch or branch
        is_dirty = pf.git_dirty
        if pf.trajectory:
            latest_pt = pf.trajectory[-1]
            commits_recent = latest_pt.commits_count
            net_src = latest_pt.source_loc
            net_tst = latest_pt.test_loc
            static_cases = latest_pt.static_test_cases
        unmerged = [b for b in pf.branches if not b.is_merged]
        active_br = len(unmerged)
        stale_br = sum(1 for b in unmerged if b.is_stale)
        conflict_br = sum(1 for b in unmerged if b.has_conflict)
        violations = len(pf.policy_violations)

    ts = result.generated_at or datetime.now(timezone.utc).isoformat()
    entry = ProgressHistoryEntry(
        timestamp=ts,
        workflow_id=workflow_id,
        git_sha=head_sha or "untracked",
        git_branch=branch,
        git_dirty=is_dirty,
        delivery_status=result.delivery_status,
        overall_health_score=result.overall_health_score,
        verified_completion_pct=verified_avg,
        commits_recent_window=commits_recent,
        net_source_loc=net_src,
        net_test_loc=net_tst,
        static_test_cases=static_cases,
        active_branches=active_br,
        stale_branches=stale_br,
        conflicting_branches=conflict_br,
        policy_violations=violations,
    )
    existing = _read_jsonl_entries(ledger_file, ProgressHistoryEntry)
    _upsert_jsonl_entry(ledger_file, existing, entry)
    return entry
