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
import os
import shutil
from pathlib import Path
from typing import Final

from pni._languages import list_supported_languages
from pni._rules.base_model import RuleInfo

BUILTIN_RULES_DIR = Path(__file__).resolve().parent
SUPPORTED_LANGUAGES: Final[tuple[str, ...]] = list_supported_languages()

_MANIFEST_LANGUAGE_RULES: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("python", ("pyproject.toml", "setup.py", "setup.cfg", "Pipfile")),
    ("java", ("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts")),
    ("php", ("composer.json", "wp-config.php", "wp-config-sample.php", "artisan", "phpunit.xml", "phpunit.xml.dist")),
    ("go", ("go.mod", "go.work")),
)

_IGNORED_SCAN_DIRS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "env",
        ".tox",
        ".nox",
        "node_modules",
        "vendor",
        "dist",
        "build",
        "target",
        "out",
        "coverage",
        ".pni",
        ".drawlib",
        ".cache",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".next",
        ".nuxt",
        ".turbo",
        ".svelte-kit",
    }
)


def _matches_source_filename(
    filename: str,
    suffixes: tuple[str, ...],
    exclude_suffixes: tuple[str, ...] = (),
) -> bool:
    """Return True if filename matches suffixes and does not match exclude_suffixes."""
    if exclude_suffixes and filename.endswith(exclude_suffixes):
        return False
    return filename.endswith(suffixes)


def _walk_has_source_files(
    root_dir: Path,
    suffixes: tuple[str, ...],
    exclude_suffixes: tuple[str, ...] = (),
    max_depth: int = 6,
) -> bool:
    """Return True if root_dir contains matching source files while pruning ignored directories."""
    base_depth = len(root_dir.parts)
    for current_root, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if _matches_source_filename(fname, suffixes, exclude_suffixes):
                return True
        depth = len(Path(current_root).parts) - base_depth
        if depth >= max_depth:
            dirnames.clear()
        else:
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in _IGNORED_SCAN_DIRS]
    return False


def _has_source_files(
    project_root: Path,
    suffixes: tuple[str, ...],
    *,
    search_dirs: tuple[str, ...] | None = None,
    exclude_suffixes: tuple[str, ...] = (),
    max_depth: int = 6,
) -> bool:
    """Scan root and candidate subdirectories for matching source files, skipping vendored/build trees."""
    if not project_root.is_dir():
        return False

    try:
        entries = list(project_root.iterdir())
    except OSError:
        return False

    for entry in entries:
        if entry.is_file() and _matches_source_filename(entry.name, suffixes, exclude_suffixes):
            return True

    if search_dirs is not None:
        candidate_dirs = [project_root / d for d in search_dirs if (project_root / d).is_dir()]
    else:
        candidate_dirs = [
            entry
            for entry in entries
            if entry.is_dir() and not entry.name.startswith(".") and entry.name not in _IGNORED_SCAN_DIRS
        ]

    return any(_walk_has_source_files(sub, suffixes, exclude_suffixes, max_depth) for sub in candidate_dirs)


def _has_python_sources(project_root: Path) -> bool:
    """Return True if root or standard Python directories contain .py source files."""
    return _has_source_files(project_root, (".py",), search_dirs=("src", "app", "lib"))


def _has_java_sources(project_root: Path) -> bool:
    """Return True if standard Maven/Gradle Java directories or .java source files exist."""
    if (project_root / "src" / "main" / "java").is_dir():
        return True
    return _has_source_files(project_root, (".java",), search_dirs=("src",))


def _has_php_sources(project_root: Path) -> bool:
    """Return True if root or standard PHP directories contain .php or .phtml source files."""
    return _has_source_files(project_root, (".php", ".phtml"), search_dirs=("src", "app", "public", "includes"))


def _has_go_sources(project_root: Path) -> bool:
    """Return True if root or standard Go directories contain .go source files."""
    return _has_source_files(project_root, (".go",), search_dirs=("cmd", "pkg", "internal", "src"))


def _has_ts_sources(project_root: Path) -> bool:
    """Return True if non-ignored project directories contain .ts or .tsx source files (excluding .d.ts)."""
    return _has_source_files(project_root, (".ts", ".tsx"), search_dirs=None, exclude_suffixes=(".d.ts",))


def _has_js_sources(project_root: Path) -> bool:
    """Return True if non-ignored project directories contain .js, .jsx, .mjs, or .cjs source files."""
    return _has_source_files(project_root, (".js", ".jsx", ".mjs", ".cjs"), search_dirs=None)


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

    if (project_root / "requirements.txt").exists() and _has_python_sources(project_root):
        return "python"

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


def _normalize_lang(lang: str | None, project_root: Path) -> str:
    """Normalize an optional language identifier or fall back to auto-detection."""
    if lang is not None and lang.strip():
        return lang.strip().lower()
    return detect_active_language(project_root)


def _extract_title_from_text(content: str, fallback_stem: str) -> str:
    """Extract markdown H1 title from content text or default to formatted stem."""
    for line in content.splitlines():
        line_str = line.strip()
        if line_str.startswith("# "):
            return line_str.removeprefix("# ").strip()
    return fallback_stem.replace("_", " ").title()


def _extract_title(file_path: Path) -> str:
    """Extract markdown h1 title or default to stem."""
    if not file_path.exists():
        return file_path.stem.replace("_", " ").title()

    with contextlib.suppress(Exception):
        return _extract_title_from_text(file_path.read_text(encoding="utf-8"), file_path.stem)

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


def _resolve_rule_file(scope: str, name: str, local_rules_dir: Path) -> tuple[Path, bool] | None:
    """Resolve the winning local or built-in rule Markdown path for (scope, name)."""
    local_file = local_rules_dir / scope / f"{name}.md"
    if local_file.is_file():
        return local_file, True
    builtin_file = BUILTIN_RULES_DIR / scope / f"{name}.md"
    if builtin_file.is_file():
        return builtin_file, False
    return None


def _load_rule_pair(scope: str, name: str, path: Path, *, is_local: bool) -> tuple[RuleInfo, str]:
    """Read a single resolved rule file once and build its (RuleInfo, content) pair."""
    content = path.read_text(encoding="utf-8")
    info = RuleInfo(
        scope=scope,
        name=name,
        title=_extract_title_from_text(content, path.stem),
        path=path,
        is_local=is_local,
    )
    return info, content


def list_rules(
    project_root: Path,
    lang: str | None = None,
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
    active_lang = _normalize_lang(lang, project_root)
    local_rules_dir = project_root / ".pni" / "rules"
    candidates = _collect_rule_candidates((BUILTIN_RULES_DIR, local_rules_dir), active_lang, include_all)

    rules: list[RuleInfo] = []
    for scope, name in candidates:
        resolved = _resolve_rule_file(scope, name, local_rules_dir)
        if resolved is None:
            continue
        file_path, is_local = resolved
        rules.append(
            RuleInfo(
                scope=scope,
                name=name,
                title=_extract_title(file_path),
                path=file_path,
                is_local=is_local,
            )
        )

    rules.sort(key=lambda r: (0 if r.scope == "common" else 1, r.scope, r.name))
    return rules


def _norm_rule_key(value: str) -> str:
    """Normalize rule lookup keys across hyphens and underscores."""
    return value.strip().lower().replace("-", "_")


def _try_direct_rule_lookup(clean_target: str, local_rules_dir: Path) -> tuple[RuleInfo, str] | None:
    """Attempt an O(1) direct file lookup for qualified '<scope>/<name>' targets without directory scans."""
    if "/" not in clean_target:
        return None
    parts = [p for p in clean_target.split("/") if p]
    if len(parts) < 2 or any(p in {".", ".."} or p.startswith(("_", ".")) for p in parts):
        return None

    scope = parts[0]
    name = "/".join(parts[1:])
    resolved = _resolve_rule_file(scope, name, local_rules_dir)
    if resolved is None:
        return None

    file_path, is_local = resolved
    root_anchor = (local_rules_dir if is_local else BUILTIN_RULES_DIR).resolve()
    if not file_path.resolve().is_relative_to(root_anchor):
        return None
    return _load_rule_pair(scope, name, file_path, is_local=is_local)


def get_rule_content(
    name_or_path: str,
    project_root: Path,
    lang: str | None = None,
) -> tuple[RuleInfo, str] | None:
    """Retrieve RuleInfo and file content for a given rule name or path.

    Args:
        name_or_path: Path-like string ('python/testing') or short name ('testing').
        project_root: Target project root.
        lang: Primary language scope.

    Returns:
        tuple[RuleInfo, str] | None: Matched RuleInfo and markdown content.
    """
    clean_target = _norm_rule_key(name_or_path.removesuffix(".md"))
    local_rules_dir = project_root / ".pni" / "rules"

    direct = _try_direct_rule_lookup(clean_target, local_rules_dir)
    if direct is not None:
        return direct

    active_lang = _normalize_lang(lang, project_root)
    candidates = sorted(
        _collect_rule_candidates((BUILTIN_RULES_DIR, local_rules_dir), active_lang, include_all=True),
        key=lambda item: (0 if item[0] == "common" else 1, item[0], item[1]),
    )

    tiers: tuple[tuple[tuple[str, str], ...], ...] = (
        tuple(c for c in candidates if _norm_rule_key(f"{c[0]}/{c[1]}") == clean_target),
        tuple(c for c in candidates if _norm_rule_key(c[1]) == clean_target and c[0] == active_lang),
        tuple(c for c in candidates if _norm_rule_key(c[1]) == clean_target and c[0] == "common"),
        tuple(c for c in candidates if _norm_rule_key(c[1]) == clean_target),
    )
    for tier in tiers:
        for scope, name in tier:
            resolved = _resolve_rule_file(scope, name, local_rules_dir)
            if resolved is not None:
                return _load_rule_pair(scope, name, resolved[0], is_local=resolved[1])

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
    lang: str | None = None,
    force: bool = False,
) -> list[Path]:
    """Copy default common and active language rules to .pni/rules/.

    Args:
        project_root: Target project directory.
        lang: Target programming language.
        force: If True, overwrite existing files.

    Returns:
        list[Path]: Created or overwritten file paths.

    Raises:
        ValueError: If an explicit unsupported language is specified.
    """
    target_lang = _normalize_lang(lang, project_root)
    if target_lang not in SUPPORTED_LANGUAGES:
        supported = ", ".join(SUPPORTED_LANGUAGES)
        msg = f"Unsupported language '{target_lang}'. Supported languages: {supported}."
        raise ValueError(msg)

    rules_dir = project_root / ".pni" / "rules"
    created: list[Path] = []
    created.extend(_copy_dir_templates(BUILTIN_RULES_DIR / "common", rules_dir / "common", "*.md", force))
    created.extend(_copy_dir_templates(BUILTIN_RULES_DIR / target_lang, rules_dir / target_lang, "*.md", force))
    return created
