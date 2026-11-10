# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go LOC, exported symbol inventory, cognitive complexity, package-level var state, and bug-risk idioms."""

from __future__ import annotations

import re
from typing import ClassVar, Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseQualityChecker
from pni._actions.ast_analyze.go._helpers import (
    extract_package_name,
    extract_receiver_type_name,
    get_go_callable_params,
    is_exported_go_name,
    iter_go_callables,
    iter_go_type_specs,
)
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_SAFE_GLOBAL_TYPE_PREFIXES: Final[tuple[str, ...]] = (
    "sync.Mutex",
    "sync.RWMutex",
    "sync.Once",
    "sync.WaitGroup",
    "sync.Pool",
    "sync.Map",
    "atomic.",
    "*regexp.Regexp",
    "embed.FS",
)
_SAFE_GLOBAL_CALL_PREFIXES: Final[tuple[str, ...]] = (
    "errors.New(",
    "fmt.Errorf(",
    "regexp.MustCompile(",
    "prometheus.",
    "promauto.",
    " slog.",
    "zap.",
    "zerolog.",
)
_SAFE_BLANK_CALL_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:fmt\.Fprint|fmt\.Print|os\.Stdout\.|os\.Stderr\.| strconv\.|\w+\.WriteString\()"
)


def _enclosing_callable_name(node: SgNode) -> str:
    """Return the enclosing Go function or method name for a CST node."""
    curr = node.parent()
    while curr is not None:
        if curr.kind() == "function_declaration":
            nm = curr.field("name")
            return nm.text().strip() if nm is not None else "<func>"
        if curr.kind() == "method_declaration":
            nm = curr.field("name")
            recv = extract_receiver_type_name(curr)
            short = nm.text().strip() if nm is not None else "<method>"
            return f"{recv}.{short}" if recv else short
        curr = curr.parent()
    return "<package>"


def _is_inside_for_loop(node: SgNode) -> bool:
    """Return True if node is inside a `for_statement` without an intervening `func_literal`."""
    curr = node.parent()
    while curr is not None:
        kind = curr.kind()
        if kind in {"func_literal", "function_declaration", "method_declaration"}:
            return False
        if kind == "for_statement":
            return True
        curr = curr.parent()
    return False


def _find_blank_error_discards(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect `_ = call()` or `x, _ = call()` assignments discarding returned error/values."""
    idioms: list[CodeLocation] = []
    for assign in unit.root.find_all(kind="assignment_statement"):
        left = assign.field("left")
        right = assign.field("right")
        if left is None or right is None:
            continue
        left_items = [s.strip() for s in left.text().split(",")]
        if not left_items or left_items[-1] != "_":
            continue
        call_node = right.find(kind="call_expression")
        if call_node is None:
            continue
        call_text = call_node.text().strip()
        if _SAFE_BLANK_CALL_RE.match(call_text):
            continue
        idioms.append(
            CodeLocation(
                file=unit.rel_path,
                line=assign.range().start.line + 1,
                symbol=_enclosing_callable_name(assign),
                detail=f"Blank identifier discards returned value/error from `{call_text.split('(', 1)[0]}(...)`",
            )
        )
    return idioms


class GoQualityChecker(BaseQualityChecker):
    """Evaluate Go code size, exported symbols, complexity, mutable package vars, and bug-risk idioms."""

    branch_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "expression_switch_statement",
            "type_switch_statement",
            "select_statement",
            "expression_case",
            "type_case",
            "communication_case",
        }
    )
    nesting_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "expression_switch_statement",
            "type_switch_statement",
            "select_statement",
            "func_literal",
        }
    )

    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment source lines in a Go file."""
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
        """Count top-level struct, interface, and named type definitions in unit."""
        return len(iter_go_type_specs(unit))

    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, SgNode]]:
        """Return `(symbol_name, node)` for all top-level functions and methods in unit."""
        return [(qual, node) for qual, _short, node in iter_go_callables(unit)]

    def count_callable_params(self, node: SgNode) -> int:
        """Count parameters on a Go function or method declaration."""
        return len(get_go_callable_params(node))

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Return sorted `(exported_types, exported_callables)` in unit."""
        pub_types = sorted(
            {tname for tname, _tkind, _spec, _decl in iter_go_type_specs(unit) if is_exported_go_name(tname)}
        )
        pub_fns: set[str] = set()
        for qual, short, node in iter_go_callables(unit):
            if not is_exported_go_name(short):
                continue
            if node.kind() == "method_declaration":
                recv = extract_receiver_type_name(node)
                if recv and not is_exported_go_name(recv):
                    continue
            pub_fns.add(qual)
        return pub_types, sorted(pub_fns)

    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect mutable package-level `var` declarations (excluding sentinel `Err*`, `sync.*`, and `_`)."""
        findings: list[CodeLocation] = []
        for child in unit.root.children():
            if child.kind() != "var_declaration":
                continue
            for spec in child.find_all(kind="var_spec"):
                name_node = spec.field("name")
                if name_node is None:
                    continue
                vname = name_node.text().strip()
                if vname == "_" or vname.startswith(("Err", "err")):
                    continue
                spec_text = spec.text().strip()
                type_node = spec.field("type")
                type_text = type_node.text().strip() if type_node is not None else ""
                if type_text.startswith(_SAFE_GLOBAL_TYPE_PREFIXES):
                    continue
                if any(tok in spec_text for tok in _SAFE_GLOBAL_CALL_PREFIXES):
                    continue
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=spec.range().start.line + 1,
                        symbol=vname,
                        detail=f"Mutable package-level variable '{vname}'",
                    )
                )
        return findings

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect ignored errors (`_ = call()`), `panic(...)` in non-main packages, and `defer` inside loops."""
        idioms = _find_blank_error_discards(unit)
        pkg_name = extract_package_name(unit)

        if pkg_name != "main":
            for call in unit.root.find_all(kind="call_expression"):
                fn_node = call.field("function")
                if fn_node is None or fn_node.text().strip() != "panic":
                    continue
                enclosing = _enclosing_callable_name(call)
                short_fn = enclosing.rsplit(".", 1)[-1]
                if short_fn.startswith("Must") or short_fn == "init":
                    continue
                idioms.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=enclosing,
                        detail="Uncaught `panic(...)` in non-main package — return an explicit `error` instead",
                    )
                )

        for defer_stmt in unit.root.find_all(kind="defer_statement"):
            if _is_inside_for_loop(defer_stmt):
                idioms.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=defer_stmt.range().start.line + 1,
                        symbol=_enclosing_callable_name(defer_stmt),
                        detail="`defer` inside `for` loop delays resource cleanup until function exit",
                    )
                )

        return idioms
