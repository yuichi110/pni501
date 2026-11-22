# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Synchronize structured workflow evidence JSONs into `<report_src_dir>/_facts/`."""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from pni._actions.base_model import PrimitiveType
from pni._cache import ensure_cache_parent
from pni._reporter.base_model import DEFAULT_REPORT_FACTS_SUBDIR, DEFAULT_REPORT_SRC_DIR

if TYPE_CHECKING:
    from pni._workflows.base_model import ActionRunRecord


def _resolve_safe_path(project_root: Path, rel_path: str) -> Path | None:
    """Resolve `rel_path` strictly inside `project_root`, returning None if outside boundary."""
    root_res = project_root.resolve()
    cleaned = rel_path.strip()
    if not cleaned or cleaned.startswith("/"):
        return None
    candidate = (root_res / cleaned).resolve()
    if candidate == root_res or not candidate.is_relative_to(root_res):
        return None
    return candidate


def resolve_report_src_dir_for_actions(actions: Sequence[ActionRunRecord]) -> str | None:
    """Return the configured `src_dir` if the workflow includes a non-skipped Drawlib report step."""
    for act in actions:
        if act.primitive_type != PrimitiveType.WRITE_DRAWLIB_REPORT:
            continue
        if str(act.status.value) == "skipped":
            continue
        raw = act.params.get("src_dir")
        if isinstance(raw, str) and raw.strip():
            return raw.strip().rstrip("/")
        return DEFAULT_REPORT_SRC_DIR
    return None


def sync_workflow_facts_to_report(
    project_root: Path,
    report_src_dir: str | None,
    *,
    source_files: dict[str, str],
) -> dict[str, str]:
    """Copy existing structured evidence JSONs into `<report_src_dir>/_facts/` and return updated paths.

    Only structured JSON artifacts (e.g., `plan.json`, `facts.json`, `architecture.json`) are copied;
    ephemeral SQLite databases, Trivy caches, and raw container logs stay strictly in `.pni/cache/`.
    """
    if not report_src_dir:
        return dict(source_files)
    src_root = _resolve_safe_path(project_root, report_src_dir)
    if src_root is None:
        return dict(source_files)

    facts_dir = src_root / DEFAULT_REPORT_FACTS_SUBDIR
    facts_dir.mkdir(parents=True, exist_ok=True)
    ws_root = project_root.resolve()
    resolved_manifest: dict[str, str] = {}

    for key, src_rel in source_files.items():
        if not src_rel or not src_rel.strip():
            continue
        src_path = _resolve_safe_path(project_root, src_rel)
        if src_path is not None and src_path.is_file():
            dest_path = facts_dir / src_path.name
            if dest_path.resolve() != src_path.resolve():
                shutil.copy2(src_path, dest_path)
            resolved_manifest[key] = dest_path.resolve().relative_to(ws_root).as_posix()
        else:
            resolved_manifest[key] = src_rel

    return resolved_manifest


def write_blueprint_to_report_facts(
    project_root: Path,
    report_src_dir: str | None,
    filename: str,
    content: str,
    fallback_rel_path: str,
) -> str:
    """Persist a generated blueprint JSON into `<report_src_dir>/_facts/<filename>` (or cache fallback)."""
    if report_src_dir:
        src_root = _resolve_safe_path(project_root, report_src_dir)
        if src_root is not None:
            dest = src_root / DEFAULT_REPORT_FACTS_SUBDIR / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            return dest.resolve().relative_to(project_root.resolve()).as_posix()

    fallback = _resolve_safe_path(project_root, fallback_rel_path)
    if fallback is not None:
        ensure_cache_parent(project_root, fallback)
        fallback.write_text(content, encoding="utf-8")
    return fallback_rel_path
