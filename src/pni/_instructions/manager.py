# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Cascade resolution and template management for AI agent instructions."""

from __future__ import annotations

import shutil
from pathlib import Path

from pni._instructions.base_model import InstructionInfo

BUILTIN_INSTRUCTIONS_DIR = Path(__file__).resolve().parent


def get_instructions_info(project_root: Path) -> InstructionInfo:
    """Retrieve agent instructions metadata and content, prioritizing local .pni overrides.

    Args:
        project_root: Target project directory.

    Returns:
        InstructionInfo: Resolved instruction metadata and markdown content.
    """
    local_candidates = [
        project_root / ".pni" / "instructions.md",
        project_root / ".pni" / "instruction.md",
    ]
    for candidate in local_candidates:
        if candidate.exists():
            return InstructionInfo(
                path=candidate,
                is_local=True,
                content=candidate.read_text(encoding="utf-8"),
            )

    builtin_agent = BUILTIN_INSTRUCTIONS_DIR / "agent.md"
    if builtin_agent.exists():
        return InstructionInfo(
            path=builtin_agent,
            is_local=False,
            content=builtin_agent.read_text(encoding="utf-8"),
        )

    return InstructionInfo(
        path=builtin_agent,
        is_local=False,
        content="# PNI Agent Instructions\nNo instructions found.",
    )


def get_instructions_content(project_root: Path) -> str:
    """Retrieve agent instructions markdown content.

    Args:
        project_root: Target project directory.

    Returns:
        str: Instructions markdown content.
    """
    return get_instructions_info(project_root).content


def copy_instruction_templates(project_root: Path, force: bool = False) -> list[Path]:
    """Copy default instruction file to .pni/instructions.md.

    Args:
        project_root: Target project directory.
        force: If True, overwrite existing local instructions.

    Returns:
        list[Path]: Created or overwritten file paths.
    """
    pni_dir = project_root / ".pni"
    pni_dir.mkdir(parents=True, exist_ok=True)

    builtin_instructions = BUILTIN_INSTRUCTIONS_DIR / "agent.md"
    dest_instructions = pni_dir / "instructions.md"

    created: list[Path] = []
    if builtin_instructions.exists() and (not dest_instructions.exists() or force):
        shutil.copy2(builtin_instructions, dest_instructions)
        created.append(dest_instructions)

    return created
