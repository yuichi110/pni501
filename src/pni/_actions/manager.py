# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Language-scoped cascade resolution and composite-to-primitive normalization for PNI actions."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import yaml

from pni._actions.base_model import (
    ActionInfo,
    CompositeActionDefinition,
    ParamValue,
    PrimitiveStep,
)
from pni._rules import detect_active_language

BUILTIN_ACTIONS_DIR = Path(__file__).resolve().parent


def _load_action_yaml(file_path: Path) -> CompositeActionDefinition | None:
    """Parse and validate a composite action YAML file into a Pydantic model."""
    if not file_path.exists():
        return None
    raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    return CompositeActionDefinition.model_validate(raw)


def _builtin_scope_dirs(active_lang: str, *, include_all: bool) -> list[tuple[str, Path]]:
    """Return ordered (scope_name, directory_path) pairs for built-in composite actions."""
    scopes: list[tuple[str, Path]] = []
    for scope_name in (active_lang, "common"):
        sdir = BUILTIN_ACTIONS_DIR / scope_name
        if sdir.is_dir():
            scopes.append((scope_name, sdir))

    if include_all:
        seen = {name for name, _ in scopes}
        for child in sorted(BUILTIN_ACTIONS_DIR.iterdir()):
            if (
                child.is_dir()
                and not child.name.startswith(("_", "."))
                and child.name not in seen
                and any(child.glob("*.yaml"))
            ):
                scopes.append((child.name, child))
    return scopes


def list_actions(
    project_root: Path,
    lang: Optional[str] = None,
    *,
    include_all: bool = False,
) -> list[ActionInfo]:
    """List available composite actions adhering to local > <lang> > common cascade resolution.

    Args:
        project_root: Target project root directory.
        lang: Target language scope (auto-detected if omitted).
        include_all: If True, include built-in actions from all language directories.

    Returns:
        list[ActionInfo]: Sorted list of available composite actions.
    """
    active_lang = lang or detect_active_language(project_root)
    local_actions_dir = project_root / ".pni" / "actions"
    resolved: dict[str, tuple[str, Path, bool]] = {}

    for scope_name, sdir in reversed(_builtin_scope_dirs(active_lang, include_all=include_all)):
        for f in sorted(sdir.glob("*.yaml")):
            key = f"{scope_name}/{f.stem}" if include_all and scope_name != "common" else f.stem
            resolved[key] = (scope_name, f, False)

    if local_actions_dir.is_dir():
        for f in sorted(local_actions_dir.glob("*.yaml")):
            existing_scope = resolved[f.stem][0] if f.stem in resolved else "local"
            resolved[f.stem] = (existing_scope, f, True)

    actions: list[ActionInfo] = []
    for key in sorted(resolved):
        scope_name, target_file, is_local = resolved[key]
        parsed = _load_action_yaml(target_file)
        if parsed is not None:
            actions.append(
                ActionInfo(
                    id=parsed.id,
                    scope=scope_name,
                    name=parsed.name,
                    description=parsed.description,
                    path=target_file,
                    is_local=is_local,
                )
            )
    return actions


def load_composite_action(
    action_id: str,
    project_root: Path,
    lang: Optional[str] = None,
) -> CompositeActionDefinition | None:
    """Load a composite action definition by id, prioritizing .pni/actions/ > <lang> > common.

    Args:
        action_id: Action identifier (e.g. 'python_ast_audit', 'java_ast_audit', or 'java/repo_structure_audit').
        project_root: Target project root directory.
        lang: Target language scope (auto-detected if omitted).

    Returns:
        CompositeActionDefinition | None: Validated Pydantic model if found.
    """
    clean_id = action_id.removesuffix(".yaml").strip()
    if "/" in clean_id:
        scope_part, stem_part = clean_id.split("/", maxsplit=1)
        scoped_local = project_root / ".pni" / "actions" / scope_part / f"{stem_part}.yaml"
        if scoped_local.is_file():
            return _load_action_yaml(scoped_local)
        scoped_builtin = BUILTIN_ACTIONS_DIR / scope_part / f"{stem_part}.yaml"
        return _load_action_yaml(scoped_builtin)

    local_file = project_root / ".pni" / "actions" / f"{clean_id}.yaml"
    if local_file.is_file():
        return _load_action_yaml(local_file)

    active_lang = lang or detect_active_language(project_root)
    for _, sdir in _builtin_scope_dirs(active_lang, include_all=True):
        candidate = sdir / f"{clean_id}.yaml"
        if candidate.is_file():
            return _load_action_yaml(candidate)

    return None


def expand_composite_action(
    step_id: str,
    step_name: str,
    action_id: str,
    project_root: Path,
    override_rules: Optional[list[str]] = None,
    override_params: Optional[dict[str, ParamValue]] = None,
    override_prompt: str = "",
    lang: Optional[str] = None,
) -> list[PrimitiveStep]:
    """Expand a composite action definition into internal PrimitiveStep instances.

    Args:
        step_id: Parent workflow step identifier.
        step_name: Parent workflow step display name.
        action_id: Composite action identifier referenced by 'uses'.
        project_root: Target project root directory.
        override_rules: Optional additional or overriding rules from the workflow step.
        override_params: Optional parameter overrides from the workflow step 'with' block.
        override_prompt: Optional additional prompt instructions from the workflow step.
        lang: Optional target language scope for resolving language-specific composite actions.

    Returns:
        list[PrimitiveStep]: Normalized sequence of internal primitive steps.
    """
    comp = load_composite_action(action_id, project_root, lang=lang)
    if comp is None:
        return []

    base_rules = list(dict.fromkeys([*comp.rules, *(override_rules or [])]))
    expanded: list[PrimitiveStep] = []

    for idx, prim in enumerate(comp.primitives, start=1):
        merged_rules = list(dict.fromkeys([*base_rules, *prim.rules]))
        merged_params: dict[str, ParamValue] = {**prim.with_params, **(override_params or {})}
        combined_prompt = prim.prompt.strip()
        if override_prompt.strip():
            combined_prompt = f"{combined_prompt}\n\n{override_prompt.strip()}".strip()

        prim_name = prim.name or f"{step_name} ({prim.type.value})"
        expanded.append(
            PrimitiveStep(
                id=f"{step_id}__{idx}_{prim.type.value}",
                name=prim_name,
                type=prim.type,
                rules=merged_rules,
                params=merged_params,
                prompt=combined_prompt,
                source_action=comp.id,
            )
        )

    return expanded


def copy_action_templates(
    project_root: Path,
    lang: Optional[str] = None,
    force: bool = False,
) -> list[Path]:
    """Copy built-in common and active-language composite action YAML templates to .pni/actions/.

    Args:
        project_root: Target project directory.
        lang: Target programming language (auto-detected if omitted).
        force: If True, overwrite existing files.

    Returns:
        list[Path]: Created or overwritten file paths.
    """
    target_lang = lang or detect_active_language(project_root)
    dest_dir = project_root / ".pni" / "actions"
    dest_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for scope_name in ("common", target_lang):
        src_dir = BUILTIN_ACTIONS_DIR / scope_name
        if not src_dir.is_dir():
            continue
        for f in sorted(src_dir.glob("*.yaml")):
            dest_file = dest_dir / f.name
            if not dest_file.exists() or force:
                shutil.copy2(f, dest_file)
                created.append(dest_file)

    return created
