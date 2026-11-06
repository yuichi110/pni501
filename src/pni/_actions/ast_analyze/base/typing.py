# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for type annotation / generic safety, weak types, and unscoped ignores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    TypingResult,
    UnitTypingStats,
)


class BaseTypingChecker(ABC):
    """Template-method base class for language static-type safety checkers."""

    applicable: ClassVar[bool] = True

    def check(self, units: list[ParsedUnit]) -> TypingResult:
        """Aggregate per-unit type safety checks and compute overall coverage percentage.

        Args:
            units: Parsed compilation units in the target project.

        Returns:
            TypingResult: Coverage percentage, missing/raw type issues, weak usages, and ignores.
        """
        if not self.applicable:
            return TypingResult(type_safety_coverage_pct=None)

        total_callables = 0
        safe_callables = 0
        issues: list[CodeLocation] = []
        weak_usages: list[CodeLocation] = []
        ignores: list[CodeLocation] = []

        for unit in units:
            stats = self.inspect_unit_typing(unit)
            total_callables += stats.total_callables
            safe_callables += stats.type_safe_callables
            issues.extend(stats.type_safety_issues)
            weak_usages.extend(stats.weak_type_usages)
            ignores.extend(stats.unscoped_type_ignores)

        coverage_pct = round((safe_callables / total_callables) * 100.0, 1) if total_callables > 0 else 100.0
        return TypingResult(
            type_safety_coverage_pct=coverage_pct,
            type_safety_issues=issues,
            weak_type_usages=weak_usages,
            unscoped_type_ignores=ignores,
        )

    @abstractmethod
    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect a single parsed unit for missing annotations/generics, weak types, and ignores."""
