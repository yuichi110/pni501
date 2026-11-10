# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java code quality, cognitive complexity, global state, and bug-risk idiom AST checker."""

from __future__ import annotations

from typing import ClassVar

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseQualityChecker
from pni._actions.ast_analyze.java._helpers import (
    JAVA_CALLABLE_KINDS,
    JAVA_TYPE_KINDS,
    callable_symbol_name,
    is_console_or_logger_unit,
    modifier_tokens,
)
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit


def _count_java_loc(source: str) -> int:
    """Count non-empty, non-comment Java source lines (skipping // and /* ... */)."""
    count = 0
    in_block = False
    for raw_line in source.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if in_block:
            if "*/" in stripped:
                in_block = False
            continue
        if stripped.startswith("//"):
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped[2:]:
                in_block = True
            continue
        count += 1
    return count


def _find_empty_catches(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect empty catch blocks whose exception parameter is not explicitly named 'ignored'."""
    findings: list[CodeLocation] = []
    for cnode in unit.root.find_all(kind="catch_clause"):
        param = cnode.find(kind="catch_formal_parameter")
        pname_node = param.field("name") if param is not None else None
        pname = pname_node.text() if pname_node is not None else ""
        if pname.startswith("ignore"):
            continue
        body = cnode.field("body")
        if body is not None and not body.named_children():
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=cnode.range().start.line + 1,
                    symbol=pname or "catch",
                    detail="Empty catch block silently swallows exception",
                )
            )
    return findings


def _find_java_idiom_risks(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect empty catches, string == comparisons, and System.out/err prints."""
    findings = _find_empty_catches(unit)
    for bnode in unit.root.find_all(kind="binary_expression"):
        op_node = bnode.field("operator")
        left = bnode.field("left")
        right = bnode.field("right")
        op_txt = op_node.text() if op_node is not None else ""
        if not op_txt and any(c.kind() in {"==", "!="} for c in bnode.children()):
            op_txt = "=="
        if op_txt in {"==", "!="} and (
            (left is not None and left.kind() == "string_literal")
            or (right is not None and right.kind() == "string_literal")
        ):
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=bnode.range().start.line + 1,
                    symbol=bnode.text().strip()[:40],
                    detail="Reference equality (== / !=) with String literal; use .equals()",
                )
            )

    if not is_console_or_logger_unit(unit):
        for inv in unit.root.find_all(kind="method_invocation"):
            obj = inv.field("object")
            if obj is not None and obj.text() in {"System.out", "System.err"}:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=inv.range().start.line + 1,
                        symbol=obj.text(),
                        detail=f"Direct console output via {obj.text()}; use structured logger (SLF4J)",
                    )
                )
    return findings


def _collect_type_public_callables(tnode: SgNode, tkind: str, pub_methods: set[str]) -> None:
    """Populate implicitly public annotation elements and interface methods into pub_methods."""
    if tkind == "annotation_type_declaration":
        for enode in tnode.find_all(kind="annotation_type_element_declaration"):
            if (en := enode.field("name")) is not None:
                pub_methods.add(en.text())
    elif tkind == "interface_declaration":
        for mnode in tnode.find_all(kind="method_declaration"):
            if "private" not in modifier_tokens(mnode):
                pub_methods.add(callable_symbol_name(mnode))


class JavaQualityChecker(BaseQualityChecker):
    """Inspect Java LOC, module inventory, cognitive complexity, static fields, and bug idioms."""

    branch_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "enhanced_for_statement",
            "while_statement",
            "do_statement",
            "catch_clause",
            "ternary_expression",
            "switch_block_statement_group",
            "switch_rule",
        }
    )

    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment lines in a Java compilation unit."""
        return _count_java_loc(unit.source)

    def count_classes(self, unit: ParsedUnit) -> int:
        """Count class, interface, enum, record, and annotation (@interface) declarations in a Java unit."""
        return sum(len(unit.root.find_all(kind=tkind)) for tkind in JAVA_TYPE_KINDS)

    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, SgNode]]:
        """Return (callable_name, cst_node) pairs for all Java methods and constructors."""
        callables: list[tuple[str, SgNode]] = []
        for mkind in JAVA_CALLABLE_KINDS:
            for mnode in unit.root.find_all(kind=mkind):
                callables.append((callable_symbol_name(mnode), mnode))
        return callables

    def count_callable_params(self, node: SgNode) -> int:
        """Count formal and varargs parameters on a Java method or constructor."""
        params_node = node.field("parameters")
        if params_node is None:
            return 0
        return sum(1 for p in params_node.named_children() if p.kind() != "receiver_parameter")

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Extract sorted public type names and public callable names for module_inventory."""
        pub_types: set[str] = set()
        pub_methods: set[str] = set()
        for tkind in JAVA_TYPE_KINDS:
            for tnode in unit.root.find_all(kind=tkind):
                if "public" not in modifier_tokens(tnode):
                    continue
                if (n := tnode.field("name")) is not None:
                    pub_types.add(n.text())
                _collect_type_public_callables(tnode, tkind, pub_methods)
        for mkind in JAVA_CALLABLE_KINDS:
            for mnode in unit.root.find_all(kind=mkind):
                if "public" in modifier_tokens(mnode):
                    pub_methods.add(callable_symbol_name(mnode))
        return sorted(pub_types), sorted(pub_methods)

    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect mutable static fields ('static' without 'final') in Java types."""
        usages: list[CodeLocation] = []
        for fnode in unit.root.find_all(kind="field_declaration"):
            fmods = modifier_tokens(fnode)
            if "static" in fmods and "final" not in fmods:
                declarators = fnode.find_all(kind="variable_declarator")
                names = [n.text() for d in declarators if (n := d.field("name")) is not None]
                fname = ", ".join(names) or fnode.text().strip()
                usages.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=fnode.range().start.line + 1,
                        symbol=fname,
                        detail=f"Mutable non-final static field: {fname}",
                    )
                )
        return usages

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect empty catch blocks, String == comparisons, and System.out/err usages."""
        return _find_java_idiom_risks(unit)
