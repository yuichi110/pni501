# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for test suite AST health and assertion-free test detection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from pni._actions.ast_analyze.models import ParsedUnit, TestAstResult


class BaseTestChecker(ABC):
    """Template-method base class for language test-suite AST checkers."""

    applicable: ClassVar[bool] = True

    def check(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Analyze parsed test units for assertion presence and source module coverage.

        Args:
            test_units: Parsed test compilation units.
            source_units: Parsed main source compilation units.
            project_root: Target project root directory.

        Returns:
            TestAstResult: Test callable count, module coverage percentage, and assertion-free tests.
        """
        if not self.applicable or not test_units:
            return TestAstResult()
        return self.inspect_test_suite(test_units, source_units, project_root)

    @abstractmethod
    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Inspect test units for test functions, assertion presence, and source coverage."""
