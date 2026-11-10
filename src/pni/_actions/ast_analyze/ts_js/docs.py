# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TSDoc / JSDoc documentation coverage and `@param` alignment checker for TypeScript & JavaScript."""

from __future__ import annotations

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseDocChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    UnitDocStats,
)
from pni._actions.ast_analyze.ts_js._helpers import (
    extract_preceding_jsdoc,
    get_ts_js_params,
    iter_ts_js_callables,
    iter_ts_js_type_declarations,
    parse_jsdoc_block,
)


def _check_jsdoc_param_mismatch(
    rel_path: str,
    line_no: int,
    qual: str,
    fn_node: SgNode,
    param_types: dict[str, str],
) -> CodeLocation | None:
    """Return a CodeLocation if JSDoc `@param` names do not match callable signature parameters."""
    if not param_types:
        return None
    actual_params = {
        pname
        for pname, _ht_flag, _ttxt in get_ts_js_params(fn_node)
        if not pname.startswith(("{", "["))
    }
    unknown_doc = sorted(set(param_types) - actual_params)
    if unknown_doc and actual_params:
        return CodeLocation(
            file=rel_path,
            line=line_no,
            symbol=qual,
            detail=f"JSDoc `@param` {unknown_doc} does not match parameters {sorted(actual_params)}",
        )
    return None


class TsJsDocChecker(BaseDocChecker):
    """Evaluate `/** ... */` JSDoc/TSDoc coverage and `@param` consistency on exported TS/JS symbols."""

    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Check exported classes, interfaces, types, functions, and public methods for JSDoc/TSDoc comments."""
        candidates = 0
        documented = 0
        annotated_doc_fns = 0
        missing: list[CodeLocation] = []
        empty: list[CodeLocation] = []
        mismatches: list[CodeLocation] = []

        for tname, tkind, is_exp, decl_node, anchor_node in iter_ts_js_type_declarations(unit):
            if not is_exp:
                continue
            candidates += 1
            raw_doc = extract_preceding_jsdoc(anchor_node)
            line_no = decl_node.range().start.line + 1
            if raw_doc is None:
                missing.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=tname,
                        detail=f"Exported {tkind} '{tname}' is missing a `/** ... */` JSDoc/TSDoc comment",
                    )
                )
            else:
                summary, _ptypes, _ret, _ht = parse_jsdoc_block(raw_doc)
                if not summary:
                    empty.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=tname,
                            detail=f"Exported {tkind} '{tname}' has an empty `/** ... */` JSDoc/TSDoc comment",
                        )
                    )
                else:
                    documented += 1

        for qual, _short, is_exp, fn_node, anchor_node in iter_ts_js_callables(unit):
            if not is_exp:
                continue
            candidates += 1
            raw_doc = extract_preceding_jsdoc(anchor_node)
            line_no = fn_node.range().start.line + 1
            if raw_doc is None:
                missing.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=qual,
                        detail=f"Exported callable '{qual}' is missing a `/** ... */` JSDoc/TSDoc comment",
                    )
                )
                continue

            summary, param_types, _ret, _ht = parse_jsdoc_block(raw_doc)
            if not summary and not param_types:
                empty.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=qual,
                        detail=f"Exported callable '{qual}' has an empty `/** ... */` JSDoc/TSDoc comment",
                    )
                )
                continue

            documented += 1
            annotated_doc_fns += 1
            mm = _check_jsdoc_param_mismatch(unit.rel_path, line_no, qual, fn_node, param_types)
            if mm is not None:
                mismatches.append(mm)

        return UnitDocStats(
            candidates=candidates,
            documented=documented,
            annotated_doc_functions=annotated_doc_fns,
            missing_docstrings=missing,
            empty_docstrings=empty,
            doc_signature_mismatches=mismatches,
        )
