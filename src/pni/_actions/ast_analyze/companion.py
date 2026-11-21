# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Polyglot companion scanner running Tier C Tree-sitter suites (Dockerfile, HCL, Protobuf, YAML, SQL, etc.)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pni._actions.ast_analyze.declarative import DECLARATIVE_SUITES
from pni._actions.ast_analyze.models import AstFacts
from pni._languages import list_supported_languages

DEFAULT_COMPANION_LANGUAGES: Final[tuple[str, ...]] = list_supported_languages(tier="companion_dsl")


def scan_companion_languages(
    project_root: Path,
    *,
    languages: Sequence[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> dict[str, AstFacts]:
    """Scan companion IaC/schema/config files present in project_root using Tier C Tree-sitter suites.

    Args:
        project_root: Target repository root directory.
        languages: Optional subset of companion language IDs to scan (defaults to all 15 Tier C languages).
        exclude_globs: Optional glob patterns to exclude from file discovery.

    Returns:
        dict[str, AstFacts]: Mapping of companion language_id -> AstFacts for languages with >= 1 file found.
    """
    selected = tuple(languages) if languages is not None else DEFAULT_COMPANION_LANGUAGES
    results: dict[str, AstFacts] = {}
    for lang_id in selected:
        suite = DECLARATIVE_SUITES.get(lang_id)
        if suite is None:
            continue
        facts = suite.analyze(
            project_root,
            targets=["."],
            display_root=project_root,
            detected_frameworks=[],
            declared_lang_version="",
            exclude_globs=exclude_globs or [],
        )
        if facts.total_files > 0:
            results[lang_id] = facts
    return results
