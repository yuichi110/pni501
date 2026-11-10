# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Language-agnostic repository governance, supply-chain, container, and documentation inspectors."""

from __future__ import annotations

import contextlib
import fnmatch
import json
import re
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Final, Literal

import yaml

RuntimeArchetype = Literal["web_api", "worker", "cli", "library"]


def matches_exclude_globs(
    file_path: Path,
    project_root: Path,
    exclude_globs: Sequence[str] = (),
) -> bool:
    """Return True if file_path matches any exclude glob relative to project_root."""
    if not exclude_globs:
        return False
    rel_posix = (
        file_path.relative_to(project_root).as_posix()
        if file_path.is_relative_to(project_root)
        else file_path.name
    )
    rel_pure = PurePosixPath(rel_posix)
    for raw_glob in exclude_globs:
        pat = raw_glob.strip()
        if not pat:
            continue
        if pat.endswith("/**"):
            prefix = pat[:-3].strip("/")
            if prefix and (rel_posix == prefix or rel_posix.startswith(f"{prefix}/")):
                return True
        if fnmatch.fnmatchcase(rel_posix, pat) or rel_pure.match(pat):
            return True
        if pat.startswith("**/") and (
            fnmatch.fnmatchcase(rel_posix, pat[3:]) or fnmatch.fnmatchcase(file_path.name, pat[3:])
        ):
            return True
    return False

_PYTHON_ENTRYPOINT_NAMES: Final[frozenset[str]] = frozenset(
    {"cli", "main", "__main__", "app", "wsgi", "asgi", "server", "worker", "commands"}
)
_WEB_FRAMEWORKS: Final[frozenset[str]] = frozenset(
    {
        "fastapi",
        "flask",
        "django",
        "litestar",
        "starlette",
        "aiohttp",
        "tornado",
        "spring-boot",
        "spring-framework",
        "jakarta-ee",
        "javax-ee",
        "quarkus",
        "micronaut",
        "laravel",
        "symfony",
        "slim",
        "cakephp",
        "codeigniter",
        "wordpress",
        "gin",
        "echo",
        "fiber",
        "chi",
        "gorilla-mux",
        "grpc",
        "express",
        "fastify",
        "nestjs",
        "hono",
        "koa",
        "nextjs",
        "nuxt",
        "react",
        "vue",
        "angular",
        "svelte",
    }
)
_WORKER_PACKAGES: Final[frozenset[str]] = frozenset(
    {"celery", "dramatiq", "rq", "arq", "huey", "temporalio", "faust", "bullmq"}
)
_CLI_PACKAGES: Final[frozenset[str]] = frozenset(
    {
        "typer",
        "click",
        "picocli",
        "jcommander",
        "commons_cli",
        "cobra",
        "urfave-cli",
        "symfony_console",
        "laravel_zero",
        "commander",
        "yargs",
    }
)
_LICENSE_CANDIDATES: Final[tuple[str, ...]] = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "LICENCE",
    "COPYING",
)
_SECURITY_POLICY_CANDIDATES: Final[tuple[str, ...]] = (
    "SECURITY.md",
    ".github/SECURITY.md",
    "docs/SECURITY.md",
)
_DEPENDENCY_AUTOMATION_CANDIDATES: Final[tuple[str, ...]] = (
    ".github/dependabot.yml",
    ".github/dependabot.yaml",
    "renovate.json",
    "renovate.json5",
    ".renovaterc",
    ".renovaterc.json",
    ".github/renovate.json",
)
_SAFE_ENV_TEMPLATES: Final[frozenset[str]] = frozenset(
    {
        ".env.example",
        ".env.sample",
        ".env.template",
        ".env.dist",
        ".env.defaults",
        ".env.schema",
    }
)
_SECRET_EXACT_FILENAMES: Final[frozenset[str]] = frozenset(
    {"id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", ".htpasswd"}
)
_SECRET_EXTENSIONS: Final[frozenset[str]] = frozenset({".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"})
_SECRET_JSON_PATTERNS: Final[tuple[str, ...]] = ("credentials", "service-account", "service_account", "client_secret")
_MUTABLE_ACTION_REFS: Final[frozenset[str]] = frozenset({"main", "master", "head", "latest", "dev", "develop"})
_TEST_OR_FIXTURE_DIRS: Final[frozenset[str]] = frozenset(
    {"test", "tests", "fixture", "fixtures", "testdata", "example", "examples"}
)
_TOP_LEVEL_DOC_CANDIDATES: Final[tuple[str, ...]] = (
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "ARCHITECTURE.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
)
_MD_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_DOCKER_FROM_RE = re.compile(r"(?i)^FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?")
_DOCKER_USER_RE = re.compile(r"(?i)^USER\s+(\S+)")


@dataclass
class GovernanceFacts:
    """Aggregated OpenSSF supply-chain, container, and Diátaxis documentation facts."""

    has_license: bool = False
    has_security_policy: bool = False
    has_dependency_automation: bool = False
    ci_workflows_found: list[str] = field(default_factory=list)
    ci_supply_chain_issues: list[str] = field(default_factory=list)
    committed_secret_files: list[str] = field(default_factory=list)
    has_dockerfile: bool = False
    container_hygiene_issues: list[str] = field(default_factory=list)
    readme_headings: list[str] = field(default_factory=list)
    docs_inventory: list[str] = field(default_factory=list)


def _has_python_cli_entrypoints(project_root: Path, src_dirs: list[str]) -> bool:
    """Return True if pyproject.toml declares CLI scripts or source tree contains __main__.py."""
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.is_file():
        with contextlib.suppress(Exception):
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            proj = data.get("project")
            if isinstance(proj, dict) and bool(proj.get("scripts")):
                return True
            tool = data.get("tool")
            poetry = tool.get("poetry") if isinstance(tool, dict) else None
            if isinstance(poetry, dict) and bool(poetry.get("scripts")):
                return True

    for rel in src_dirs:
        candidate = project_root / rel
        if candidate.is_dir() and any(candidate.rglob("__main__.py")):
            return True
    return False


def _count_public_pkg_members(pkg_dir: Path) -> int:
    """Count public (non-underscore, non-entrypoint) modules and subpackages inside a Python package."""
    count = 0
    with contextlib.suppress(OSError):
        for entry in pkg_dir.iterdir():
            name = entry.name
            if name.startswith(("_", ".")):
                continue
            if entry.is_file() and name.endswith(".py"):
                stem = name[:-3]
                if stem not in _PYTHON_ENTRYPOINT_NAMES:
                    count += 1
            elif (
                entry.is_dir()
                and name not in _PYTHON_ENTRYPOINT_NAMES
                and name.lower() not in _TEST_OR_FIXTURE_DIRS
                and (entry / "__init__.py").is_file()
            ):
                count += 1
    return count


def _has_python_sdk_surface(project_root: Path, src_dirs: list[str], *, is_service: bool = False) -> bool:
    """Return True if a Python package exposes >= 2 public SDK modules/subpackages beyond entrypoints."""
    for rel in src_dirs:
        candidate = project_root / rel
        if not candidate.is_dir():
            continue
        pkg_dirs: list[Path] = []
        if (candidate / "__init__.py").is_file():
            pkg_dirs.append(candidate)
        else:
            with contextlib.suppress(OSError):
                pkg_dirs.extend(
                    d
                    for d in candidate.iterdir()
                    if d.is_dir()
                    and not d.name.startswith(("_", "."))
                    and d.name.lower() not in _TEST_OR_FIXTURE_DIRS
                    and (d / "__init__.py").is_file()
                )
        for pkg_dir in pkg_dirs:
            if is_service and not (pkg_dir / "py.typed").is_file():
                continue
            if _count_public_pkg_members(pkg_dir) >= 2:
                return True
    return False


def _detect_php_archetype_signals(project_root: Path) -> tuple[bool, bool, bool]:
    """Return (has_php_web, has_php_cli, force_php_library) from composer.json and entry scripts."""
    composer_path = project_root / "composer.json"
    has_cli = (project_root / "artisan").is_file()
    force_lib = False
    if composer_path.is_file():
        with contextlib.suppress(Exception):
            cdata = json.loads(composer_path.read_text(encoding="utf-8"))
            if isinstance(cdata, dict):
                ctype = str(cdata.get("type", "")).strip().lower()
                if ctype == "library":
                    force_lib = True
                if cdata.get("bin"):
                    has_cli = True

    has_web = (
        (project_root / "public" / "index.php").is_file()
        or (project_root / "wp-config.php").is_file()
        or (not force_lib and (project_root / "index.php").is_file())
    )
    return has_web, has_cli, force_lib


def _detect_go_or_node_archetype_signals(project_root: Path) -> tuple[bool, bool, bool]:
    """Return (has_go_main, has_node_bin, has_sdk) from Go cmd/pkg directories or Node package.json."""
    has_go_main = (
        (project_root / "main.go").is_file()
        or ((project_root / "cmd").is_dir() and any((project_root / "cmd").rglob("main.go")))
    )
    has_node_bin = False
    has_sdk = (project_root / "pkg").is_dir() and any((project_root / "pkg").rglob("*.go"))

    pkg_json = project_root / "package.json"
    if pkg_json.is_file():
        with contextlib.suppress(Exception):
            pdata = json.loads(pkg_json.read_text(encoding="utf-8"))
            if isinstance(pdata, dict):
                if pdata.get("bin"):
                    has_node_bin = True
                if (pdata.get("main") or pdata.get("exports")) and not pdata.get("private", False):
                    has_sdk = True
    return has_go_main, has_node_bin, has_sdk


def infer_runtime_types(
    project_root: Path,
    *,
    frameworks: list[str],
    dep_names: set[str],
    src_dirs: list[str],
) -> list[RuntimeArchetype]:
    """Infer deterministic list of runtime archetypes ('web_api', 'worker', 'cli', 'library').

    Args:
        project_root: Target project root directory.
        frameworks: Detected framework identifiers.
        dep_names: Normalized runtime dependency names.
        src_dirs: Effective source directories relative to project_root.

    Returns:
        list[RuntimeArchetype]: Ordered list of applicable runtime archetypes (non-empty).
    """
    fw_set = set(frameworks)
    php_web, php_cli, force_php_lib = _detect_php_archetype_signals(project_root)
    go_main, node_bin, go_node_sdk = _detect_go_or_node_archetype_signals(project_root)
    has_web = (bool((fw_set | dep_names) & _WEB_FRAMEWORKS) or php_web) and not force_php_lib
    has_worker = bool(dep_names & _WORKER_PACKAGES)
    has_cli = (
        bool((fw_set | dep_names) & _CLI_PACKAGES)
        or _has_python_cli_entrypoints(project_root, src_dirs)
        or node_bin
        or (php_cli and not has_web)
        or (go_main and not has_web)
    )
    has_sdk = (
        force_php_lib
        or (go_node_sdk and not has_web)
        or _has_python_sdk_surface(
            project_root,
            src_dirs,
            is_service=(has_web or has_worker),
        )
    )

    types: list[RuntimeArchetype] = []
    if has_web:
        types.append("web_api")
    if has_worker:
        types.append("worker")
    if has_cli:
        types.append("cli")
    if has_sdk or not types:
        types.append("library")
    return types


def _has_prt_trigger(triggers: object) -> bool:
    """Return True if a GitHub Actions 'on' configuration includes pull_request_target."""
    if isinstance(triggers, str):
        return triggers == "pull_request_target"
    if isinstance(triggers, list):
        return "pull_request_target" in triggers
    if isinstance(triggers, dict):
        return "pull_request_target" in triggers
    return False


def _collect_workflow_uses(jobs: dict[object, object]) -> list[str]:
    """Collect all external 'uses:' action/workflow references across GitHub Actions jobs."""
    refs: list[str] = []
    for job_val in jobs.values():
        if not isinstance(job_val, dict):
            continue
        job_uses = job_val.get("uses")
        if isinstance(job_uses, str):
            refs.append(job_uses.strip())
        steps = job_val.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if isinstance(step, dict) and isinstance(step.get("uses"), str):
                refs.append(str(step["uses"]).strip())
    return refs


def _audit_github_workflow_file(wf_path: Path, rel_wf: str) -> list[str]:
    """Inspect a single GitHub Actions workflow YAML for OpenSSF Scorecard supply-chain risks."""
    issues: list[str] = []
    data: object = None
    with contextlib.suppress(Exception):
        data = yaml.safe_load(wf_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return issues

    triggers = data.get("on") if "on" in data else data.get(True)
    if _has_prt_trigger(triggers):
        issues.append(
            f"{rel_wf}: uses privileged 'pull_request_target' trigger — verify untrusted PR code is never executed"
        )

    raw_jobs = data.get("jobs")
    jobs = raw_jobs if isinstance(raw_jobs, dict) else {}
    has_root_perms = "permissions" in data
    all_jobs_have_perms = bool(jobs) and all(
        isinstance(j, dict) and "permissions" in j for j in jobs.values()
    )
    if not has_root_perms and not all_jobs_have_perms:
        issues.append(f"{rel_wf}: missing explicit GITHUB_TOKEN 'permissions:' block (OpenSSF Token-Permissions)")

    for ref in _collect_workflow_uses(jobs):
        if ref.startswith(("./", "docker://")) or "@" not in ref:
            continue
        version_ref = ref.rsplit("@", maxsplit=1)[1].strip()
        if version_ref.lower() in _MUTABLE_ACTION_REFS:
            issues.append(f"{rel_wf}: unpinned mutable action '{ref}' — pin to an immutable commit SHA or release tag")
    return issues


def _is_secret_candidate(file_path: Path, rel_parts: tuple[str, ...]) -> bool:
    """Return True if file_path looks like an accidentally committed .env, private key, or credential file."""
    if any(part.lower() in _TEST_OR_FIXTURE_DIRS for part in rel_parts[:-1]):
        return False
    name = file_path.name
    lower_name = name.lower()
    if lower_name == ".env" or (lower_name.startswith(".env.") and lower_name not in _SAFE_ENV_TEMPLATES):
        return True
    if lower_name in _SECRET_EXACT_FILENAMES or file_path.suffix.lower() in _SECRET_EXTENSIONS:
        return True
    return lower_name.endswith(".json") and any(tok in lower_name for tok in _SECRET_JSON_PATTERNS)


def _scan_committed_secrets(
    project_root: Path,
    ignored_dirs: frozenset[str],
    *,
    skip_files: Sequence[str] = (),
    gitignored_files: frozenset[str] = frozenset(),
) -> list[str]:
    """Scan workspace for committed .env, private key, and service-account credential files."""
    found: list[str] = []
    for candidate in sorted(project_root.rglob("*")):
        if not candidate.is_file():
            continue
        rel_path = candidate.relative_to(project_root)
        rel_parts = rel_path.parts
        if any(part in ignored_dirs or (part.startswith(".") and part != ".github") for part in rel_parts[:-1]):
            continue
        rel_posix = rel_path.as_posix()
        if rel_posix in gitignored_files:
            continue
        if skip_files and matches_exclude_globs(candidate, project_root, skip_files):
            continue
        if _is_secret_candidate(candidate, rel_parts):
            found.append(rel_posix)
    return found


def _inspect_dockerfile(project_root: Path) -> tuple[bool, list[str]]:
    """Inspect Dockerfile/Containerfile for :latest base images, root execution, and .dockerignore."""
    dockerfile = next(
        (project_root / n for n in ("Dockerfile", "Containerfile") if (project_root / n).is_file()),
        None,
    )
    if dockerfile is None:
        return False, []

    issues: list[str] = []
    dname = dockerfile.name
    stage_aliases: set[str] = set()
    last_stage_user: str | None = None
    saw_from = False

    with contextlib.suppress(Exception):
        for raw_line in dockerfile.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            from_match = _DOCKER_FROM_RE.match(line)
            if from_match:
                saw_from = True
                last_stage_user = None
                image_ref = from_match.group(1)
                alias = from_match.group(2)
                if alias:
                    stage_aliases.add(alias.lower())
                lower_img = image_ref.lower()
                is_unpinned = (
                    lower_img != "scratch"
                    and lower_img not in stage_aliases
                    and not lower_img.startswith("$")
                    and ("@sha256:" not in lower_img)
                    and (":" not in lower_img or lower_img.endswith(":latest"))
                )
                if is_unpinned:
                    issues.append(f"{dname}: base image '{image_ref}' uses mutable ':latest' or untagged reference")
                continue

            user_match = _DOCKER_USER_RE.match(line)
            if user_match:
                last_stage_user = user_match.group(1).strip()

    if saw_from and (last_stage_user is None or last_stage_user.lower() in {"root", "0", "0:0"}):
        issues.append(f"{dname}: final stage runs as root (missing non-root 'USER' instruction)")
    if not (project_root / ".dockerignore").is_file():
        issues.append(f"{dname}: missing '.dockerignore' (risks leaking .git or secrets into build context)")
    return True, issues


def _extract_markdown_headings(readme_path: Path) -> list[str]:
    """Extract H1-H3 Markdown headings outside fenced code blocks for Diátaxis / Standard Readme checks."""
    headings: list[str] = []
    in_fence = False
    with contextlib.suppress(Exception):
        for raw_line in readme_path.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if stripped.startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = _MD_HEADING_RE.match(stripped)
            if match:
                headings.append(f"{match.group(1)} {match.group(2)}")
    return headings[:40]


def _collect_docs_inventory(project_root: Path, doc_files: list[str], ignored_dirs: frozenset[str]) -> list[str]:
    """Collect relative paths of top-level governance docs and docs/ directory files."""
    inventory: list[str] = []
    for name in (*doc_files, *_TOP_LEVEL_DOC_CANDIDATES):
        p = project_root / name
        if p.is_file():
            rel = p.relative_to(project_root).as_posix()
            if rel not in inventory:
                inventory.append(rel)

    for doc_dir_name in ("docs", "doc"):
        doc_dir = project_root / doc_dir_name
        if not doc_dir.is_dir():
            continue
        for ext in ("*.md", "*.rst", "*.adoc"):
            for found in sorted(doc_dir.rglob(ext)):
                rel_parts = found.relative_to(project_root).parts
                if any(part in ignored_dirs or part.startswith(".") for part in rel_parts[:-1]):
                    continue
                rel = found.relative_to(project_root).as_posix()
                if rel not in inventory:
                    inventory.append(rel)
    return inventory


def inspect_governance_and_docs(
    project_root: Path,
    doc_files: list[str],
    ignored_dirs: frozenset[str],
    *,
    skip_files: Sequence[str] = (),
    skip_dirs: Sequence[str] = (),
    gitignored_files: frozenset[str] = frozenset(),
) -> GovernanceFacts:
    """Run deterministic OpenSSF supply-chain, container, secret-file, and Diátaxis doc checks.

    Args:
        project_root: Target project root directory.
        doc_files: Documentation files configured for inspection.
        ignored_dirs: Directory names excluded from recursive workspace scans.
        skip_files: Additional file patterns skipped from secret scanning.
        skip_dirs: Additional directory names skipped from secret scanning.
        gitignored_files: Set of relative paths ignored by git (.gitignore).

    Returns:
        GovernanceFacts: Language-agnostic repository governance and documentation facts.
    """
    eff_ignored_dirs = ignored_dirs | frozenset(d.strip("/") for d in skip_dirs if d.strip("/"))
    gh_wf_dir = project_root / ".github" / "workflows"
    ci_workflows: list[str] = []
    ci_issues: list[str] = []
    if gh_wf_dir.is_dir():
        wf_files = sorted([*gh_wf_dir.glob("*.yml"), *gh_wf_dir.glob("*.yaml")])
        for wf in wf_files:
            rel_wf = wf.relative_to(project_root).as_posix()
            ci_workflows.append(rel_wf)
            ci_issues.extend(_audit_github_workflow_file(wf, rel_wf))
    if (project_root / ".gitlab-ci.yml").is_file():
        ci_workflows.append(".gitlab-ci.yml")

    has_dockerfile, container_issues = _inspect_dockerfile(project_root)

    readme_headings: list[str] = []
    for df in doc_files:
        rp = project_root / df
        if rp.is_file() and rp.suffix.lower() in {".md", ".markdown"}:
            readme_headings = _extract_markdown_headings(rp)
            break

    return GovernanceFacts(
        has_license=any((project_root / c).is_file() for c in _LICENSE_CANDIDATES),
        has_security_policy=any((project_root / c).is_file() for c in _SECURITY_POLICY_CANDIDATES),
        has_dependency_automation=any((project_root / c).is_file() for c in _DEPENDENCY_AUTOMATION_CANDIDATES),
        ci_workflows_found=ci_workflows,
        ci_supply_chain_issues=ci_issues,
        committed_secret_files=_scan_committed_secrets(
            project_root,
            eff_ignored_dirs,
            skip_files=skip_files,
            gitignored_files=gitignored_files,
        ),
        has_dockerfile=has_dockerfile,
        container_hygiene_issues=container_issues,
        readme_headings=readme_headings,
        docs_inventory=_collect_docs_inventory(project_root, doc_files, eff_ignored_dirs),
    )
