# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Multi-language deterministic AST analyzer registry and entrypoint across all 55 languages."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Optional

from pni._actions.ast_analyze._cst import CstNode, CstPos, CstRange, parse_cst
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
from pni._actions.ast_analyze.companion import (
    DEFAULT_COMPANION_LANGUAGES,
    scan_companion_languages,
)
from pni._actions.ast_analyze.declarative import DECLARATIVE_SUITES
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
from pni._languages import LANGUAGE_REGISTRY, get_language_by_path, resolve_language_id
from pni._rules import detect_active_language

SUITE_REGISTRY: Final[dict[str, LanguageAnalyzerSuite]] = {
    "python": PYTHON_SUITE,
    "java": JAVA_SUITE,
    "php": PHP_SUITE,
    "go": GO_SUITE,
    "typescript": TYPESCRIPT_SUITE,
    "javascript": JAVASCRIPT_SUITE,
    **DECLARATIVE_SUITES,
}


def _detect_extended_dir_language(candidate: Path) -> str | None:
    """Detect non-core Tier A/B language from file extensions inside candidate directory."""
    core_ids = {"python", "java", "php", "go", "typescript", "javascript"}
    for spec in LANGUAGE_REGISTRY.values():
        if spec.language_id in core_ids or spec.tier == "companion_dsl":
            continue
        if any(any(candidate.rglob(f"*{ext}")) for ext in spec.file_extensions):
            return spec.language_id
    return None


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
    return _detect_extended_dir_language(candidate)


def _detect_target_language(project_root: Path, targets: Optional[list[str]]) -> str:
    """Resolve analyzer language from explicit target files/directories or project manifests."""
    if targets:
        for target in targets:
            candidate = project_root / target
            if candidate.is_file():
                spec = get_language_by_path(candidate)
                if spec is not None:
                    return spec.language_id
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
    """Analyze source and test files in target directories deterministically using tree-sitter.

    Args:
        project_root: Target project root directory.
        targets: Relative source directory or file names inside project_root.
        display_root: Optional workspace root used to format file paths in CodeLocation.
        lang: Optional explicit language override (any of the 55 registered language IDs or aliases).
        test_targets: Optional relative test directory names inside project_root.
        detected_frameworks: Optional pre-detected framework identifiers.
        declared_lang_version: Optional declared language version constraint from ProjectFacts.
        exclude_globs: Optional glob patterns relative to project_root to exclude from discovery.

    Returns:
        AstFacts: Language-agnostic deterministic AST metrics and pinpointed code locations.
    """
    active_lang = resolve_language_id(lang) if lang else _detect_target_language(project_root, targets)
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
    "DECLARATIVE_SUITES",
    "DEFAULT_COMPANION_LANGUAGES",
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
    "CstNode",
    "CstPos",
    "CstRange",
    "LanguageAnalyzerSuite",
    "ModuleAstSummary",
    "ParsedUnit",
    "SecuritySinkLocation",
    "parse_cst",
    "run_ast_analyze",
    "scan_companion_languages",
]
