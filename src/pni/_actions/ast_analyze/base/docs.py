# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for docstring / Javadoc coverage, empty docs, and signature consistency."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from pni._actions.ast_analyze.models import (
    CodeLocation,
    DocResult,
    ParsedUnit,
    UnitDocStats,
)


class BaseDocChecker(ABC):
    """Template-method base class for language docstring / Javadoc checkers."""

    applicable: ClassVar[bool] = True

    def check(self, units: list[ParsedUnit]) -> DocResult:
        """Aggregate per-unit documentation checks and compute overall coverage percentage.

        Args:
            units: Parsed compilation units in the target project.

        Returns:
            DocResult: Coverage percentage, missing/empty docs, and parameter mismatches.
        """
        if not self.applicable:
            return DocResult(docstring_coverage_pct=None)

        candidates = 0
        documented = 0
        annotated_doc_fns = 0
        missing: list[CodeLocation] = []
        empty: list[CodeLocation] = []
        mismatches: list[CodeLocation] = []

        for unit in units:
            stats = self.inspect_unit_docs(unit)
            candidates += stats.candidates
            documented += stats.documented
            annotated_doc_fns += stats.annotated_doc_functions
            missing.extend(stats.missing_docstrings)
            empty.extend(stats.empty_docstrings)
            mismatches.extend(stats.doc_signature_mismatches)

        coverage_pct = round((documented / candidates) * 100.0, 1) if candidates > 0 else 100.0
        return DocResult(
            docstring_coverage_pct=coverage_pct,
            annotated_doc_functions_count=annotated_doc_fns,
            missing_docstrings=missing,
            empty_docstrings=empty,
            doc_signature_mismatches=mismatches,
        )

    @abstractmethod
    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Inspect a single parsed unit for public documentation coverage and consistency."""
