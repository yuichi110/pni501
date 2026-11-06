# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java AST analyzer suite binding Java import, quality, typing, docs, dep, test, and framework checkers."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.java.dependencies import JavaDependencyChecker
from pni._actions.ast_analyze.java.docs import JavaDocChecker
from pni._actions.ast_analyze.java.frameworks import (
    JavaModernSyntaxChecker,
    SpringBootFrameworkChecker,
)
from pni._actions.ast_analyze.java.imports import JavaImportChecker
from pni._actions.ast_analyze.java.operational import JavaOperationalChecker
from pni._actions.ast_analyze.java.quality import JavaQualityChecker
from pni._actions.ast_analyze.java.security import JavaSecurityChecker
from pni._actions.ast_analyze.java.testing import JavaTestChecker
from pni._actions.ast_analyze.java.typing import JavaTypingChecker
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite

JAVA_SUITE: Final[LanguageAnalyzerSuite] = LanguageAnalyzerSuite(
    language="java",
    ast_grep_lang="java",
    file_extensions=(".java",),
    default_target_dirs=("src/main/java", "src"),
    fallback_dirs=("src/main/java", "src"),
    import_checker=JavaImportChecker(),
    quality_checker=JavaQualityChecker(),
    typing_checker=JavaTypingChecker(),
    doc_checker=JavaDocChecker(),
    dependency_checker=JavaDependencyChecker(),
    test_checker=JavaTestChecker(),
    operational_checker=JavaOperationalChecker(),
    security_checker=JavaSecurityChecker(),
    default_test_dirs=("src/test/java", "test", "tests"),
    framework_checkers=(
        SpringBootFrameworkChecker(),
        JavaModernSyntaxChecker(),
    ),
)

__all__ = [
    "JAVA_SUITE",
    "JavaDependencyChecker",
    "JavaDocChecker",
    "JavaImportChecker",
    "JavaModernSyntaxChecker",
    "JavaOperationalChecker",
    "JavaQualityChecker",
    "JavaSecurityChecker",
    "JavaTestChecker",
    "JavaTypingChecker",
    "SpringBootFrameworkChecker",
]
