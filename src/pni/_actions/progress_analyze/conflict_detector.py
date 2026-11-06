# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Non-destructive 3-stage Git conflict detection (`git merge-tree` & working-tree checks)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from pni._actions.progress_analyze.git_exec import (
    detect_git_version,
    run_git_readonly,
    validate_safe_git_ref,
)
from pni._actions.progress_analyze.models import (
    BranchHealthFact,
    OverlappingFileHotspot,
    WorkingTreeConflictState,
)

_HEX_OID_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{40,64}$")
_CONFLICT_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"^(?:<{7}\s|>{7}\s)", re.MULTILINE)
_SCANNABLE_SUFFIXES: Final[frozenset[str]] = frozenset(
    {".py", ".java", ".php", ".js", ".ts", ".tsx", ".go", ".rs", ".rb", ".yaml", ".yml", ".json", ".toml", ".md"}
)
_IN_PROGRESS_SENTINELS: Final[tuple[tuple[str, str], ...]] = (
    ("MERGE_HEAD", "merge"),
    ("REBASE_HEAD", "rebase"),
    ("rebase-merge", "rebase"),
    ("rebase-apply", "rebase"),
    ("CHERRY_PICK_HEAD", "cherry-pick"),
    ("REVERT_HEAD", "revert"),
)


def _resolve_git_dir(repo_dir: Path) -> Path | None:
    """Resolve the active `.git` directory (supporting worktrees and submodules)."""
    res = run_git_readonly(repo_dir, ["rev-parse", "--git-dir"], timeout_sec=5.0)
    if res.exit_code != 0 or not res.stdout.strip():
        return None
    raw = Path(res.stdout.strip())
    return raw if raw.is_absolute() else (repo_dir / raw).resolve()


def _scan_committed_conflict_markers(repo_dir: Path, target_dirs: list[str]) -> list[str]:
    """Scan tracked text files under `target_dirs` for accidental `<<<<<<< ` / `>>>>>>> ` markers."""
    flagged: list[str] = []
    root_resolved = repo_dir.resolve()
    for rel_dir in target_dirs:
        candidate = (root_resolved / rel_dir).resolve()
        if not candidate.exists() or not candidate.is_relative_to(root_resolved):
            continue
        files = [candidate] if candidate.is_file() else list(candidate.rglob("*"))
        for fpath in files:
            if not fpath.is_file() or fpath.suffix.lower() not in _SCANNABLE_SUFFIXES:
                continue
            try:
                if fpath.stat().st_size > 1_000_000:
                    continue
                text = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if _CONFLICT_MARKER_RE.search(text):
                flagged.append(str(fpath.relative_to(root_resolved)).replace("\\", "/"))
    return sorted(set(flagged))


def inspect_working_tree_conflicts(repo_dir: Path, scan_paths: list[str]) -> WorkingTreeConflictState:
    """Detect Stage C1 active unmerged index paths, paused Git ops, and committed conflict markers."""
    unmerged_res = run_git_readonly(repo_dir, ["ls-files", "-u"], timeout_sec=5.0)
    unmerged_files: set[str] = set()
    if unmerged_res.exit_code == 0:
        for line in unmerged_res.stdout.splitlines():
            parts = line.split("\t", maxsplit=1)
            if len(parts) == 2 and parts[1].strip():
                unmerged_files.add(parts[1].strip())

    ops: list[str] = []
    git_dir = _resolve_git_dir(repo_dir)
    if git_dir is not None and git_dir.exists():
        seen_ops: set[str] = set()
        for sentinel, label in _IN_PROGRESS_SENTINELS:
            if (git_dir / sentinel).exists() and label not in seen_ops:
                seen_ops.add(label)
                ops.append(label)

    markers = _scan_committed_conflict_markers(repo_dir, scan_paths)
    return WorkingTreeConflictState(
        unmerged_index_files=sorted(unmerged_files),
        in_progress_operations=ops,
        committed_conflict_markers=markers,
    )


def _simulate_merge_modern(repo_dir: Path, base_ref: str, branch_ref: str) -> tuple[bool, list[str]]:
    """Run Git 2.38+ `git merge-tree --write-tree --name-only` in memory without touching worktree."""
    res = run_git_readonly(
        repo_dir,
        ["merge-tree", "--write-tree", "--name-only", base_ref, branch_ref],
        timeout_sec=10.0,
    )
    if res.exit_code == 0:
        return (False, [])

    conflicting: list[str] = []
    lines = res.stdout.splitlines()
    for idx, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if idx == 0 and _HEX_OID_RE.match(stripped):
            continue
        if not stripped:
            break
        conflicting.append(stripped)
    return (True, sorted(set(conflicting)))


def _simulate_merge_legacy(
    repo_dir: Path,
    merge_base_sha: str,
    base_ref: str,
    branch_ref: str,
) -> tuple[bool, list[str]]:
    """Fallback 3-argument `git merge-tree` parser for Git versions older than 2.38."""
    if not merge_base_sha:
        return (False, [])
    safe_mb = validate_safe_git_ref(merge_base_sha)
    res = run_git_readonly(repo_dir, ["merge-tree", safe_mb, base_ref, branch_ref], timeout_sec=10.0)
    if "+<<<<<<<" not in res.stdout and "changed in both" not in res.stdout:
        return (False, [])

    files: set[str] = set()
    for line in res.stdout.splitlines():
        if line.startswith(("  our    ", "  their  ", "  base   ")):
            parts = line.split(maxsplit=3)
            if len(parts) == 4:
                files.add(parts[3].strip())
    return (True, sorted(files))


def simulate_branch_merge_conflict(
    repo_dir: Path,
    base_ref: str,
    branch_ref: str,
    merge_base_sha: str = "",
) -> tuple[bool, list[str]]:
    """Simulate merging `branch_ref` into `base_ref` cleanly in memory (`(has_conflict, files)`)."""
    safe_base = validate_safe_git_ref(base_ref)
    safe_branch = validate_safe_git_ref(branch_ref)
    if detect_git_version(repo_dir) >= (2, 38):
        return _simulate_merge_modern(repo_dir, safe_base, safe_branch)
    return _simulate_merge_legacy(repo_dir, merge_base_sha, safe_base, safe_branch)


def detect_overlapping_branch_files(branches: list[BranchHealthFact]) -> list[OverlappingFileHotspot]:
    """Identify Stage C3 files modified concurrently by two or more active unmerged branches."""
    file_to_branches: dict[str, list[str]] = {}
    for br in branches:
        if br.is_merged or br.ahead_commits == 0:
            continue
        for fpath in br.touched_files:
            file_to_branches.setdefault(fpath, []).append(br.branch_name)

    hotspots = [
        OverlappingFileHotspot(file_path=fp, branches=sorted(set(brs)))
        for fp, brs in file_to_branches.items()
        if len(set(brs)) >= 2
    ]
    hotspots.sort(key=lambda h: (-len(h.branches), h.file_path))
    return hotspots
