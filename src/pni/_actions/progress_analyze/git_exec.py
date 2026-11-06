# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Hardened, read-only Git CLI wrapper preventing option injection and working-tree mutation."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Final

from pni._actions.runtime_check.engine_detect import CommandExecResult, run_safe_command

_SAFE_GIT_REF_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@~^-]{0,240}$")
_GIT_VERSION_RE: Final[re.Pattern[str]] = re.compile(r"(\d+)\.(\d+)")
_DEFAULT_GIT_TIMEOUT_SEC: Final[float] = 15.0


def validate_safe_git_ref(ref: str) -> str:
    """Validate a Git branch, tag, or commit reference against option/traversal injection.

    Rejects leading '-', '..', whitespace, control characters, and shell metacharacters.
    """
    cleaned = ref.strip()
    if (
        not cleaned
        or cleaned.startswith("-")
        or ".." in cleaned
        or "//" in cleaned
        or cleaned.endswith(".lock")
        or not _SAFE_GIT_REF_RE.match(cleaned)
    ):
        msg = f"Unsafe or malformed Git reference rejected: {ref!r}"
        raise ValueError(msg)
    return cleaned


def resolve_git_binary() -> str | None:
    """Locate the system `git` executable via PATH."""
    return shutil.which("git")


def run_git_readonly(
    repo_dir: Path,
    git_args: list[str],
    *,
    timeout_sec: float = _DEFAULT_GIT_TIMEOUT_SEC,
) -> CommandExecResult:
    """Execute a read-only Git subcommand with `shell=False` and terminal prompts disabled."""
    git_bin = resolve_git_binary()
    if git_bin is None:
        return CommandExecResult(
            exit_code=127,
            timed_out=False,
            duration_sec=0.0,
            stdout="",
            stderr="git executable not found on PATH",
        )
    resolved_dir = repo_dir.resolve()
    cmd = [git_bin, "-c", "core.quotepath=false", *git_args]
    return run_safe_command(cmd, timeout_sec=timeout_sec, cwd=resolved_dir)


def detect_git_version(repo_dir: Path) -> tuple[int, int]:
    """Return `(major, minor)` version of the installed Git CLI, or `(0, 0)` if unavailable."""
    res = run_git_readonly(repo_dir, ["--version"], timeout_sec=5.0)
    if res.exit_code != 0:
        return (0, 0)
    match = _GIT_VERSION_RE.search(res.stdout)
    if match is None:
        return (0, 0)
    return (int(match.group(1)), int(match.group(2)))


def inspect_git_repo_head(repo_dir: Path) -> tuple[bool, str, str, bool, bool]:
    """Inspect basic Git repository state `(git_available, branch, short_sha, is_dirty, is_shallow)`."""
    inside = run_git_readonly(repo_dir, ["rev-parse", "--is-inside-work-tree"], timeout_sec=5.0)
    if inside.exit_code != 0 or inside.stdout.strip().lower() != "true":
        return (False, "", "", False, False)

    head_res = run_git_readonly(repo_dir, ["rev-parse", "--short=8", "HEAD"], timeout_sec=5.0)
    head_sha = head_res.stdout.strip() if head_res.exit_code == 0 else ""

    br_res = run_git_readonly(repo_dir, ["symbolic-ref", "--short", "-q", "HEAD"], timeout_sec=5.0)
    branch = br_res.stdout.strip() if br_res.exit_code == 0 else "HEAD"

    status_res = run_git_readonly(repo_dir, ["status", "--porcelain", "--untracked-files=no"], timeout_sec=5.0)
    is_dirty = bool(status_res.stdout.strip()) if status_res.exit_code == 0 else False

    shallow_res = run_git_readonly(repo_dir, ["rev-parse", "--is-shallow-repository"], timeout_sec=5.0)
    is_shallow = shallow_res.stdout.strip().lower() == "true" if shallow_res.exit_code == 0 else False

    return (True, branch, head_sha, is_dirty, is_shallow)
