# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Cascade resolution and target-scoped .pni/dockerfiles/ management."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from pni._cache import default_target_dockerfile_rel_path

BUILTIN_DOCKERFILES_DIR: Final[Path] = Path(__file__).resolve().parent
DOCKERFILES_REL_DIR: Final[str] = ".pni/dockerfiles"

_DEFAULT_DOCKERIGNORE_CONTENT: Final[str] = """# Created by pni automatically for isolated build context hygiene.
.git
.pni
.drawlib
.venv
venv
__pycache__
.pytest_cache
.ruff_cache
.mypy_cache
node_modules
vendor
reports
reports_src
target
build
.gradle
"""

_FALLBACK_TOOL_BY_LANG: Final[dict[str, str]] = {
    "python": "pip",
    "java": "maven",
    "php": "composer",
}


def list_builtin_dockerfiles() -> list[str]:
    """Return sorted relative identifiers (e.g. 'python/uv.dockerfile') of built-in templates."""
    items: list[str] = []
    for child in sorted(BUILTIN_DOCKERFILES_DIR.iterdir()):
        if not child.is_dir() or child.name.startswith(("_", ".")):
            continue
        for df in sorted(child.glob("*.dockerfile")):
            items.append(f"{child.name}/{df.name}")
    return items


def resolve_template_dockerfile(workspace_root: Path, lang: str, tool: str) -> tuple[Path, str]:
    """Resolve a template .dockerfile prioritizing .pni/dockerfiles/_templates/<lang>/<tool>.dockerfile.

    Args:
        workspace_root: Workspace root directory.
        lang: Target language ('python', 'java', 'php').
        tool: Build tool identifier ('uv', 'poetry', 'pip', 'maven', 'gradle', 'composer', 'raw').

    Returns:
        tuple[Path, str]: Resolved template path and logical template identifier.

    Raises:
        FileNotFoundError: If neither requested nor fallback template exists for the language.
    """
    clean_lang = lang.strip().lower()
    clean_tool = tool.strip().lower().removesuffix(".dockerfile")

    local_candidate = workspace_root / DOCKERFILES_REL_DIR / "_templates" / clean_lang / f"{clean_tool}.dockerfile"
    if local_candidate.is_file():
        return local_candidate, f"local:{clean_lang}/{clean_tool}.dockerfile"

    builtin_candidate = BUILTIN_DOCKERFILES_DIR / clean_lang / f"{clean_tool}.dockerfile"
    if builtin_candidate.is_file():
        return builtin_candidate, f"{clean_lang}/{clean_tool}.dockerfile"

    fallback_tool = _FALLBACK_TOOL_BY_LANG.get(clean_lang)
    if fallback_tool is not None:
        fallback_path = BUILTIN_DOCKERFILES_DIR / clean_lang / f"{fallback_tool}.dockerfile"
        if fallback_path.is_file():
            return fallback_path, f"{clean_lang}/{fallback_tool}.dockerfile"

    msg = f"No built-in or local harness dockerfile found for lang={lang!r}, tool={tool!r}"
    raise FileNotFoundError(msg)


def ensure_target_dockerfile(
    workspace_root: Path,
    target_root: str,
    lang: str,
    tool: str,
    *,
    explicit_dockerfile: str = "",
    force_regenerate: bool = False,
) -> tuple[Path, str]:
    """Materialize or reuse the target-scoped harness Dockerfile in .pni/dockerfiles/.

    Args:
        workspace_root: Workspace root directory.
        target_root: Workflow targets.root relative to workspace_root (e.g. '.' or 'examples/python/lib_clean').
        lang: Target language ('python', 'java', 'php').
        tool: Build tool identifier ('uv', 'poetry', 'pip', 'maven', 'gradle', 'composer', 'raw').
        explicit_dockerfile: Optional explicit Dockerfile path relative to workspace_root.
        force_regenerate: If True, overwrite existing harness Dockerfile from template.

    Returns:
        tuple[Path, str]: Materialized Dockerfile path and logical template identifier.

    Raises:
        FileNotFoundError: If an explicit_dockerfile was specified and does not exist.
    """
    if explicit_dockerfile.strip():
        ws_resolved = workspace_root.resolve()
        custom_path = (ws_resolved / explicit_dockerfile.strip()).resolve()
        if not custom_path.is_relative_to(ws_resolved):
            msg = f"Explicit dockerfile must stay within workspace: {explicit_dockerfile!r}"
            raise ValueError(msg)
        if not custom_path.is_file():
            msg = f"Explicit dockerfile does not exist: {explicit_dockerfile!r}"
            raise FileNotFoundError(msg)
        return custom_path, f"custom:{explicit_dockerfile.strip()}"

    template_path, template_id = resolve_template_dockerfile(workspace_root, lang, tool)
    dest_rel = default_target_dockerfile_rel_path(target_root)
    dest_file = workspace_root / dest_rel
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    if not dest_file.is_file() or force_regenerate:
        shutil.copy2(template_path, dest_file)

    dockerignore_sidecar = dest_file.parent / f"{dest_file.name}.dockerignore"
    if not dockerignore_sidecar.is_file() or force_regenerate:
        dockerignore_sidecar.write_text(_DEFAULT_DOCKERIGNORE_CONTENT, encoding="utf-8")

    return dest_file, template_id
