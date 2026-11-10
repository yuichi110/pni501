# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java raw-generics, untyped Object, and @SuppressWarnings AST checker."""

from __future__ import annotations

from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTypingChecker
from pni._actions.ast_analyze.java._helpers import (
    JAVA_CALLABLE_KINDS,
    JAVA_TYPE_KINDS,
    callable_symbol_name,
    find_unchecked_suppress,
     get_modifiers_node,
    has_override_annotation,
)
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitTypingStats

_COMMON_GENERIC_TYPES: Final[frozenset[str]] = frozenset(
    {
        "List",
        "ArrayList",
        "LinkedList",
        "Map",
        "HashMap",
        "TreeMap",
        "ConcurrentHashMap",
        "Set",
        "HashSet",
        "Collection",
        "Iterable",
        "Iterator",
        "Optional",
        "Stream",
        "Future",
        "CompletableFuture",
        "Class",
        "Comparable",
        "Comparator",
        "Supplier",
        "Consumer",
        "Function",
        "Predicate",
    }
)


def _find_broad_suppress_all(decl: SgNode) -> str | None:
    """Return @SuppressWarnings('all') annotation text when present on decl."""
    mods = get_modifiers_node(decl)
    if mods is None:
        return None
    for child in mods.named_children():
        txt = child.text()
        if "SuppressWarnings" in txt and '"all"' in txt:
            return txt.strip()
    return None


def _is_scope_qualifier_or_parameterized(tid: SgNode) -> bool:
    """Return True if a type_identifier is an enclosing scope prefix (e.g. Map in Map.Entry) or parameterized."""
    parent = tid.parent()
    if parent is None:
        return False
    if parent.kind() == "scoped_type_identifier":
        named = parent.named_children()
        if not named or named[-1].range().start.index != tid.range().start.index:
            return True
        grandparent = parent.parent()
        first_gp_child = grandparent.child(0) if grandparent is not None else None
        return (
            grandparent is not None
            and grandparent.kind() == "generic_type"
            and first_gp_child is not None
            and first_gp_child.range().start.index == parent.range().start.index
        )
    first_child = parent.child(0)
    return (
        parent.kind() == "generic_type"
        and first_child is not None
        and first_child.range().start.index == tid.range().start.index
    )


def _find_raw_generics_in_type(type_node: SgNode | None) -> list[str]:
    """Find unparameterized raw generic type identifiers inside a Java type node."""
    if type_node is None:
        return []
    raw_names: list[str] = []
    candidates = [type_node] if type_node.kind() == "type_identifier" else []
    candidates.extend(type_node.find_all(kind="type_identifier"))
    seen_indices: set[int] = set()

    for tid in candidates:
        idx = tid.range().start.index
        if idx in seen_indices:
            continue
        seen_indices.add(idx)
        tname = tid.text()
        if tname not in _COMMON_GENERIC_TYPES:
            continue
        if not _is_scope_qualifier_or_parameterized(tid):
            raw_names.append(tname)
    return raw_names


def _inspect_callable_signature(
    m_node: SgNode,
    rel_path: str,
) -> tuple[bool, list[CodeLocation], list[CodeLocation], list[CodeLocation]]:
    """Inspect a Java method or constructor signature for raw generics, Object, and suppressions."""
    m_name = callable_symbol_name(m_node)
    lineno = m_node.range().start.line + 1
    is_override = has_override_annotation(m_node)
    issues: list[CodeLocation] = []
    weak: list[CodeLocation] = []
    unscoped: list[CodeLocation] = []

    ret_type = m_node.field("type")
    raw_issues = [f"return raw '{r}'" for r in _find_raw_generics_in_type(ret_type)]
    if ret_type is not None and ret_type.text().strip() == "Object" and not is_override:
        weak.append(
            CodeLocation(file=rel_path, line=lineno, symbol=m_name, detail="Return type uses untyped 'Object'")
        )

    params_node = m_node.field("parameters")
    if params_node is not None:
        for param in params_node.named_children():
            ptype = param.field("type")
            pname_node = param.field("name")
            pname = pname_node.text() if pname_node is not None else param.text()
            raw_issues.extend(f"param '{pname}' uses raw '{rp}'" for rp in _find_raw_generics_in_type(ptype))
            if ptype is not None and ptype.text().strip() == "Object" and m_name != "equals" and not is_override:
                weak.append(
                    CodeLocation(
                        file=rel_path,
                        line=lineno,
                        symbol=m_name,
                        detail=f"Parameter '{pname}' uses untyped 'Object'",
                    )
                )

    suppressed = find_unchecked_suppress(m_node)
    if suppressed:
        weak.append(
            CodeLocation(file=rel_path, line=lineno, symbol=m_name, detail=f"Type suppression: {suppressed}")
        )
    broad_sup = _find_broad_suppress_all(m_node)
    if broad_sup:
        unscoped.append(
            CodeLocation(file=rel_path, line=lineno, symbol=m_name, detail=f"Broad suppression: {broad_sup}")
        )

    is_safe = len(raw_issues) == 0
    if not is_safe:
        issues.append(
            CodeLocation(
                file=rel_path,
                line=lineno,
                symbol=m_name,
                detail=f"Raw generic types: {', '.join(raw_issues)}",
            )
        )
    return is_safe, issues, weak, unscoped


class JavaTypingChecker(BaseTypingChecker):
    """Check Java generic type parameterization, untyped Object signatures, and type suppressions."""

    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect type-level suppressions and all callable signatures in a Java unit."""
        total_callables = 0
        safe_callables = 0
        issues: list[CodeLocation] = []
        weak_usages: list[CodeLocation] = []
        unscoped: list[CodeLocation] = []

        for tkind in JAVA_TYPE_KINDS:
            for tnode in unit.root.find_all(kind=tkind):
                tname_node = tnode.field("name")
                tname = tname_node.text() if tname_node is not None else unit.file_path.stem
                lineno = tnode.range().start.line + 1
                suppressed = find_unchecked_suppress(tnode)
                if suppressed:
                    weak_usages.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=lineno,
                            symbol=tname,
                            detail=f"Type suppression: {suppressed}",
                        )
                    )
                broad_sup = _find_broad_suppress_all(tnode)
                if broad_sup:
                    unscoped.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=lineno,
                            symbol=tname,
                            detail=f"Broad suppression: {broad_sup}",
                        )
                    )

        for mkind in JAVA_CALLABLE_KINDS:
            for mnode in unit.root.find_all(kind=mkind):
                total_callables += 1
                is_safe, m_issues, m_weak, m_unscoped = _inspect_callable_signature(mnode, unit.rel_path)
                if is_safe:
                    safe_callables += 1
                issues.extend(m_issues)
                weak_usages.extend(m_weak)
                unscoped.extend(m_unscoped)

        return UnitTypingStats(
            total_callables=total_callables,
            type_safe_callables=safe_callables,
            type_safety_issues=issues,
            weak_type_usages=weak_usages,
            unscoped_type_ignores=unscoped,
        )
