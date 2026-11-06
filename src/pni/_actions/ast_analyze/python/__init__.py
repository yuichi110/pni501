# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python AST analyzer suite binding all Python language and framework checkers."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.python.dependencies import PythonDependencyChecker
from pni._actions.ast_analyze.python.docs import PythonDocChecker
from pni._actions.ast_analyze.python.frameworks import (
    FastApiFrameworkChecker,
    FlaskModernizationChecker,
    PydanticFrameworkChecker,
    PythonModernSyntaxChecker,
)
from pni._actions.ast_analyze.python.imports import PythonImportChecker
from pni._actions.ast_analyze.python.operational import PythonOperationalChecker
from pni._actions.ast_analyze.python.quality import PythonQualityChecker
from pni._actions.ast_analyze.python.security import PythonSecurityChecker
from pni._actions.ast_analyze.python.testing import PythonTestChecker
from pni._actions.ast_analyze.python.typing import PythonTypingChecker
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite

PYTHON_SUITE: Final[LanguageAnalyzerSuite] = LanguageAnalyzerSuite(
    language="python",
    ast_grep_lang="python",
    file_extensions=(".py",),
    default_target_dirs=("src",),
    fallback_dirs=(),
    import_checker=PythonImportChecker(),
    quality_checker=PythonQualityChecker(),
    typing_checker=PythonTypingChecker(),
    doc_checker=PythonDocChecker(),
    dependency_checker=PythonDependencyChecker(),
    test_checker=PythonTestChecker(),
    operational_checker=PythonOperationalChecker(),
    security_checker=PythonSecurityChecker(),
    default_test_dirs=("tests",),
    framework_checkers=(
        FastApiFrameworkChecker(),
        PydanticFrameworkChecker(),
        FlaskModernizationChecker(),
        PythonModernSyntaxChecker(),
    ),
)

__all__ = [
    "PYTHON_SUITE",
    "FastApiFrameworkChecker",
    "FlaskModernizationChecker",
    "PydanticFrameworkChecker",
    "PythonDependencyChecker",
    "PythonDocChecker",
    "PythonImportChecker",
    "PythonModernSyntaxChecker",
    "PythonOperationalChecker",
    "PythonQualityChecker",
    "PythonSecurityChecker",
    "PythonTestChecker",
    "PythonTypingChecker",
]
