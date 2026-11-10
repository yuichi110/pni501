# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript LOC, public symbol inventory, cognitive complexity, globals, and bug idioms."""

from __future__ import annotations

from typing import ClassVar

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseQualityChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit
from pni._actions.ast_analyze.ts_js._helpers import (
    extract_companion_dts_types,
    get_ts_js_params,
    iter_ts_js_callables,
    iter_ts_js_type_declarations,
)


def _enclosing_ts_js_callable_name(node: SgNode) -> str:
    """Return the enclosing function or method name for a CST node."""
    curr = node.parent()
    while curr is not None:
        kind = curr.kind()
        if kind in {"function_declaration", "generator_function_declaration", "method_definition"}:
            nm = curr.field("name")
            if nm is not None:
                return nm.text().strip()
        if kind == "variable_declarator":
            nm = curr.field("name")
            if nm is not None:
                return nm.text().strip()
        curr = curr.parent()
    return "<module>"


class TsJsQualityChecker(BaseQualityChecker):
    """Evaluate TypeScript/JavaScript LOC, exported symbols, complexity, mutable module state, and bug idioms."""

    branch_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "for_in_statement",
            "while_statement",
            "do_statement",
            "switch_case",
            "catch_clause",
            "ternary_expression",
        }
    )
    nesting_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "for_in_statement",
            "while_statement",
            "do_statement",
            "switch_statement",
            "catch_clause",
            "arrow_function",
            "function_expression",
        }
    )

    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment source lines in a TS/JS file."""
        count = 0
        in_block_comment = False
        for raw_line in unit.source.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if in_block_comment:
                if "*/" in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith("/*"):
                if "*/" not in stripped:
                    in_block_comment = True
                continue
            if stripped.startswith("//"):
                continue
            count += 1
        return count

    def count_classes(self, unit: ParsedUnit) -> int:
        """Count class, interface, type alias, and enum declarations in unit (plus companion .d.ts types)."""
        own_names = {tname for tname, _tkind, _is_exp, _node, _anchor in iter_ts_js_type_declarations(unit)}
        dts_names = set(extract_companion_dts_types(unit))
        return len(own_names | dts_names)

    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, SgNode]]:
        """Return `(qualified_name, fn_node)` for all functions and methods in unit."""
        return [(qual, fn_node) for qual, _short, _is_exp, fn_node, _anchor in iter_ts_js_callables(unit)]

    def count_callable_params(self, node: SgNode) -> int:
        """Count formal parameters on a TypeScript/JavaScript function or method."""
        return len(get_ts_js_params(node))

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Extract sorted `(exported_types, exported_callables)` for module_inventory."""
        pub_types = sorted(
            {tname for tname, _tkind, is_exp, _node, _anchor in iter_ts_js_type_declarations(unit) if is_exp}
            | set(extract_companion_dts_types(unit))
        )
        pub_fns = sorted(
            {qual for qual, _short, is_exp, _node, _anchor in iter_ts_js_callables(unit) if is_exp}
        )
        return pub_types, pub_fns

    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect mutable module-level `let` or `var` declarations."""
        findings: list[CodeLocation] = []
        for child in unit.root.children():
            target = child
            if child.kind() == "export_statement":
                decl = child.field("declaration")
                if decl is None:
                    continue
                target = decl
            if target.kind() not in {"lexical_declaration", "variable_declaration"}:
                continue
            text = target.text().lstrip()
            if not text.startswith(("let ", "var ")):
                continue
            for declarator in target.find_all(kind="variable_declarator"):
                if declarator.parent() != target:
                    continue
                nm = declarator.field("name")
                vname = nm.text().strip() if nm is not None else "<var>"
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=declarator.range().start.line + 1,
                        symbol=vname,
                        detail=f"Mutable module-level state `{'let' if text.startswith('let ') else 'var'} {vname}`",
                    )
                )
        return findings

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect loose equality (`==` / `!=`), empty `catch {}` blocks, and legacy `var` bindings."""
        idioms: list[CodeLocation] = []

        for bin_expr in unit.root.find_all(kind="binary_expression"):
            op_node = bin_expr.field("operator")
            if op_node is None:
                continue
            op_text = op_node.text().strip()
            if op_text not in {"==", "!="}:
                continue
            left = bin_expr.field("left")
            right = bin_expr.field("right")
            left_txt = left.text().strip() if left is not None else ""
            right_txt = right.text().strip() if right is not None else ""
            if left_txt in {"null", "undefined"} or right_txt in {"null", "undefined"}:
                continue
            strict_op = "===" if op_text == "==" else "!=="
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=bin_expr.range().start.line + 1,
                    symbol=_enclosing_ts_js_callable_name(bin_expr),
                    detail=f"Loose equality `{op_text}` performs coercive type juggling — use `{strict_op}`",
                )
            )

        for catch_node in unit.root.find_all(kind="catch_clause"):
            body = catch_node.field("body")
            if body is None:
                continue
            non_punct = [
                c
                for c in body.children()
                if c.kind() not in {"{", "}", "comment"}
            ]
            if not non_punct:
                idioms.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=catch_node.range().start.line + 1,
                        symbol=_enclosing_ts_js_callable_name(catch_node),
                        detail="Empty `catch` block silently swallows exceptions/rejected Promises",
                    )
                )

        for var_decl in unit.root.find_all(kind="variable_declaration"):
            if var_decl.text().lstrip().startswith("var "):
                idioms.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=var_decl.range().start.line + 1,
                        symbol=_enclosing_ts_js_callable_name(var_decl),
                        detail="Legacy function-scoped `var` declaration — use block-scoped `const` or `let`",
                    )
                )

        return idioms
