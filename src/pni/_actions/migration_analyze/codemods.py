# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Preflight readiness checker, transformation mode classifier, and codemod/blocker mapper."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze.models import AstFacts
from pni._actions.migration_analyze.models import (
    BoundaryTouchpoint,
    CodemodRecipeMatch,
    MigrationBlocker,
    MigrationOptions,
    PreflightReadinessHint,
    ResolvedMigrationStrategy,
    TransformationMode,
)
from pni._actions.project_inspect import ProjectFacts
from pni._actions.runtime_check.models import RuntimeFacts

_VAGUE_BRIEF_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:tbd|todo|undecided)\b|未定|いい感じ|よしなに|おまかせ|お任せ",
    re.IGNORECASE,
)
_VAGUE_LATEST_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:to\s+latest|最新版?へ|最新化のみ)(?!\s*\(?\s*\d)",
    re.IGNORECASE,
)
_ARCH_RESTRUCTURE_RE: Final[re.Pattern[str]] = re.compile(
    r"clean\s*arch|クリーンアーキテクチャ|hexagonal|ヘキサゴナル|onion|オニオン|"
    r"\bport\b|\badapter\b|ddd|ドメイン駆動|modular\s*monolith|モジュラー|"
    r"\bredis\b|\bpostgres|\bpostgresql\b|\bjpa\b|\bflyway\b|\bsqlalchemy\b",
    re.IGNORECASE,
)


def check_migration_preflight_hints(
    options: MigrationOptions,
    resolved_brief: str,
) -> list[PreflightReadinessHint]:
    """Inspect MigrationOptions and brief text for underspecified or unpinned settings.

    Args:
        options: Parsed migration step options.
        resolved_brief: Merged free-format brief text from `brief` and `brief_file`.

    Returns:
        list[PreflightReadinessHint]: Deterministic readiness recommendations before `workflows start`.
    """
    hints: list[PreflightReadinessHint] = []
    clean = resolved_brief.strip()
    if not clean:
        hints.append(
            PreflightReadinessHint(
                code="MISSING_BRIEF",
                message=(
                    "`brief` / `brief_file` is empty. Ask the user to clarify target versions, DB/Cache choices, "
                    "architecture boundaries, and API compatibility, then write them into `.pni/workflows/*.yaml`."
                ),
            )
        )
    elif len(clean) < 40:
        hints.append(
            PreflightReadinessHint(
                code="BRIEF_TOO_TERSE",
                message=(
                    f"`brief` is very short ({len(clean)} chars). Clarify target versions, stateful middleware, "
                    "API compatibility, and non-goals with the user before starting the workflow."
                ),
            )
        )

    if clean and (_VAGUE_BRIEF_RE.search(clean) or _VAGUE_LATEST_RE.search(clean)):
        hints.append(
            PreflightReadinessHint(
                code="VAGUE_BRIEF_TERMS",
                message=(
                    "`brief` contains vague placeholders ('latest'/'最新'/'未定'/'TBD'/'いい感じ'). "
                    "Confirm concrete runtime/framework versions and constraints with the user and update YAML."
                ),
            )
        )

    if options.migration_strategy == "auto":
        hints.append(
            PreflightReadinessHint(
                code="UNPINNED_STRATEGY",
                message=(
                    "`migration_strategy` is set to 'auto'. Recommend confirming 'phased_pr', 'strangler_fig', "
                    "or 'rewrite' with the user and pinning it explicitly in `.pni/workflows/*.yaml`."
                ),
            )
        )

    if options.codemod_tool == "auto":
        hints.append(
            PreflightReadinessHint(
                code="UNPINNED_CODEMOD_TOOL",
                message=(
                    "`codemod_tool` is set to 'auto'. Consider pinning 'openrewrite', 'rector', 'ruff', "
                    "or 'manual_only' after confirming the target stack."
                ),
            )
        )
    return hints


_CROSS_STACK_TOKENS: dict[str, tuple[str, ...]] = {
    "php": ("fastapi", "python", "spring boot", "golang", "typescript", "nestjs"),
    "java": ("kotlin", "golang", "go へ", "python", "fastapi", "rust"),
    "python": ("golang", "rust", "java 21", "spring boot", "typescript"),
    "go": ("rust", "java 21", "spring boot", "python", "fastapi", "typescript"),
    "typescript": ("golang", "rust", "java 21", "spring boot", "python", "fastapi"),
    "javascript": ("golang", "rust", "java 21", "spring boot", "python", "fastapi"),
}


def _detect_cross_stack(source_lang: str, brief_low: str, frameworks: list[str]) -> bool:
    """Return True when the brief requests migrating across languages or from raw PHP to a full framework."""
    lang = source_lang.lower()
    tokens = _CROSS_STACK_TOKENS.get(lang, ())
    if any(tok in brief_low for tok in tokens):
        return True
    if lang == "php":
        is_legacy_php = not any(fw in frameworks for fw in ("laravel", "symfony"))
        return is_legacy_php and any(tok in brief_low for tok in ("laravel", "symfony"))
    return False


def classify_transformation_mode(
    source_lang: str,
    resolved_brief: str,
    project_facts: ProjectFacts | None,
    touchpoints: list[BoundaryTouchpoint],
) -> TransformationMode:
    """Classify migration complexity into same_lang_upgrade, architectural_restructure, or cross_stack_replacement."""
    brief_low = resolved_brief.lower()
    fws = [f.lower() for f in (project_facts.detected_frameworks if project_facts else [])]
    if _detect_cross_stack(source_lang, brief_low, fws):
        return "cross_stack_replacement"
    if _ARCH_RESTRUCTURE_RE.search(resolved_brief) or (
        len(touchpoints) >= 2 and any(k in brief_low for k in ("cache", "キャッシュ", "db", "データベース", "layer"))
    ):
        return "architectural_restructure"
    return "same_lang_upgrade"


def resolve_effective_strategy(
    options: MigrationOptions,
    mode: TransformationMode,
) -> ResolvedMigrationStrategy:
    """Resolve effective rollout strategy from explicit option or transformation mode."""
    if options.migration_strategy in ("phased_pr", "strangler_fig", "rewrite"):
        return options.migration_strategy
    if mode == "cross_stack_replacement":
        return "strangler_fig"
    return "phased_pr"


def _java_codemods(total_files: int, brief_low: str, ast_facts: AstFacts | None) -> list[CodemodRecipeMatch]:
    """Match OpenRewrite recipes applicable to a Java project."""
    recipes = [
        CodemodRecipeMatch(
            tool="openrewrite",
            recipe_id="org.openrewrite.java.migrate.UpgradeToJava21",
            title="Upgrade Java Compiler Target & Standard Library Idioms to Java 21 LTS",
            applicable_files_count=max(total_files, 1),
            rationale="Automates Java 8->21 POM properties, diamond operators, and deprecated JDK API replacements.",
        ),
    ]
    if "spring" in brief_low or "jakarta" in brief_low or (ast_facts and ast_facts.framework_issues):
        recipes.append(
            CodemodRecipeMatch(
                tool="openrewrite",
                recipe_id="org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_4",
                title="Migrate Spring Boot 2.x (javax.*) to Spring Boot 3.4 (jakarta.*) & Constructor DI",
                applicable_files_count=max(total_files, 1),
                rationale="Rewrites javax.servlet/persistence imports to jakarta.* and updates Spring Boot starters.",
            )
        )
    recipes.append(
        CodemodRecipeMatch(
            tool="openrewrite",
            recipe_id="org.openrewrite.java.testing.junit5.JUnit4to5Migration",
            title="Migrate JUnit 4 @Test / Assertions to JUnit 5 Jupiter",
            applicable_files_count=1,
            rationale="Converts org.junit.Test and Assert.* calls to org.junit.jupiter.api.* deterministically.",
        )
    )
    return recipes


def _php_codemods(total_files: int, brief_low: str) -> list[CodemodRecipeMatch]:
    """Match Rector and Composer recipes applicable to a PHP project."""
    recipes = [
        CodemodRecipeMatch(
            tool="rector",
            recipe_id="Rector\\Set\\ValueObject\\LevelSetList::UP_TO_PHP_83",
            title="Upgrade PHP Syntax, Typed Properties & Null-Safe Idioms up to PHP 8.3",
            applicable_files_count=max(total_files, 1),
            rationale="Applies deterministic PHP 8.x parameter/return type promotions and legacy syntax upgrades.",
        ),
        CodemodRecipeMatch(
            tool="rector",
            recipe_id="Rector\\TypeDeclaration\\Rector\\StmtsAwareInterface\\DeclareStrictTypesRector",
            title="Enforce declare(strict_types=1) on Refactored PHP Modules",
            applicable_files_count=max(total_files, 1),
            rationale="Prevents silent PHP type-juggling coercions once characterization tests pass.",
        ),
    ]
    if "laravel" in brief_low:
        recipes.append(
            CodemodRecipeMatch(
                tool="rector",
                recipe_id="RectorLaravel\\Set\\LaravelSetList::LARAVEL_110",
                title="Standardize Laravel 11 Service/Controller Conventions",
                applicable_files_count=max(total_files, 1),
                rationale="Aligns newly extracted Laravel controllers, FormRequests, and Eloquent models to v11.",
            )
        )
    return recipes


def _python_codemods(total_files: int, brief_low: str) -> list[CodemodRecipeMatch]:
    """Match Ruff and Pydantic codemod recipes applicable to a Python project."""
    recipes = [
        CodemodRecipeMatch(
            tool="ruff",
            recipe_id="ruff check --select UP,I,FA --fix",
            title="Modernize Python Typing & Import Syntax (pyupgrade + isort)",
            applicable_files_count=max(total_files, 1),
            rationale="Upgrades legacy typing/import constructs deterministically across Python modules.",
        ),
    ]
    if "pydantic" in brief_low or "fastapi" in brief_low:
        recipes.append(
            CodemodRecipeMatch(
                tool="bump-pydantic",
                recipe_id="bump-pydantic",
                title="Migrate Pydantic v1 BaseModel Validators/Config to Pydantic v2",
                applicable_files_count=max(total_files, 1),
                rationale="Rewrites @validator and class Config blocks to ConfigDict and @field_validator.",
            )
        )
    return recipes


def _go_codemods(total_files: int) -> list[CodemodRecipeMatch]:
    """Match Go toolchain and golangci-lint codemod recipes applicable to a Go project."""
    return [
        CodemodRecipeMatch(
            tool="gofix",
            recipe_id="go fix ./... && golangci-lint run --fix",
            title="Modernize Go Toolchain APIs, Generics (`any`), & Lint Rules",
            applicable_files_count=max(total_files, 1),
            rationale="Rewrites legacy `interface{}` / `io/ioutil` APIs and enforces modern Go idioms.",
        ),
    ]


def _node_codemods(total_files: int, lang: str) -> list[CodemodRecipeMatch]:
    """Match ESLint / TypeScript codemod recipes applicable to a Node.js project."""
    recipes = [
        CodemodRecipeMatch(
            tool="eslint",
            recipe_id="eslint --fix .",
            title="Standardize Modern ES Module Syntax & Async/Await Patterns",
            applicable_files_count=max(total_files, 1),
            rationale="Applies deterministic ESLint / Biome auto-fixes across source and test modules.",
        ),
    ]
    if lang == "javascript":
        recipes.append(
            CodemodRecipeMatch(
                tool="ts-migrate",
                recipe_id="npx ts-migrate-full .",
                title="Incremental JavaScript-to-TypeScript Strictness Migration",
                applicable_files_count=max(total_files, 1),
                rationale="Bootstraps tsconfig.json and explicit TypeScript annotations when upgrading JS modules.",
            )
        )
    return recipes


def match_codemod_recipes(
    source_lang: str,
    options: MigrationOptions,
    resolved_brief: str,
    ast_facts: AstFacts | None,
) -> list[CodemodRecipeMatch]:
    """Return applicable deterministic codemod recipes unless manual_only is selected."""
    if options.codemod_tool == "manual_only":
        return []
    total_files = ast_facts.total_files if ast_facts is not None else 1
    brief_low = resolved_brief.lower()
    lang = source_lang.lower()

    if options.codemod_tool == "openrewrite" or (options.codemod_tool == "auto" and lang == "java"):
        return _java_codemods(total_files, brief_low, ast_facts)
    if options.codemod_tool == "rector" or (options.codemod_tool == "auto" and lang == "php"):
        return _php_codemods(total_files, brief_low)
    if options.codemod_tool == "ruff" or (options.codemod_tool == "auto" and lang == "python"):
        return _python_codemods(total_files, brief_low)
    if options.codemod_tool == "auto" and lang in ("go", "typescript", "javascript"):
        return _go_codemods(total_files) if lang == "go" else _node_codemods(total_files, lang)
    return []


def collect_migration_blockers(
    project_facts: ProjectFacts | None,
    ast_facts: AstFacts | None,
    runtime_facts: RuntimeFacts | None,
) -> list[MigrationBlocker]:
    """Collect structural and build blockers that must be resolved in Phase 0 / Phase 1."""
    blockers: list[MigrationBlocker] = []
    idx = 1

    if ast_facts is not None:
        for loc in ast_facts.language_version_mismatches:
            blockers.append(
                MigrationBlocker(
                    blocker_id=f"BLK-{idx:02d}",
                    severity="critical",
                    file=loc.file,
                    line=loc.line,
                    description=loc.detail,
                    resolution_hint=(
                        "Align build manifest compiler target/toolchain in Phase 0 so baseline build & "
                        "OpenRewrite/Rector AST parsers can compile the project."
                    ),
                )
            )
            idx += 1

        for cyc in ast_facts.circular_dependencies:
            blockers.append(
                MigrationBlocker(
                    blocker_id=f"BLK-{idx:02d}",
                    severity="high",
                    file=cyc[0] if cyc else None,
                    description=f"Bidirectional circular dependency across modules: {' <-> '.join(cyc)}",
                    resolution_hint="Break back-edge in Phase 1 before extracting Clean Architecture / domain layers.",
                )
            )
            idx += 1

        for udep in ast_facts.undeclared_dependencies[:5]:
            blockers.append(
                MigrationBlocker(
                    blocker_id=f"BLK-{idx:02d}",
                    severity="medium",
                    file=udep.file,
                    line=udep.line,
                    description=f"Undeclared or dev-scoped import `{udep.symbol}`: {udep.detail}",
                    resolution_hint="Declare explicit runtime dependency or remove stray import before upgrade.",
                )
            )
            idx += 1

    if project_facts is not None and not project_facts.manifest_files:
        blockers.append(
            MigrationBlocker(
                blocker_id=f"BLK-{idx:02d}",
                severity="high",
                description="No package/build manifest (`composer.json`, `pom.xml`, `pyproject.toml`) detected.",
                resolution_hint="Initialize manifest and PSR-4 / module autoloading in Phase 0 before refactoring.",
            )
        )
        idx += 1

    if (
        runtime_facts is not None
        and runtime_facts.harness_build.status == "failed"
        and not (ast_facts and ast_facts.language_version_mismatches)
    ):
        blockers.append(
            MigrationBlocker(
                blocker_id=f"BLK-{idx:02d}",
                severity="critical",
                description="Container harness build currently fails; baseline test harness cannot execute.",
                resolution_hint="Restore minimal green build in Phase 0 prior to structural refactoring.",
            )
        )

    return blockers
