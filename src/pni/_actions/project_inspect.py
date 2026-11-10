# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Language-agnostic deterministic project metadata, dependency, framework, and legacy inspector."""

from __future__ import annotations

import contextlib
import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Optional

from pydantic import BaseModel, Field, model_validator

from pni._actions._repo_governance import (
    RuntimeArchetype,
    infer_runtime_types,
    inspect_governance_and_docs,
    matches_exclude_globs,
)
from pni._config import (
    OptOutEntry,
    detect_git_tag_version,
    discover_gitignored_paths,
    extract_composer_psr4_dirs,
    load_pni_config,
    match_opt_out,
)
from pni._rules import detect_active_language

LOCKFILE_CANDIDATES: Final[tuple[str, ...]] = (
    "uv.lock",
    "poetry.lock",
    "pdm.lock",
    "Pipfile.lock",
    "gradle.lockfile",
    "mvnw",
    "gradlew",
    "composer.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "go.sum",
)
PYTHON_VERSION_SPECIFIERS: Final[tuple[str, ...]] = ("==", ">=", "<=", "~=", "!=", ">", "<", "@")
IGNORED_PATH_PARTS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".pni",
        ".drawlib",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        "vendor",
        "target",
        "build",
        ".gradle",
        "reports",
        "reports_src",
    }
)
FAT_BASH_LOC_THRESHOLD: Final[int] = 100

_GRADLE_STRING_DEP_RE = re.compile(
    r"\b(testImplementation|testCompileOnly|testRuntimeOnly|implementation|api|compileOnly|runtimeOnly)"
    r"\s*\(?\s*['\"]([^'\"]+)['\"]\s*\)?"
)
_GRADLE_CATALOG_DEP_RE = re.compile(
    r"\b(testImplementation|testCompileOnly|testRuntimeOnly|implementation|api|compileOnly|runtimeOnly)"
    r"\s*\(\s*(libs\.[A-Za-z0-9_.]+)\s*\)"
)
_DEP_NAME_SPLIT_RE = re.compile(r"[<>=!~@;\[\s]")

_PYTHON_FRAMEWORK_KEYS: Final[tuple[tuple[str, str], ...]] = (
    ("fastapi", "fastapi"),
    ("flask", "flask"),
    ("django", "django"),
    ("litestar", "litestar"),
    ("pydantic", "pydantic"),
    ("sqlalchemy", "sqlalchemy"),
    ("typer", "typer"),
    ("click", "click"),
    ("pytest", "pytest"),
    ("httpx", "httpx"),
    ("requests", "requests"),
)
_JAVA_FRAMEWORK_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    ("spring-boot", "spring-boot"),
    ("spring-framework", "org.springframework"),
    ("jakarta-ee", "jakarta."),
    ("javax-ee", "javax.servlet"),
    ("javax-ee", "javax.persistence"),
    ("junit5", "junit-jupiter"),
    ("junit4", "junit:junit"),
    ("lombok", "lombok"),
    ("hibernate", "hibernate"),
)
_PHP_FRAMEWORK_PATTERNS: Final[tuple[tuple[str, str], ...]] = (
    ("laravel", "laravel/framework"),
    ("laravel", "laravel/lumen-framework"),
    ("laravel", "illuminate/"),
    ("symfony", "symfony/framework-bundle"),
    ("symfony", "symfony/http-kernel"),
    ("slim", "slim/slim"),
    ("cakephp", "cakephp/cakephp"),
    ("codeigniter", "codeigniter4/framework"),
    ("wordpress", "johnpbloch/wordpress"),
    ("wordpress", "roots/wordpress"),
    ("wordpress", "wpackagist-"),
    ("phpunit", "phpunit/phpunit"),
    ("pest", "pestphp/pest"),
    ("phpstan", "phpstan/phpstan"),
    ("psalm", "vimeo/psalm"),
)
_WP_PLUGIN_HEADER_RE = re.compile(r"(?mi)^\s*\*?\s*Plugin Name\s*:\s*\S+")
_WP_THEME_HEADER_RE = re.compile(r"(?mi)^\s*\*?\s*Theme Name\s*:\s*\S+")


def _default_runtime_types() -> list[RuntimeArchetype]:
    """Return default runtime archetype list for ProjectFacts."""
    return ["library"]


class ProjectFacts(BaseModel):
    """Language-agnostic deterministic facts extracted from repository structure and manifests."""

    project_name: str
    version: str = "0.0.0"
    language: str = "python"
    runtime_types: list[RuntimeArchetype] = Field(default_factory=_default_runtime_types)
    build_system: str = "unknown"
    language_version_constraint: Optional[str] = None
    has_type_marker: Optional[bool] = None
    manifest_files: list[str] = Field(default_factory=list)
    lockfiles_found: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    unpinned_dependencies: list[str] = Field(default_factory=list)
    dev_dependencies: list[str] = Field(default_factory=list)
    detected_frameworks: list[str] = Field(default_factory=list)
    legacy_language_findings: list[str] = Field(default_factory=list)
    tooling_modernization_issues: list[str] = Field(default_factory=list)
    source_files_count: int = 0
    test_files_count: int = 0
    has_readme: bool = False
    readme_line_count: int = 0
    readme_headings: list[str] = Field(default_factory=list)
    docs_inventory: list[str] = Field(default_factory=list)
    has_gitignore: bool = False
    has_license: bool = False
    has_security_policy: bool = False
    has_dependency_automation: bool = False
    ci_workflows_found: list[str] = Field(default_factory=list)
    ci_supply_chain_issues: list[str] = Field(default_factory=list)
    committed_secret_files: list[str] = Field(default_factory=list)
    has_dockerfile: bool = False
    container_hygiene_issues: list[str] = Field(default_factory=list)
    opt_out_counts: dict[str, int] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _coerce_legacy_runtime_type_hint(cls, data: object) -> object:
        """Accept legacy 'runtime_type_hint' string in cached ProjectFacts payloads."""
        if not isinstance(data, dict) or "runtime_types" in data or "runtime_type_hint" not in data:
            return data
        updated = dict(data)
        legacy = updated.pop("runtime_type_hint", None)
        if legacy == "hybrid":
            updated["runtime_types"] = ["web_api", "cli"]
        elif legacy in {"web_api", "worker", "cli", "library"}:
            updated["runtime_types"] = [legacy]
        return updated


@dataclass
class _ManifestInspection:
    """Internal result of parsing language-specific build manifests."""

    project_name: str
    version: str = "0.0.0"
    build_system: str = "unknown"
    language_version_constraint: Optional[str] = None
    manifest_files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    unpinned_dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)


def normalize_python_dep_name(raw_spec: str) -> str:
    """Normalize a PEP 508 requirement string into a canonical snake_case package name."""
    head = _DEP_NAME_SPLIT_RE.split(raw_spec.strip(), maxsplit=1)[0]
    return re.sub(r"[-_.]+", "_", head).lower().strip("_")


def _is_ignored_rel(project_root: Path, file_path: Path) -> bool:
    """Return True if file_path has any ignored directory segment relative to project_root."""
    rel_parts = file_path.relative_to(project_root).parts
    return any(part in IGNORED_PATH_PARTS or part.startswith(".") for part in rel_parts[:-1])


def _count_matching_files(
    project_root: Path,
    rel_dirs: list[str],
    patterns: tuple[str, ...],
    *,
    exclude_dirs: Optional[list[str]] = None,
    exclude_globs: Optional[list[str]] = None,
) -> int:
    """Count unique matching files across relative target directories or file paths."""
    excluded_roots = {
        (project_root / ex).resolve()
        for ex in (exclude_dirs or [])
        if ex != "." and (project_root / ex).exists()
    }
    globs = exclude_globs or []
    matched: set[Path] = set()
    for rel in rel_dirs:
        candidate = project_root / rel
        if candidate.is_dir():
            for pat in patterns:
                for found in candidate.rglob(pat):
                    if _is_ignored_rel(project_root, found):
                        continue
                    resolved = found.resolve()
                    if any(resolved.is_relative_to(ex_root) for ex_root in excluded_roots):
                        continue
                    if matches_exclude_globs(found, project_root, globs):
                        continue
                    matched.add(found)
        elif candidate.is_file() and not matches_exclude_globs(candidate, project_root, globs):
            matched.add(candidate)
    return len(matched)


def _detect_python_build_system(project_root: Path, data: dict[str, object]) -> str:
    """Determine Python build tool name from pyproject.toml and repository files."""
    build_sec = data.get("build-system")
    backend = str(build_sec.get("build-backend", "")) if isinstance(build_sec, dict) else ""
    tool_sec = data.get("tool")
    has_poetry_tool = isinstance(tool_sec, dict) and "poetry" in tool_sec

    if (project_root / "uv.lock").exists() or "uv_build" in backend:
        return "uv"
    if "poetry" in backend or has_poetry_tool:
        return "poetry"
    if "hatch" in backend:
        return "hatch"
    if "setuptools" in backend:
        return "setuptools"
    return "pyproject"


def _extract_pyproject_dev_deps(data: dict[str, object]) -> list[str]:
    """Extract development dependencies from PEP 735 dependency-groups and optional-dependencies."""
    dev_deps: list[str] = []
    dep_groups = data.get("dependency-groups")
    if isinstance(dep_groups, dict):
        raw_dev = dep_groups.get("dev", [])
        if isinstance(raw_dev, list):
            dev_deps.extend(str(d) for d in raw_dev if isinstance(d, str))

    project_sec = data.get("project")
    if isinstance(project_sec, dict):
        opt_deps = project_sec.get("optional-dependencies")
        if isinstance(opt_deps, dict):
            raw_opt_dev = opt_deps.get("dev", [])
            if isinstance(raw_opt_dev, list):
                dev_deps.extend(str(d) for d in raw_opt_dev if str(d) not in dev_deps)
    return dev_deps


def _parse_requirements_txt(req_path: Path) -> list[str]:
    """Extract requirement entries from requirements.txt."""
    if not req_path.exists():
        return []
    deps: list[str] = []
    with contextlib.suppress(Exception):
        for raw_line in req_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith(("#", "-")):
                deps.append(line)
    return deps


def _apply_pyproject_metadata(project_root: Path, data: dict[str, object], res: _ManifestInspection) -> None:
    """Populate _ManifestInspection fields from parsed pyproject.toml dictionary."""
    res.build_system = _detect_python_build_system(project_root, data)
    project_sec = data.get("project")
    if isinstance(project_sec, dict):
        res.project_name = str(project_sec.get("name", res.project_name))
        res.version = str(project_sec.get("version", res.version))
        req_py = project_sec.get("requires-python")
        if isinstance(req_py, str) and req_py.strip():
            res.language_version_constraint = req_py.strip()
        raw_deps = project_sec.get("dependencies", [])
        if isinstance(raw_deps, list):
            res.dependencies = [str(d) for d in raw_deps]
    res.dev_dependencies = _extract_pyproject_dev_deps(data)


def _inspect_python_manifests(project_root: Path) -> _ManifestInspection:
    """Inspect Python manifests (pyproject.toml, requirements.txt, setup.py)."""
    manifests = [m for m in ("pyproject.toml", "requirements.txt", "setup.py") if (project_root / m).exists()]
    res = _ManifestInspection(project_name=project_root.name, manifest_files=manifests)
    pyproject_path = project_root / "pyproject.toml"

    if pyproject_path.exists():
        with contextlib.suppress(Exception):
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            _apply_pyproject_metadata(project_root, data, res)
    elif (project_root / "requirements.txt").exists():
        res.build_system = "pip"
        res.dependencies = _parse_requirements_txt(project_root / "requirements.txt")
    elif (project_root / "setup.py").exists():
        res.build_system = "setuptools"

    res.unpinned_dependencies = [
        d for d in res.dependencies if not any(op in d for op in PYTHON_VERSION_SPECIFIERS)
    ]
    return res


def _xml_tag_value(block: str, tag: str) -> str:
    """Extract trimmed text of the first <tag>...</tag> occurrence inside an XML block."""
    match = re.search(rf"<{tag}>\s*([^<]*?)\s*</{tag}>", block, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _resolve_maven_prop(value: str, props: dict[str, str]) -> str:
    """Resolve simple ${property} placeholders defined in Maven <properties>."""
    if value.startswith("${") and value.endswith("}"):
        key = value[2:-1].strip()
        return props.get(key, value)
    return value


def _is_unpinned_java_version(version: str, *, managed_by_bom: bool) -> bool:
    """Return True if a Maven/Gradle dependency version is missing or uses dynamic ranges."""
    if not version:
        return not managed_by_bom
    upper = version.upper()
    return upper in {"LATEST", "RELEASE", "LATEST.RELEASE", "LATEST.INTEGRATION"} or version.endswith("+")


def _parse_maven_dependencies(
    cleaned_pom: str,
    props: dict[str, str],
    *,
    managed_by_bom: bool,
) -> tuple[list[str], list[str], list[str]]:
    """Extract compile/runtime dependencies, unpinned dependencies, and test dependencies from pom.xml."""
    without_mgmt = re.sub(r"<dependencyManagement>.*?</dependencyManagement>", "", cleaned_pom, flags=re.DOTALL)
    deps: list[str] = []
    unpinned: list[str] = []
    dev_deps: list[str] = []

    for dep_match in re.finditer(r"<dependency>(.*?)</dependency>", without_mgmt, flags=re.DOTALL):
        dep_block = dep_match.group(1)
        group_id = _xml_tag_value(dep_block, "groupId")
        artifact_id = _xml_tag_value(dep_block, "artifactId")
        if not artifact_id:
            continue
        raw_ver = _resolve_maven_prop(_xml_tag_value(dep_block, "version"), props)
        scope = _xml_tag_value(dep_block, "scope").lower()
        coord = f"{group_id}:{artifact_id}:{raw_ver}" if raw_ver else f"{group_id}:{artifact_id}"

        if scope == "test":
            dev_deps.append(coord)
        else:
            deps.append(coord)
            if _is_unpinned_java_version(raw_ver, managed_by_bom=managed_by_bom):
                unpinned.append(coord)

    return deps, unpinned, dev_deps


def _extract_maven_java_version(props: dict[str, str]) -> Optional[str]:
    """Extract target Java release/version from Maven <properties> if configured."""
    for key in ("java.version", "maven.compiler.release", "maven.compiler.target", "maven.compiler.source"):
        if props.get(key):
            return props[key]
    return None


def _inspect_maven_pom(pom_path: Path, manifests: list[str], default_name: str) -> _ManifestInspection:
    """Inspect a Maven pom.xml file without external XML entity expansion."""
    res = _ManifestInspection(project_name=default_name, build_system="maven", manifest_files=manifests)
    with contextlib.suppress(Exception):
        raw = pom_path.read_text(encoding="utf-8")
        cleaned = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)

        props: dict[str, str] = {}
        props_match = re.search(r"<properties>(.*?)</properties>", cleaned, flags=re.DOTALL)
        if props_match:
            for pmatch in re.finditer(r"<([A-Za-z0-9_.-]+)>\s*([^<]*?)\s*</\1>", props_match.group(1)):
                props[pmatch.group(1)] = pmatch.group(2).strip()
        res.language_version_constraint = _extract_maven_java_version(props)

        parent_ver = ""
        parent_match = re.search(r"<parent>(.*?)</parent>", cleaned, flags=re.DOTALL)
        if parent_match:
            parent_ver = _xml_tag_value(parent_match.group(1), "version")

        header = re.sub(
            r"<(parent|dependencies|dependencyManagement|build|profiles|reporting)>.*?</\1>",
            "",
            cleaned,
            flags=re.DOTALL,
        )
        artifact = _xml_tag_value(header, "artifactId")
        version = _resolve_maven_prop(_xml_tag_value(header, "version") or parent_ver, props)
        if artifact:
            res.project_name = artifact
        if version:
            res.version = version

        managed = "<dependencyManagement>" in cleaned or parent_match is not None
        res.dependencies, res.unpinned_dependencies, res.dev_dependencies = _parse_maven_dependencies(
            cleaned, props, managed_by_bom=managed
        )
    return res


def _strip_c_style_comments(text: str) -> str:
    """Remove /* ... */ block comments and // single-line comments from Gradle scripts."""
    no_block = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", no_block)


def _extract_gradle_java_version(btext: str) -> Optional[str]:
    """Extract Java languageVersion or sourceCompatibility from Gradle build script text."""
    for pat in (
        r"JavaLanguageVersion\.of\(\s*(\d+)\s*\)",
        r"sourceCompatibility\s*=\s*['\"]?([0-9.]+)['\"]?",
        r"jvmTarget\s*=\s*['\"]([0-9.]+)['\"]",
    ):
        match = re.search(pat, btext)
        if match:
            return match.group(1)
    return None


def _inspect_gradle_files(project_root: Path, manifests: list[str]) -> _ManifestInspection:
    """Inspect Gradle build.gradle(.kts) and settings.gradle(.kts) manifests."""
    res = _ManifestInspection(project_name=project_root.name, build_system="gradle", manifest_files=manifests)

    for settings_name in ("settings.gradle.kts", "settings.gradle"):
        sp = project_root / settings_name
        if sp.is_file():
            stext = _strip_c_style_comments(sp.read_text(encoding="utf-8"))
            name_match = re.search(r"rootProject\.name\s*=\s*['\"]([^'\"]+)['\"]", stext)
            if name_match:
                res.project_name = name_match.group(1).strip()
                break

    build_file = next(
        (project_root / n for n in ("build.gradle.kts", "build.gradle") if (project_root / n).is_file()),
        None,
    )
    if build_file is None:
        return res

    btext = _strip_c_style_comments(build_file.read_text(encoding="utf-8"))
    res.language_version_constraint = _extract_gradle_java_version(btext)
    ver_match = re.search(r"(?m)^\s*version\s*=?\s*['\"]([^'\"]+)['\"]", btext)
    if ver_match:
        res.version = ver_match.strip() if isinstance(ver_match, str) else ver_match.group(1).strip()

    has_platform = "platform(" in btext or "enforcedPlatform(" in btext
    for cfg, coord in _GRADLE_STRING_DEP_RE.findall(btext):
        if cfg.startswith("test"):
            res.dev_dependencies.append(coord)
        else:
            res.dependencies.append(coord)
            parts = coord.split(":")
            ver_part = parts[2] if len(parts) >= 3 else ""
            if _is_unpinned_java_version(ver_part, managed_by_bom=has_platform):
                res.unpinned_dependencies.append(coord)

    for cfg, catalog_ref in _GRADLE_CATALOG_DEP_RE.findall(btext):
        target_list = res.dev_dependencies if cfg.startswith("test") else res.dependencies
        target_list.append(catalog_ref)

    return res


def _inspect_java_manifests(project_root: Path) -> _ManifestInspection:
    """Inspect Java Maven or Gradle manifests in project_root."""
    java_candidates = (
        "pom.xml",
        "build.gradle.kts",
        "build.gradle",
        "settings.gradle.kts",
        "settings.gradle",
        "gradle/libs.versions.toml",
    )
    manifests = [m for m in java_candidates if (project_root / m).exists()]
    pom_path = project_root / "pom.xml"
    if pom_path.is_file():
        return _inspect_maven_pom(pom_path, manifests, project_root.name)
    if any(m.endswith((".gradle", ".gradle.kts")) for m in manifests):
        return _inspect_gradle_files(project_root, manifests)
    return _ManifestInspection(project_name=project_root.name, manifest_files=manifests)


def _is_unpinned_composer_version(version_spec: str) -> bool:
    """Return True if a Composer constraint uses wildcard '*', mutable dev-* branches, or unbounded '>='."""
    spec = version_spec.strip()
    if not spec or spec == "*":
        return True
    lower = spec.lower()
    if lower.startswith("dev-") or lower.endswith("-dev") or "@dev" in lower:
        return True
    return spec.startswith(">=") and "<" not in spec and "^" not in spec and "~" not in spec


def _extract_wp_header_metadata(project_root: Path) -> tuple[Optional[str], Optional[str], bool]:
    """Scan root PHP files and style.css for WordPress Plugin/Theme headers, Version, and Requires PHP."""
    candidates = [*sorted(project_root.glob("*.php")), project_root / "style.css"]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        with contextlib.suppress(Exception):
            head = candidate.read_text(encoding="utf-8", errors="ignore")[:8192]
            if _WP_PLUGIN_HEADER_RE.search(head) or (
                candidate.name == "style.css" and _WP_THEME_HEADER_RE.search(head)
            ):
                ver_m = re.search(r"(?mi)^\s*\*?\s*Version\s*:\s*([^\r\n]+)", head)
                php_m = re.search(r"(?mi)^\s*\*?\s*Requires PHP\s*:\s*([^\r\n]+)", head)
                ver = ver_m.group(1).strip() if ver_m else None
                req_php = php_m.group(1).strip() if php_m else None
                return ver, req_php, True
    return None, None, False


def _collect_composer_dep_list(
    section: object,
    target_list: list[str],
    unpinned_list: Optional[list[str]] = None,
) -> Optional[str]:
    """Populate Composer package coordinates from require/require-dev and return PHP constraint if present."""
    if not isinstance(section, dict):
        return None
    php_constraint: Optional[str] = None
    php_ver = section.get("php")
    if isinstance(php_ver, str) and php_ver.strip():
        php_constraint = php_ver.strip()
    for pkg_raw, ver_raw in section.items():
        pkg = str(pkg_raw).strip()
        ver = str(ver_raw).strip()
        if pkg == "php" or pkg.startswith(("ext-", "lib-", "composer-")):
            continue
        coord = f"{pkg}:{ver}" if ver else pkg
        target_list.append(coord)
        if unpinned_list is not None and _is_unpinned_composer_version(ver):
            unpinned_list.append(coord)
    return php_constraint


def _populate_composer_json_fields(data: dict[str, object], res: _ManifestInspection) -> None:
    """Populate _ManifestInspection fields from parsed composer.json dictionary."""
    raw_name = data.get("name")
    if isinstance(raw_name, str) and raw_name.strip():
        res.project_name = raw_name.strip()
    raw_ver = data.get("version")
    if isinstance(raw_ver, str) and raw_ver.strip():
        res.version = raw_ver.strip()

    res.language_version_constraint = _collect_composer_dep_list(
        data.get("require"),
        res.dependencies,
        res.unpinned_dependencies,
    )
    if not res.language_version_constraint:
        cfg = data.get("config")
        platform = cfg.get("platform") if isinstance(cfg, dict) else None
        plat_php = platform.get("php") if isinstance(platform, dict) else None
        if isinstance(plat_php, str) and plat_php.strip():
            res.language_version_constraint = plat_php.strip()

    _collect_composer_dep_list(data.get("require-dev"), res.dev_dependencies)


def _inspect_php_manifests(project_root: Path) -> _ManifestInspection:
    """Inspect PHP composer.json or legacy Composer-less / WordPress repository metadata."""
    php_candidates = ("composer.json", "phpunit.xml", "phpunit.xml.dist", "wp-config.php")
    manifests = [m for m in php_candidates if (project_root / m).is_file()]
    composer_path = project_root / "composer.json"

    if not composer_path.is_file():
        res = _ManifestInspection(
            project_name=project_root.name,
            build_system="raw_php",
            manifest_files=manifests,
        )
        wp_ver, wp_php, _ = _extract_wp_header_metadata(project_root)
        if wp_ver:
            res.version = wp_ver
        if wp_php:
            res.language_version_constraint = f">={wp_php}" if wp_php[0].isdigit() else wp_php
        return res

    res = _ManifestInspection(project_name=project_root.name, build_system="composer", manifest_files=manifests)
    with contextlib.suppress(Exception):
        data = json.loads(composer_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            _populate_composer_json_fields(data, res)
    return res


def _detect_php_frameworks(project_root: Path, deps: list[str], dev_deps: list[str]) -> list[str]:
    """Detect active PHP frameworks and QA tools from Composer packages and WordPress/Laravel files."""
    detected: list[str] = []
    joined = "\n".join([*deps, *dev_deps]).lower()
    for fw_id, needle in _PHP_FRAMEWORK_PATTERNS:
        if needle in joined and fw_id not in detected:
            detected.append(fw_id)

    if (project_root / "artisan").is_file() and "laravel" not in detected:
        detected.append("laravel")
    if (project_root / "wp-config.php").is_file() or (project_root / "wp-config-sample.php").is_file():
        if "wordpress" not in detected:
            detected.append("wordpress")
    else:
        _, _, has_wp_header = _extract_wp_header_metadata(project_root)
        if has_wp_header and "wordpress" not in detected:
            detected.append("wordpress")

    if (
        (project_root / "phpunit.xml").is_file() or (project_root / "phpunit.xml.dist").is_file()
    ) and "phpunit" not in detected:
        detected.append("phpunit")
    return detected


def _detect_frameworks(
    lang: str,
    deps: list[str],
    dev_deps: list[str],
    project_root: Optional[Path] = None,
) -> list[str]:
    """Detect active frameworks and libraries from declared dependencies."""
    detected: list[str] = []
    combined = [*deps, *dev_deps]
    if lang == "java":
        joined = "\n".join(combined).lower()
        for fw_id, needle in _JAVA_FRAMEWORK_PATTERNS:
            if needle in joined and fw_id not in detected:
                detected.append(fw_id)
        return detected
    if lang == "php":
        return _detect_php_frameworks(project_root or Path("."), deps, dev_deps)

    norm_names = {normalize_python_dep_name(d) for d in combined}
    for fw_id, pkg_key in _PYTHON_FRAMEWORK_KEYS:
        if pkg_key in norm_names and fw_id not in detected:
            detected.append(fw_id)
    return detected


_FIXTURE_PATH_PARTS: Final[frozenset[str]] = frozenset(
    {"test", "tests", "fixture", "fixtures", "testdata", "example", "examples"}
)


def _is_ignored_or_fixture_rel(project_root: Path, file_path: Path) -> bool:
    """Return True if file_path is inside an ignored, hidden, test, fixture, or example directory."""
    if _is_ignored_rel(project_root, file_path):
        return True
    rel_parts = file_path.relative_to(project_root).parts
    return any(part.lower() in _FIXTURE_PATH_PARTS for part in rel_parts[:-1])


def _check_type_marker(project_root: Path, lang: str, src_dirs: list[str]) -> Optional[bool]:
    """Check language package type-completeness marker (e.g. PEP 561 py.typed for Python)."""
    if lang != "python":
        return None
    for rel in src_dirs:
        candidate = project_root / rel
        if candidate.is_dir() and any(
            not _is_ignored_rel(project_root, p) for p in candidate.rglob("py.typed")
        ):
            return True
    return any(not _is_ignored_or_fixture_rel(project_root, p) for p in project_root.rglob("py.typed"))


def _count_script_loc(path: Path) -> int:
    """Count non-empty, non-comment lines in a script file."""
    with contextlib.suppress(Exception):
        return sum(
            1
            for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        )
    return 0


def _scan_legacy_language_assets(project_root: Path) -> list[str]:
    """Scan repository for migration-candidate legacy scripts (Perl, Batch/VBS, oversized Bash)."""
    findings: list[str] = []
    perl_files = [
        p
        for ext in ("*.pl", "*.pm", "*.cgi")
        for p in project_root.rglob(ext)
        if not _is_ignored_or_fixture_rel(project_root, p)
    ]
    if perl_files:
        total_loc = sum(_count_script_loc(p) for p in perl_files)
        findings.append(
            f"Perl scripts detected ({len(perl_files)} files, {total_loc} LOC) — "
            "recommend migrating to Python or Go"
        )

    win_legacy = [
        p
        for ext in ("*.bat", "*.vbs")
        for p in project_root.rglob(ext)
        if not _is_ignored_or_fixture_rel(project_root, p)
    ]
    if win_legacy:
        findings.append(f"Legacy Batch/VBScript files detected ({len(win_legacy)} files)")

    for sh_file in sorted(project_root.rglob("*.sh")):
        if _is_ignored_or_fixture_rel(project_root, sh_file):
            continue
        loc = _count_script_loc(sh_file)
        if loc > FAT_BASH_LOC_THRESHOLD:
            rel_sh = sh_file.relative_to(project_root).as_posix()
            findings.append(
                f"Oversized Bash script '{rel_sh}' ({loc} LOC > {FAT_BASH_LOC_THRESHOLD}) — "
                "recommend replacing with a typed Python (Typer) or Go CLI"
            )
    return findings


def _detect_python_tooling_issues(
    info: _ManifestInspection,
    lockfiles: list[str],
    runtime_types: list[RuntimeArchetype],
) -> list[str]:
    """Identify objective Python packaging, SemVer library boundary, and linter modernization issues."""
    issues: list[str] = []
    if "setup.py" in info.manifest_files and "pyproject.toml" not in info.manifest_files:
        issues.append("Legacy setup.py without PEP 621 pyproject.toml")
    if info.dependencies and not lockfiles:
        issues.append("Missing lockfile (uv.lock / poetry.lock / pdm.lock) for reproducible installs")
    if "pyproject.toml" in info.manifest_files and not info.language_version_constraint:
        issues.append("Missing 'requires-python' constraint in pyproject.toml")

    if "library" in runtime_types and "pyproject.toml" in info.manifest_files:
        exact_pins = [d for d in info.dependencies if "==" in d]
        if exact_pins:
            issues.append(
                f"Library runtime dependencies use strict '==' pins ({exact_pins}) — "
                "prefer '>=' lower bounds for SemVer compatibility"
            )

    dev_names = {normalize_python_dep_name(d) for d in info.dev_dependencies}
    legacy_linters = dev_names & {"flake8", "isort", "black", "pycodestyle", "pydocstyle"}
    if legacy_linters and "ruff" not in dev_names:
        joined = ", ".join(sorted(legacy_linters))
        issues.append(f"Split legacy linters ({joined}) without Ruff — consider unifying onto Ruff")
    return issues


def _detect_java_tooling_issues(info: _ManifestInspection, frameworks: list[str]) -> list[str]:
    """Identify objective Java version and ecosystem modernization issues."""
    issues: list[str] = []
    if "junit4" in frameworks:
        issues.append("Legacy JUnit 4 dependency detected — migrate to JUnit 5 (junit-jupiter)")
    if "javax-ee" in frameworks:
        issues.append("Legacy javax.* EE namespace detected — migrate to jakarta.* (Spring Boot 3+)")
    if info.language_version_constraint in {"1.8", "8", "11"}:
        issues.append(
            f"Aging Java target '{info.language_version_constraint}' — consider upgrading to Java 21 LTS"
        )
    return issues


def _is_eol_php_constraint(constraint: str) -> bool:
    """Return True if a PHP version constraint targets EOL PHP (< 8.1) without modern 8.2+ bounds."""
    if re.search(r"(?:\^|~|>=|>)\s*8\.[1-9]", constraint):
        return False
    return bool(re.search(r"(?:^|[^\d.])([57](?:\.\d+|\.\*)?|8\.0)(?:\b|\*)", constraint))


def _detect_php_tooling_issues(
    project_root: Path,
    info: _ManifestInspection,
    lockfiles: list[str],
    frameworks: list[str],
) -> list[str]:
    """Identify objective PHP Composer, PSR-4 autoload, PHP version, and test/static-analysis issues."""
    issues: list[str] = []
    composer_path = project_root / "composer.json"
    if info.build_system == "raw_php" or not composer_path.is_file():
        issues.append(
            "Missing composer.json — dependencies and PSR-4 autoloading are unmanaged (legacy raw PHP)"
        )
    else:
        if info.dependencies and "composer.lock" not in lockfiles:
            issues.append("Missing composer.lock for deterministic Composer dependency resolution")
        if not info.language_version_constraint:
            issues.append("Missing 'require.php' version constraint in composer.json")
        with contextlib.suppress(Exception):
            cdata = json.loads(composer_path.read_text(encoding="utf-8"))
            autoload = cdata.get("autoload") if isinstance(cdata, dict) else None
            if not isinstance(autoload, dict) or not autoload.get("psr-4"):
                issues.append("Missing PSR-4 autoload mapping ('autoload.psr-4') in composer.json")
        if "phpstan" not in frameworks and "psalm" not in frameworks:
            issues.append("No static type analyzer (PHPStan / Psalm) declared in composer.json require-dev")

    if info.language_version_constraint and _is_eol_php_constraint(info.language_version_constraint):
        issues.append(
            f"EOL PHP version constraint '{info.language_version_constraint}' — upgrade to active PHP 8.2+ / 8.3+"
        )
    if "phpunit" not in frameworks and "pest" not in frameworks:
        issues.append("No automated PHP test runner (PHPUnit / Pest) configured")
    return issues


def _resolve_default_dirs(project_root: Path, lang: str) -> tuple[list[str], list[str]]:
    """Return default (source_dirs, test_dirs) appropriate for the target language."""
    if lang == "java":
        src = ["src/main/java"] if (project_root / "src" / "main" / "java").exists() else ["src"]
        tst = ["src/test/java"] if (project_root / "src" / "test" / "java").exists() else ["test", "tests"]
        return src, tst
    if lang == "php":
        psr4_src, psr4_tst = extract_composer_psr4_dirs(project_root)
        tst = psr4_tst or (["tests"] if (project_root / "tests").is_dir() else ["test", "tests"])
        has_root_php = any(
            p.name != "artisan" for p in project_root.glob("*.php")
        ) or any(project_root.glob("*.phtml"))
        if has_root_php and not psr4_src:
            return ["."], tst
        modern_dirs = [d for d in ("app", "src", "routes", "includes", "public") if (project_root / d).is_dir()]
        combined_src = list(dict.fromkeys([*psr4_src, *modern_dirs]))
        return (combined_src or ["src"]), tst
    return ["src"], ["tests"]


def _inspect_readme(project_root: Path, doc_files: list[str]) -> tuple[bool, int]:
    """Check whether documentation exists and count non-empty lines."""
    for df in doc_files:
        p = project_root / df
        if p.is_file():
            lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
            return True, len(lines)
    return False, 0


def _dispatch_manifest_inspect(project_root: Path, active_lang: str) -> _ManifestInspection:
    """Dispatch manifest inspection according to active project language."""
    if active_lang == "java":
        res = _inspect_java_manifests(project_root)
    elif active_lang == "php":
        res = _inspect_php_manifests(project_root)
    else:
        res = _inspect_python_manifests(project_root)
    if res.version == "0.0.0":
        git_ver = detect_git_tag_version(project_root)
        if git_ver:
            res.version = git_ver
    return res


def _source_and_test_patterns(active_lang: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return file glob patterns for source and test files of active_lang."""
    if active_lang == "java":
        return ("*.java",), ("*Test.java", "*Tests.java", "Test*.java", "*IT.java")
    if active_lang == "php":
        return ("*.php", "*.phtml"), ("*Test.php", "Test*.php", "*_test.php")
    return ("*.py",), ("test_*.py", "*_test.py")


def _dispatch_tooling_issues(
    project_root: Path,
    active_lang: str,
    manifest_info: _ManifestInspection,
    lockfiles: list[str],
    frameworks: list[str],
    runtime_types: list[RuntimeArchetype],
) -> list[str]:
    """Dispatch language-specific tooling modernization checks."""
    if active_lang == "java":
        return _detect_java_tooling_issues(manifest_info, frameworks)
    if active_lang == "php":
        return _detect_php_tooling_issues(project_root, manifest_info, lockfiles, frameworks)
    return _detect_python_tooling_issues(manifest_info, lockfiles, runtime_types)


def _filter_project_opt_outs(
    active_lang: str,
    tooling_issues: list[str],
    container_issues: list[str],
    opt_outs: list[OptOutEntry],
) -> tuple[list[str], list[str], dict[str, int]]:
    """Filter deterministic tooling and container hygiene issues against [[opt_out]] waivers."""
    if not opt_outs:
        return tooling_issues, container_issues, {}

    counts: dict[str, int] = {}
    filtered_tooling: list[str] = []
    for issue in tooling_issues:
        check_ids: list[str] = [f"{active_lang}/tooling", "common/dependencies"]
        if "Missing lockfile" in issue or "Missing composer.lock" in issue:
            check_ids.extend(["python/lockfile_committed", "common/lockfile_committed"])
        matched = match_opt_out(opt_outs, check_ids, "pyproject.toml")
        if matched is not None:
            counts[matched.id] = counts.get(matched.id, 0) + 1
        else:
            filtered_tooling.append(issue)

    filtered_container: list[str] = []
    for issue in container_issues:
        file_part = issue.split(":", 1)[0].strip() if ":" in issue else "Dockerfile"
        c_ids: list[str] = ["common/container_security"]
        if "final stage runs as root" in issue:
            c_ids.extend(["DS-0002", "AVD-DS-0002"])
        elif "mutable ':latest'" in issue:
            c_ids.extend(["DS-0001", "AVD-DS-0001"])
        matched = match_opt_out(opt_outs, c_ids, file_part)
        if matched is not None:
            counts[matched.id] = counts.get(matched.id, 0) + 1
        else:
            filtered_container.append(issue)

    return filtered_tooling, filtered_container, counts


def run_project_inspect(
    project_root: Path,
    source_dirs: Optional[list[str]] = None,
    test_dirs: Optional[list[str]] = None,
    doc_files: Optional[list[str]] = None,
    lang: Optional[str] = None,
    exclude_globs: Optional[list[str]] = None,
) -> ProjectFacts:
    """Inspect repository structure, build manifests, governance, supply chain, and documentation.

    Args:
        project_root: Target project root directory.
        source_dirs: Relative source code directories or files (language-aware defaults if omitted).
        test_dirs: Relative test directories (language-aware defaults if omitted).
        doc_files: Documentation files to check (defaults to ['README.md', 'README.rst']).
        lang: Optional explicit language override ('python', 'java', 'php', etc.).
        exclude_globs: Optional glob patterns excluded from source and test file counts.

    Returns:
        ProjectFacts: Language-agnostic deterministically extracted project facts.
    """
    pni_cfg = load_pni_config(project_root)
    active_lang = lang or detect_active_language(project_root)
    manifest_info = _dispatch_manifest_inspect(project_root, active_lang)

    default_src, default_tst = _resolve_default_dirs(project_root, active_lang)
    eff_src = (
        source_dirs
        if source_dirs is not None
        else (list(pni_cfg.targets.source) if pni_cfg.targets.source else default_src)
    )
    eff_tst = (
        test_dirs
        if test_dirs is not None
        else (list(pni_cfg.targets.tests) if pni_cfg.targets.tests else default_tst)
    )
    eff_docs = (
        doc_files
        or (list(pni_cfg.targets.docs) if pni_cfg.targets.docs else ["README.md", "README.rst"])
    )
    eff_excludes = (
        exclude_globs
        if exclude_globs is not None
        else (list(pni_cfg.targets.exclude) if pni_cfg.targets.exclude else None)
    )
    src_patterns, test_patterns = _source_and_test_patterns(active_lang)

    lockfiles = [lf for lf in LOCKFILE_CANDIDATES if (project_root / lf).exists()]
    frameworks = _detect_frameworks(
        active_lang, manifest_info.dependencies, manifest_info.dev_dependencies, project_root
    )
    dep_names = {normalize_python_dep_name(d) for d in manifest_info.dependencies}
    inferred_archetypes = infer_runtime_types(
        project_root,
        frameworks=frameworks,
        dep_names=dep_names,
        src_dirs=eff_src,
    )
    archetypes: list[RuntimeArchetype] = (
        list(pni_cfg.project.archetypes) if pni_cfg.project.archetypes else inferred_archetypes
    )
    raw_tooling_issues = _dispatch_tooling_issues(
        project_root, active_lang, manifest_info, lockfiles, frameworks, archetypes
    )
    has_readme, readme_lines = _inspect_readme(project_root, eff_docs)
    ignored_files, ignored_dirs = (
        discover_gitignored_paths(project_root, include_gitignored=pni_cfg.scan.include_gitignored)
        if pni_cfg.scan.respect_gitignore
        else ([], [])
    )
    gov = inspect_governance_and_docs(
        project_root,
        eff_docs,
        IGNORED_PATH_PARTS,
        skip_files=pni_cfg.scan.skip_files,
        skip_dirs=(*pni_cfg.scan.skip_dirs, *ignored_dirs),
        gitignored_files=frozenset(ignored_files),
    )
    tooling_issues, container_issues, opt_out_counts = _filter_project_opt_outs(
        active_lang,
        raw_tooling_issues,
        gov.container_hygiene_issues,
        pni_cfg.opt_out,
    )

    return ProjectFacts(
        project_name=pni_cfg.project.name or manifest_info.project_name,
        version=pni_cfg.project.version or manifest_info.version,
        language=active_lang,
        runtime_types=archetypes,
        build_system=manifest_info.build_system,
        language_version_constraint=manifest_info.language_version_constraint,
        has_type_marker=_check_type_marker(project_root, active_lang, eff_src),
        manifest_files=manifest_info.manifest_files,
        lockfiles_found=lockfiles,
        dependencies=manifest_info.dependencies,
        unpinned_dependencies=manifest_info.unpinned_dependencies,
        dev_dependencies=manifest_info.dev_dependencies,
        detected_frameworks=frameworks,
        legacy_language_findings=_scan_legacy_language_assets(project_root),
        tooling_modernization_issues=tooling_issues,
        source_files_count=_count_matching_files(
            project_root,
            eff_src,
            src_patterns,
            exclude_dirs=eff_tst,
            exclude_globs=eff_excludes,
        ),
        test_files_count=_count_matching_files(
            project_root,
            eff_tst,
            test_patterns,
            exclude_globs=eff_excludes,
        ),
        has_readme=has_readme,
        readme_line_count=readme_lines,
        readme_headings=gov.readme_headings,
        docs_inventory=gov.docs_inventory,
        has_gitignore=(project_root / ".gitignore").exists(),
        has_license=gov.has_license,
        has_security_policy=gov.has_security_policy,
        has_dependency_automation=gov.has_dependency_automation,
        ci_workflows_found=gov.ci_workflows_found,
        ci_supply_chain_issues=gov.ci_supply_chain_issues,
        committed_secret_files=gov.committed_secret_files,
        has_dockerfile=gov.has_dockerfile,
        container_hygiene_issues=container_issues,
        opt_out_counts=opt_out_counts,
    )
