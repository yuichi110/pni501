# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Historical Git trajectory analyzer for commit velocity, LOC growth, churn, and static test counts."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Final

from pni._actions.progress_analyze.git_exec import run_git_readonly, validate_safe_git_ref
from pni._actions.progress_analyze.models import ChurnHotspotItem, TrajectoryPoint
from pni._cache import normalize_target_subpath

_LOCKFILE_NAMES: Final[frozenset[str]] = frozenset(
    {
        "uv.lock",
        "poetry.lock",
        "Pipfile.lock",
        "package-lock.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "composer.lock",
        "Cargo.lock",
        "Gemfile.lock",
    }
)
_CODE_EXTS: Final[frozenset[str]] = frozenset({".py", ".java", ".php", ".ts", ".tsx", ".js", ".go", ".rs", ".rb"})
_DOC_EXTS: Final[frozenset[str]] = frozenset({".md", ".rst", ".adoc", ".txt"})
_TEST_FUNC_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:^\s*(?:async\s+)?def\s+test_[A-Za-z0-9_]+|^\s*@Test\b|^\s*#\[Test\]|^\s*public\s+function\s+test[A-Z_])",
    re.MULTILINE,
)


def _normalize_prefixes(target_root: str, rel_items: list[str]) -> list[str]:
    """Build normalized repo-relative POSIX path prefixes for target classification."""
    base = normalize_target_subpath(target_root)
    prefixes: list[str] = []
    for item in rel_items:
        sub = normalize_target_subpath(item)
        combined = f"{base}/{sub}".strip("/") if base else sub
        prefixes.append(combined)
    return prefixes


def _matches_any_prefix(repo_rel_path: str, prefixes: list[str]) -> bool:
    """Return True if `repo_rel_path` equals or resides inside any prefix in `prefixes`."""
    for pref in prefixes:
        if not pref:
            return True
        if repo_rel_path == pref or repo_rel_path.startswith(f"{pref}/"):
            return True
    return False


def _classify_repo_file(
    repo_rel_path: str,
    src_prefixes: list[str],
    test_prefixes: list[str],
    doc_prefixes: list[str],
) -> str | None:
    """Classify a repo-relative path into `'source'`, `'tests'`, `'docs'`, or `None` (ignored/lockfile)."""
    fname = repo_rel_path.rsplit("/", maxsplit=1)[-1]
    if fname in _LOCKFILE_NAMES or "/__pycache__/" in repo_rel_path or "/node_modules/" in repo_rel_path:
        return None
    suffix = Path(fname).suffix.lower()
    if _matches_any_prefix(repo_rel_path, test_prefixes) and suffix in _CODE_EXTS:
        return "tests"
    if _matches_any_prefix(repo_rel_path, doc_prefixes) and (suffix in _DOC_EXTS or repo_rel_path in doc_prefixes):
        return "docs"
    if _matches_any_prefix(repo_rel_path, src_prefixes) and suffix in _CODE_EXTS:
        return "source"
    return None


def _list_classified_tree_files(
    repo_dir: Path,
    safe_sha: str,
    src_prefixes: list[str],
    test_prefixes: list[str],
    doc_prefixes: list[str],
) -> list[tuple[str, str]]:
    """List `(path, kind)` pairs in `git ls-tree` at `safe_sha`."""
    ls_res = run_git_readonly(repo_dir, ["ls-tree", "-r", "--name-only", safe_sha], timeout_sec=10.0)
    if ls_res.exit_code != 0:
        return []
    classified: list[tuple[str, str]] = []
    for raw_path in ls_res.stdout.splitlines():
        fpath = raw_path.strip()
        if not fpath:
            continue
        kind = _classify_repo_file(fpath, src_prefixes, test_prefixes, doc_prefixes)
        if kind is not None:
            classified.append((fpath, kind))
    return classified


def _sample_tree_snapshot(
    repo_dir: Path,
    commit_sha: str,
    src_prefixes: list[str],
    test_prefixes: list[str],
    doc_prefixes: list[str],
) -> tuple[int, int, int, int, int]:
    """Measure `(source_loc, test_loc, docs_loc, test_files, test_cases)` at `commit_sha` via Git show."""
    safe_sha = validate_safe_git_ref(commit_sha)
    classified = _list_classified_tree_files(repo_dir, safe_sha, src_prefixes, test_prefixes, doc_prefixes)
    if not classified:
        return (0, 0, 0, 0, 0)

    source_loc = 0
    test_loc = 0
    docs_loc = 0
    test_files = 0
    test_cases = 0

    for fpath, kind in classified[:600]:
        show_res = run_git_readonly(repo_dir, ["show", f"{safe_sha}:{fpath}"], timeout_sec=5.0)
        if show_res.exit_code != 0:
            continue
        line_count = len(show_res.stdout.splitlines())
        if kind == "source":
            source_loc += line_count
        elif kind == "tests":
            test_loc += line_count
            test_files += 1
            test_cases += len(_TEST_FUNC_RE.findall(show_res.stdout))
        elif kind == "docs":
            docs_loc += line_count

    return (source_loc, test_loc, docs_loc, test_files, test_cases)


class _ParsedCommit:
    """Internal representation of a single parsed `git log --numstat` commit."""

    def __init__(self, sha: str, cdate: date, author: str) -> None:
        self.sha = sha
        self.cdate = cdate
        self.author = author
        self.file_stats: list[tuple[str, int, int]] = []


def _load_numstat_commits(
    repo_dir: Path,
    base_ref: str,
    since_date: date,
    until_date: date,
) -> list[_ParsedCommit]:
    """Load commits in `[since_date, until_date]` with per-file numstat additions/deletions."""
    safe_ref = validate_safe_git_ref(base_ref)
    res = run_git_readonly(
        repo_dir,
        [
            "log",
            safe_ref,
            f"--since={since_date.isoformat()}T00:00:00",
            f"--until={until_date.isoformat()}T23:59:59",
            "--date=short",
            "--format=@@COMMIT@@|%h|%ad|%ae",
            "--numstat",
        ],
        timeout_sec=15.0,
    )
    if res.exit_code != 0:
        return []

    commits: list[_ParsedCommit] = []
    current: _ParsedCommit | None = None
    for raw_line in res.stdout.splitlines():
        if raw_line.startswith("@@COMMIT@@|"):
            parts = raw_line.split("|", maxsplit=3)
            if len(parts) == 4:
                try:
                    cdate = date.fromisoformat(parts[2].strip())
                except ValueError:
                    continue
                current = _ParsedCommit(parts[1].strip(), cdate, parts[3].strip())
                commits.append(current)
        elif current is not None and "\t" in raw_line:
            fparts = raw_line.split("\t")
            if len(fparts) == 3 and fparts[0].isdigit() and fparts[1].isdigit():
                current.file_stats.append((fparts[2].strip(), int(fparts[0]), int(fparts[1])))
    return commits


def _resolve_commit_at_or_before(repo_dir: Path, base_ref: str, cutoff_date: date) -> str:
    """Find the latest commit SHA on `base_ref` on or before `cutoff_date`."""
    safe_ref = validate_safe_git_ref(base_ref)
    res = run_git_readonly(
        repo_dir,
        ["rev-list", "-n", "1", f"--before={cutoff_date.isoformat()}T23:59:59", safe_ref],
        timeout_sec=5.0,
    )
    if res.exit_code == 0 and res.stdout.strip():
        return res.stdout.strip()[:12]
    return ""


def _summarize_week_commits(
    wk_commits: list[_ParsedCommit],
    src_prefixes: list[str],
    test_prefixes: list[str],
    doc_prefixes: list[str],
) -> tuple[int, int, int]:
    """Return `(active_authors_count, lines_added, lines_deleted)` across `wk_commits`."""
    added = 0
    deleted = 0
    authors: set[str] = set()
    for c in wk_commits:
        authors.add(c.author)
        for fpath, a_cnt, d_cnt in c.file_stats:
            if _classify_repo_file(fpath, src_prefixes, test_prefixes, doc_prefixes) is not None:
                added += a_cnt
                deleted += d_cnt
    return (len(authors), added, deleted)


def _compute_churn_hotspots(
    commits: list[_ParsedCommit],
    churn_cutoff: date,
    src_prefixes: list[str],
    test_prefixes: list[str],
    doc_prefixes: list[str],
) -> list[ChurnHotspotItem]:
    """Identify recent multi-commit rework churn hotspots."""
    per_file: dict[str, list[int]] = {}
    for c in commits:
        if c.cdate < churn_cutoff:
            continue
        for fpath, a_cnt, d_cnt in c.file_stats:
            if _classify_repo_file(fpath, src_prefixes, test_prefixes, doc_prefixes) is None:
                continue
            acc = per_file.setdefault(fpath, [0, 0, 0])
            acc[0] += 1
            acc[1] += a_cnt
            acc[2] += d_cnt

    hotspots: list[ChurnHotspotItem] = []
    for fpath, (c_cnt, a_sum, d_sum) in per_file.items():
        if c_cnt < 2 or (a_sum + d_sum) < 10:
            continue
        rework = round(min(a_sum, d_sum) / max(a_sum, d_sum), 3) if max(a_sum, d_sum) > 0 else 0.0
        hotspots.append(
            ChurnHotspotItem(
                file_path=fpath,
                commits_count=c_cnt,
                lines_added=a_sum,
                lines_deleted=d_sum,
                rework_ratio=rework,
            )
        )
    hotspots.sort(key=lambda h: (-(h.lines_added + h.lines_deleted), -h.commits_count, h.file_path))
    return hotspots[:15]


def analyze_history_trajectory(
    repo_dir: Path,
    base_ref: str,
    *,
    target_root: str,
    source_targets: list[str],
    test_targets: list[str],
    doc_targets: list[str],
    as_of: date,
    lookback_weeks: int = 12,
) -> tuple[list[TrajectoryPoint], list[ChurnHotspotItem]]:
    """Compute weekly commit/LOC/test trajectories and recent rework-churn hotspots."""
    src_prefixes = _normalize_prefixes(target_root, source_targets)
    test_prefixes = _normalize_prefixes(target_root, test_targets)
    doc_prefixes = _normalize_prefixes(target_root, doc_targets)

    effective_weeks = max(1, min(lookback_weeks, 26))
    start_window = as_of - timedelta(days=effective_weeks * 7 - 1)
    commits = _load_numstat_commits(repo_dir, base_ref, start_window, as_of)

    points: list[TrajectoryPoint] = []
    snapshot_cache: dict[str, tuple[int, int, int, int, int]] = {}

    for wk_idx in range(effective_weeks):
        wk_start = start_window + timedelta(days=wk_idx * 7)
        wk_end = min(as_of, wk_start + timedelta(days=6))
        wk_commits = [c for c in commits if wk_start <= c.cdate <= wk_end]
        anchor_sha = _resolve_commit_at_or_before(repo_dir, base_ref, wk_end)
        if not anchor_sha and not wk_commits:
            continue

        authors_cnt, added, deleted = _summarize_week_commits(wk_commits, src_prefixes, test_prefixes, doc_prefixes)
        if anchor_sha:
            if anchor_sha not in snapshot_cache:
                snapshot_cache[anchor_sha] = _sample_tree_snapshot(
                    repo_dir, anchor_sha, src_prefixes, test_prefixes, doc_prefixes
                )
            s_loc, t_loc, d_loc, t_files, t_cases = snapshot_cache[anchor_sha]
        else:
            s_loc, t_loc, d_loc, t_files, t_cases = (0, 0, 0, 0, 0)

        points.append(
            TrajectoryPoint(
                period_label=f"W{wk_idx + 1} ({wk_end.strftime('%m-%d')})",
                period_end_date=wk_end.isoformat(),
                commit_sha=anchor_sha,
                commits_count=len(wk_commits),
                active_authors=authors_cnt,
                lines_added=added,
                lines_deleted=deleted,
                source_loc=s_loc,
                test_loc=t_loc,
                docs_loc=d_loc,
                test_to_code_ratio=round(t_loc / s_loc, 3) if s_loc > 0 else 0.0,
                static_test_files=t_files,
                static_test_cases=t_cases,
            )
        )

    hotspots = _compute_churn_hotspots(commits, as_of - timedelta(days=14), src_prefixes, test_prefixes, doc_prefixes)
    return (points, hotspots)
