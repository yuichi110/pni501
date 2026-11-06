# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java import hygiene AST checker (wildcard imports, static/normal separation, ASCII sort)."""

from __future__ import annotations

from dataclasses import dataclass

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseImportChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitImportStats


@dataclass(frozen=True)
class _JavaImportEntry:
    """Parsed metadata for a single Java import_declaration node."""

    start_line: int
    end_line: int
    is_static: bool
    is_wildcard: bool
    target: str


def _parse_java_import(node: SgNode) -> _JavaImportEntry:
    """Extract target FQN, static modifier, and wildcard flag from a Java import node."""
    raw = node.text().removeprefix("import").strip().removesuffix(";").strip()
    is_static = raw.startswith("static ")
    target = raw.removeprefix("static ").strip()
    return _JavaImportEntry(
        start_line=node.range().start.line + 1,
        end_line=node.range().end.line + 1,
        is_static=is_static,
        is_wildcard=target.endswith(".*"),
        target=target,
    )


def _check_java_import_order(entries: list[_JavaImportEntry], rel_path: str) -> list[CodeLocation]:
    """Verify static/non-static separation and lexicographical ordering within contiguous blocks."""
    unsorted: list[CodeLocation] = []
    seen_static_block = False
    seen_normal_block = False

    for idx, entry in enumerate(entries):
        if idx == 0:
            seen_static_block = entry.is_static
            seen_normal_block = not entry.is_static
            continue

        prev = entries[idx - 1]
        is_new_paragraph = entry.start_line - prev.end_line > 1

        if entry.is_static != prev.is_static:
            if not is_new_paragraph:
                unsorted.append(
                    CodeLocation(
                        file=rel_path,
                        line=entry.start_line,
                        symbol=entry.target,
                        detail="Missing blank line between static and non-static imports",
                    )
                )
            if (entry.is_static and seen_static_block) or (not entry.is_static and seen_normal_block):
                unsorted.append(
                    CodeLocation(
                        file=rel_path,
                        line=entry.start_line,
                        symbol=entry.target,
                        detail="Interleaved static and non-static import blocks",
                    )
                )
            seen_static_block = seen_static_block or entry.is_static
            seen_normal_block = seen_normal_block or (not entry.is_static)
            continue

        if not is_new_paragraph and entry.target < prev.target:
            unsorted.append(
                CodeLocation(
                    file=rel_path,
                    line=entry.start_line,
                    symbol=entry.target,
                    detail=f"Unsorted Java import '{entry.target}' after '{prev.target}'",
                )
            )
    return unsorted


class JavaImportChecker(BaseImportChecker):
    """Check Java import declarations for star imports, block separation, and alphabetical order."""

    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Inspect a Java compilation unit for wildcard imports and unsorted import blocks."""
        _ = root_packages
        entries = [_parse_java_import(n) for n in unit.root.find_all(kind="import_declaration")]
        wildcards = [
            CodeLocation(
                file=unit.rel_path,
                line=e.start_line,
                symbol=e.target,
                detail=f"Wildcard import 'import {'static ' if e.is_static else ''}{e.target};'",
            )
            for e in entries
            if e.is_wildcard
        ]
        unsorted = _check_java_import_order(entries, unit.rel_path)
        return UnitImportStats(
            is_clean=not unsorted and not wildcards,
            unsorted_imports=unsorted,
            wildcard_imports=wildcards,
        )
