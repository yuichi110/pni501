# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP AST analyzer suite binding PSR-4/Composer and legacy Raw-PHP/WordPress checkers."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.php._helpers import normalize_php_source_for_cst
from pni._actions.ast_analyze.php.dependencies import PhpDependencyChecker
from pni._actions.ast_analyze.php.docs import PhpDocChecker
from pni._actions.ast_analyze.php.frameworks import LaravelFrameworkChecker, WordPressFrameworkChecker
from pni._actions.ast_analyze.php.imports import PhpImportChecker
from pni._actions.ast_analyze.php.operational import PhpOperationalChecker
from pni._actions.ast_analyze.php.quality import PhpQualityChecker
from pni._actions.ast_analyze.php.security import PhpSecurityChecker
from pni._actions.ast_analyze.php.testing import PhpTestChecker
from pni._actions.ast_analyze.php.typing import PhpTypingChecker
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite

PHP_SUITE: Final[LanguageAnalyzerSuite] = LanguageAnalyzerSuite(
    language="php",
    ast_grep_lang="php",
    file_extensions=(".php", ".phtml"),
    default_target_dirs=("app", "src", "routes", "includes", "public"),
    fallback_dirs=(".",),
    default_test_dirs=("tests", "test"),
    import_checker=PhpImportChecker(),
    quality_checker=PhpQualityChecker(),
    typing_checker=PhpTypingChecker(),
    doc_checker=PhpDocChecker(),
    dependency_checker=PhpDependencyChecker(),
    test_checker=PhpTestChecker(),
    operational_checker=PhpOperationalChecker(),
    security_checker=PhpSecurityChecker(),
    framework_checkers=(LaravelFrameworkChecker(), WordPressFrameworkChecker()),
    source_preprocessor=normalize_php_source_for_cst,
)

__all__ = [
    "PHP_SUITE",
    "LaravelFrameworkChecker",
    "PhpDependencyChecker",
    "PhpDocChecker",
    "PhpImportChecker",
    "PhpOperationalChecker",
    "PhpQualityChecker",
    "PhpSecurityChecker",
    "PhpTestChecker",
    "PhpTypingChecker",
    "WordPressFrameworkChecker",
    "normalize_php_source_for_cst",
]
