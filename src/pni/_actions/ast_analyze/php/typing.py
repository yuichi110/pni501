# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP `declare(strict_types=1)`, parameter/return type hint, `mixed`, and ignore checker."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTypingChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitTypingStats
from pni._actions.ast_analyze.php._helpers import (
    NON_TYPE_PARAM_CHILD_KINDS,
    extract_formal_param_nodes,
    extract_node_name,
    iter_php_callables,
)

_NO_RETURN_MAGIC_METHODS: Final[frozenset[str]] = frozenset({"__construct", "__destruct", "__clone"})
_UNSCOPED_IGNORE_RE: Final[re.Pattern[str]] = re.compile(
    r"@(?:phpstan-ignore-next-line|phpstan-ignore-line|psalm-suppress\b(?![^\n]*--))"
)


def _has_strict_types_declaration(root: SgNode) -> bool:
    """Return True if unit declares `declare(strict_types=1);`."""
    for decl in root.find_all(kind="declare_statement"):
        compact = re.sub(r"\s+", "", decl.text())
        if "strict_types=1" in compact:
            return True
    return False


def _param_type_text(param_node: SgNode) -> str:
    """Return the type annotation text of a PHP parameter node, or empty string if untyped."""
    for child in param_node.children():
        ckind = child.kind()
        if ckind == "variable_name":
            break
        if ckind not in NON_TYPE_PARAM_CHILD_KINDS:
            return child.text().strip()
    return ""


def _return_type_text(callable_node: SgNode) -> str:
    """Return the return type annotation text of a PHP callable node, or empty string if untyped."""
    saw_colon = False
    for child in callable_node.children():
        ckind = child.kind()
        if ckind == ":":
            saw_colon = True
            continue
        if saw_colon and ckind not in {"compound_statement", ";"}:
            return child.text().strip()
    return ""


class PhpTypingChecker(BaseTypingChecker):
    """Evaluate `declare(strict_types=1)`, parameter/return type hints, `mixed` usage, and ignores."""

    def _inspect_callable_typing(
        self,
        unit: ParsedUnit,
        symbol: str,
        cnode: SgNode,
        *,
        has_strict: bool,
        issues: list[CodeLocation],
        weak_usages: list[CodeLocation],
    ) -> bool:
        """Inspect a single PHP callable and return True if fully typed under strict_types."""
        line = cnode.range().start.line + 1
        untyped_params: list[str] = []
        for pnode in extract_formal_param_nodes(cnode):
            var_node = pnode.find(kind="variable_name")
            pname = var_node.text().strip() if var_node is not None else "<param>"
            ptype = _param_type_text(pnode)
            if not ptype:
                untyped_params.append(pname)
            elif ptype == "mixed":
                weak_usages.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=pnode.range().start.line + 1,
                        symbol=symbol,
                        detail=f"Weak 'mixed' type on parameter '{pname}'",
                    )
                )

        needs_return = extract_node_name(cnode).lower() not in _NO_RETURN_MAGIC_METHODS
        rtype = _return_type_text(cnode)
        missing_return = needs_return and not rtype
        if rtype == "mixed":
            weak_usages.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line,
                    symbol=symbol,
                    detail="Weak 'mixed' return type declaration",
                )
            )

        if not untyped_params and not missing_return and has_strict:
            return True
        if untyped_params or missing_return:
            parts: list[str] = []
            if untyped_params:
                parts.append(f"untyped params: {', '.join(untyped_params)}")
            if missing_return:
                parts.append("missing return type")
            issues.append(CodeLocation(file=unit.rel_path, line=line, symbol=symbol, detail="; ".join(parts)))
        return False

    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect a PHP file for strict_types, callable type completeness, weak `mixed`, and ignores."""
        issues: list[CodeLocation] = []
        weak_usages: list[CodeLocation] = []
        ignores: list[CodeLocation] = []

        has_strict = _has_strict_types_declaration(unit.root)
        if not has_strict:
            issues.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=1,
                    symbol=unit.file_path.name,
                    detail="Missing 'declare(strict_types=1);' at file entry (allows silent scalar coercion)",
                )
            )

        callables = iter_php_callables(unit.root)
        total_callables = len(callables)
        safe_callables = sum(
            1
            for symbol, cnode in callables
            if self._inspect_callable_typing(
                unit,
                symbol,
                cnode,
                has_strict=has_strict,
                issues=issues,
                weak_usages=weak_usages,
            )
        )

        # If a raw procedural PHP script has zero functions/classes and no strict_types, count script unit
        if total_callables == 0 and not has_strict:
            total_callables = 1
            safe_callables = 0

        for idx, raw_line in enumerate(unit.source.splitlines(), start=1):
            match = _UNSCOPED_IGNORE_RE.search(raw_line)
            if match:
                ignores.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=idx,
                        symbol=match.group(0).strip(),
                        detail="Unscoped static-analysis suppression without inline justification",
                    )
                )

        return UnitTypingStats(
            total_callables=total_callables,
            type_safe_callables=safe_callables,
            type_safety_issues=issues,
            weak_type_usages=weak_usages,
            unscoped_type_ignores=ignores,
        )
