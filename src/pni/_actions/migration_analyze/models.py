# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for deterministic migration analysis and structured migration plans."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

MigrationStrategy = Literal["auto", "phased_pr", "strangler_fig", "rewrite"]
ResolvedMigrationStrategy = Literal["phased_pr", "strangler_fig", "rewrite"]
ApiCompatibilityPolicy = Literal["strict", "versioned_v2", "flexible"]
BugHandlingPolicy = Literal["ask_human", "preserve_behavior", "fix_in_phase3"]
CodemodToolChoice = Literal["auto", "openrewrite", "rector", "ruff", "manual_only"]
TransformationMode = Literal["same_lang_upgrade", "architectural_restructure", "cross_stack_replacement"]
TouchpointKind = Literal["in_memory_state", "persistence_db", "external_http_rpc"]
MigrationRiskLevel = Literal["critical", "high", "medium", "low", "info"]
MigrationAxisCategory = Literal[
    "language_runtime",
    "framework",
    "architecture_pattern",
    "database_persistence",
    "cache_state",
    "auth_security",
    "messaging_async",
    "container_cicd",
    "custom",
]


def resolve_migration_plan_rel_path(
    output_dir: str,
    target: str,
    explicit_plan_path: str = "",
) -> str:
    """Resolve workspace-relative path for `<output_dir>/<target>_migration_plan.json`.

    Avoids duplicate `_migration_migration_plan.json` suffixes when `target` already ends
    with `_migration` or `_migration_plan`.

    Args:
        output_dir: Output directory (e.g. 'reports/java').
        target: Workflow or report target identifier (e.g. 'api_spring_messy_migration').
        explicit_plan_path: Explicit override path if configured.

    Returns:
        str: Normalized workspace-relative JSON file path.
    """
    if explicit_plan_path.strip():
        return explicit_plan_path.strip()
    clean_out = output_dir.rstrip("/") or "reports"
    clean_tgt = target.strip().removesuffix("_src") or "migration"
    if clean_tgt.endswith("_migration_plan"):
        stem = clean_tgt
    elif clean_tgt.endswith("_migration"):
        stem = f"{clean_tgt}_plan"
    else:
        stem = f"{clean_tgt}_migration_plan"
    return f"{clean_out}/{stem}.json"


class MigrationOptions(BaseModel):
    """Input configuration and guardrails for migration_analyze and migration_proposal."""

    base_audit_workflow: str = ""
    brief: str = ""
    brief_file: Optional[str] = None
    migration_strategy: MigrationStrategy = "auto"
    api_compatibility: ApiCompatibilityPolicy = "strict"
    bug_handling_policy: BugHandlingPolicy = "ask_human"
    codemod_tool: CodemodToolChoice = "auto"
    output_dir: str = "reports"
    target: str = ""
    plan_path: str = ""


class PreflightReadinessHint(BaseModel):
    """Deterministic warning emitted when a migration workflow contains vague or unpinned settings."""

    code: str
    message: str


class CycleCutSuggestion(BaseModel):
    """Recommended edge removal to break an internal strongly connected component (SCC)."""

    cycle_modules: list[str] = Field(default_factory=list)
    recommended_cut_from: str
    recommended_cut_to: str
    rationale: str


class RefactoringWave(BaseModel):
    """Topological refactoring wave grouping modules from leaf DTOs (Wave 1) to entrypoints (Wave 4)."""

    wave: int = Field(ge=1, le=4)
    label: str
    modules: list[str] = Field(default_factory=list)
    rationale: str = ""


class ContractFieldSpec(BaseModel):
    """Single implicit request/response field key extracted from dynamic Map/dict/superglobal access."""

    key: str
    direction: Literal["input", "output"]
    inferred_type: str = "string"
    default_value: Optional[str] = None
    file: str
    line: int


class ImplicitEndpointContract(BaseModel):
    """Implicit external I/O contract reconstructed for an API route or script entrypoint."""

    endpoint_or_file: str
    http_method: str = "ANY"
    handler: str = ""
    input_fields: list[ContractFieldSpec] = Field(default_factory=list)
    output_fields: list[ContractFieldSpec] = Field(default_factory=list)


class EnvVarContract(BaseModel):
    """Environment variable, framework property, or configuration constant contract."""

    name: str
    default_value: Optional[str] = None
    file: str
    line: int
    kind: Literal["env", "config_property", "constant"] = "env"


class BoundaryTouchpoint(BaseModel):
    """Pinpointed stateful, database, or outbound HTTP coupling requiring Port/Adapter isolation."""

    kind: TouchpointKind
    file: str
    line: int
    symbol: str
    current_coupling: str
    recommended_port_hint: str = ""


class CodemodRecipeMatch(BaseModel):
    """Deterministic automated transformation recipe matched to the source and target stack."""

    tool: str
    recipe_id: str
    title: str
    applicable_files_count: int = 0
    rationale: str


class MigrationBlocker(BaseModel):
    """Structural or build blocker that must be resolved before automated codemods or framework upgrades."""

    blocker_id: str
    severity: MigrationRiskLevel = "high"
    file: Optional[str] = None
    line: Optional[int] = None
    description: str
    resolution_hint: str


class SpecVsBugCandidate(BaseModel):
    """Ambiguous legacy behavior that could be an intentional contract quirk or an accidental bug."""

    candidate_id: str
    file: str
    line: int
    symbol: str = ""
    observed_behavior: str
    risk_if_changed_silently: str
    options: list[str] = Field(default_factory=list)


class MigrationFacts(BaseModel):
    """Deterministic As-Is migration intelligence artifact (.pni/cache/<wf>/migration_facts.json)."""

    project_name: str
    source_language: str
    base_audit_workflow: str = ""
    resolved_brief: str = ""
    effective_options: MigrationOptions = Field(default_factory=MigrationOptions)
    transformation_mode: TransformationMode = "same_lang_upgrade"
    resolved_strategy: ResolvedMigrationStrategy = "phased_pr"
    preflight_hints: list[PreflightReadinessHint] = Field(default_factory=list)
    refactoring_waves: list[RefactoringWave] = Field(default_factory=list)
    cycle_cuts: list[CycleCutSuggestion] = Field(default_factory=list)
    implicit_contracts: list[ImplicitEndpointContract] = Field(default_factory=list)
    env_contracts: list[EnvVarContract] = Field(default_factory=list)
    boundary_touchpoints: list[BoundaryTouchpoint] = Field(default_factory=list)
    mechanical_codemods: list[CodemodRecipeMatch] = Field(default_factory=list)
    manual_blockers: list[MigrationBlocker] = Field(default_factory=list)
    spec_vs_bug_candidates: list[SpecVsBugCandidate] = Field(default_factory=list)


class MigrationAxis(BaseModel):
    """Dynamic As-Is -> To-Be transformation axis derived from free-format migration requirements."""

    category: MigrationAxisCategory
    title: str
    as_is: str
    to_be: str
    migration_approach: str
    risk_level: MigrationRiskLevel = "medium"
    affected_files: list[str] = Field(
        default_factory=list,
        description="Exact existing repository-relative file or directory paths ONLY (no parenthetical descriptions).",
    )


class TargetLayerSpec(BaseModel):
    """To-Be architectural layer or ring definition with explicit dependency and import constraints."""

    layer_name: str
    package_or_dir: str
    responsibility: str
    allowed_dependencies: list[str] = Field(default_factory=list)
    forbidden_imports: list[str] = Field(default_factory=list)


class ComponentMigrationMapping(BaseModel):
    """Concrete mapping from an existing legacy source file/symbol to its To-Be layer and Port/Adapter."""

    source_file: str = Field(
        description="Exact existing repository-relative source file path ONLY (no parenthetical descriptions)."
    )
    source_symbol: str = ""
    target_layer: str
    target_component: str
    port_or_adapter_role: str = ""
    refactoring_note: str


class TargetArchitectureDesign(BaseModel):
    """Target architectural philosophy (e.g. Clean Architecture, Modular Laravel) and component mapping."""

    pattern_name: str
    summary: str = ""
    dependency_rules: list[str] = Field(default_factory=list)
    target_layers: list[TargetLayerSpec] = Field(default_factory=list)
    component_mappings: list[ComponentMigrationMapping] = Field(default_factory=list)


class DecisionLogItem(BaseModel):
    """Stakeholder sign-off item ('Spec vs. Bug') isolated prior to business-logic changes in Phase 3."""

    decision_id: str
    file_path: str = Field(
        description="Exact existing repository-relative file path ONLY (no parenthetical descriptions)."
    )
    line: Optional[int] = None
    current_behavior: str
    impact_if_changed: str
    recommended_option: str
    stakeholder_options: list[str] = Field(default_factory=list)


class MigrationPhaseGate(BaseModel):
    """Single stage in the 5-phase gated migration execution roadmap (Phase 0..Phase 4)."""

    phase_number: int = Field(ge=0, le=4)
    title: str
    objective: str
    key_tasks: list[str] = Field(default_factory=list)
    exit_criteria: list[str] = Field(default_factory=list)
    rollback_or_coexistence_note: str = ""


class MigrationPrTicket(BaseModel):
    """Actionable PR-sized work breakdown ticket ordered topologically across Phase 0..Phase 4."""

    pr_id: str
    phase_number: int = Field(ge=0, le=4)
    wave: int = Field(default=1, ge=1, le=4)
    axis_category: MigrationAxisCategory = "architecture_pattern"
    title: str
    target_files: list[str] = Field(
        default_factory=list,
        description="Exact repository-relative As-Is or To-Be file paths ONLY (no parenthetical descriptions).",
    )
    changes_summary: str
    automated_or_manual: Literal["codemod", "manual", "hybrid"] = "manual"
    verification_cmd: str
    estimated_size: Literal["XS", "S", "M", "L"] = "S"
    depends_on_prs: list[str] = Field(default_factory=list)


class MigrationPlanResult(BaseModel):
    """Validated To-Be migration execution plan artifact (reports/<lang>/<target>_migration_plan.json)."""

    project_name: str
    workflow_id: str = ""
    workflow_run_id: str = ""
    generated_at: str = ""
    source_language: str
    target_root: str = "."
    migration_facts_file: str = ""
    transformation_mode: TransformationMode = "architectural_restructure"
    migration_strategy: ResolvedMigrationStrategy = "phased_pr"
    api_compatibility: ApiCompatibilityPolicy = "strict"
    bug_handling_policy: BugHandlingPolicy = "ask_human"
    executive_summary: str
    confirmed_assumptions: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    target_axes: list[MigrationAxis] = Field(default_factory=list)
    target_architecture: TargetArchitectureDesign
    decision_log: list[DecisionLogItem] = Field(default_factory=list)
    phase_gates: list[MigrationPhaseGate] = Field(default_factory=list)
    pr_wbs: list[MigrationPrTicket] = Field(default_factory=list)
    migration_facts: Optional[MigrationFacts] = None
