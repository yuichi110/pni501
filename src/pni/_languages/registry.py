# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Declarative single-source-of-truth registry for supported languages and Tree-sitter grammars."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

LanguageTier = Literal["full_audit", "static_audit", "companion_dsl"]
LanguageCategory = Literal[
    "app_language",
    "systems_hdl",
    "legacy_enterprise",
    "frontend_sfc",
    "iac_schema_config",
]
GrammarSource = Literal["package", "language_pack", "extra_wheel"]


@dataclass(frozen=True)
class GrammarProviderSpec:
    """Tree-sitter grammar loader binding for a single grammar identifier."""

    grammar_id: str
    module_name: str
    callable_name: str = "language"
    source: GrammarSource = "package"


@dataclass(frozen=True)
class LanguageSpec:
    """Canonical metadata describing one PNI-supported language."""

    language_id: str
    display_name: str
    tier: LanguageTier
    category: LanguageCategory
    default_grammar: str
    file_extensions: tuple[str, ...] = ()
    filenames: tuple[str, ...] = ()
    ext_grammars: tuple[tuple[str, str], ...] = ()
    primary_manifests: tuple[str, ...] = ()
    secondary_manifests: tuple[str, ...] = ()
    default_source_dirs: tuple[str, ...] = ("src",)
    default_test_dirs: tuple[str, ...] = ("tests",)
    test_file_patterns: tuple[str, ...] = ()
    excluded_source_suffixes: tuple[str, ...] = ()
    has_runtime_harness: bool = False


GRAMMAR_PROVIDERS: dict[str, GrammarProviderSpec] = {
    "python": GrammarProviderSpec("python", "tree_sitter_python", "language"),
    "java": GrammarProviderSpec("java", "tree_sitter_java", "language"),
    "php": GrammarProviderSpec("php", "tree_sitter_php", "language_php"),
    "php_only": GrammarProviderSpec("php_only", "tree_sitter_php", "language_php_only"),
    "go": GrammarProviderSpec("go", "tree_sitter_go", "language"),
    "typescript": GrammarProviderSpec("typescript", "tree_sitter_typescript", "language_typescript"),
    "tsx": GrammarProviderSpec("tsx", "tree_sitter_typescript", "language_tsx"),
    "javascript": GrammarProviderSpec("javascript", "tree_sitter_javascript", "language"),
}

LANGUAGE_REGISTRY: dict[str, LanguageSpec] = {
    "python": LanguageSpec(
        language_id="python",
        display_name="Python",
        tier="full_audit",
        category="app_language",
        default_grammar="python",
        file_extensions=(".py",),
        primary_manifests=("pyproject.toml", "setup.py", "setup.cfg", "Pipfile"),
        secondary_manifests=("requirements.txt",),
        default_source_dirs=("src",),
        default_test_dirs=("tests",),
        has_runtime_harness=True,
    ),
    "java": LanguageSpec(
        language_id="java",
        display_name="Java",
        tier="full_audit",
        category="app_language",
        default_grammar="java",
        file_extensions=(".java",),
        primary_manifests=("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"),
        default_source_dirs=("src/main/java",),
        default_test_dirs=("src/test/java",),
        has_runtime_harness=True,
    ),
    "php": LanguageSpec(
        language_id="php",
        display_name="PHP",
        tier="full_audit",
        category="app_language",
        default_grammar="php",
        file_extensions=(".php", ".phtml"),
        primary_manifests=(
            "composer.json",
            "wp-config.php",
            "wp-config-sample.php",
            "artisan",
            "phpunit.xml",
            "phpunit.xml.dist",
        ),
        default_source_dirs=("app", "src", "routes"),
        default_test_dirs=("tests",),
        has_runtime_harness=True,
    ),
    "go": LanguageSpec(
        language_id="go",
        display_name="Go",
        tier="full_audit",
        category="app_language",
        default_grammar="go",
        file_extensions=(".go",),
        primary_manifests=("go.mod", "go.work"),
        default_source_dirs=(".",),
        default_test_dirs=(".",),
        test_file_patterns=("*_test.go",),
        has_runtime_harness=True,
    ),
    "typescript": LanguageSpec(
        language_id="typescript",
        display_name="TypeScript",
        tier="full_audit",
        category="app_language",
        default_grammar="typescript",
        file_extensions=(".ts", ".tsx"),
        ext_grammars=((".ts", "typescript"), (".tsx", "tsx")),
        primary_manifests=("tsconfig.json", "tsconfig.base.json"),
        secondary_manifests=("package.json",),
        default_source_dirs=("src",),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*.test.ts", "*.spec.ts", "*.test.tsx", "*.spec.tsx"),
        excluded_source_suffixes=(".d.ts",),
        has_runtime_harness=True,
    ),
    "javascript": LanguageSpec(
        language_id="javascript",
        display_name="JavaScript",
        tier="full_audit",
        category="app_language",
        default_grammar="tsx",
        file_extensions=(".js", ".jsx", ".mjs", ".cjs"),
        ext_grammars=((".js", "tsx"), (".jsx", "tsx"), (".mjs", "tsx"), (".cjs", "tsx")),
        primary_manifests=("jsconfig.json",),
        secondary_manifests=("package.json",),
        default_source_dirs=("src",),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*.test.js", "*.spec.js", "*.test.jsx", "*.spec.jsx", "*.test.mjs", "*.spec.mjs"),
        has_runtime_harness=True,
    ),
}


def register_grammar_provider(spec: GrammarProviderSpec) -> None:
    """Register or override a Tree-sitter grammar provider entry."""
    GRAMMAR_PROVIDERS[spec.grammar_id.lower()] = spec


def get_grammar_provider(grammar_id: str) -> GrammarProviderSpec | None:
    """Look up a registered Tree-sitter grammar provider by grammar_id."""
    return GRAMMAR_PROVIDERS.get(grammar_id.strip().lower())


def register_language_spec(spec: LanguageSpec) -> None:
    """Register or override a language specification in the central registry."""
    LANGUAGE_REGISTRY[spec.language_id.lower()] = spec


def get_language_spec(language_id: str) -> LanguageSpec | None:
    """Return the LanguageSpec for a normalized language_id, or None if unregistered."""
    return LANGUAGE_REGISTRY.get(language_id.strip().lower())


def iter_language_specs(*, tier: LanguageTier | None = None) -> tuple[LanguageSpec, ...]:
    """Return registered LanguageSpec entries, optionally filtered by support tier."""
    if tier is None:
        return tuple(LANGUAGE_REGISTRY.values())
    return tuple(spec for spec in LANGUAGE_REGISTRY.values() if spec.tier == tier)


def list_supported_languages(*, tier: LanguageTier | None = None) -> tuple[str, ...]:
    """Return registered language IDs in deterministic registration order."""
    return tuple(spec.language_id for spec in iter_language_specs(tier=tier))
