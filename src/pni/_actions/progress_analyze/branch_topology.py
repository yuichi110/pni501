# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Git branch lineage, ahead/behind divergence, and merge-methodology compliance analyzer."""

from __future__ import annotations

import fnmatch
import re
from datetime import date
from pathlib import Path
from typing import Final

from pni._actions.progress_analyze.conflict_detector import simulate_branch_merge_conflict
from pni._actions.progress_analyze.git_exec import run_git_readonly, validate_safe_git_ref
from pni._actions.progress_analyze.models import (
    BranchHealthFact,
    GitPolicy,
    GitPolicyViolation,
)

_CONVENTIONAL_COMMIT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(?:\([a-zA-Z0-9_./-]+\))?!?: .+"
)
_WIP_SUBJECT_RE: Final[re.Pattern[str]] = re.compile(r"^(?:wip\b|fixup!|squash!|temp\b|tmp\b)", re.IGNORECASE)


def resolve_effective_base_branch(repo_dir: Path, policy: GitPolicy, current_branch: str) -> str:
    """Resolve the active integration/trunk reference present in `repo_dir`."""
    candidates = [
        b
        for b in (
            policy.integration_branch,
            policy.trunk_branch,
            f"origin/{policy.integration_branch}" if policy.integration_branch else None,
            f"origin/{policy.trunk_branch}",
            current_branch,
            "main",
            "master",
        )
        if b
    ]
    for cand in candidates:
        try:
            safe_cand = validate_safe_git_ref(cand)
        except ValueError:
            continue
        res = run_git_readonly(repo_dir, ["rev-parse", "--verify", "--quiet", safe_cand], timeout_sec=5.0)
        if res.exit_code == 0 and res.stdout.strip():
            return safe_cand
    return policy.trunk_branch


def _list_repo_branches(repo_dir: Path) -> list[tuple[str, str, bool, str]]:
    """List `(display_name, git_ref, is_remote, committer_iso_date)` deduplicating local vs origin."""
    res = run_git_readonly(
        repo_dir,
        [
            "for-each-ref",
            "--format=%(refname:short)|%(refname)|%(committerdate:short)",
            "refs/heads",
            "refs/remotes/origin",
        ],
        timeout_sec=10.0,
    )
    if res.exit_code != 0:
        return []

    local_names: set[str] = set()
    rows: list[tuple[str, str, bool, str]] = []
    raw_items: list[tuple[str, str, str]] = []
    for line in res.stdout.splitlines():
        parts = line.split("|")
        if len(parts) != 3:
            continue
        short_name, full_ref, cdate = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if short_name in {"origin/HEAD", "origin"} or full_ref.endswith("/HEAD"):
            continue
        raw_items.append((short_name, full_ref, cdate))
        if full_ref.startswith("refs/heads/"):
            local_names.add(short_name)

    for short_name, full_ref, cdate in raw_items:
        is_remote = full_ref.startswith("refs/remotes/origin/")
        clean_name = short_name.removeprefix("origin/") if is_remote else short_name
        if is_remote and clean_name in local_names:
            continue
        try:
            validate_safe_git_ref(short_name)
        except ValueError:
            continue
        rows.append((clean_name, short_name, is_remote, cdate))
    return rows


def _matches_allowed_patterns(branch_name: str, policy: GitPolicy) -> bool:
    """Check whether `branch_name` matches `git_policy.allowed_branch_patterns` or trunk/integration."""
    exempt = {policy.trunk_branch, policy.integration_branch or "", "main", "master", "develop"}
    if branch_name in exempt:
        return True
    if not policy.allowed_branch_patterns:
        return True
    return any(fnmatch.fnmatch(branch_name, pat) for pat in policy.allowed_branch_patterns)


def _compute_diff_stats(repo_dir: Path, merge_base_sha: str, branch_ref: str) -> tuple[int, list[str]]:
    """Compute `(total_changed_lines, touched_files)` from `merge_base_sha..branch_ref`."""
    if not merge_base_sha:
        return (0, [])
    res = run_git_readonly(
        repo_dir,
        ["diff", "--numstat", f"{merge_base_sha}..{branch_ref}"],
        timeout_sec=10.0,
    )
    if res.exit_code != 0:
        return (0, [])
    changed = 0
    touched: list[str] = []
    for line in res.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add_s, del_s, fpath = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if add_s.isdigit():
            changed += int(add_s)
        if del_s.isdigit():
            changed += int(del_s)
        if fpath:
            touched.append(fpath)
    return (changed, sorted(set(touched)))


def _inspect_single_branch(
    repo_dir: Path,
    clean_name: str,
    git_ref: str,
    is_remote: bool,
    last_date_str: str,
    base_ref: str,
    policy: GitPolicy,
    as_of: date,
) -> BranchHealthFact:
    """Gather divergence, freshness, policy, and merge-conflict facts for one branch."""
    mb_res = run_git_readonly(repo_dir, ["merge-base", base_ref, git_ref], timeout_sec=5.0)
    mb_sha = mb_res.stdout.strip()[:12] if mb_res.exit_code == 0 and mb_res.stdout.strip() else ""

    branched_at = ""
    if mb_sha:
        bd_res = run_git_readonly(repo_dir, ["show", "-s", "--format=%cs", mb_sha], timeout_sec=5.0)
        if bd_res.exit_code == 0:
            branched_at = bd_res.stdout.strip()

    lr_res = run_git_readonly(
        repo_dir,
        ["rev-list", "--left-right", "--count", f"{base_ref}...{git_ref}"],
        timeout_sec=5.0,
    )
    behind, ahead = 0, 0
    if lr_res.exit_code == 0 and lr_res.stdout.strip():
        parts = lr_res.stdout.strip().split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            behind, ahead = int(parts[0]), int(parts[1])

    is_merged = ahead == 0
    age_days = 0
    if last_date_str:
        try:
            age_days = max(0, (as_of - date.fromisoformat(last_date_str)).days)
        except ValueError:
            age_days = 0

    changed_lines, touched_files = _compute_diff_stats(repo_dir, mb_sha, git_ref) if ahead > 0 else (0, [])
    has_conflict, conflict_files = (
        simulate_branch_merge_conflict(repo_dir, base_ref, git_ref, merge_base_sha=mb_sha)
        if ahead > 0
        else (False, [])
    )

    th = policy.thresholds
    is_stale = (not is_merged) and age_days >= th.stale_branch_days
    naming_ok = _matches_allowed_patterns(clean_name, policy)

    return BranchHealthFact(
        branch_name=clean_name,
        is_remote=is_remote,
        merge_base_sha=mb_sha,
        branched_at=branched_at,
        last_commit_date=last_date_str,
        age_days=age_days,
        ahead_commits=ahead,
        behind_commits=behind,
        changed_lines=changed_lines,
        touched_files=touched_files,
        is_merged=is_merged,
        is_stale=is_stale,
        naming_compliant=naming_ok,
        exceeds_behind=(not is_merged) and behind > th.max_behind_commits,
        exceeds_ahead=(not is_merged) and ahead > th.max_ahead_commits,
        exceeds_size=(not is_merged) and changed_lines > th.max_unmerged_changed_lines,
        clean_mergeable=not has_conflict,
        has_conflict=has_conflict,
        conflicting_files=conflict_files,
    )


def _inspect_merge_commit(
    short_sha: str,
    subject: str,
    policy: GitPolicy,
    foxtrot_re: re.Pattern[str],
    violations: list[GitPolicyViolation],
) -> int:
    """Evaluate a merge commit on trunk and return 1 if it is a Foxtrot merge, else 0."""
    if policy.merge_strategy in {"squash_only", "rebase_ff"}:
        violations.append(
            GitPolicyViolation(
                code="unexpected_merge_commit_on_linear_trunk",
                severity="medium",
                branch_or_sha=short_sha,
                detail=(
                    f"Merge commit '{short_sha}' ('{subject}') violates "
                    f"merge_strategy='{policy.merge_strategy}'."
                ),
            )
        )
    if foxtrot_re.search(subject):
        if policy.forbid_foxtrot_merges:
            violations.append(
                GitPolicyViolation(
                    code="foxtrot_merge_detected",
                    severity="high",
                    branch_or_sha=short_sha,
                    detail=f"Foxtrot merge '{short_sha}' ('{subject}') inverted first-parent trunk lineage.",
                )
            )
        return 1
    return 0


def _inspect_non_merge_commit(
    short_sha: str,
    subject: str,
    parent_count: int,
    base_ref: str,
    policy: GitPolicy,
    violations: list[GitPolicyViolation],
) -> int:
    """Evaluate a non-merge commit on trunk and return 1 if Conventional Commit compliant."""
    if policy.merge_strategy == "merge_commit" and policy.forbid_direct_trunk_commits and parent_count == 1:
        violations.append(
            GitPolicyViolation(
                code="direct_trunk_commit",
                severity="medium",
                branch_or_sha=short_sha,
                detail=f"Non-merge commit '{short_sha}' ('{subject}') landed directly on '{base_ref}'.",
            )
        )
    return 1 if _CONVENTIONAL_COMMIT_RE.match(subject) else 0


def _audit_trunk_history(
    repo_dir: Path,
    base_ref: str,
    policy: GitPolicy,
) -> tuple[float, int, int, int, list[GitPolicyViolation]]:
    """Inspect `first-parent` trunk commits for merge strategy, Foxtrot merges, WIP, and commit style."""
    res = run_git_readonly(
        repo_dir,
        ["log", "--first-parent", "-n", "100", "--format=%h|%P|%s", base_ref],
        timeout_sec=10.0,
    )
    if res.exit_code != 0 or not res.stdout.strip():
        return (1.0, 0, 0, 0, [])

    violations: list[GitPolicyViolation] = []
    total_non_merge = 0
    conventional_ok = 0
    merge_commits = 0
    foxtrot_count = 0
    wip_count = 0

    base_plain = base_ref.removeprefix("origin/")
    foxtrot_re = re.compile(
        rf"\bMerge (?:remote-tracking )?branch '(?:origin/)?{re.escape(base_plain)}'\s+into\b",
        re.IGNORECASE,
    )

    for line in res.stdout.splitlines():
        parts = line.split("|", maxsplit=2)
        if len(parts) != 3:
            continue
        short_sha, parents_raw, subject = parts[0].strip(), parts[1].strip(), parts[2].strip()
        parents = [p for p in parents_raw.split() if p]
        if len(parents) >= 2:
            merge_commits += 1
            foxtrot_count += _inspect_merge_commit(short_sha, subject, policy, foxtrot_re, violations)
        else:
            total_non_merge += 1
            conventional_ok += _inspect_non_merge_commit(
                short_sha, subject, len(parents), base_ref, policy, violations
            )

        if _WIP_SUBJECT_RE.search(subject):
            wip_count += 1
            if policy.forbid_wip_commits_on_trunk:
                violations.append(
                    GitPolicyViolation(
                        code="wip_commit_on_trunk",
                        severity="low",
                        branch_or_sha=short_sha,
                        detail=f"Un-squashed WIP/fixup commit '{short_sha}' ('{subject}') found on '{base_ref}'.",
                    )
                )

    conv_ratio = round(conventional_ok / total_non_merge, 3) if total_non_merge > 0 else 1.0
    if policy.commit_convention == "conventional_commits" and total_non_merge >= 3 and conv_ratio < 0.7:
        violations.append(
            GitPolicyViolation(
                code="low_conventional_commit_compliance",
                severity="low",
                branch_or_sha=base_ref,
                detail=(
                    f"Only {conventional_ok}/{total_non_merge} ({conv_ratio * 100:.0f}%) non-merge commits on "
                    f"'{base_ref}' follow Conventional Commits."
                ),
            )
        )
    return (conv_ratio, merge_commits, foxtrot_count, wip_count, violations)


def analyze_branch_topology_and_policy(
    repo_dir: Path,
    policy: GitPolicy,
    current_branch: str,
    as_of: date,
) -> tuple[str, list[BranchHealthFact], float, int, int, int, list[GitPolicyViolation]]:
    """Analyze all branches and trunk history against `policy`."""
    base_ref = resolve_effective_base_branch(repo_dir, policy, current_branch)
    base_plain = base_ref.removeprefix("origin/")
    raw_branches = _list_repo_branches(repo_dir)

    branch_facts: list[BranchHealthFact] = []
    branch_violations: list[GitPolicyViolation] = []

    for clean_name, git_ref, is_remote, last_date in raw_branches:
        if clean_name == base_plain:
            continue
        fact = _inspect_single_branch(repo_dir, clean_name, git_ref, is_remote, last_date, base_ref, policy, as_of)
        branch_facts.append(fact)

        if fact.has_conflict:
            branch_violations.append(
                GitPolicyViolation(
                    code="branch_merge_conflict",
                    severity="high",
                    branch_or_sha=clean_name,
                    detail=(
                        f"Branch '{clean_name}' has merge conflicts against '{base_ref}' in "
                        f"{len(fact.conflicting_files)} file(s): {fact.conflicting_files[:5]}."
                    ),
                )
            )
        if not fact.naming_compliant and not fact.is_merged:
            branch_violations.append(
                GitPolicyViolation(
                    code="branch_naming_violation",
                    severity="low",
                    branch_or_sha=clean_name,
                    detail=f"Branch '{clean_name}' does not match allowed patterns {policy.allowed_branch_patterns}.",
                )
            )
        if fact.is_stale:
            branch_violations.append(
                GitPolicyViolation(
                    code="stale_unmerged_branch",
                    severity="medium",
                    branch_or_sha=clean_name,
                    detail=f"Unmerged branch '{clean_name}' has been inactive for {fact.age_days} days.",
                )
            )
        if fact.exceeds_behind:
            branch_violations.append(
                GitPolicyViolation(
                    code="branch_severely_behind_trunk",
                    severity="medium",
                    branch_or_sha=clean_name,
                    detail=f"Branch '{clean_name}' is {fact.behind_commits} commits behind '{base_ref}'.",
                )
            )
        if fact.exceeds_size or fact.exceeds_ahead:
            branch_violations.append(
                GitPolicyViolation(
                    code="oversized_unmerged_branch",
                    severity="medium",
                    branch_or_sha=clean_name,
                    detail=(
                        f"Branch '{clean_name}' carries {fact.ahead_commits} unmerged commits / "
                        f"{fact.changed_lines} changed lines."
                    ),
                )
            )

    branch_facts.sort(key=lambda b: (b.is_merged, not b.has_conflict, -b.ahead_commits, b.branch_name))
    conv_ratio, merge_cnt, foxtrot_cnt, wip_cnt, trunk_violations = _audit_trunk_history(repo_dir, base_ref, policy)
    all_violations = branch_violations + trunk_violations
    return (base_ref, branch_facts, conv_ratio, merge_cnt, foxtrot_cnt, wip_cnt, all_violations)
