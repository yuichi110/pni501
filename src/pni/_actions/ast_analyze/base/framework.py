# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Composable 1:N base plugin checker for framework best practices and modernization hints."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from pni._actions.ast_analyze.models import (
    CodeLocation,
    FrameworkCheckResult,
    ParsedUnit,
)


class BaseFrameworkChecker(ABC):
    """Composable base class for framework-specific AST checks and modernization signals."""

    framework_id: ClassVar[str]

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Return True if this checker should execute for the target project."""
        _ = units
        return self.framework_id in detected_frameworks

    def check(self, units: list[ParsedUnit]) -> FrameworkCheckResult:
        """Aggregate framework best-practice issues and modernization hints across units."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []
        for unit in units:
            res = self.inspect_unit(unit)
            issues.extend(res.framework_issues)
            hints.extend(res.modernization_hints)
        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)

    @abstractmethod
    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Inspect a single parsed unit for framework anti-patterns or modernization hints."""
