# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Containerized dynamic verification (build, unit tests, coverage, smoke boot) package."""

from __future__ import annotations

from pni._actions.runtime_check.models import (
    BootFailureKind,
    ContainerBuildResult,
    CoverageResult,
    FailedTestCase,
    ModuleCoverageItem,
    RuntimeFacts,
    RuntimeStageStatus,
    SmokeCheckResult,
    TestExecutionResult,
)
from pni._actions.runtime_check.parsers import extract_verbatim_error_excerpt
from pni._actions.runtime_check.runner import RuntimeCheckOptions, run_runtime_check

__all__ = [
    "BootFailureKind",
    "ContainerBuildResult",
    "CoverageResult",
    "FailedTestCase",
    "ModuleCoverageItem",
    "RuntimeCheckOptions",
    "RuntimeFacts",
    "RuntimeStageStatus",
    "SmokeCheckResult",
    "TestExecutionResult",
    "extract_verbatim_error_excerpt",
    "run_runtime_check",
]
