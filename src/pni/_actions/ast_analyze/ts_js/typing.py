# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript type safety checker (TS annotations/any/@ts-ignore & JSDoc @param/@returns)."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTypingChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    UnitTypingStats,
)
from pni._actions.ast_analyze.ts_js._helpers import (
    extract_preceding_jsdoc,
    find_companion_dts_files,
    get_ts_js_params,
    has_ts_return_type,
    iter_ts_js_callables,
    parse_jsdoc_block,
)

_TS_IGNORE_RE: Final[re.Pattern[str]] = re.compile(
    r"@ts-(?:ignore|nocheck)\b|@ts-expect-error(?:\s*$|\s+\*/)"
)
_ESLINT_UNSCOPED_RE: Final[re.Pattern[str]] = re.compile(
    r"eslint-disable(?:-next-line|-line)?\s*(?:\*/|$)"
)
_TS_CHECK_HEADER_RE: Final[re.Pattern[str]] = re.compile(r"//\s*@ts-check\b")


def _inspect_ts_callable(
    qual: str,
    short: str,
    fn_node: SgNode,
    rel_path: str,
) -> tuple[bool, list[CodeLocation]]:
    """Verify parameter and return type annotations on a TypeScript callable."""
    issues: list[CodeLocation] = []
    params = get_ts_js_params(fn_node)
    untyped_params = [pname for pname, has_type, _ttxt in params if not has_type]
    has_ret, _ret_txt = has_ts_return_type(fn_node)
    if short == "constructor":
        has_ret = True

    line_no = fn_node.range().start.line + 1
    if untyped_params:
        issues.append(
            CodeLocation(
                file=rel_path,
                line=line_no,
                symbol=qual,
                detail=f"Missing TypeScript type annotation for parameter(s): {', '.join(untyped_params)}",
            )
        )
    if not has_ret:
        issues.append(
            CodeLocation(
                file=rel_path,
                line=line_no,
                symbol=qual,
                detail=f"Missing explicit return type annotation on '{qual}'",
            )
        )
    return (not issues), issues


def _inspect_js_callable(
    qual: str,
    short: str,
    is_exp: bool,
    fn_node: SgNode,
    anchor_node: SgNode,
    rel_path: str,
    has_companion_dts: bool,
) -> tuple[bool, list[CodeLocation], list[CodeLocation]]:
    """Verify JSDoc `@param {Type}` / `@returns {Type}` or `.d.ts` contract on a JavaScript callable."""
    if has_companion_dts:
        return True, [], []
    params = get_ts_js_params(fn_node)
    raw_jsdoc = extract_preceding_jsdoc(anchor_node)
    line_no = fn_node.range().start.line + 1
    issues: list[CodeLocation] = []
    weak: list[CodeLocation] = []

    if raw_jsdoc is None:
        if is_exp:
            issues.append(
                CodeLocation(
                    file=rel_path,
                    line=line_no,
                    symbol=qual,
                    detail=f"Exported JavaScript callable '{qual}' lacks JSDoc `@param`/`@returns` type annotations",
                )
            )
            return False, issues, weak
        return True, [], []

    _summary, param_types, ret_type, has_type_tag = parse_jsdoc_block(raw_jsdoc)
    if has_type_tag:
        return True, [], []

    untyped_params = [pname for pname, _ht, _tt in params if not param_types.get(pname)]
    if untyped_params and is_exp:
        issues.append(
            CodeLocation(
                file=rel_path,
                line=line_no,
                symbol=qual,
                detail=f"Missing JSDoc `@param {{Type}}` for parameter(s): {', '.join(untyped_params)}",
            )
        )

    for pname, ptype in param_types.items():
        if ptype in {"*", "any", "Object", "Function"}:
            weak.append(
                CodeLocation(
                    file=rel_path,
                    line=line_no,
                    symbol=qual,
                    detail=f"Weak JSDoc `@param {{{ptype}}} {pname}` — specify a concrete type or `@typedef`",
                )
            )
    if ret_type in {"*", "any"}:
        weak.append(
            CodeLocation(
                file=rel_path,
                line=line_no,
                symbol=qual,
                detail=f"Weak JSDoc `@returns {{{ret_type}}}` — specify a concrete return type",
            )
        )

    is_safe = not issues and (bool(param_types) or ret_type is not None or not params or short == "constructor")
    return is_safe, issues, weak


def _collect_ts_js_unscoped_ignores(unit: ParsedUnit) -> list[CodeLocation]:
    """Collect unscoped `@ts-ignore`, `@ts-expect-error`, and `eslint-disable` comments."""
    ignores: list[CodeLocation] = []
    for cnode in unit.root.find_all(kind="comment"):
        ctext = cnode.text().strip()
        if _TS_IGNORE_RE.search(ctext):
            ignores.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=cnode.range().start.line + 1,
                    symbol="@ts-ignore",
                    detail=f"Unscoped TypeScript suppression `{ctext[:40]}`",
                )
            )
        elif _ESLINT_UNSCOPED_RE.search(ctext):
            ignores.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=cnode.range().start.line + 1,
                    symbol="eslint-disable",
                    detail="Unscoped `eslint-disable` without specific rule name",
                )
            )
    return ignores


class TsJsTypingChecker(BaseTypingChecker):
    """Evaluate static typing in TypeScript (`: any`, `@ts-ignore`) and JavaScript (JSDoc `@param`/`@returns`)."""

    def __init__(self, *, language: str = "typescript") -> None:
        """Initialize the checker for `'typescript'` or `'javascript'` mode."""
        self.language = language.lower()

    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect a TS or JS unit for type coverage, weak `any` usages, and unscoped suppressions."""
        is_ts_file = self.language == "typescript" or unit.file_path.suffix.lower() in {".ts", ".tsx"}
        callables = iter_ts_js_callables(unit)
        total_callables = len(callables)
        safe_callables = 0
        issues: list[CodeLocation] = []
        weak_usages: list[CodeLocation] = []

        has_ts_check = bool(_TS_CHECK_HEADER_RE.search(unit.source[:500]))
        dts_files = find_companion_dts_files(unit.file_path)
        dts_idents: set[str] = set()
        for dts_path in dts_files:
            try:
                dts_idents.update(re.findall(r"\b[A-Za-z_$][\w$]*\b", dts_path.read_text(encoding="utf-8")))
            except OSError:
                continue

        for qual, short, is_exp, fn_node, anchor_node in callables:
            if is_ts_file:
                is_safe, fn_issues = _inspect_ts_callable(qual, short, fn_node, unit.rel_path)
                issues.extend(fn_issues)
                if is_safe:
                    safe_callables += 1
            else:
                owner = qual.split(".", 1)[0]
                covered_by_dts = has_ts_check or (
                    bool(dts_files) and (not dts_idents or short in dts_idents or owner in dts_idents)
                )
                is_safe, fn_issues, fn_weak = _inspect_js_callable(
                    qual, short, is_exp, fn_node, anchor_node, unit.rel_path, covered_by_dts
                )
                issues.extend(fn_issues)
                weak_usages.extend(fn_weak)
                if is_safe:
                    safe_callables += 1

        if is_ts_file:
            for ptype in unit.root.find_all(kind="predefined_type"):
                if ptype.text().strip() == "any":
                    weak_usages.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=ptype.range().start.line + 1,
                            symbol="any",
                            detail="Explicit `any` type disables TypeScript checking — prefer `unknown` or generics",
                        )
                    )

        return UnitTypingStats(
            total_callables=total_callables,
            type_safe_callables=safe_callables,
            type_safety_issues=issues,
            omitted_init_return_annotations=[],
            weak_type_usages=weak_usages,
            unscoped_type_ignores=_collect_ts_js_unscoped_ignores(unit),
        )
