# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go type safety checker: empty `interface{}` / `any`, `unsafe.Pointer`, and unscoped `//nolint`."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTypingChecker
from pni._actions.ast_analyze.go._helpers import iter_go_callables
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    UnitTypingStats,
)

_UNSCOPED_NOLINT_RE: Final[re.Pattern[str]] = re.compile(r"//\s*nolint(?:\s*$|\s+//)")
_ANY_WORD_RE: Final[re.Pattern[str]] = re.compile(r"\bany\b|interface\s*\{\s*\}")


def _signature_uses_weak_any(callable_node: SgNode) -> list[str]:
    """Return list of parameter or result segments using untyped `any` or `interface{}`."""
    matches: list[str] = []
    params = callable_node.field("parameters")
    if params is not None and _ANY_WORD_RE.search(params.text()):
        matches.append("parameters")
    result = callable_node.field("result")
    if result is not None and _ANY_WORD_RE.search(result.text()):
        matches.append("return")
    return matches


class GoTypingChecker(BaseTypingChecker):
    """Evaluate Go type safety: `interface{}` / `any` signatures, `unsafe.Pointer`, and bare `//nolint`."""

    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect a Go compilation unit for `unsafe.Pointer`, `interface{}`/`any`, and unscoped `//nolint`."""
        callables = iter_go_callables(unit)
        total_callables = len(callables)
        safe_callables = 0
        issues: list[CodeLocation] = []
        weak_usages: list[CodeLocation] = []
        ignores: list[CodeLocation] = []

        for qual, _short, node in callables:
            weak_parts = _signature_uses_weak_any(node)
            if weak_parts:
                weak_usages.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=node.range().start.line + 1,
                        symbol=qual,
                        detail=f"Signature uses untyped `any` / `interface{{}}` in {', '.join(weak_parts)}",
                    )
                )
            else:
                safe_callables += 1

        for qtype in unit.root.find_all(kind="qualified_type"):
            if qtype.text().strip() == "unsafe.Pointer":
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=qtype.range().start.line + 1,
                        symbol="unsafe.Pointer",
                        detail="Use of `unsafe.Pointer` bypasses Go compile-time type and memory safety",
                    )
                )

        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            if fn is not None and fn.text().strip() == "unsafe.Pointer":
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol="unsafe.Pointer",
                        detail="Conversion to `unsafe.Pointer(...)` bypasses Go type safety",
                    )
                )

        for cnode in unit.root.find_all(kind="comment"):
            ctext = cnode.text().strip()
            if _UNSCOPED_NOLINT_RE.match(ctext):
                ignores.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=cnode.range().start.line + 1,
                        symbol="//nolint",
                        detail="Unscoped `//nolint` directive without analyzer name (e.g. `//nolint:errcheck`)",
                    )
                )

        return UnitTypingStats(
            total_callables=total_callables,
            type_safe_callables=safe_callables,
            type_safety_issues=issues,
            omitted_init_return_annotations=[],
            weak_type_usages=weak_usages,
            unscoped_type_ignores=ignores,
        )
