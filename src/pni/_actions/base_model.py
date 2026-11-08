# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for PNI primitive actions, composite actions, architecture records, and scores."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pni._actions._repo_governance import RuntimeArchetype
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    CodeLocation,
    ModuleAstSummary,
    SecuritySinkLocation,
)
from pni._actions.pentest.models import PentestFacts
from pni._actions.runtime_check.models import RuntimeFacts
from pni._actions.security_scan.models import SecurityFacts

ParamValue = str | int | float | bool | list[str]
MetricScalar = str | int | float | bool | list[str]
SeverityLevel = Literal["critical", "high", "medium", "low", "info"]
HealthGrade = Literal["S", "A", "B", "C", "D"]
PriorityLevel = Literal["P0", "P1", "P2"]
RuleComplianceStatus = Literal["pass", "warn", "fail", "not_applicable"]
ArchitectureAspect = Literal["purpose_and_stack", "layers_and_modules", "flows_and_state", "all"]
__exported_archetype__ = RuntimeArchetype


class PrimitiveType(str, Enum):
    """Canonical internal primitive action types executed or rendered by PNI."""

    AST_ANALYZE = "ast_analyze"
    PROJECT_INSPECT = "project_inspect"
    RUN_CHECK = "run_check"
    SECURITY_SCAN = "security_scan"
    WEB_PENTEST = "web_pentest"
    MIGRATION_ANALYZE = "migration_analyze"
    PROGRESS_ANALYZE = "progress_analyze"
    LOAD_RULES = "load_rules"
    RECORD_ARCHITECTURE = "record_architecture"
    AI_INTERPRET = "ai_interpret"
    EMIT_SCORE = "emit_score"
    EMIT_MIGRATION_PLAN = "emit_migration_plan"
    EMIT_PROGRESS = "emit_progress"
    WRITE_DRAWLIB_REPORT = "write_drawlib_report"


class PrimitiveStep(BaseModel):
    """Normalized internal primitive action step."""

    id: str
    name: str
    type: PrimitiveType
    rules: list[str] = Field(default_factory=list)
    params: dict[str, ParamValue] = Field(default_factory=dict)
    prompt: str = ""
    source_action: Optional[str] = None


class CompositePrimitiveSpec(BaseModel):
    """Specification of a single primitive inside a composite action YAML."""

    model_config = ConfigDict(populate_by_name=True)

    type: PrimitiveType
    name: Optional[str] = None
    rules: list[str] = Field(default_factory=list)
    with_params: dict[str, ParamValue] = Field(default_factory=dict, alias="with")
    prompt: str = ""


class CompositeActionDefinition(BaseModel):
    """User or built-in composite action definition that expands into primitives."""

    id: str
    name: str
    description: str = ""
    rules: list[str] = Field(default_factory=list)
    primitives: list[CompositePrimitiveSpec] = Field(default_factory=list)


class ActionInfo(BaseModel):
    """Metadata describing an available composite action."""

    id: str
    scope: str = "common"
    name: str
    description: str
    path: Path
    is_local: bool


class CategoryScores(BaseModel):
    """Standardized 0-100 scores across the 7 core PNI engineering dimensions."""

    architecture: int = Field(ge=0, le=100)
    code_quality: int = Field(ge=0, le=100)
    typing: int = Field(ge=0, le=100)
    testing: int = Field(ge=0, le=100)
    dependencies: int = Field(ge=0, le=100)
    security: int = Field(default=100, ge=0, le=100)
    documentation: int = Field(ge=0, le=100)


class CategoryRationales(BaseModel):
    """Concise evidence-backed explanation for each of the 7 category scores."""

    architecture: str = ""
    code_quality: str = ""
    typing: str = ""
    testing: str = ""
    dependencies: str = ""
    security: str = ""
    documentation: str = ""


class ModuleSummary(BaseModel):
    """Module/component map entry to guide downstream AI architecture diagrams and reviews."""

    path: str = Field(
        description="Exact existing repository-relative file or directory path ONLY (no parenthetical descriptions)."
    )
    role: str
    key_symbols: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    health_note: str = ""


class SystemProfile(BaseModel):
    """Aspect 1 (purpose_and_stack): Grounded system purpose, runtime profile, and stack."""

    system_purpose: str
    domain_context: str = ""
    runtime_types: list[str] = Field(default_factory=lambda: ["library"])
    tech_stack: list[str] = Field(default_factory=list)
    external_integrations: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_runtime_type(cls, data: object) -> object:
        """Accept legacy single-string 'runtime_type' from historical score/architecture JSON files."""
        if not isinstance(data, dict):
            return data
        updated = dict(data)
        if "runtime_types" in updated:
            raw_rt = updated["runtime_types"]
            if isinstance(raw_rt, str):
                updated["runtime_types"] = [raw_rt] if raw_rt.strip() else ["library"]
            return updated
        legacy = updated.pop("runtime_type", None)
        if isinstance(legacy, str) and legacy.strip():
            updated["runtime_types"] = ["web_api", "cli"] if legacy.strip() == "hybrid" else [legacy.strip()]
        elif isinstance(legacy, list):
            updated["runtime_types"] = [str(x) for x in legacy if str(x).strip()] or ["library"]
        return updated


class ArchitectureLayer(BaseModel):
    """Grounded architectural layer mapping directories/files and allowed dependency directions."""

    name: str
    responsibility: str
    paths: list[str] = Field(
        default_factory=list,
        description="Exact existing repository-relative file or directory paths ONLY (no parenthetical descriptions).",
    )
    allowed_dependencies: list[str] = Field(default_factory=list)


class StructureMap(BaseModel):
    """Aspect 2 (layers_and_modules): Grounded layer definitions, module roles, and boundary health."""

    architecture_pattern: str
    layers: list[ArchitectureLayer] = Field(default_factory=list)
    modules: list[ModuleSummary] = Field(default_factory=list)
    boundary_assessment: str = ""


class ExecutionFlow(BaseModel):
    """Grounded runtime call/data flow tracing real repository files."""

    name: str
    trigger: str
    steps: list[str] = Field(default_factory=list)
    involved_files: list[str] = Field(
        default_factory=list,
        description="Exact 'path/to/file' or 'path/to/file:Symbol' strings ONLY (no parenthetical descriptions).",
    )


class ExecutionFlowMap(BaseModel):
    """Aspect 3 (flows_and_state): Grounded entry points, execution flows, and state management."""

    entry_points: list[str] = Field(
        default_factory=list,
        description="Exact 'path/to/file' or 'path/to/file:Symbol' strings ONLY (no parenthetical descriptions).",
    )
    execution_flows: list[ExecutionFlow] = Field(default_factory=list)
    state_and_storage: list[str] = Field(default_factory=list)
    error_and_concurrency_model: str = ""


class ArchitectureRecord(BaseModel):
    """Persisted post-AST 3-aspect architecture record (.pni/cache/<workflow_id>/architecture.json)."""

    workflow_id: str = ""
    workflow_run_id: str = ""
    recorded_at: str = ""
    target_root: str = "."
    system_profile: Optional[SystemProfile] = None
    structure_map: Optional[StructureMap] = None
    execution_flow_map: Optional[ExecutionFlowMap] = None


class ArchitectureOverview(BaseModel):
    """High-level structural summary of the target project for downstream AI consumption."""

    pattern: str = ""
    entry_points: list[str] = Field(
        default_factory=list,
        description="Exact 'path/to/file' or 'path/to/file:Symbol' strings ONLY (no parenthetical descriptions).",
    )
    modules: list[ModuleSummary] = Field(default_factory=list)
    dependency_notes: str = ""


class RuleCheckResult(BaseModel):
    """Compliance verdict and deterministic evidence for a single active engineering rule."""

    rule_id: str
    status: RuleComplianceStatus
    source_action: str = ""
    evidence: str = ""
    summary: str = ""


class AuditDimensionScore(BaseModel):
    """Scorecard for an individual executed audit step in the workflow pipeline."""

    action_id: str
    audit_id: str
    title: str
    score: int = Field(ge=0, le=100)
    grade: HealthGrade = "B"
    rules_evaluated: list[str] = Field(default_factory=list)
    pass_count: int = 0
    warn_count: int = 0
    fail_count: int = 0
    summary: str = ""


class ModuleHotspot(BaseModel):
    """Deterministically computed per-file risk density (0.0-1.0) and violation summary."""

    file_path: str
    loc: int = 0
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    finding_counts: dict[str, int] = Field(default_factory=dict)
    top_rules: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    """A single rule-based finding with exact code location and deterministic evidence."""

    severity: SeverityLevel
    category: str = ""
    rule_id: str
    file_path: Optional[str] = Field(
        default=None,
        description="Exact existing repository-relative file path ONLY (no line numbers or parenthetical notes).",
    )
    line: Optional[int] = None
    symbol: Optional[str] = None
    evidence: str = ""
    description: str
    recommendation: str


class ConsolidatedFinding(BaseModel):
    """Location-grouped finding combining overlapping rule violations at the same file and line."""

    severity: SeverityLevel
    file_path: str
    line: Optional[int] = None
    symbol: Optional[str] = None
    rule_ids: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    primary_description: str
    combined_evidence: str = ""
    merged_recommendation: str = ""


_FINDING_SEVERITY_RANK: dict[str, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


def _dedup_texts(items: list[str]) -> list[str]:
    """Return non-empty strings preserving order while deduplicating case-insensitively."""
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        clean = raw.strip()
        low = clean.lower()
        if clean and low not in seen:
            seen.add(low)
            out.append(clean)
    return out


def consolidate_findings_by_location(findings: list[Finding]) -> list[ConsolidatedFinding]:
    """Consolidate normalized findings sharing the same (file_path, line) into single multi-rule rows."""
    deduped: dict[tuple[str, str, int, str], Finding] = {}
    for item in findings:
        norm_key = (
            item.rule_id.strip(),
            (item.file_path or "").strip(),
            item.line or 0,
            (item.symbol or item.description[:48]).strip(),
        )
        existing = deduped.get(norm_key)
        if existing is None or _FINDING_SEVERITY_RANK.get(item.severity, 99) < _FINDING_SEVERITY_RANK.get(
            existing.severity, 99
        ):
            deduped[norm_key] = item

    sorted_items = sorted(
        deduped.values(),
        key=lambda f: (
            _FINDING_SEVERITY_RANK.get(f.severity, 99),
            f.category,
            f.rule_id,
            f.file_path or "~",
            f.line or 0,
        ),
    )

    buckets: dict[tuple[str, int], list[Finding]] = {}
    for idx, item in enumerate(sorted_items):
        raw_path = (item.file_path or "").strip()
        key = (raw_path, item.line or 0) if raw_path else (f"~standalone~{idx}", 0)
        buckets.setdefault(key, []).append(item)

    consolidated: list[ConsolidatedFinding] = []
    for group in buckets.values():
        lead = group[0]
        rule_ids = _dedup_texts([f.rule_id for f in group if f.rule_id.strip()])
        categories = _dedup_texts([f.category for f in group if f.category.strip()])
        symbols = [f.symbol.strip() for f in group if f.symbol and f.symbol.strip()]
        evidences = _dedup_texts([f.evidence or f.description for f in group])
        recommendations = _dedup_texts([f.recommendation for f in group if f.recommendation.strip()])
        consolidated.append(
            ConsolidatedFinding(
                severity=lead.severity,
                file_path=(lead.file_path or "").strip(),
                line=lead.line,
                symbol=symbols[0] if symbols else None,
                rule_ids=rule_ids,
                categories=categories,
                primary_description=lead.description,
                combined_evidence=" | ".join(evidences),
                merged_recommendation=" / ".join(recommendations),
            )
        )

    return sorted(
        consolidated,
        key=lambda cf: (
            _FINDING_SEVERITY_RANK.get(cf.severity, 99),
            cf.file_path or "~",
            cf.line or 0,
            cf.rule_ids[0] if cf.rule_ids else "",
        ),
    )


class ActionItem(BaseModel):
    """Prioritized remediation or enhancement item for engineers and AI coding agents."""

    priority: PriorityLevel
    title: str
    category: str
    target_files: list[str] = Field(
        default_factory=list,
        description="Exact existing repository-relative file or directory paths ONLY (no parenthetical descriptions).",
    )
    related_rules: list[str] = Field(default_factory=list)
    action: str
    expected_impact: str


class AppliedOptOut(BaseModel):
    """Record of a declarative design waiver ([[opt_out]] in .pni/pni.toml) applied during the audit."""

    id: str
    scope: list[str] = Field(default_factory=list)
    reason: str
    matched_count: int = 0


class ScoreResult(BaseModel):
    """Rich intermediate diagnostic artifact (reports/<target>_score.json) for AI report & remediation."""

    project_name: str
    workflow_id: str
    workflow_run_id: str = ""
    evaluated_at: str = ""
    language: str
    target_root: str = "."
    facts_file: str = ""
    key_files_inspected: list[str] = Field(default_factory=list)
    overall_score: int = Field(ge=0, le=100)
    grade: HealthGrade = "B"
    category_scores: CategoryScores
    category_rationales: CategoryRationales = Field(default_factory=CategoryRationales)
    metrics_snapshot: dict[str, MetricScalar] = Field(default_factory=dict)
    runtime_facts: Optional[RuntimeFacts] = None
    security_facts: Optional[SecurityFacts] = None
    pentest_facts: Optional[PentestFacts] = None
    module_inventory: list[ModuleAstSummary] = Field(default_factory=list)
    dangerous_sinks: list[SecuritySinkLocation] = Field(default_factory=list)
    api_endpoints: list[ApiEndpointFact] = Field(default_factory=list)
    language_version_mismatches: list[CodeLocation] = Field(default_factory=list)
    architecture_overview: ArchitectureOverview = Field(default_factory=ArchitectureOverview)
    architecture_record: Optional[ArchitectureRecord] = None
    audit_dimensions: list[AuditDimensionScore] = Field(default_factory=list)
    rule_compliance: list[RuleCheckResult] = Field(default_factory=list)
    module_hotspots: list[ModuleHotspot] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    consolidated_findings: list[ConsolidatedFinding] = Field(default_factory=list)
    action_plan: list[ActionItem] = Field(default_factory=list)
    opt_outs: list[AppliedOptOut] = Field(default_factory=list)
    report_hints: list[str] = Field(default_factory=list)
    summary: str


class DeterministicAckInput(BaseModel):
    """Agent acknowledgment payload pushed after reviewing a deterministic step."""

    acknowledged: bool = True
    note: str = ""


class InterpretationInput(BaseModel):
    """Structured payload pushed by the AI agent after completing an ai_interpret step."""

    summary: str
    step_score: Optional[int] = Field(default=None, ge=0, le=100)
    rule_checks: list[RuleCheckResult] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    category_rationales: dict[str, str] = Field(default_factory=dict)
    suggested_scores: dict[str, int] = Field(default_factory=dict)
    modules: list[ModuleSummary] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)


class ReportCompletionInput(BaseModel):
    """Structured payload pushed by the AI agent after completing write_drawlib_report."""

    generated_files: list[str] = Field(min_length=1)
    summary: str
