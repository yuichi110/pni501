# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript AST analyzer suites sharing unified ES/TS CST checkers."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite
from pni._actions.ast_analyze.ts_js.dependencies import TsJsDependencyChecker
from pni._actions.ast_analyze.ts_js.docs import TsJsDocChecker
from pni._actions.ast_analyze.ts_js.frameworks import TsJsFrameworkChecker
from pni._actions.ast_analyze.ts_js.imports import TsJsImportChecker
from pni._actions.ast_analyze.ts_js.operational import TsJsOperationalChecker
from pni._actions.ast_analyze.ts_js.quality import TsJsQualityChecker
from pni._actions.ast_analyze.ts_js.security import TsJsSecurityChecker
from pni._actions.ast_analyze.ts_js.testing import TsJsTestChecker
from pni._actions.ast_analyze.ts_js.typing import TsJsTypingChecker

_TS_TEST_PATTERNS: Final[tuple[str, ...]] = (
    "*.test.ts",
    "*.spec.ts",
    "*.test.tsx",
    "*.spec.tsx",
    "*_test.ts",
    "test_*.ts",
    "*.test.js",
    "*.spec.js",
    "*.test.jsx",
    "*.spec.jsx",
)
_JS_TEST_PATTERNS: Final[tuple[str, ...]] = (
    "*.test.js",
    "*.spec.js",
    "*.test.jsx",
    "*.spec.jsx",
    "*.test.mjs",
    "*.spec.mjs",
    "*_test.js",
    "test_*.js",
)

TYPESCRIPT_SUITE: Final[LanguageAnalyzerSuite] = LanguageAnalyzerSuite(
    language="typescript",
    ast_grep_lang="typescript",
    file_extensions=(".ts", ".tsx"),
    default_target_dirs=("src", "app", "lib", "pages", "components"),
    fallback_dirs=("src", "."),
    default_test_dirs=("tests", "test", "__tests__", "src"),
    test_file_patterns=_TS_TEST_PATTERNS,
    excluded_source_suffixes=(".d.ts",),
    import_checker=TsJsImportChecker(),
    quality_checker=TsJsQualityChecker(),
    typing_checker=TsJsTypingChecker(language="typescript"),
    doc_checker=TsJsDocChecker(),
    dependency_checker=TsJsDependencyChecker(),
    test_checker=TsJsTestChecker(),
    operational_checker=TsJsOperationalChecker(),
    security_checker=TsJsSecurityChecker(),
    framework_checkers=(TsJsFrameworkChecker(),),
)

JAVASCRIPT_SUITE: Final[LanguageAnalyzerSuite] = LanguageAnalyzerSuite(
    language="javascript",
    ast_grep_lang="javascript",
    file_extensions=(".js", ".jsx", ".mjs", ".cjs"),
    default_target_dirs=("src", "app", "lib", "pages", "components"),
    fallback_dirs=("src", "lib", "."),
    default_test_dirs=("tests", "test", "__tests__", "src"),
    test_file_patterns=_JS_TEST_PATTERNS,
    excluded_source_suffixes=(".d.ts", ".min.js"),
    import_checker=TsJsImportChecker(),
    quality_checker=TsJsQualityChecker(),
    typing_checker=TsJsTypingChecker(language="javascript"),
    doc_checker=TsJsDocChecker(),
    dependency_checker=TsJsDependencyChecker(),
    test_checker=TsJsTestChecker(),
    operational_checker=TsJsOperationalChecker(),
    security_checker=TsJsSecurityChecker(),
    framework_checkers=(TsJsFrameworkChecker(),),
)

__all__ = ["JAVASCRIPT_SUITE", "TYPESCRIPT_SUITE"]
