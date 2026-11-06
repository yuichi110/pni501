# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic orchestrator for `progress_analyze` generating `ProgressFacts`."""

from __future__ import annotations

import fnmatch
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Final

from pni._actions.base_model import ScoreResult
from pni._actions.progress_analyze.branch_topology import analyze_branch_topology_and_policy
from pni._actions.progress_analyze.conflict_detector import (
    detect_overlapping_branch_files,
    inspect_working_tree_conflicts,
)
from pni._actions.progress_analyze.git_exec import inspect_git_repo_head, run_git_readonly
from pni._actions.progress_analyze.history_ledger import read_audit_history, read_progress_history
from pni._actions.progress_analyze.history_trajectory import analyze_history_trajectory
from pni._actions.progress_analyze.models import (
    AuditSummarySnapshot,
    BranchHealthFact,
    ProgressFacts,
    ProgressOptions,
    ProgressPlanDefinition,
    ProgressPreflightHint,
    ProgressTaskSpec,
    TaskDeterministicEvidence,
    TaskScheduleState,
)
from pni._actions.progress_analyze.plan_loader import load_and_validate_progress_plan
from pni._cache import default_progress_facts_rel_path, ensure_cache_parent

_STUB_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(?:TODO|FIXME|NotImplementedError|UnsupportedOperationException)\b"
)
_SOURCE_CODE_SUFFIXES: Final[frozenset[str]] = frozenset({".py", ".java", ".php", ".ts", ".tsx", ".js", ".go", ".rs"})


def _resolve_as_of_date(raw_as_of: str) -> date:
    """Resolve `as_of_date` string (`YYYY-MM-DD`) or default to `date.today()`."""
    cleaned = raw_as_of.strip()
    if not cleaned:
        return date.today()
    try:
        return date.fromisoformat(cleaned)
    except ValueError as exc:
        msg = f"Invalid as_of_date '{raw_as_of}' (expected YYYY-MM-DD)."
        raise ValueError(msg) from exc


def _collect_files_under_hit(hit: Path) -> list[Path]:
    """Return `[hit]` if file, or all nested files if directory."""
    if hit.is_file():
        return [hit]
    if hit.is_dir():
        return [f for f in hit.rglob("*") if f.is_file()]
    return []


def _expand_expected_paths(target_root_dir: Path, raw_paths: list[str]) -> tuple[list[str], list[str], list[Path]]:
    """Resolve task `expected_paths` (literal or glob) within `target_root_dir`."""
    resolved_root = target_root_dir.resolve()
    existing: list[str] = []
    missing: list[str] = []
    matched_files: list[Path] = []

    for pat in raw_paths:
        clean_pat = pat.strip().strip("/")
        if not clean_pat:
            continue
        if any(ch in clean_pat for ch in ("*", "?", "[")):
            hits = [p for p in resolved_root.glob(clean_pat) if p.resolve().is_relative_to(resolved_root)]
            if not hits:
                missing.append(pat)
                continue
            for hp in sorted(hits):
                existing.append(str(hp.relative_to(resolved_root)).replace("\\", "/"))
                matched_files.extend(_collect_files_under_hit(hp))
        else:
            cand = (resolved_root / clean_pat).resolve()
            if cand.exists() and cand.is_relative_to(resolved_root):
                existing.append(clean_pat)
                matched_files.extend(_collect_files_under_hit(cand))
            else:
                missing.append(pat)

    return (sorted(set(existing)), missing, matched_files)


def _count_stubs_and_tests(files: list[Path], test_targets: list[str], target_root_dir: Path) -> tuple[int, bool]:
    """Count stub/TODO markers and detect test file presence among `files`."""
    stubs = 0
    has_tests = False
    root_res = target_root_dir.resolve()
    norm_tests = [t.strip("/") for t in test_targets if t.strip("/")]

    for fpath in files[:300]:
        if fpath.suffix.lower() not in _SOURCE_CODE_SUFFIXES:
            continue
        rel = str(fpath.resolve().relative_to(root_res)).replace("\\", "/")
        fname = fpath.name.lower()
        if (
            fname.startswith("test_")
            or fname.endswith(("_test.py", "test.java", "tests.java", "test.php"))
            or any(rel == tp or rel.startswith(f"{tp}/") for tp in norm_tests)
        ):
            has_tests = True
        try:
            if fpath.stat().st_size <= 500_000:
                stubs += len(_STUB_PATTERN.findall(fpath.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return (stubs, has_tests)


def _query_paths_git_activity(
    repo_dir: Path,
    target_root_dir: Path,
    existing_rel_paths: list[str],
    as_of: date,
) -> tuple[str, int]:
    """Query `(last_commit_date, commits_last_14d)` for `existing_rel_paths` safely using `--`."""
    if not existing_rel_paths:
        return ("", 0)
    repo_res = repo_dir.resolve()
    t_res = target_root_dir.resolve()
    pathspecs: list[str] = []
    for rel in existing_rel_paths[:20]:
        full = (t_res / rel).resolve()
        if full.is_relative_to(repo_res):
            pathspecs.append(str(full.relative_to(repo_res)).replace("\\", "/"))
    if not pathspecs:
        return ("", 0)

    res = run_git_readonly(
        repo_dir,
        ["log", "-n", "50", f"--until={as_of.isoformat()}T23:59:59", "--format=%cs", "--", *pathspecs],
        timeout_sec=10.0,
    )
    if res.exit_code != 0 or not res.stdout.strip():
        return ("", 0)

    dates = [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]
    if not dates:
        return ("", 0)
    cutoff = as_of - timedelta(days=14)
    recent = 0
    for d_str in dates:
        try:
            if date.fromisoformat(d_str) >= cutoff:
                recent += 1
        except ValueError:
            continue
    return (dates[0], recent)


def _evaluate_single_task(
    task: ProgressTaskSpec,
    branches: list[BranchHealthFact],
    repo_dir: Path,
    target_root_dir: Path,
    test_targets: list[str],
    git_available: bool,
    as_of: date,
) -> TaskDeterministicEvidence:
    """Collect objective branch, path, commit, stub, and schedule state evidence for `task`."""
    p_start = date.fromisoformat(task.planned_start)
    p_end = date.fromisoformat(task.planned_end)
    days_delta = (p_end - as_of).days

    if task.status == "done":
        sched_state: TaskScheduleState = "completed_declared"
    elif as_of > p_end:
        sched_state = "overdue"
    elif as_of < p_start:
        sched_state = "upcoming"
    else:
        sched_state = "active"

    matched_brs: list[BranchHealthFact] = []
    if task.branch_pattern.strip():
        matched_brs = [b for b in branches if fnmatch.fnmatch(b.branch_name, task.branch_pattern.strip())]

    existing_p, missing_p, matched_files = _expand_expected_paths(target_root_dir, task.expected_paths)
    stubs, has_tests = _count_stubs_and_tests(matched_files, test_targets, target_root_dir)
    last_cdate, recent_cnt = (
        _query_paths_git_activity(repo_dir, target_root_dir, existing_p, as_of) if git_available else ("", 0)
    )

    return TaskDeterministicEvidence(
        task_id=task.id,
        milestone_id=task.milestone,
        name=task.name,
        planned_start=task.planned_start,
        planned_end=task.planned_end,
        declared_status=task.status,
        declared_progress=task.declared_progress or 0,
        schedule_state=sched_state,
        days_delta=days_delta,
        matched_branches=[b.branch_name for b in matched_brs],
        branch_merged=bool(matched_brs) and all(b.is_merged for b in matched_brs),
        branch_has_conflict=any(b.has_conflict for b in matched_brs),
        existing_paths=existing_p,
        missing_paths=missing_p,
        last_commit_date=last_cdate,
        recent_commits_count=recent_cnt,
        stub_todo_count=stubs,
        has_tests=has_tests,
    )


def _load_audit_summary_snapshot(
    project_root: Path,
    base_workflow_id: str,
    score_output_dir: str = "reports",
) -> AuditSummarySnapshot | None:
    """Load Git-tracked `.pni/history/audit/<id>.jsonl` and optional `*_score.json` summary."""
    clean_id = base_workflow_id.strip()
    if not clean_id:
        return None

    history = read_audit_history(project_root, clean_id)
    if history:
        latest = history[-1]
        delta = (latest.overall_score - history[-2].overall_score) if len(history) >= 2 else None
        return AuditSummarySnapshot(
            base_workflow_id=clean_id,
            latest_score=latest.overall_score,
            latest_grade=latest.health_grade,
            score_delta=delta,
            latest_category_scores=dict(latest.category_scores),
            critical_findings=latest.finding_counts.get("critical", 0),
            high_findings=latest.finding_counts.get("high", 0),
            history_points=history[-10:],
        )

    score_candidate = (project_root / score_output_dir / f"{clean_id}_score.json").resolve()
    if score_candidate.is_file() and score_candidate.is_relative_to(project_root.resolve()):
        try:
            sr = ScoreResult.model_validate_json(score_candidate.read_text(encoding="utf-8"))
            crit = sum(1 for f in sr.findings if f.severity == "critical")
            high = sum(1 for f in sr.findings if f.severity == "high")
            return AuditSummarySnapshot(
                base_workflow_id=clean_id,
                latest_score=sr.overall_score,
                latest_grade=sr.grade,
                score_delta=None,
                latest_category_scores={k: int(v) for k, v in sr.category_scores.model_dump().items()},
                critical_findings=crit,
                high_findings=high,
                history_points=[],
            )
        except Exception:
            return AuditSummarySnapshot(base_workflow_id=clean_id)

    return AuditSummarySnapshot(base_workflow_id=clean_id)


def run_progress_analyze(
    workspace_root: Path,
    workflow_id: str,
    *,
    target_root: str = ".",
    source_targets: list[str] | None = None,
    test_targets: list[str] | None = None,
    doc_targets: list[str] | None = None,
    options: ProgressOptions | None = None,
) -> ProgressFacts:
    """Execute deterministic Git, conflict, trajectory, and schedule inspection (`progress_analyze`)."""
    opts = options or ProgressOptions()
    srcs = source_targets if source_targets is not None else ["src"]
    tsts = test_targets if test_targets is not None else ["tests"]
    docs = doc_targets if doc_targets is not None else ["README.md"]
    as_of = _resolve_as_of_date(opts.as_of_date)

    plan_arg = opts.plan_file or opts.target or workflow_id
    plan, plan_rel, plan_sha, plan_hints = load_and_validate_progress_plan(
        workspace_root,
        plan_arg,
        fallback_id=workflow_id,
    )

    t_root_dir = (workspace_root / target_root).resolve()
    if not t_root_dir.is_relative_to(workspace_root.resolve()):
        msg = f"target_root escapes workspace root: {target_root!r}"
        raise ValueError(msg)

    git_ok, cur_branch, head_sha, is_dirty, is_shallow = inspect_git_repo_head(workspace_root)
    hints: list[ProgressPreflightHint] = list(plan_hints)

    if is_shallow:
        hints.append(
            ProgressPreflightHint(
                code="shallow_git_repository",
                message=(
                    "Repository is a shallow clone (`git rev-parse --is-shallow-repository == true`); "
                    "run `git fetch --unshallow` for complete historical LOC/commit trajectories."
                ),
            )
        )

    if git_ok:
        wt_conflicts = inspect_working_tree_conflicts(t_root_dir, [*srcs, *tsts])
        base_ref, br_facts, conv_ratio, m_cnt, fox_cnt, wip_cnt, violations = analyze_branch_topology_and_policy(
            workspace_root,
            plan.git_policy,
            cur_branch,
            as_of,
        )
        overlaps = detect_overlapping_branch_files(br_facts)
        trajectory, churn = analyze_history_trajectory(
            workspace_root,
            base_ref,
            target_root=target_root,
            source_targets=srcs,
            test_targets=tsts,
            doc_targets=docs,
            as_of=as_of,
            lookback_weeks=opts.lookback_weeks,
        )
    else:
        hints.append(
            ProgressPreflightHint(
                code="git_unavailable",
                message="Workspace is not inside a Git worktree; branch/commit metrics are unavailable.",
            )
        )
        wt_conflicts_empty = inspect_working_tree_conflicts(t_root_dir, [])
        wt_conflicts = wt_conflicts_empty
        base_ref = plan.git_policy.trunk_branch
        br_facts = []
        conv_ratio, m_cnt, fox_cnt, wip_cnt = 1.0, 0, 0, 0
        violations = []
        overlaps = []
        trajectory = []
        churn = []

    task_ev = [
        _evaluate_single_task(t, br_facts, workspace_root, t_root_dir, tsts, git_ok, as_of) for t in plan.tasks
    ]
    audit_sum = _load_audit_summary_snapshot(workspace_root, opts.base_audit_workflow, opts.output_dir)
    prog_hist = read_progress_history(workspace_root, workflow_id)

    facts = ProgressFacts(
        project_name=plan.name,
        workflow_id=workflow_id,
        as_of_date=as_of.isoformat(),
        plan_file=plan_rel,
        plan_sha256=plan_sha,
        plan=plan,
        git_available=git_ok,
        is_shallow_repository=is_shallow,
        current_branch=cur_branch,
        head_sha=head_sha,
        git_dirty=is_dirty,
        resolved_base_branch=base_ref,
        conventional_commit_ratio=conv_ratio,
        trunk_merge_commits_count=m_cnt,
        foxtrot_merges_count=fox_cnt,
        wip_commits_on_trunk=wip_cnt,
        working_tree_conflicts=wt_conflicts,
        branches=br_facts,
        overlapping_file_hotspots=overlaps,
        policy_violations=violations,
        trajectory=trajectory,
        churn_hotspots=churn,
        task_evidence=task_ev,
        audit_summary=audit_sum,
        progress_history=prog_hist[-10:],
        preflight_hints=hints,
    )

    out_file = workspace_root / default_progress_facts_rel_path(workflow_id)
    ensure_cache_parent(workspace_root, out_file)
    out_file.write_text(facts.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return facts


__all__ = ["ProgressPlanDefinition", "run_progress_analyze"]
