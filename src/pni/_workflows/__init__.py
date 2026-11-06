# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Workflows package encapsulating workflow models, SQLite state, and execution engine."""

from __future__ import annotations

from pni._workflows._progress_engine import inspect_progress_plan_prerequisite
from pni._workflows.adhoc import (
    AdhocActionOutcome,
    run_workflow_action_adhoc,
    select_workflow_primitives,
)
from pni._workflows.aggregator import (
    CompiledAuditDigest,
    compile_workflow_digest,
    consolidate_findings_by_location,
)
from pni._workflows.base_model import (
    ActionRunRecord,
    RunStatus,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowFactsBundle,
    WorkflowInfo,
    WorkflowOutputs,
    WorkflowPrerequisiteError,
    WorkflowRunRecord,
    WorkflowStepSpec,
    WorkflowTargets,
)
from pni._workflows.engine import (
    get_workflow_action,
    inspect_base_audit_status,
    inspect_pentests_prerequisite,
    push_workflow_action,
    start_workflow_run,
)
from pni._workflows.inspector import (
    ActionStepSummary,
    InspectedActionItem,
    WorkflowRunDetail,
    WorkflowRunSummary,
    build_workflow_run_detail,
    build_workflow_run_summary,
    inspect_workflow_run_actions,
    query_workflow_run_summaries,
    resolve_run_actions_by_selector,
    resolve_run_by_id_or_workflow,
)
from pni._workflows.manager import (
    copy_workflow_templates,
    list_workflows,
    load_workflow,
    normalize_workflow_steps,
    resolve_workflow_outputs,
)
from pni._workflows.state_db import DEFAULT_STATE_DB_REL_PATH, WorkflowStateDB

__all__ = [
    "ActionRunRecord",
    "ActionStepSummary",
    "AdhocActionOutcome",
    "CompiledAuditDigest",
    "DEFAULT_STATE_DB_REL_PATH",
    "InspectedActionItem",
    "RunStatus",
    "WorkflowCategory",
    "WorkflowDefinition",
    "WorkflowFactsBundle",
    "WorkflowInfo",
    "WorkflowOutputs",
    "WorkflowPrerequisiteError",
    "WorkflowRunDetail",
    "WorkflowRunRecord",
    "WorkflowRunSummary",
    "WorkflowStateDB",
    "WorkflowStepSpec",
    "WorkflowTargets",
    "build_workflow_run_detail",
    "build_workflow_run_summary",
    "compile_workflow_digest",
    "consolidate_findings_by_location",
    "copy_workflow_templates",
    "get_workflow_action",
    "inspect_base_audit_status",
    "inspect_pentests_prerequisite",
    "inspect_progress_plan_prerequisite",
    "inspect_workflow_run_actions",
    "list_workflows",
    "load_workflow",
    "normalize_workflow_steps",
    "push_workflow_action",
    "query_workflow_run_summaries",
    "resolve_run_actions_by_selector",
    "resolve_run_by_id_or_workflow",
    "resolve_workflow_outputs",
    "run_workflow_action_adhoc",
    "select_workflow_primitives",
    "start_workflow_run",
]
