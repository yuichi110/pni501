# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHPDoc (`/** ... */`) coverage, empty docblock, and `@param` signature consistency checker."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseDocChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitDocStats
from pni._actions.ast_analyze.php._helpers import (
    extract_formal_param_nodes,
    extract_node_name,
    find_preceding_phpdoc,
    get_visibility,
    iter_php_types,
)

_PHPDOC_PARAM_RE: Final[re.Pattern[str]] = re.compile(
    r"@param\s+(?:[^\s$]+\s+)?(&?\.\.\.|&|\.\.\.)?(\$[A-Za-z_\x80-\xff][A-Za-z0-9_\x80-\xff]*)"
)


def _clean_phpdoc_body(doc: str) -> str:
    """Strip `/**`, `*/`, and leading `*` markers from a PHPDoc comment."""
    inner = doc.strip().removeprefix("/**").removesuffix("*/")
    lines = [re.sub(r"^\s*\*\s?", "", ln).strip() for ln in inner.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def _has_override_attribute(method_node: SgNode) -> bool:
    """Return True if a PHP method carries `#[Override]` or `@inheritdoc`."""
    for child in method_node.children():
        if child.kind() == "attribute_list" and "Override" in child.text():
            return True
    return False


class PhpDocChecker(BaseDocChecker):
    """Evaluate PHPDoc coverage and `@param` alignment on public PHP types, functions, and methods."""

    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Inspect public types, top-level functions, and public methods for PHPDoc completeness."""
        candidates = 0
        documented = 0
        missing: list[CodeLocation] = []
        empty: list[CodeLocation] = []
        mismatches: list[CodeLocation] = []

        for type_name, tnode in iter_php_types(unit.root):
            candidates += 1
            doc = find_preceding_phpdoc(tnode)
            tline = tnode.range().start.line + 1
            if doc is None:
                missing.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=tline,
                        symbol=type_name,
                        detail=f"Missing PHPDoc '/** ... */' on {tnode.kind().replace('_', ' ')}",
                    )
                )
            elif not _clean_phpdoc_body(doc):
                empty.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=tline,
                        symbol=type_name,
                        detail="Empty PHPDoc block without summary",
                    )
                )
            else:
                documented += 1

            for mnode in tnode.find_all(kind="method_declaration"):
                if get_visibility(mnode) != "public" or _has_override_attribute(mnode):
                    continue
                mname = extract_node_name(mnode)
                if mname == "__construct" and not extract_formal_param_nodes(mnode):
                    continue
                symbol = f"{type_name}::{mname}"
                candidates += 1
                if self._check_callable_doc(unit, mnode, symbol, missing, empty, mismatches):
                    documented += 1

        for fn_node in unit.root.find_all(kind="function_definition"):
            fname = extract_node_name(fn_node)
            candidates += 1
            if self._check_callable_doc(unit, fn_node, fname, missing, empty, mismatches):
                documented += 1

        return UnitDocStats(
            candidates=candidates,
            documented=documented,
            missing_docstrings=missing,
            empty_docstrings=empty,
            doc_signature_mismatches=mismatches,
        )

    @staticmethod
    def _check_callable_doc(
        unit: ParsedUnit,
        cnode: SgNode,
        symbol: str,
        missing: list[CodeLocation],
        empty: list[CodeLocation],
        mismatches: list[CodeLocation],
    ) -> bool:
        """Validate PHPDoc presence, non-emptiness, and `@param` consistency for a callable."""
        line = cnode.range().start.line + 1
        doc = find_preceding_phpdoc(cnode)
        if doc is None:
            missing.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line,
                    symbol=symbol,
                    detail="Missing PHPDoc '/** ... */' on public callable",
                )
            )
            return False

        body = _clean_phpdoc_body(doc)
        if not body:
            empty.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line,
                    symbol=symbol,
                    detail="Empty PHPDoc block on callable",
                )
            )
            return False

        if "@inheritdoc" in body.lower():
            return True

        doc_params = [m.group(2) for m in _PHPDOC_PARAM_RE.finditer(doc)]
        if doc_params:
            actual_params = {
                v.text().strip()
                for p in extract_formal_param_nodes(cnode)
                if (v := p.find(kind="variable_name")) is not None
            }
            stale = [dp for dp in doc_params if dp not in actual_params]
            if stale:
                mismatches.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=symbol,
                        detail=f"PHPDoc @param {stale} does not match signature parameters {sorted(actual_params)}",
                    )
                )
        return True
