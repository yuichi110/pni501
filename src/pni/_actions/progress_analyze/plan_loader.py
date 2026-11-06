# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Progress plan scaffolding (`pni progress init`), YAML loading, and SHA-256 baseline hashing."""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from pathlib import Path

import yaml

from pni._actions.progress_analyze.models import (
    ProgressPlanDefinition,
    ProgressPreflightHint,
)
from pni._cache import default_progress_plan_rel_path


def resolve_bounded_plan_path(project_root: Path, plan_file_or_target: str, fallback_id: str = "") -> tuple[Path, str]:
    """Resolve `.pni/progress/<target>.yaml` strictly within `project_root`."""
    raw = plan_file_or_target.strip()
    if not raw:
        rel_str = default_progress_plan_rel_path(fallback_id or "project_progress")
    elif raw.endswith((".yaml", ".yml")) and ("/" in raw or raw.startswith(".pni/")):
        rel_str = raw
    else:
        rel_str = default_progress_plan_rel_path(raw)

    root_resolved = project_root.resolve()
    candidate = (root_resolved / rel_str).resolve()
    if candidate == root_resolved or not candidate.is_relative_to(root_resolved):
        msg = f"Progress plan path escapes workspace root: {plan_file_or_target!r}"
        raise ValueError(msg)
    normalized_rel = str(candidate.relative_to(root_resolved)).replace("\\", "/")
    return candidate, normalized_rel


def render_progress_plan_template(
    plan_id: str,
    *,
    source_dir: str = "src",
    test_dir: str = "tests",
    today: date | None = None,
) -> str:
    """Render a commented YAML starter template for `.pni/progress/<target>.yaml`."""
    d0 = today or date.today()
    d_m1 = (d0 + timedelta(days=14)).isoformat()
    d_m2 = (d0 + timedelta(days=28)).isoformat()
    d_mid = (d0 + timedelta(days=15)).isoformat()
    start_s = d0.isoformat()

    return (
        f"# PNI Project Progress & Git Governance Plan ({plan_id})\n"
        f"# Edit milestones, tasks, and git_policy directly, then verify with: pni progress validate {plan_id}\n"
        f"id: {plan_id}\n"
        f'name: "{plan_id} Development Progress Plan"\n'
        f'start_date: "{start_s}"\n'
        f'target_date: "{d_m2}"\n'
        f'description: "Milestone schedule and Git branching/merge governance policy."\n\n'
        "git_policy:\n"
        "  # github_flow | trunk_based | git_flow | release_flow | custom\n"
        '  methodology: "github_flow"\n'
        '  trunk_branch: "main"\n'
        "  integration_branch: null\n"
        "  # squash_only | rebase_ff | merge_commit | any\n"
        '  merge_strategy: "squash_only"\n'
        "  forbid_foxtrot_merges: true\n"
        "  forbid_direct_trunk_commits: false\n"
        "  forbid_wip_commits_on_trunk: true\n"
        "  allowed_branch_patterns:\n"
        '    - "feat/*"\n'
        '    - "fix/*"\n'
        '    - "refactor/*"\n'
        '    - "docs/*"\n'
        '    - "chore/*"\n'
        '    - "hotfix/*"\n'
        '  commit_convention: "conventional_commits"\n'
        "  thresholds:\n"
        "    stale_branch_days: 14\n"
        "    max_behind_commits: 30\n"
        "    max_ahead_commits: 25\n"
        "    max_unmerged_changed_lines: 800\n\n"
        "milestones:\n"
        "  - id: M1\n"
        '    name: "Core Implementation"\n'
        f'    due_date: "{d_m1}"\n'
        "  - id: M2\n"
        '    name: "Integration & Stabilization"\n'
        f'    due_date: "{d_m2}"\n\n'
        "tasks:\n"
        "  - id: T-01\n"
        "    milestone: M1\n"
        '    name: "Core Module & Unit Tests"\n'
        f'    planned_start: "{start_s}"\n'
        f'    planned_end: "{d_m1}"\n'
        '    status: "in_progress"\n'
        "    declared_progress: 50\n"
        '    branch_pattern: "feat/*"\n'
        "    expected_paths:\n"
        f'      - "{source_dir}"\n'
        f'      - "{test_dir}"\n'
        '    acceptance_summary: "Core feature modules and unit test suite implemented."\n'
        "    depends_on: []\n\n"
        "  - id: T-02\n"
        "    milestone: M2\n"
        '    name: "End-to-End Verification & Release Readiness"\n'
        f'    planned_start: "{d_mid}"\n'
        f'    planned_end: "{d_m2}"\n'
        '    status: "todo"\n'
        "    declared_progress: 0\n"
        '    branch_pattern: "fix/*"\n'
        "    expected_paths:\n"
        f'      - "{test_dir}"\n'
        '    acceptance_summary: "All branch conflicts resolved and regression tests passing."\n'
        "    depends_on:\n"
        '      - "T-01"\n'
    )


def scaffold_progress_plan(
    project_root: Path,
    target_or_id: str,
    *,
    source_dir: str = "src",
    test_dir: str = "tests",
    force: bool = False,
) -> tuple[Path, str, bool]:
    """Create `.pni/progress/<target>.yaml` if absent (or overwrite when `force=True`).

    Returns:
        tuple[Path, str, bool]: `(absolute_path, workspace_rel_path, was_written)`.
    """
    plan_path, rel_str = resolve_bounded_plan_path(project_root, target_or_id)
    if plan_path.exists() and not force:
        return plan_path, rel_str, False

    plan_id = plan_path.stem
    content = render_progress_plan_template(plan_id, source_dir=source_dir, test_dir=test_dir)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(content, encoding="utf-8")
    return plan_path, rel_str, True


def load_and_validate_progress_plan(
    project_root: Path,
    plan_file_or_target: str,
    *,
    fallback_id: str = "",
) -> tuple[ProgressPlanDefinition, str, str, list[ProgressPreflightHint]]:
    """Load, validate, and hash `.pni/progress/<target>.yaml` using `yaml.safe_load`.

    Returns:
        tuple[ProgressPlanDefinition, str, str, list[ProgressPreflightHint]]:
            `(validated_plan, workspace_rel_path, sha256_hex, preflight_hints)`.
    """
    plan_path, rel_str = resolve_bounded_plan_path(project_root, plan_file_or_target, fallback_id=fallback_id)
    if not plan_path.is_file():
        init_arg = fallback_id or plan_path.stem
        msg = (
            f"Progress plan file '{rel_str}' does not exist. "
            f"Create and tailor it first with 'pni progress init {init_arg}' "
            f"(then verify with 'pni progress validate {rel_str}')."
        )
        raise FileNotFoundError(msg)

    raw_bytes = plan_path.read_bytes()
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest()
    raw_obj = yaml.safe_load(raw_bytes.decode("utf-8"))
    if not isinstance(raw_obj, dict):
        msg = f"Progress plan '{rel_str}' must be a YAML mapping."
        raise ValueError(msg)

    plan = ProgressPlanDefinition.model_validate(raw_obj)
    hints: list[ProgressPreflightHint] = []
    if plan.git_policy.methodology == "git_flow" and not plan.git_policy.integration_branch:
        hints.append(
            ProgressPreflightHint(
                code="git_flow_missing_integration_branch",
                message=(
                    "git_policy.methodology is 'git_flow' without 'integration_branch' "
                    "(consider setting integration_branch: 'develop')."
                ),
            )
        )
    if not plan.tasks:
        hints.append(
            ProgressPreflightHint(
                code="empty_tasks_list",
                message=f"Progress plan '{rel_str}' defines 0 tasks; add planned tasks under 'tasks:' before running.",
            )
        )
    return plan, rel_str, sha256_hex, hints
