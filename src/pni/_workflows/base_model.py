# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for workflows, targets, outputs, and SQLite state records."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pni._actions import (
    ArchitectureRecord,
    AstFacts,
    MigrationFacts,
    ParamValue,
    PentestFacts,
    PrimitiveType,
    ProgressFacts,
    ProjectFacts,
    RuntimeFacts,
    ScoreResult,
    SecurityFacts,
)


class RunStatus(str, Enum):
    """Lifecycle status of a workflow run or individual action run."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowCategory(str, Enum):
    """High-level classification of a PNI workflow definition."""

    AUDIT = "audit"
    MIGRATION = "migration"
    PROGRESS = "progress"


class WorkflowPrerequisiteError(ValueError):
    """Raised when a workflow's prerequisite 'based_on' audit workflow or progress/pentest input is missing."""


class WorkflowTargets(BaseModel):
    """Target root directory and relative source/test/doc paths evaluated by the workflow."""

    root: str = "."
    source: list[str] = Field(default_factory=lambda: ["src"])
    tests: list[str] = Field(default_factory=lambda: ["tests"])
    docs: list[str] = Field(default_factory=lambda: ["README.md"])
    exclude: list[str] = Field(default_factory=list)


class WorkflowOutputs(BaseModel):
    """Resolved or overridden output destinations for facts, score JSON, and report artifact."""

    facts: Optional[str] = None
    score: Optional[str] = None
    report: Optional[str] = None


class WorkflowStepSpec(BaseModel):
    """Specification of a single step inside a workflow YAML."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: Optional[str] = None
    description: str = ""
    uses: Optional[str] = None
    action: Optional[PrimitiveType] = None
    rules: list[str] = Field(default_factory=list)
    with_params: dict[str, ParamValue] = Field(default_factory=dict, alias="with")
    prompt: str = ""


class WorkflowDefinition(BaseModel):
    """Complete workflow definition parsed from .pni/workflows/*.yaml."""

    id: str
    category: WorkflowCategory = WorkflowCategory.AUDIT
    based_on: Optional[str] = None
    name: str
    description: str = ""
    targets: WorkflowTargets = Field(default_factory=WorkflowTargets)
    outputs: WorkflowOutputs = Field(default_factory=WorkflowOutputs)
    steps: list[WorkflowStepSpec] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_category_and_based_on(self) -> WorkflowDefinition:
        """Normalize 'based_on' and enforce audit/migration/progress relationship invariants."""
        if self.based_on is not None:
            cleaned = self.based_on.strip().removesuffix(".yaml").strip()
            self.based_on = cleaned or None

        if self.based_on == self.id:
            msg = f"Workflow '{self.id}' cannot reference itself in 'based_on'."
            raise ValueError(msg)

        if self.category == WorkflowCategory.MIGRATION and not self.based_on:
            msg = (
                f"Workflow '{self.id}' has category='migration' and must specify "
                "'based_on: <audit_workflow_id>'."
            )
            raise ValueError(msg)

        if self.category == WorkflowCategory.AUDIT and self.based_on is not None:
            msg = (
                f"Workflow '{self.id}' has category='audit' and cannot specify 'based_on' "
                "(set 'category: migration' or 'category: progress' instead)."
            )
            raise ValueError(msg)

        return self


class WorkflowInfo(BaseModel):
    """Metadata describing an available local workflow."""

    id: str
    category: WorkflowCategory = WorkflowCategory.AUDIT
    based_on: Optional[str] = None
    name: str
    description: str
    path: Path
    step_count: int
    targets: WorkflowTargets
    outputs: WorkflowOutputs


class WorkflowFactsBundle(BaseModel):
    """Aggregated deterministic facts and grounded architecture record for a workflow run."""

    workflow_id: str
    targets: WorkflowTargets
    outputs: WorkflowOutputs
    project_facts: Optional[ProjectFacts] = None
    ast_facts: Optional[AstFacts] = None
    runtime_facts: Optional[RuntimeFacts] = None
    security_facts: Optional[SecurityFacts] = None
    pentest_facts: Optional[PentestFacts] = None
    migration_facts: Optional[MigrationFacts] = None
    progress_facts: Optional[ProgressFacts] = None
    architecture_record: Optional[ArchitectureRecord] = None
    base_score_result: Optional[ScoreResult] = None


class ActionRunRecord(BaseModel):
    """SQLite-persisted execution state of a single normalized primitive action."""

    run_id: str
    action_id: str
    seq: int
    primitive_type: PrimitiveType
    name: str
    source_action: Optional[str] = None
    rules: list[str] = Field(default_factory=list)
    params: dict[str, ParamValue] = Field(default_factory=dict)
    prompt: str = ""
    status: RunStatus = RunStatus.PENDING
    deterministic_output_json: Optional[str] = None
    agent_input_json: Optional[str] = None
    updated_at: str = ""


class WorkflowRunRecord(BaseModel):
    """SQLite-persisted execution state of a started workflow session."""

    run_id: str
    workflow_id: str
    category: WorkflowCategory = WorkflowCategory.AUDIT
    based_on: Optional[str] = None
    based_on_run_id: Optional[str] = None
    workflow_name: str
    description: str = ""
    status: RunStatus = RunStatus.IN_PROGRESS
    targets: WorkflowTargets
    outputs: WorkflowOutputs
    created_at: str
    updated_at: str
