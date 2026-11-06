# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Shared models, parsed CST units, and checker result types for multi-language AST analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal, Optional

from ast_grep_py import SgNode
from pydantic import BaseModel, Field

from pni._actions._repo_governance import matches_exclude_globs

SecuritySinkCategory = Literal[
    "sql_injection",
    "xss",
    "command_injection",
    "file_inclusion_or_traversal",
    "unsafe_deserialization",
    "code_execution",
    "weak_cryptography",
    "insecure_transport",
    "loose_comparison_or_auth",
    "permissive_cors_or_debug",
]
SinkSeverity = Literal["high", "medium", "low"]

MAX_FUNCTION_LINES: Final[int] = 50
MAX_BRANCH_COUNT: Final[int] = 7
MAX_COGNITIVE_COMPLEXITY: Final[int] = 15
MAX_CALLABLE_PARAMS: Final[int] = 6
IGNORED_DIR_NAMES: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        ".pni",
        ".drawlib",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "vendor",
        "target",
        "build",
        ".gradle",
        "out",
        "reports",
        "reports_src",
    }
)
__all_helpers__ = [matches_exclude_globs]


class CodeLocation(BaseModel):
    """Pinpointed source code location for a deterministic finding."""

    file: str
    line: int
    symbol: str
    detail: str


class SecuritySinkLocation(BaseModel):
    """Deterministic AST-detected dangerous code sink with CWE classification."""

    category: SecuritySinkCategory
    cwe_id: str
    severity: SinkSeverity = "high"
    file: str
    line: int
    symbol: Optional[str] = None
    detail: str = ""


class ApiEndpointFact(BaseModel):
    """Deterministic API route specification extracted from framework routing definitions."""

    http_method: str
    path: str
    handler: str
    file: str
    line: int
    has_auth_hint: bool = False
    auth_mechanisms: list[str] = Field(default_factory=list)


class ModuleAstSummary(BaseModel):
    """Deterministic per-file symbol inventory grounding downstream AI architecture mapping."""

    file: str
    loc: int = 0
    public_types: list[str] = Field(default_factory=list)
    public_callables: list[str] = Field(default_factory=list)


class AstFacts(BaseModel):
    """Language-agnostic deterministic AST analysis facts across target directories."""

    language: str = "python"
    total_files: int = 0
    total_loc: int = 0
    total_classes: int = 0
    total_functions: int = 0
    module_inventory: list[ModuleAstSummary] = Field(default_factory=list)

    # 1. Import Hygiene (BaseImportChecker)
    import_hygiene_coverage_pct: Optional[float] = 100.0
    unsorted_imports: list[CodeLocation] = Field(default_factory=list)
    wildcard_imports: list[CodeLocation] = Field(default_factory=list)
    late_imports: list[CodeLocation] = Field(default_factory=list)

    # 2. Type Safety (BaseTypingChecker)
    type_safety_coverage_pct: Optional[float] = 100.0
    type_safety_issues: list[CodeLocation] = Field(default_factory=list)
    weak_type_usages: list[CodeLocation] = Field(default_factory=list)
    unscoped_type_ignores: list[CodeLocation] = Field(default_factory=list)

    # 3. API Documentation (BaseDocChecker)
    docstring_coverage_pct: Optional[float] = 100.0
    missing_docstrings: list[CodeLocation] = Field(default_factory=list)
    empty_docstrings: list[CodeLocation] = Field(default_factory=list)
    doc_signature_mismatches: list[CodeLocation] = Field(default_factory=list)

    # 4. Code Quality & Bug-Risk Idioms (BaseQualityChecker)
    complex_functions: list[CodeLocation] = Field(default_factory=list)
    excessive_parameters: list[CodeLocation] = Field(default_factory=list)
    global_state_usages: list[CodeLocation] = Field(default_factory=list)
    bug_risk_idioms: list[CodeLocation] = Field(default_factory=list)

    # 5. Dependencies & Architecture Boundaries (BaseDependencyChecker)
    internal_import_graph: dict[str, list[str]] = Field(default_factory=dict)
    circular_dependencies: list[list[str]] = Field(default_factory=list)
    type_checking_cycles: list[list[str]] = Field(default_factory=list)
    unused_dependencies: list[str] = Field(default_factory=list)
    undeclared_dependencies: list[CodeLocation] = Field(default_factory=list)
    boundary_violations: list[CodeLocation] = Field(default_factory=list)

    # 6. Test Suite Health (BaseTestChecker)
    test_functions_count: int = 0
    module_test_coverage_pct: Optional[float] = None
    assertion_free_tests: list[CodeLocation] = Field(default_factory=list)
    test_harness_notes: list[str] = Field(default_factory=list)

    # 7. Framework & Modernization Signals (BaseFrameworkChecker)
    framework_issues: list[CodeLocation] = Field(default_factory=list)
    modernization_hints: list[CodeLocation] = Field(default_factory=list)
    language_version_mismatches: list[CodeLocation] = Field(default_factory=list)

    # 8. Operational, 12-Factor, SRE PRR & Security Signals (BaseOperationalChecker)
    missing_io_timeouts: list[CodeLocation] = Field(default_factory=list)
    scattered_env_access: list[CodeLocation] = Field(default_factory=list)
    unstructured_logging: list[CodeLocation] = Field(default_factory=list)
    hardcoded_secrets: list[CodeLocation] = Field(default_factory=list)

    # 9. Security Sinks & API Attack Surface (BaseSecurityChecker)
    dangerous_sinks: list[SecuritySinkLocation] = Field(default_factory=list)
    api_endpoints: list[ApiEndpointFact] = Field(default_factory=list)
    opt_out_counts: dict[str, int] = Field(default_factory=dict)


@dataclass(frozen=True)
class ParsedUnit:
    """Single source file parsed once via ast-grep-py and shared across all AST checkers."""

    file_path: Path
    rel_path: str
    source: str
    root: SgNode


@dataclass(frozen=True)
class UnitImportStats:
    """Per-file import ordering, wildcard, and non-top-level import findings."""

    is_clean: bool = True
    unsorted_imports: list[CodeLocation] = field(default_factory=list)
    wildcard_imports: list[CodeLocation] = field(default_factory=list)
    late_imports: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class ImportResult:
    """Aggregated import hygiene coverage and pinpointed import violations."""

    import_hygiene_coverage_pct: Optional[float] = 100.0
    unsorted_imports: list[CodeLocation] = field(default_factory=list)
    wildcard_imports: list[CodeLocation] = field(default_factory=list)
    late_imports: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class QualityResult:
    """Aggregated code size, module inventory, complexity, parameter counts, globals, and bug idioms."""

    total_loc: int = 0
    total_classes: int = 0
    total_functions: int = 0
    module_inventory: list[ModuleAstSummary] = field(default_factory=list)
    complex_functions: list[CodeLocation] = field(default_factory=list)
    excessive_parameters: list[CodeLocation] = field(default_factory=list)
    global_state_usages: list[CodeLocation] = field(default_factory=list)
    bug_risk_idioms: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class UnitTypingStats:
    """Per-file type-safety counts and findings returned by BaseTypingChecker subclasses."""

    total_callables: int = 0
    type_safe_callables: int = 0
    type_safety_issues: list[CodeLocation] = field(default_factory=list)
    weak_type_usages: list[CodeLocation] = field(default_factory=list)
    unscoped_type_ignores: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class TypingResult:
    """Aggregated type-safety coverage and pinpointed typing issues across all files."""

    type_safety_coverage_pct: Optional[float] = 100.0
    type_safety_issues: list[CodeLocation] = field(default_factory=list)
    weak_type_usages: list[CodeLocation] = field(default_factory=list)
    unscoped_type_ignores: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class UnitDocStats:
    """Per-file documentation counts and locations returned by BaseDocChecker subclasses."""

    candidates: int = 0
    documented: int = 0
    missing_docstrings: list[CodeLocation] = field(default_factory=list)
    empty_docstrings: list[CodeLocation] = field(default_factory=list)
    doc_signature_mismatches: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class DocResult:
    """Aggregated docstring / Javadoc coverage, missing/empty docs, and signature mismatches."""

    docstring_coverage_pct: Optional[float] = 100.0
    missing_docstrings: list[CodeLocation] = field(default_factory=list)
    empty_docstrings: list[CodeLocation] = field(default_factory=list)
    doc_signature_mismatches: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class DependencyResult:
    """Internal dependency graph, cycles, manifest mismatches, and boundary violations."""

    internal_import_graph: dict[str, list[str]] = field(default_factory=dict)
    circular_dependencies: list[list[str]] = field(default_factory=list)
    type_checking_cycles: list[list[str]] = field(default_factory=list)
    unused_dependencies: list[str] = field(default_factory=list)
    undeclared_dependencies: list[CodeLocation] = field(default_factory=list)
    boundary_violations: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class TestAstResult:
    """Aggregated test callable count, module test coverage, and assertion-free tests."""

    test_functions_count: int = 0
    module_test_coverage_pct: Optional[float] = None
    assertion_free_tests: list[CodeLocation] = field(default_factory=list)
    test_harness_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FrameworkCheckResult:
    """Aggregated framework best-practice issues and ecosystem modernization hints."""

    framework_issues: list[CodeLocation] = field(default_factory=list)
    modernization_hints: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class OperationalResult:
    """Aggregated 12-Factor, SRE PRR, and OWASP ASVS operational/security AST signals."""

    missing_io_timeouts: list[CodeLocation] = field(default_factory=list)
    scattered_env_access: list[CodeLocation] = field(default_factory=list)
    unstructured_logging: list[CodeLocation] = field(default_factory=list)
    hardcoded_secrets: list[CodeLocation] = field(default_factory=list)


@dataclass(frozen=True)
class SecurityAstResult:
    """Aggregated dangerous code sinks (CWE) and extracted API route endpoints."""

    dangerous_sinks: list[SecuritySinkLocation] = field(default_factory=list)
    api_endpoints: list[ApiEndpointFact] = field(default_factory=list)

