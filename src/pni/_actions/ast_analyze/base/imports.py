# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for import grouping, alphabetical sorting, wildcards, and late imports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from pni._actions.ast_analyze.models import (
    CodeLocation,
    ImportResult,
    ParsedUnit,
    UnitImportStats,
)


class BaseImportChecker(ABC):
    """Template-method base class for language import hygiene and sorting checkers."""

    applicable: ClassVar[bool] = True

    def check(self, units: list[ParsedUnit], project_root: Path) -> ImportResult:
        """Aggregate per-unit import hygiene checks and compute clean-file coverage percentage.

        Args:
            units: Parsed compilation units in the target project.
            project_root: Target project root directory.

        Returns:
            ImportResult: Import hygiene coverage percentage and pinpointed import violations.
        """
        if not self.applicable:
            return ImportResult(import_hygiene_coverage_pct=None)

        root_packages = self.discover_root_packages(units, project_root)
        clean_units = 0
        unsorted: list[CodeLocation] = []
        wildcards: list[CodeLocation] = []
        late: list[CodeLocation] = []

        for unit in units:
            stats = self.inspect_unit_imports(unit, root_packages)
            if stats.is_clean and not stats.unsorted_imports and not stats.wildcard_imports:
                clean_units += 1
            unsorted.extend(stats.unsorted_imports)
            wildcards.extend(stats.wildcard_imports)
            late.extend(stats.late_imports)

        pct = round((clean_units / len(units)) * 100.0, 1) if units else 100.0
        return ImportResult(
            import_hygiene_coverage_pct=pct,
            unsorted_imports=unsorted,
            wildcard_imports=wildcards,
            late_imports=late,
        )

    def discover_root_packages(self, units: list[ParsedUnit], project_root: Path) -> set[str]:
        """Discover internal root package/namespace identifiers for import classification."""
        _ = (units, project_root)
        return set()

    @abstractmethod
    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Inspect a single parsed unit for import ordering, blank lines, wildcards, and late imports."""
