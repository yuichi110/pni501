# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic migration intelligence analyzer package."""

from __future__ import annotations

from pni._actions.migration_analyze.codemods import check_migration_preflight_hints
from pni._actions.migration_analyze.models import (
    ApiCompatibilityPolicy,
    BoundaryTouchpoint,
    BugHandlingPolicy,
    CodemodRecipeMatch,
    CodemodToolChoice,
    ComponentMigrationMapping,
    ContractFieldSpec,
    CycleCutSuggestion,
    DecisionLogItem,
    EnvVarContract,
    ImplicitEndpointContract,
    MigrationAxis,
    MigrationAxisCategory,
    MigrationBlocker,
    MigrationFacts,
    MigrationOptions,
    MigrationPhaseGate,
    MigrationPlanResult,
    MigrationPrTicket,
    MigrationStrategy,
    PreflightReadinessHint,
    RefactoringWave,
    ResolvedMigrationStrategy,
    SpecVsBugCandidate,
    TargetArchitectureDesign,
    TargetLayerSpec,
    TouchpointKind,
    TransformationMode,
    resolve_migration_plan_rel_path,
)
from pni._actions.migration_analyze.runner import resolve_migration_brief, run_migration_analyze

__all__ = [
    "ApiCompatibilityPolicy",
    "BoundaryTouchpoint",
    "BugHandlingPolicy",
    "CodemodRecipeMatch",
    "CodemodToolChoice",
    "ComponentMigrationMapping",
    "ContractFieldSpec",
    "CycleCutSuggestion",
    "DecisionLogItem",
    "EnvVarContract",
    "ImplicitEndpointContract",
    "MigrationAxis",
    "MigrationAxisCategory",
    "MigrationBlocker",
    "MigrationFacts",
    "MigrationOptions",
    "MigrationPhaseGate",
    "MigrationPlanResult",
    "MigrationPrTicket",
    "MigrationStrategy",
    "PreflightReadinessHint",
    "RefactoringWave",
    "ResolvedMigrationStrategy",
    "SpecVsBugCandidate",
    "TargetArchitectureDesign",
    "TargetLayerSpec",
    "TouchpointKind",
    "TransformationMode",
    "check_migration_preflight_hints",
    "resolve_migration_brief",
    "resolve_migration_plan_rel_path",
    "run_migration_analyze",
]
