# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go import ordering and dot-import (wildcard) AST checker."""

from __future__ import annotations

from pathlib import Path

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseImportChecker
from pni._actions.ast_analyze.go._helpers import parse_go_module_info
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    UnitImportStats,
)


def _extract_import_spec_info(spec: SgNode) -> tuple[str, bool, int]:
    """Return `(import_path, is_dot_import, line_1based)` from a Go `import_spec` node."""
    path_node = spec.field("path")
    imp_path = path_node.text().strip().strip('"`') if path_node is not None else ""
    name_node = spec.field("name")
    is_dot = False
    if name_node is not None and name_node.text().strip() == ".":
        is_dot = True
    elif any(c.kind() == "dot" or c.text().strip() == "." for c in spec.children()):
        is_dot = True
    return imp_path, is_dot, spec.range().start.line + 1


class GoImportChecker(BaseImportChecker):
    """Evaluate Go `import` grouping, alphabetical sorting within groups, and dot-imports."""

    def discover_root_packages(self, units: list[ParsedUnit], project_root: Path) -> set[str]:
        """Return the declared module path from `go.mod` if present."""
        _ = units
        mod_path, _ = parse_go_module_info(project_root)
        return {mod_path} if mod_path else set()

    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Inspect a Go compilation unit for dot imports and unsorted import groups."""
        _ = root_packages
        unsorted: list[CodeLocation] = []
        wildcards: list[CodeLocation] = []

        for decl in unit.root.find_all(kind="import_declaration"):
            specs = list(decl.find_all(kind="import_spec"))
            prev_path = ""
            prev_line = -1
            reported_decl = False
            for spec in specs:
                imp_path, is_dot, line_no = _extract_import_spec_info(spec)
                if not imp_path:
                    continue
                if is_dot:
                    wildcards.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=imp_path,
                            detail=f"Dot import `import . \"{imp_path}\"` pollutes package namespace",
                        )
                    )
                if prev_line != -1 and line_no == prev_line + 1:
                    if imp_path < prev_path and not reported_decl:
                        unsorted.append(
                            CodeLocation(
                                file=unit.rel_path,
                                line=line_no,
                                symbol=imp_path,
                                detail=f"Unsorted Go import '{imp_path}' after '{prev_path}' (run goimports/gofmt)",
                            )
                        )
                        reported_decl = True
                prev_path = imp_path
                prev_line = line_no

        is_clean = not unsorted and not wildcards
        return UnitImportStats(
            is_clean=is_clean,
            unsorted_imports=unsorted,
            wildcard_imports=wildcards,
            late_imports=[],
        )
