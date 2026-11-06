# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java public type and public method Javadoc AST checker (presence, non-empty, @param match)."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseDocChecker
from pni._actions.ast_analyze.java._helpers import (
    JAVA_CALLABLE_KINDS,
    JAVA_TYPE_KINDS,
    callable_symbol_name,
    has_override_annotation,
    modifier_tokens,
)
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitDocStats

_STUB_WORDS: Final[frozenset[str]] = frozenset({"todo", "tbd", "fixme", "wip", "none", "placeholder"})
_PARAM_TAG_RE: Final[re.Pattern[str]] = re.compile(r"@param\s+([A-Za-z_$][A-Za-z0-9_$]*)")


def _extract_javadoc_text(decl: SgNode) -> str | None:
    """Return raw /** ... */ Javadoc block text immediately preceding decl, or None."""
    prev = decl.prev()
    while prev is not None and prev.kind() == "line_comment":
        prev = prev.prev()
    if prev is not None and prev.kind() == "block_comment" and prev.text().startswith("/**"):
        return prev.text()
    return None


def _is_empty_javadoc(raw_doc: str) -> bool:
    """Return True if a Javadoc block contains no meaningful prose (empty or TODO stub)."""
    body = raw_doc.removeprefix("/**").removesuffix("*/")
    lines = [re.sub(r"^\s*\*\s?", "", ln).strip() for ln in body.splitlines()]
    prose_words = [
        w.lower().strip(".:;-")
        for ln in lines
        if ln and not ln.startswith("@")
        for w in ln.split()
    ]
    meaningful = [w for w in prose_words if w and w not in _STUB_WORDS]
    return len(meaningful) == 0


def _check_javadoc_params(mnode: SgNode, raw_doc: str, m_name: str, rel_path: str) -> CodeLocation | None:
    """Compare @param tags in Javadoc against formal method parameters when @param is used."""
    doc_params = _PARAM_TAG_RE.findall(raw_doc)
    if not doc_params:
        return None
    params_node = mnode.field("parameters")
    formal_params: list[str] = []
    if params_node is not None:
        for param in params_node.named_children():
            pname_node = param.field("name")
            if pname_node is not None:
                formal_params.append(pname_node.text())
    missing_tags = sorted(set(formal_params) - set(doc_params))
    stale_tags = sorted(set(doc_params) - set(formal_params))
    if not missing_tags and not stale_tags:
        return None
    parts: list[str] = []
    if missing_tags:
        parts.append(f"undocumented params: {', '.join(missing_tags)}")
    if stale_tags:
        parts.append(f"unknown @param tags: {', '.join(stale_tags)}")
    return CodeLocation(
        file=rel_path,
        line=mnode.range().start.line + 1,
        symbol=m_name,
        detail=f"Javadoc @param mismatch ({'; '.join(parts)})",
    )


def _inspect_type_javadocs(unit: ParsedUnit) -> tuple[int, int, list[CodeLocation], list[CodeLocation]]:
    """Inspect public Java types for Javadoc presence and non-empty prose."""
    candidates = 0
    documented = 0
    missing: list[CodeLocation] = []
    empty: list[CodeLocation] = []
    for tkind in JAVA_TYPE_KINDS:
        for tnode in unit.root.find_all(kind=tkind):
            if "public" not in modifier_tokens(tnode):
                continue
            tname_node = tnode.field("name")
            tname = tname_node.text() if tname_node is not None else unit.file_path.stem
            candidates += 1
            lineno = tnode.range().start.line + 1
            raw_doc = _extract_javadoc_text(tnode)
            if raw_doc is None:
                missing.append(
                    CodeLocation(file=unit.rel_path, line=lineno, symbol=tname, detail="Missing public type Javadoc")
                )
            elif _is_empty_javadoc(raw_doc):
                empty.append(
                    CodeLocation(
                        file=unit.rel_path, line=lineno, symbol=tname, detail="Empty or stub public type Javadoc"
                    )
                )
            else:
                documented += 1
    return candidates, documented, missing, empty


def _inspect_callable_javadocs(
    unit: ParsedUnit,
) -> tuple[int, int, list[CodeLocation], list[CodeLocation], list[CodeLocation]]:
    """Inspect public non-@Override Java methods and constructors for Javadoc and @param sync."""
    candidates = 0
    documented = 0
    missing: list[CodeLocation] = []
    empty: list[CodeLocation] = []
    mismatches: list[CodeLocation] = []
    for mkind in JAVA_CALLABLE_KINDS:
        for mnode in unit.root.find_all(kind=mkind):
            m_name = callable_symbol_name(mnode)
            if "public" not in modifier_tokens(mnode) or has_override_annotation(mnode) or m_name == "main":
                continue
            candidates += 1
            lineno = mnode.range().start.line + 1
            raw_doc = _extract_javadoc_text(mnode)
            if raw_doc is None:
                missing.append(
                    CodeLocation(file=unit.rel_path, line=lineno, symbol=m_name, detail="Missing public method Javadoc")
                )
            elif _is_empty_javadoc(raw_doc):
                empty.append(
                    CodeLocation(
                        file=unit.rel_path, line=lineno, symbol=m_name, detail="Empty or stub public method Javadoc"
                    )
                )
            else:
                documented += 1
                mismatch = _check_javadoc_params(mnode, raw_doc, m_name, unit.rel_path)
                if mismatch is not None:
                    mismatches.append(mismatch)
    return candidates, documented, missing, empty, mismatches


class JavaDocChecker(BaseDocChecker):
    """Check Javadoc comments on public Java types and non-@Override public methods."""

    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Inspect public types and public callables for Javadoc presence, quality, and @param sync."""
        tc, td, tmiss, temp = _inspect_type_javadocs(unit)
        mc, md, mmiss, memp, mmis = _inspect_callable_javadocs(unit)
        return UnitDocStats(
            candidates=tc + mc,
            documented=td + md,
            missing_docstrings=[*tmiss, *mmiss],
            empty_docstrings=[*temp, *memp],
            doc_signature_mismatches=mmis,
        )
