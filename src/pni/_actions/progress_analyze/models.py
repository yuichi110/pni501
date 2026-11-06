# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for project progress plans, Git governance, history ledgers, and progress results."""

from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

GitMethodology = Literal["github_flow", "trunk_based", "git_flow", "release_flow", "custom"]
GitMergeStrategy = Literal["squash_only", "rebase_ff", "merge_commit", "any"]
CommitConvention = Literal["conventional_commits", "freeform"]
TaskDeclaredStatus = Literal["todo", "in_progress", "blocked", "done"]
TaskScheduleState = Literal["upcoming", "active", "overdue", "completed_declared"]
DeliveryStatus = Literal["on_track", "at_risk", "delayed", "blocked"]
ProgressSeverity = Literal["critical", "high", "medium", "low", "info"]
ProgressPriority = Literal["P0", "P1", "P2"]

_STATUS_DEFAULT_PROGRESS: dict[TaskDeclaredStatus, int] = {
    "todo": 0,
    "in_progress": 50,
    "blocked": 25,
    "done": 100,
}


def _parse_iso_date(raw: str, field_name: str) -> date:
    """Parse and validate a strict YYYY-MM-DD date string."""
    cleaned = raw.strip()
    try:
        return date.fromisoformat(cleaned)
    except ValueError as exc:
        msg = f"Invalid ISO date '{raw}' in '{field_name}' (expected YYYY-MM-DD)."
        raise ValueError(msg) from exc


def _validate_safe_rel_paths(paths: list[str], field_name: str) -> None:
    """Reject absolute paths or parent-directory traversal ('..') in user-configured paths."""
    invalid = [
        p
        for p in paths
        if p.strip().startswith("/") or ".." in [seg for seg in p.replace("\\", "/").split("/") if seg]
    ]
    if invalid:
        msg = f"Invalid non-relative path(s) in '{field_name}': {invalid}."
        raise ValueError(msg)


def resolve_progress_result_rel_path(
    output_dir: str,
    target: str,
    explicit_progress_path: str = "",
) -> str:
    """Resolve workspace-relative path for `<output_dir>/<target>_progress.json`.

    Avoids duplicate `_progress_progress.json` suffixes when `target` already ends with `_progress`.
    """
    if explicit_progress_path.strip():
        return explicit_progress_path.strip()
    clean_out = output_dir.rstrip("/") or "reports"
    clean_tgt = target.strip().removesuffix("_src") or "project_progress"
    stem = clean_tgt if clean_tgt.endswith("_progress") else f"{clean_tgt}_progress"
    return f"{clean_out}/{stem}.json"


class GitThresholds(BaseModel):
    """Quantitative branch freshness, divergence, and size guardrails."""

    stale_branch_days: int = Field(default=14, ge=1)
    max_behind_commits: int = Field(default=30, ge=1)
    max_ahead_commits: int = Field(default=25, ge=1)
    max_unmerged_changed_lines: int = Field(default=800, ge=1)


class GitPolicy(BaseModel):
    """Project Git branching methodology, merge strategy, and hygiene rules."""

    methodology: GitMethodology = "github_flow"
    trunk_branch: str = "main"
    integration_branch: Optional[str] = None
    merge_strategy: GitMergeStrategy = "squash_only"
    forbid_foxtrot_merges: bool = True
    forbid_direct_trunk_commits: bool = False
    forbid_wip_commits_on_trunk: bool = True
    allowed_branch_patterns: list[str] = Field(
        default_factory=lambda: ["feat/*", "fix/*", "refactor/*", "docs/*", "chore/*", "hotfix/*", "release/*"]
    )
    commit_convention: CommitConvention = "conventional_commits"
    thresholds: GitThresholds = Field(default_factory=GitThresholds)


class ProgressMilestoneSpec(BaseModel):
    """Single project milestone inside `.pni/progress/<target>.yaml`."""

    id: str
    name: str
    due_date: str
    description: str = ""

    @model_validator(mode="after")
    def _validate_due_date(self) -> ProgressMilestoneSpec:
        """Ensure due_date is a valid YYYY-MM-DD string and id is non-empty."""
        if not self.id.strip():
            raise ValueError("Milestone 'id' cannot be empty.")
        _parse_iso_date(self.due_date, f"milestones[{self.id}].due_date")
        return self


class ProgressTaskSpec(BaseModel):
    """Single tracked task or phase inside `.pni/progress/<target>.yaml`."""

    id: str
    milestone: str
    name: str
    planned_start: str
    planned_end: str
    status: TaskDeclaredStatus = "todo"
    declared_progress: Optional[int] = Field(default=None, ge=0, le=100)
    branch_pattern: str = ""
    expected_paths: list[str] = Field(default_factory=list)
    acceptance_summary: str = ""
    depends_on: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_task_fields(self) -> ProgressTaskSpec:
        """Validate dates, default declared_progress from status, and check path safety."""
        if not self.id.strip():
            raise ValueError("Task 'id' cannot be empty.")
        start_dt = _parse_iso_date(self.planned_start, f"tasks[{self.id}].planned_start")
        end_dt = _parse_iso_date(self.planned_end, f"tasks[{self.id}].planned_end")
        if start_dt > end_dt:
            msg = f"Task '{self.id}' has planned_start ({self.planned_start}) > planned_end ({self.planned_end})."
            raise ValueError(msg)
        if self.declared_progress is None:
            self.declared_progress = _STATUS_DEFAULT_PROGRESS[self.status]
        if self.expected_paths:
            _validate_safe_rel_paths(self.expected_paths, f"tasks[{self.id}].expected_paths")
        return self


def _dfs_visit_task(node_id: str, by_id: dict[str, ProgressTaskSpec], state: dict[str, int]) -> None:
    """Depth-first cycle detector over task `depends_on` edges."""
    state[node_id] = 1
    for dep_id in by_id[node_id].depends_on:
        dep_state = state.get(dep_id, 0)
        if dep_state == 1:
            msg = f"Circular task dependency detected involving '{node_id}' -> '{dep_id}'."
            raise ValueError(msg)
        if dep_state == 0:
            _dfs_visit_task(dep_id, by_id, state)
    state[node_id] = 2


def _ensure_acyclic_dependencies(tasks: list[ProgressTaskSpec]) -> None:
    """Verify task depends_on references exist and form a Directed Acyclic Graph (DAG)."""
    by_id = {t.id: t for t in tasks}
    for task in tasks:
        for dep in task.depends_on:
            if dep not in by_id:
                msg = f"Task '{task.id}' depends_on unknown task ID '{dep}'."
                raise ValueError(msg)
            if dep == task.id:
                msg = f"Task '{task.id}' cannot depend on itself."
                raise ValueError(msg)

    state: dict[str, int] = {}
    for tid in by_id:
        if state.get(tid, 0) == 0:
            _dfs_visit_task(tid, by_id, state)


class ProgressPlanDefinition(BaseModel):
    """Complete progress plan and Git governance manifest parsed from `.pni/progress/<target>.yaml`."""

    id: str
    name: str
    start_date: str
    target_date: str
    description: str = ""
    git_policy: GitPolicy = Field(default_factory=GitPolicy)
    milestones: list[ProgressMilestoneSpec] = Field(default_factory=list)
    tasks: list[ProgressTaskSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_plan_integrity(self) -> ProgressPlanDefinition:
        """Enforce date order, unique milestone/task IDs, valid milestone refs, and acyclic task DAG."""
        if not self.id.strip():
            raise ValueError("Progress plan 'id' cannot be empty.")
        start_dt = _parse_iso_date(self.start_date, "start_date")
        end_dt = _parse_iso_date(self.target_date, "target_date")
        if start_dt > end_dt:
            msg = f"Plan start_date ({self.start_date}) cannot be after target_date ({self.target_date})."
            raise ValueError(msg)

        ms_ids: set[str] = set()
        for ms in self.milestones:
            if ms.id in ms_ids:
                msg = f"Duplicate milestone ID '{ms.id}' in progress plan."
                raise ValueError(msg)
            ms_ids.add(ms.id)

        task_ids: set[str] = set()
        for task in self.tasks:
            if task.id in task_ids:
                msg = f"Duplicate task ID '{task.id}' in progress plan."
                raise ValueError(msg)
            task_ids.add(task.id)
            if task.milestone not in ms_ids:
                msg = f"Task '{task.id}' references unknown milestone '{task.milestone}'."
                raise ValueError(msg)

        _ensure_acyclic_dependencies(self.tasks)
        return self


class ProgressOptions(BaseModel):
    """Input configuration options for `progress_analyze` and `progress_assessment`."""

    plan_file: str = ""
    lookback_weeks: int = Field(default=12, ge=1, le=104)
    as_of_date: str = ""
    base_audit_workflow: str = ""
    output_dir: str = "reports"
    target: str = ""
    progress_path: str = ""


class AuditLocSummary(BaseModel):
    """Compact LOC summary stored inside `.pni/history/audit/*.jsonl`."""

    source: int = 0
    tests: int = 0
    docs: int = 0


class AuditTestSummary(BaseModel):
    """Compact dynamic test & coverage summary stored inside `.pni/history/audit/*.jsonl`."""

    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage_pct: Optional[float] = None


class AuditHistoryEntry(BaseModel):
    """Single compact JSONL line recorded in `.pni/history/audit/<workflow_id>.jsonl`."""

    timestamp: str
    workflow_id: str
    git_sha: str
    git_branch: str = ""
    git_dirty: bool = False
    overall_score: int = Field(ge=0, le=100)
    health_grade: str
    category_scores: dict[str, int] = Field(default_factory=dict)
    finding_counts: dict[str, int] = Field(default_factory=dict)
    loc: AuditLocSummary = Field(default_factory=AuditLocSummary)
    test_execution: AuditTestSummary = Field(default_factory=AuditTestSummary)
    vuln_count: int = 0


class ProgressHistoryEntry(BaseModel):
    """Single compact JSONL line recorded in `.pni/history/progress/<workflow_id>.jsonl`."""

    timestamp: str
    workflow_id: str
    git_sha: str
    git_branch: str = ""
    git_dirty: bool = False
    delivery_status: DeliveryStatus
    overall_health_score: int = Field(ge=0, le=100)
    verified_completion_pct: float = Field(ge=0.0, le=100.0)
    commits_recent_window: int = 0
    net_source_loc: int = 0
    net_test_loc: int = 0
    static_test_cases: int = 0
    active_branches: int = 0
    stale_branches: int = 0
    conflicting_branches: int = 0
    policy_violations: int = 0


class BranchHealthFact(BaseModel):
    """Deterministic branch lineage, freshness, policy compliance, and merge-tree conflict status."""

    branch_name: str
    is_remote: bool = False
    merge_base_sha: str = ""
    branched_at: str = ""
    last_commit_date: str = ""
    age_days: int = 0
    ahead_commits: int = 0
    behind_commits: int = 0
    changed_lines: int = 0
    touched_files: list[str] = Field(default_factory=list)
    is_merged: bool = False
    is_stale: bool = False
    naming_compliant: bool = True
    exceeds_behind: bool = False
    exceeds_ahead: bool = False
    exceeds_size: bool = False
    clean_mergeable: bool = True
    has_conflict: bool = False
    conflicting_files: list[str] = Field(default_factory=list)


class OverlappingFileHotspot(BaseModel):
    """File touched concurrently by two or more unmerged branches (cross-branch conflict risk)."""

    file_path: str
    branches: list[str] = Field(default_factory=list)


class GitPolicyViolation(BaseModel):
    """Deterministic Git methodology or merge-hygiene violation detected in repository history."""

    code: str
    severity: ProgressSeverity = "medium"
    branch_or_sha: str = ""
    detail: str


class WorkingTreeConflictState(BaseModel):
    """Active working-tree / index conflict state and committed conflict marker remnants."""

    unmerged_index_files: list[str] = Field(default_factory=list)
    in_progress_operations: list[str] = Field(default_factory=list)
    committed_conflict_markers: list[str] = Field(default_factory=list)


class ChurnHotspotItem(BaseModel):
    """File exhibiting high short-term addition/deletion rework churn."""

    file_path: str
    commits_count: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    rework_ratio: float = 0.0


class TrajectoryPoint(BaseModel):
    """Historical weekly snapshot of commits, churn, LOC, and static test counts."""

    period_label: str
    period_end_date: str
    commit_sha: str = ""
    commits_count: int = 0
    active_authors: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    source_loc: int = 0
    test_loc: int = 0
    docs_loc: int = 0
    test_to_code_ratio: float = 0.0
    static_test_files: int = 0
    static_test_cases: int = 0


class TaskDeterministicEvidence(BaseModel):
    """Objective repository evidence collected for a single planned task."""

    task_id: str
    milestone_id: str
    name: str
    planned_start: str
    planned_end: str
    declared_status: TaskDeclaredStatus
    declared_progress: int = 0
    schedule_state: TaskScheduleState = "active"
    days_delta: int = 0
    matched_branches: list[str] = Field(default_factory=list)
    branch_merged: bool = False
    branch_has_conflict: bool = False
    existing_paths: list[str] = Field(default_factory=list)
    missing_paths: list[str] = Field(default_factory=list)
    last_commit_date: str = ""
    recent_commits_count: int = 0
    stub_todo_count: int = 0
    has_tests: bool = False


class AuditSummarySnapshot(BaseModel):
    """Lightweight summary linked from `.pni/history/audit/*.jsonl` and latest `*_score.json`."""

    base_workflow_id: str
    latest_score: Optional[int] = None
    latest_grade: str = ""
    score_delta: Optional[int] = None
    latest_category_scores: dict[str, int] = Field(default_factory=dict)
    critical_findings: int = 0
    high_findings: int = 0
    history_points: list[AuditHistoryEntry] = Field(default_factory=list)


class ProgressPreflightHint(BaseModel):
    """Advisory hint emitted when progress/Git configuration has notable caveats."""

    code: str
    message: str


class ProgressFacts(BaseModel):
    """Deterministic project progress & Git governance intelligence (`.pni/cache/<wf>/progress_facts.json`)."""

    project_name: str
    workflow_id: str
    as_of_date: str
    plan_file: str
    plan_sha256: str
    plan: ProgressPlanDefinition
    git_available: bool = True
    is_shallow_repository: bool = False
    current_branch: str = ""
    head_sha: str = ""
    git_dirty: bool = False
    resolved_base_branch: str = "main"
    conventional_commit_ratio: float = 1.0
    trunk_merge_commits_count: int = 0
    foxtrot_merges_count: int = 0
    wip_commits_on_trunk: int = 0
    working_tree_conflicts: WorkingTreeConflictState = Field(default_factory=WorkingTreeConflictState)
    branches: list[BranchHealthFact] = Field(default_factory=list)
    overlapping_file_hotspots: list[OverlappingFileHotspot] = Field(default_factory=list)
    policy_violations: list[GitPolicyViolation] = Field(default_factory=list)
    trajectory: list[TrajectoryPoint] = Field(default_factory=list)
    churn_hotspots: list[ChurnHotspotItem] = Field(default_factory=list)
    task_evidence: list[TaskDeterministicEvidence] = Field(default_factory=list)
    audit_summary: Optional[AuditSummarySnapshot] = None
    progress_history: list[ProgressHistoryEntry] = Field(default_factory=list)
    preflight_hints: list[ProgressPreflightHint] = Field(default_factory=list)


class ProgressDimensionScores(BaseModel):
    """0-100 health scores across the 4 core delivery & Git governance axes."""

    schedule_adherence: int = Field(ge=0, le=100)
    git_and_merge_hygiene: int = Field(ge=0, le=100)
    momentum_and_churn: int = Field(ge=0, le=100)
    test_and_quality_trajectory: int = Field(ge=0, le=100)


class TaskProgressAssessment(BaseModel):
    """Evidence-backed progress assessment for a single planned task."""

    task_id: str
    name: str
    declared_progress: int = Field(ge=0, le=100)
    verified_progress: int = Field(ge=0, le=100)
    status_verdict: Literal["on_track", "ahead", "at_risk", "delayed", "blocked", "completed"]
    evidence_summary: str
    risk_note: str = ""


class BranchIntegrationAssessment(BaseModel):
    """Integration risk evaluation and merge guidance for an active or conflicting branch."""

    branch_name: str
    integration_risk: ProgressSeverity = "low"
    merge_recommendation: str
    conflicting_files: list[str] = Field(default_factory=list)


class ProgressActionItem(BaseModel):
    """Prioritized P0-P2 operational next action to unblock delivery or resolve Git risks."""

    priority: ProgressPriority
    category: Literal["conflict_resolution", "branch_hygiene", "schedule_recovery", "test_gap", "git_policy"]
    title: str
    description: str
    target_files: list[str] = Field(default_factory=list)
    target_branches: list[str] = Field(default_factory=list)
    expected_impact: str = ""


class ProgressResult(BaseModel):
    """Canonical structured progress assessment output (`reports/<target>_progress.json`)."""

    project_name: str
    workflow_id: str = ""
    workflow_run_id: str = ""
    generated_at: str = ""
    as_of_date: str = ""
    target_root: str = "."
    plan_file: str = ""
    plan_sha256: str = ""
    delivery_status: DeliveryStatus
    overall_health_score: int = Field(ge=0, le=100)
    dimension_scores: ProgressDimensionScores
    executive_summary: str
    audit_status_note: str = ""
    task_assessments: list[TaskProgressAssessment] = Field(default_factory=list)
    branch_assessments: list[BranchIntegrationAssessment] = Field(default_factory=list)
    bottlenecks_and_risks: list[str] = Field(default_factory=list)
    next_actions: list[ProgressActionItem] = Field(default_factory=list)
    progress_facts_file: str = ""
    progress_facts: Optional[ProgressFacts] = None
