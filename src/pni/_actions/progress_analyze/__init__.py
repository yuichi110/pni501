# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic project progress, Git methodology, and history ledger analysis subpackage."""

from __future__ import annotations

from pni._actions.progress_analyze.history_ledger import (
    read_audit_history,
    read_progress_history,
    record_audit_history_from_score,
    record_progress_history_from_result,
)
from pni._actions.progress_analyze.models import (
    AuditHistoryEntry,
    AuditLocSummary,
    AuditSummarySnapshot,
    AuditTestSummary,
    BranchHealthFact,
    BranchIntegrationAssessment,
    ChurnHotspotItem,
    DeliveryStatus,
    GitMergeStrategy,
    GitMethodology,
    GitPolicy,
    GitPolicyViolation,
    GitThresholds,
    OverlappingFileHotspot,
    ProgressActionItem,
    ProgressDimensionScores,
    ProgressFacts,
    ProgressHistoryEntry,
    ProgressMilestoneSpec,
    ProgressOptions,
    ProgressPlanDefinition,
    ProgressPreflightHint,
    ProgressResult,
    ProgressTaskSpec,
    TaskDeclaredStatus,
    TaskDeterministicEvidence,
    TaskProgressAssessment,
    TrajectoryPoint,
    WorkingTreeConflictState,
    resolve_progress_result_rel_path,
)
from pni._actions.progress_analyze.plan_loader import (
    load_and_validate_progress_plan,
    render_progress_plan_template,
    resolve_bounded_plan_path,
    scaffold_progress_plan,
)
from pni._actions.progress_analyze.runner import run_progress_analyze

__all__ = [
    "AuditHistoryEntry",
    "AuditLocSummary",
    "AuditSummarySnapshot",
    "AuditTestSummary",
    "BranchHealthFact",
    "BranchIntegrationAssessment",
    "ChurnHotspotItem",
    "DeliveryStatus",
    "GitMergeStrategy",
    "GitMethodology",
    "GitPolicy",
    "GitPolicyViolation",
    "GitThresholds",
    "OverlappingFileHotspot",
    "ProgressActionItem",
    "ProgressDimensionScores",
    "ProgressFacts",
    "ProgressHistoryEntry",
    "ProgressMilestoneSpec",
    "ProgressOptions",
    "ProgressPlanDefinition",
    "ProgressPreflightHint",
    "ProgressResult",
    "ProgressTaskSpec",
    "TaskDeclaredStatus",
    "TaskDeterministicEvidence",
    "TaskProgressAssessment",
    "TrajectoryPoint",
    "WorkingTreeConflictState",
    "load_and_validate_progress_plan",
    "read_audit_history",
    "read_progress_history",
    "record_audit_history_from_score",
    "record_progress_history_from_result",
    "render_progress_plan_template",
    "resolve_bounded_plan_path",
    "resolve_progress_result_rel_path",
    "run_progress_analyze",
    "scaffold_progress_plan",
]
