# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Multi-language deterministic AST analyzer registry and entrypoint."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Optional

from pni._actions.ast_analyze.base import (
    BaseDependencyChecker,
    BaseDocChecker,
    BaseFrameworkChecker,
    BaseImportChecker,
    BaseOperationalChecker,
    BaseQualityChecker,
    BaseSecurityChecker,
    BaseTestChecker,
    BaseTypingChecker,
)
from pni._actions.ast_analyze.go import GO_SUITE
from pni._actions.ast_analyze.java import JAVA_SUITE
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    AstFacts,
    CodeLocation,
    ModuleAstSummary,
    ParsedUnit,
    SecuritySinkLocation,
)
from pni._actions.ast_analyze.php import PHP_SUITE
from pni._actions.ast_analyze.python import PYTHON_SUITE
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite
from pni._actions.ast_analyze.ts_js import JAVASCRIPT_SUITE, TYPESCRIPT_SUITE
from pni._rules import detect_active_language

SUITE_REGISTRY: Final[dict[str, LanguageAnalyzerSuite]] = {
    "python": PYTHON_SUITE,
    "java": JAVA_SUITE,
    "php": PHP_SUITE,
    "go": GO_SUITE,
    "typescript": TYPESCRIPT_SUITE,
    "javascript": JAVASCRIPT_SUITE,
}

_EXT_TO_LANG: Final[dict[str, str]] = {
    ".java": "java",
    ".php": "php",
    ".phtml": "php",
    ".go": "go",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}


def _detect_dir_language(candidate: Path) -> str | None:
    """Detect language from source files inside a directory when no .py files exist."""
    if any(candidate.rglob("*.py")):
        return None
    for pat, lang in (
        ("*.java", "java"),
        ("*.php", "php"),
        ("*.phtml", "php"),
        ("*.go", "go"),
        ("*.tsx", "typescript"),
    ):
        if any(candidate.rglob(pat)):
            return lang
    if any(not f.name.endswith(".d.ts") for f in candidate.rglob("*.ts")):
        return "typescript"
    if any(any(candidate.rglob(pat)) for pat in ("*.js", "*.jsx", "*.mjs", "*.cjs")):
        return "javascript"
    return None


def _detect_target_language(project_root: Path, targets: Optional[list[str]]) -> str:
    """Resolve analyzer language from explicit target file extensions or project manifests."""
    if targets:
        for target in targets:
            candidate = project_root / target
            if candidate.is_file():
                mapped = _EXT_TO_LANG.get(candidate.suffix.lower())
                if mapped is not None:
                    return mapped
            elif candidate.is_dir():
                dir_lang = _detect_dir_language(candidate)
                if dir_lang is not None:
                    return dir_lang
    return detect_active_language(project_root)


def run_ast_analyze(
    project_root: Path,
    targets: Optional[list[str]] = None,
    display_root: Optional[Path] = None,
    lang: Optional[str] = None,
    test_targets: Optional[list[str]] = None,
    detected_frameworks: Optional[list[str]] = None,
    declared_lang_version: Optional[str] = None,
    exclude_globs: Optional[list[str]] = None,
) -> AstFacts:
    """Analyze source and test files in target directories deterministically using ast-grep-py.

    Args:
        project_root: Target project root directory.
        targets: Relative source directory or file names inside project_root.
        display_root: Optional workspace root used to format file paths in CodeLocation.
        lang: Optional explicit language override ('python', 'java', 'php', 'go', 'typescript', 'javascript').
        test_targets: Optional relative test directory names inside project_root.
        detected_frameworks: Optional pre-detected framework identifiers.
        declared_lang_version: Optional declared language version constraint from ProjectFacts.
        exclude_globs: Optional glob patterns relative to project_root to exclude from discovery.

    Returns:
        AstFacts: Language-agnostic deterministic AST metrics and pinpointed code locations.
    """
    active_lang = (lang or _detect_target_language(project_root, targets)).lower()
    suite = SUITE_REGISTRY.get(active_lang, PYTHON_SUITE)
    return suite.analyze(
        project_root,
        targets=targets,
        display_root=display_root,
        test_targets=test_targets,
        detected_frameworks=detected_frameworks,
        declared_lang_version=declared_lang_version,
        exclude_globs=exclude_globs,
    )


__all__ = [
    "GO_SUITE",
    "JAVASCRIPT_SUITE",
    "JAVA_SUITE",
    "PHP_SUITE",
    "PYTHON_SUITE",
    "SUITE_REGISTRY",
    "TYPESCRIPT_SUITE",
    "ApiEndpointFact",
    "AstFacts",
    "BaseDependencyChecker",
    "BaseDocChecker",
    "BaseFrameworkChecker",
    "BaseImportChecker",
    "BaseOperationalChecker",
    "BaseQualityChecker",
    "BaseSecurityChecker",
    "BaseTestChecker",
    "BaseTypingChecker",
    "CodeLocation",
    "LanguageAnalyzerSuite",
    "ModuleAstSummary",
    "ParsedUnit",
    "SecuritySinkLocation",
    "run_ast_analyze",
]
