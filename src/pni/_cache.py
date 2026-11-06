# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Self-healing .pni/cache/ directory management and canonical cache paths."""

from __future__ import annotations

from pathlib import Path
from typing import Final

CACHE_REL_DIR: Final[str] = ".pni/cache"
DEFAULT_STATE_DB_REL_PATH: Final[str] = f"{CACHE_REL_DIR}/workflow_state.db"

_CACHE_GITIGNORE_CONTENT: Final[str] = "# Created by pni automatically.\n*\n"
_CACHEDIR_TAG_CONTENT: Final[str] = (
    "Signature: 8a477f597d28d172789f06886806bc55\n"
    "# This file is a cache directory tag created by pni.\n"
    "# For information about cache directory tags, see:\n"
    "#\thttps://bford.info/cachedir/spec.html\n"
)


def ensure_cache_dir(project_root: Path) -> Path:
    """Ensure .pni/cache/ exists alongside its self-healing .gitignore and CACHEDIR.TAG.

    Args:
        project_root: Workspace root directory.

    Returns:
        Path: Path to <project_root>/.pni/cache.
    """
    cache_dir = project_root / CACHE_REL_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    gitignore = cache_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(_CACHE_GITIGNORE_CONTENT, encoding="utf-8")

    cachedir_tag = cache_dir / "CACHEDIR.TAG"
    if not cachedir_tag.exists():
        cachedir_tag.write_text(_CACHEDIR_TAG_CONTENT, encoding="utf-8")

    return cache_dir


def ensure_cache_parent(project_root: Path, target_file: Path) -> None:
    """Ensure parent directories for target_file exist and .pni/cache/.gitignore is present if applicable.

    Args:
        project_root: Workspace root directory.
        target_file: Target file path about to be written.
    """
    cache_root = (project_root / CACHE_REL_DIR).resolve()
    resolved_target = target_file.resolve()
    if resolved_target == cache_root or resolved_target.is_relative_to(cache_root):
        ensure_cache_dir(project_root)
    target_file.parent.mkdir(parents=True, exist_ok=True)


def default_facts_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's deterministic facts snapshot."""
    return f"{CACHE_REL_DIR}/{workflow_id}/facts.json"


def default_architecture_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's grounded ArchitectureRecord JSON."""
    return f"{CACHE_REL_DIR}/{workflow_id}/architecture.json"


def default_blueprint_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's pre-sorted ReportBlueprint JSON."""
    return f"{CACHE_REL_DIR}/{workflow_id}/blueprint.json"


def default_migration_facts_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's deterministic MigrationFacts JSON."""
    return f"{CACHE_REL_DIR}/{workflow_id}/migration_facts.json"


def default_migration_blueprint_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's pre-sorted MigrationBlueprint JSON."""
    return f"{CACHE_REL_DIR}/{workflow_id}/migration_blueprint.json"


def normalize_target_subpath(target_root: str) -> str:
    """Normalize a workflow target_root string into a safe relative POSIX subpath ('' for '.').

    Args:
        target_root: Raw workflow targets.root string (e.g. '.', 'examples/python/lib_clean').

    Returns:
        str: Normalized POSIX subpath without leading/trailing slashes, or '' for workspace root.

    Raises:
        ValueError: If target_root attempts parent-directory traversal ('..') or is absolute.
    """
    cleaned = target_root.strip().replace("\\", "/")
    if cleaned.startswith("/"):
        msg = f"target_root must be workspace-relative, got: {target_root!r}"
        raise ValueError(msg)
    parts = [seg for seg in cleaned.split("/") if seg and seg != "."]
    if any(seg == ".." for seg in parts):
        msg = f"Parent traversal '..' is not allowed in target_root: {target_root!r}"
        raise ValueError(msg)
    return "/".join(parts)


def default_target_dockerfile_rel_path(target_root: str = ".") -> str:
    """Return workspace-relative path for a target source's harness Dockerfile in .pni/dockerfiles/.

    Maps '.' -> '.pni/dockerfiles/Dockerfile' and
    'examples/python/lib_clean' -> '.pni/dockerfiles/examples/python/lib_clean/Dockerfile'.
    """
    sub = normalize_target_subpath(target_root)
    if not sub:
        return ".pni/dockerfiles/Dockerfile"
    return f".pni/dockerfiles/{sub}/Dockerfile"


def default_runtime_rel_dir(workflow_id: str) -> str:
    """Return workspace-relative directory for a workflow's container runtime logs and reports."""
    return f"{CACHE_REL_DIR}/{workflow_id}/runtime"


def default_runtime_facts_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's deterministic RuntimeFacts JSON."""
    return f"{default_runtime_rel_dir(workflow_id)}/runtime_facts.json"


def default_trivy_cache_rel_dir() -> str:
    """Return workspace-relative shared Trivy vulnerability DB cache directory."""
    return f"{CACHE_REL_DIR}/trivy-cache"


def default_security_rel_dir(workflow_id: str) -> str:
    """Return workspace-relative directory for a workflow's security scan artifacts."""
    return f"{CACHE_REL_DIR}/{workflow_id}/security"


def default_security_facts_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's deterministic SecurityFacts JSON."""
    return f"{default_security_rel_dir(workflow_id)}/security_facts.json"


def default_target_pentests_rel_dir(target_root: str = ".") -> str:
    """Return workspace-relative directory for a target's explicit httpx pentest suite in .pni/pentests/.

    Maps '.' -> '.pni/pentests' and
    'examples/php/legacy_shop_messy' -> '.pni/pentests/examples/php/legacy_shop_messy'.
    """
    sub = normalize_target_subpath(target_root)
    if not sub:
        return ".pni/pentests"
    return f".pni/pentests/{sub}"


def default_pentest_rel_dir(workflow_id: str) -> str:
    """Return workspace-relative cache directory for a workflow's dynamic pentest logs and XML."""
    return f"{CACHE_REL_DIR}/{workflow_id}/pentest"


def default_pentest_facts_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's deterministic PentestFacts JSON."""
    return f"{default_pentest_rel_dir(workflow_id)}/pentest_facts.json"


def _sanitize_identifier_segment(raw_name: str, field_name: str = "identifier") -> str:
    """Validate and normalize a single file-stem identifier without path separators or '..'."""
    cleaned = raw_name.strip().removesuffix(".yaml").removesuffix(".yml").removesuffix(".jsonl").strip()
    if not cleaned or "/" in cleaned or "\\" in cleaned or ".." in cleaned or cleaned.startswith("."):
        msg = f"Invalid {field_name}: {raw_name!r}"
        raise ValueError(msg)
    return cleaned


def default_progress_plan_rel_path(target_or_workflow_id: str) -> str:
    """Return workspace-relative path for a progress plan YAML in .pni/progress/<target>.yaml."""
    sub = normalize_target_subpath(target_or_workflow_id)
    if not sub:
        return ".pni/progress/project_progress.yaml"
    if sub.endswith((".yaml", ".yml")):
        return sub if sub.startswith(".pni/progress/") else f".pni/progress/{sub}"
    return f".pni/progress/{sub}.yaml"


def default_audit_history_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a Git-tracked audit history JSONL ledger."""
    safe_id = _sanitize_identifier_segment(workflow_id, "workflow_id")
    return f".pni/history/audit/{safe_id}.jsonl"


def default_progress_history_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a Git-tracked progress history JSONL ledger."""
    safe_id = _sanitize_identifier_segment(workflow_id, "workflow_id")
    return f".pni/history/progress/{safe_id}.jsonl"


def default_progress_facts_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's deterministic ProgressFacts JSON."""
    safe_id = _sanitize_identifier_segment(workflow_id, "workflow_id")
    return f"{CACHE_REL_DIR}/{safe_id}/progress_facts.json"


def default_progress_blueprint_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path for a workflow's pre-sorted ProgressBlueprint JSON."""
    safe_id = _sanitize_identifier_segment(workflow_id, "workflow_id")
    return f"{CACHE_REL_DIR}/{safe_id}/progress_blueprint.json"


