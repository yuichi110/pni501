# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for containerized build, unit test, coverage, and startup smoke checks."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

RuntimeStageStatus = Literal["passed", "failed", "skipped", "blocked", "timeout", "error"]
BootFailureKind = Literal[
    "none",
    "import_or_di_error",
    "config_missing",
    "external_service_unreachable",
    "timeout",
    "crash",
]


class ContainerBuildResult(BaseModel):
    """Execution outcome of a container image build (project Dockerfile or PNI harness)."""

    attempted: bool = False
    status: RuntimeStageStatus = "skipped"
    dockerfile_used: str = ""
    duration_sec: float = 0.0
    exit_code: Optional[int] = None
    error_tail: list[str] = Field(default_factory=list)


class FailedTestCase(BaseModel):
    """Pinpointed test failure or error extracted from JUnit XML reports."""

    classname: str
    name: str
    kind: Literal["failure", "error"] = "failure"
    message: str = ""


class TestExecutionResult(BaseModel):
    """Structured summary of containerized unit test execution."""

    attempted: bool = False
    status: RuntimeStageStatus = "skipped"
    command: str = ""
    duration_sec: float = 0.0
    exit_code: Optional[int] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    failures: list[FailedTestCase] = Field(default_factory=list)
    log_tail: list[str] = Field(default_factory=list)


class ModuleCoverageItem(BaseModel):
    """Per-file measured line and branch coverage metrics sorted lowest-first."""

    file_path: str
    line_coverage_pct: float
    branch_coverage_pct: Optional[float] = None
    covered_lines: int = 0
    total_statements: int = 0
    missing_lines_preview: list[int] = Field(default_factory=list)


class CoverageResult(BaseModel):
    """Measured line and branch coverage parsed from pytest-cov JSON or JaCoCo XML."""

    measured: bool = False
    tool: str = ""
    line_coverage_pct: Optional[float] = None
    branch_coverage_pct: Optional[float] = None
    covered_lines: int = 0
    total_statements: int = 0
    lowest_covered_modules: list[ModuleCoverageItem] = Field(default_factory=list)


class SmokeCheckResult(BaseModel):
    """Archetype-aware startup / import / CLI help verification outcome."""

    attempted: bool = False
    archetype: str = "library"
    status: RuntimeStageStatus = "skipped"
    command: str = ""
    duration_sec: float = 0.0
    exit_code: Optional[int] = None
    http_status: Optional[int] = None
    probed_endpoint: Optional[str] = None
    failure_kind: BootFailureKind = "none"
    detail: str = ""
    log_tail: list[str] = Field(default_factory=list)


class RuntimeFacts(BaseModel):
    """Aggregated deterministic facts from containerized dynamic verification."""

    status: RuntimeStageStatus = "skipped"
    container_engine: Optional[str] = None
    engine_available: bool = False
    skip_reason: str = ""
    language: str = "python"
    selected_dockerfile_template: str = ""
    harness_dockerfile_path: str = ""
    build_args: dict[str, str] = Field(default_factory=dict)
    artifacts_dir: str = ""
    project_dockerfile_build: Optional[ContainerBuildResult] = None
    harness_build: ContainerBuildResult = Field(default_factory=ContainerBuildResult)
    test_execution: TestExecutionResult = Field(default_factory=TestExecutionResult)
    coverage: CoverageResult = Field(default_factory=CoverageResult)
    smoke_check: SmokeCheckResult = Field(default_factory=SmokeCheckResult)
