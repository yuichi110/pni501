# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript and JavaScript ES import ordering, namespace wildcard, and late require/import checker."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseImportChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    UnitImportStats,
)

_ALLOWED_NAMESPACE_IMPORTS: Final[frozenset[str]] = frozenset(
    {"React", "ReactDOM", "THREE", "d3", "z", "yup", "path", "fs", "os", "crypto", "http", "https", "url", "util"}
)


def _extract_import_source(imp_node: SgNode) -> str:
    """Return the unquoted module specifier string from an ES `import_statement`."""
    src_node = imp_node.field("source")
    if src_node is not None:
        return src_node.text().strip().strip("'\"")
    return ""


def _import_sort_group(specifier: str) -> int:
    """Classify import specifier into 0=node builtin, 1=external package, 2=internal alias, 3=relative."""
    if specifier.startswith("node:"):
        return 0
    if specifier.startswith(("@/", "~/", "#")):
        return 2
    if specifier.startswith("."):
        return 3
    return 1


def _is_top_level_require(call: SgNode) -> bool:
    """Return True if a `require(...)` call_expression is at module top level."""
    curr = call.parent()
    while curr is not None:
        if curr.kind() in {
            "function_declaration",
            "arrow_function",
            "function_expression",
            "method_definition",
        }:
            return False
        if curr.kind() == "program":
            return True
        curr = curr.parent()
    return False


def _inspect_require_calls(
    unit: ParsedUnit,
    has_es_imports: bool,
    unsorted: list[CodeLocation],
    late: list[CodeLocation],
) -> None:
    """Check `require(...)` calls for late function-level usage or mixed CJS/ESM usage."""
    for call in unit.root.find_all(kind="call_expression"):
        fn = call.field("function")
        if fn is None or fn.text().strip() != "require":
            continue
        if not _is_top_level_require(call):
            late.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=call.range().start.line + 1,
                    symbol="require",
                    detail="Late `require(...)` inside function/method body — move imports to module top-level",
                )
            )
        elif has_es_imports:
            unsorted.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=call.range().start.line + 1,
                    symbol="require",
                    detail="Mixed CommonJS `require(...)` and ES `import` in the same module",
                )
            )


class TsJsImportChecker(BaseImportChecker):
    """Evaluate ES `import` grouping/sorting, `import * as` wildcards, and non-top-level `require()` calls."""

    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Inspect a TypeScript or JavaScript unit for unsorted imports, wildcards, and late imports."""
        _ = root_packages
        unsorted: list[CodeLocation] = []
        wildcards: list[CodeLocation] = []
        late: list[CodeLocation] = []

        prev_spec = ""
        prev_group = -1
        prev_line = -1
        reported_unsorted = False

        for imp in unit.root.find_all(kind="import_statement"):
            line_no = imp.range().start.line + 1
            spec = _extract_import_source(imp)
            if not spec:
                continue

            imp_parent = imp.parent()
            if imp_parent is not None and imp_parent.kind() != "program":
                late.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=spec,
                        detail=f"Non-top-level import of '{spec}'",
                    )
                )
                continue

            ns_import = imp.find(kind="namespace_import")
            if ns_import is not None:
                alias_ident = ns_import.find(kind="identifier")
                alias_name = alias_ident.text().strip() if alias_ident is not None else "*"
                if alias_name not in _ALLOWED_NAMESPACE_IMPORTS and not spec.startswith("node:"):
                    wildcards.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=spec,
                            detail=f"Namespace wildcard `import * as {alias_name} from '{spec}'` inhibits tree-shaking",
                        )
                    )

            grp = _import_sort_group(spec)
            if (
                prev_line != -1
                and line_no == prev_line + 1
                and grp == prev_group
                and spec.lower() < prev_spec.lower()
                and not reported_unsorted
            ):
                unsorted.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=spec,
                        detail=f"Unsorted import '{spec}' after '{prev_spec}'",
                    )
                )
                reported_unsorted = True

            prev_spec = spec
            prev_group = grp
            prev_line = line_no

        _inspect_require_calls(unit, prev_line != -1, unsorted, late)
        is_clean = not unsorted and not wildcards and not late
        return UnitImportStats(
            is_clean=is_clean,
            unsorted_imports=unsorted,
            wildcard_imports=wildcards,
            late_imports=late,
        )
