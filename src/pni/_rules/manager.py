# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Language auto-detection, cascade resolution, and template management for rules."""

from __future__ import annotations

import contextlib
import json
import shutil
from pathlib import Path
from typing import Final, Optional

from pni._rules.base_model import RuleInfo

BUILTIN_RULES_DIR = Path(__file__).resolve().parent
SUPPORTED_LANGUAGES: Final[tuple[str, ...]] = (
    "python",
    "java",
    "php",
    "go",
    "typescript",
    "javascript",
)

_MANIFEST_LANGUAGE_RULES: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("python", ("pyproject.toml", "setup.py", "requirements.txt")),
    ("java", ("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts")),
    ("php", ("composer.json", "wp-config.php", "wp-config-sample.php", "artisan", "phpunit.xml", "phpunit.xml.dist")),
    ("go", ("go.mod", "go.work")),
)


def _has_java_sources(project_root: Path) -> bool:
    """Return True if standard Maven/Gradle Java directories or .java source files exist."""
    if (project_root / "src" / "main" / "java").is_dir():
        return True
    if any(project_root.glob("*.java")):
        return True
    src_dir = project_root / "src"
    return src_dir.is_dir() and any(src_dir.rglob("*.java"))


def _has_php_sources(project_root: Path) -> bool:
    """Return True if root or standard PHP directories contain .php or .phtml source files."""
    if any(project_root.glob("*.php")) or any(project_root.glob("*.phtml")):
        return True
    for dir_name in ("src", "app", "public", "includes"):
        sub = project_root / dir_name
        if sub.is_dir() and (any(sub.rglob("*.php")) or any(sub.rglob("*.phtml"))):
            return True
    return False


def _has_go_sources(project_root: Path) -> bool:
    """Return True if root or standard Go directories contain .go source files."""
    if any(project_root.glob("*.go")):
        return True
    for dir_name in ("cmd", "pkg", "internal", "src"):
        sub = project_root / dir_name
        if sub.is_dir() and any(sub.rglob("*.go")):
            return True
    return False


def _has_ts_sources(project_root: Path) -> bool:
    """Return True if root or standard directories contain .ts or .tsx source files (excluding .d.ts)."""
    for pat in ("*.ts", "*.tsx"):
        for f in project_root.glob(pat):
            if not f.name.endswith(".d.ts"):
                return True
    for dir_name in ("src", "app", "lib", "packages", "pages", "components"):
        sub = project_root / dir_name
        if not sub.is_dir():
            continue
        for pat in ("*.ts", "*.tsx"):
            for f in sub.rglob(pat):
                if not f.name.endswith(".d.ts"):
                    return True
    return False


def _has_js_sources(project_root: Path) -> bool:
    """Return True if root or standard directories contain .js, .jsx, .mjs, or .cjs source files."""
    js_exts = ("*.js", "*.jsx", "*.mjs", "*.cjs")
    if any(any(project_root.glob(pat)) for pat in js_exts):
        return True
    for dir_name in ("src", "app", "lib", "packages", "pages", "components", "bin"):
        sub = project_root / dir_name
        if sub.is_dir() and any(any(sub.rglob(pat)) for pat in js_exts):
            return True
    return False


def _detect_node_language(project_root: Path) -> str | None:
    """Distinguish 'typescript' vs 'javascript' for Node/Frontend projects."""
    if (project_root / "tsconfig.json").exists() or (project_root / "tsconfig.base.json").exists():
        return "typescript"
    if (project_root / "jsconfig.json").exists():
        return "javascript"

    pkg_json = project_root / "package.json"
    if not pkg_json.exists():
        return None

    with contextlib.suppress(Exception):
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            deps = data.get("dependencies") if isinstance(data.get("dependencies"), dict) else {}
            dev_deps = data.get("devDependencies") if isinstance(data.get("devDependencies"), dict) else {}
            if "typescript" in deps or "typescript" in dev_deps:
                return "typescript"
    if _has_ts_sources(project_root) or not _has_js_sources(project_root):
        return "typescript"
    return "javascript"


def detect_active_language(project_root: Path) -> str:
    """Detect the primary programming language for the project.

    Args:
        project_root: Target project directory.

    Returns:
        str: Language keyword ('python', 'java', 'php', 'go', 'typescript', 'javascript').
    """
    for lang, manifests in _MANIFEST_LANGUAGE_RULES:
        if any((project_root / mf).exists() for mf in manifests):
            return lang

    node_lang = _detect_node_language(project_root)
    if node_lang is not None:
        return node_lang

    for check_fn, detected_lang in (
        (_has_java_sources, "java"),
        (_has_php_sources, "php"),
        (_has_go_sources, "go"),
        (_has_ts_sources, "typescript"),
        (_has_js_sources, "javascript"),
    ):
        if check_fn(project_root):
            return detected_lang

    return "python"


def _extract_title(file_path: Path) -> str:
    """Extract markdown h1 title or default to stem."""
    if not file_path.exists():
        return file_path.stem.replace("_", " ").title()

    with contextlib.suppress(Exception):
        content = file_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line_str = line.strip()
            if line_str.startswith("# "):
                return line_str.removeprefix("# ").strip()

    return file_path.stem.replace("_", " ").title()


def _collect_rule_candidates(
    roots: tuple[Path, ...],
    active_lang: str,
    include_all: bool,
) -> set[tuple[str, str]]:
    """Collect (scope, relative_rule_name) pairs across builtin and local rule directories."""
    candidates: set[tuple[str, str]] = set()
    for rdir in roots:
        if not rdir.exists():
            continue
        for scope_dir in rdir.iterdir():
            if not scope_dir.is_dir() or scope_dir.name.startswith(("_", ".")):
                continue
            if not include_all and scope_dir.name not in ("common", active_lang):
                continue
            for md_file in scope_dir.rglob("*.md"):
                rel_parts = md_file.relative_to(scope_dir).parts
                if not any(part.startswith(("_", ".")) for part in rel_parts):
                    candidates.add((scope_dir.name, md_file.relative_to(scope_dir).with_suffix("").as_posix()))
    return candidates


def list_rules(
    project_root: Path,
    lang: Optional[str] = None,
    include_all: bool = False,
) -> list[RuleInfo]:
    """Scan and list all available rules adhering to cascade resolution.

    Args:
        project_root: Target project root.
        lang: Primary language scope (defaults to detected language).
        include_all: If True, include rules from all languages.

    Returns:
        list[RuleInfo]: Sorted list of available rules.
    """
    active_lang = lang or detect_active_language(project_root)
    local_rules_dir = project_root / ".pni" / "rules"
    candidates = _collect_rule_candidates((BUILTIN_RULES_DIR, local_rules_dir), active_lang, include_all)

    rules: list[RuleInfo] = []
    for scope, name in candidates:
        local_file = local_rules_dir / scope / f"{name}.md"
        builtin_file = BUILTIN_RULES_DIR / scope / f"{name}.md"

        if local_file.exists():
            rules.append(
                RuleInfo(
                    scope=scope,
                    name=name,
                    title=_extract_title(local_file),
                    path=local_file,
                    is_local=True,
                )
            )
        elif builtin_file.exists():
            rules.append(
                RuleInfo(
                    scope=scope,
                    name=name,
                    title=_extract_title(builtin_file),
                    path=builtin_file,
                    is_local=False,
                )
            )

    rules.sort(key=lambda r: (0 if r.scope == "common" else 1, r.scope, r.name))
    return rules


def _norm_rule_key(value: str) -> str:
    """Normalize rule lookup keys across hyphens and underscores."""
    return value.strip().lower().replace("-", "_")


def get_rule_content(
    name_or_path: str,
    project_root: Path,
    lang: Optional[str] = None,
) -> tuple[RuleInfo, str] | None:
    """Retrieve RuleInfo and file content for a given rule name or path.

    Args:
        name_or_path: Path-like string ('python/testing') or short name ('testing').
        project_root: Target project root.
        lang: Primary language scope.

    Returns:
        tuple[RuleInfo, str] | None: Matched RuleInfo and markdown content.
    """
    active_lang = lang or detect_active_language(project_root)
    clean_target = _norm_rule_key(name_or_path.removesuffix(".md"))

    available = list_rules(project_root, lang=active_lang, include_all=True)

    for rule in available:
        if _norm_rule_key(rule.identifier) == clean_target:
            return rule, rule.path.read_text(encoding="utf-8")

    for rule in available:
        if _norm_rule_key(rule.name) == clean_target and rule.scope == active_lang:
            return rule, rule.path.read_text(encoding="utf-8")

    for rule in available:
        if _norm_rule_key(rule.name) == clean_target and rule.scope == "common":
            return rule, rule.path.read_text(encoding="utf-8")

    for rule in available:
        if _norm_rule_key(rule.name) == clean_target:
            return rule, rule.path.read_text(encoding="utf-8")

    return None


_META_GUIDE_FILENAMES = frozenset({"agent_instruction.md", "workflow_guide.md"})


def _copy_dir_templates(
    src_dir: Path,
    dest_dir: Path,
    pattern: str,
    force: bool,
) -> list[Path]:
    """Copy matching rule template files recursively from src_dir to dest_dir, skipping meta-guides."""
    created: list[Path] = []
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not src_dir.exists():
        return created

    for f in sorted(src_dir.rglob(pattern)):
        rel = f.relative_to(src_dir)
        if f.name in _META_GUIDE_FILENAMES or any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        dest_file = dest_dir / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        if not dest_file.exists() or force:
            shutil.copy2(f, dest_file)
            created.append(dest_file)

    return created


def copy_rule_templates(
    project_root: Path,
    lang: Optional[str] = None,
    force: bool = False,
) -> list[Path]:
    """Copy default common and active language rules to .pni/rules/.

    Args:
        project_root: Target project directory.
        lang: Target programming language.
        force: If True, overwrite existing files.

    Returns:
        list[Path]: Created or overwritten file paths.
    """
    target_lang = lang or detect_active_language(project_root)
    rules_dir = project_root / ".pni" / "rules"

    created: list[Path] = []
    created.extend(_copy_dir_templates(BUILTIN_RULES_DIR / "common", rules_dir / "common", "*.md", force))
    created.extend(_copy_dir_templates(BUILTIN_RULES_DIR / target_lang, rules_dir / target_lang, "*.md", force))
    return created
