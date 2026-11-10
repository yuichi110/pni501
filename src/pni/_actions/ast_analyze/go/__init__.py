# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go AST analyzer suite binding Go checkers and framework plugins."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.go.dependencies import GoDependencyChecker
from pni._actions.ast_analyze.go.docs import GoDocChecker
from pni._actions.ast_analyze.go.frameworks import GoModernizationChecker
from pni._actions.ast_analyze.go.imports import GoImportChecker
from pni._actions.ast_analyze.go.operational import GoOperationalChecker
from pni._actions.ast_analyze.go.quality import GoQualityChecker
from pni._actions.ast_analyze.go.security import GoSecurityChecker
from pni._actions.ast_analyze.go.testing import GoTestChecker
from pni._actions.ast_analyze.go.typing import GoTypingChecker
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite

GO_SUITE: Final[LanguageAnalyzerSuite] = LanguageAnalyzerSuite(
    language="go",
    ast_grep_lang="go",
    file_extensions=(".go",),
    default_target_dirs=("cmd", "internal", "pkg", "."),
    fallback_dirs=(".",),
    default_test_dirs=("cmd", "internal", "pkg", "."),
    test_file_patterns=("*_test.go",),
    import_checker=GoImportChecker(),
    quality_checker=GoQualityChecker(),
    typing_checker=GoTypingChecker(),
    doc_checker=GoDocChecker(),
    dependency_checker=GoDependencyChecker(),
    test_checker=GoTestChecker(),
    operational_checker=GoOperationalChecker(),
    security_checker=GoSecurityChecker(),
    framework_checkers=(GoModernizationChecker(),),
)

__all__ = ["GO_SUITE"]
