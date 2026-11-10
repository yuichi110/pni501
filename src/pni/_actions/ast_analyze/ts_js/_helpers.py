# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Shared AST traversal and JSDoc/TSDoc helpers for TypeScript and JavaScript checkers."""

from __future__ import annotations

import re
from typing import Final, Optional

from ast_grep_py import SgNode

from pni._actions.ast_analyze.models import ParsedUnit

_TYPE_DECL_KINDS: Final[dict[str, str]] = {
    "class_declaration": "class",
    "abstract_class_declaration": "class",
    "interface_declaration": "interface",
    "type_alias_declaration": "type",
    "enum_declaration": "enum",
}
_FN_VALUE_KINDS: Final[frozenset[str]] = frozenset(
    {"arrow_function", "function_expression", "generator_function"}
)
_JSDOC_PARAM_RE: Final[re.Pattern[str]] = re.compile(
    r"@param\s+(?:\{([^}]*)\}\s+)?(?:\[?([A-Za-z_$][\w$]*)(?:=[^\]]*)?\]?)"
)
_JSDOC_RETURN_RE: Final[re.Pattern[str]] = re.compile(r"@returns?\s*\{([^}]*)\}")
_JSDOC_TYPE_RE: Final[re.Pattern[str]] = re.compile(r"@type\s*\{([^}]*)\}")


def _collect_named_exports(unit: ParsedUnit) -> set[str]:
    """Collect identifiers exported via `export { a, b }` or `module.exports = ...`."""
    exported: set[str] = set()
    for exp in unit.root.find_all(kind="export_specifier"):
        name_node = exp.field("name")
        if name_node is not None:
            exported.add(name_node.text().strip())
    for m in re.finditer(r"\b(?:module\.)?exports\.([A-Za-z_$][\w$]*)\s*=", unit.source):
        exported.add(m.group(1))
    for m in re.finditer(r"\bmodule\.exports\s*=\s*\{([^}]+)\}", unit.source):
        for token in m.group(1).split(","):
            ident = token.split(":", 1)[0].strip()
            if ident.isidentifier():
                exported.add(ident)
    return exported


def _is_exported_node(node: SgNode, name: str, named_exports: set[str]) -> bool:
    """Return True if `node` is directly inside an `export_statement` or listed in `named_exports`."""
    if name in named_exports:
        return True
    parent = node.parent()
    while parent is not None:
        if parent.kind() == "export_statement":
            return True
        if parent.kind() in {"program", "statement_block"}:
            break
        parent = parent.parent()
    return False


def iter_ts_js_type_declarations(unit: ParsedUnit) -> list[tuple[str, str, bool, SgNode, SgNode]]:
    """Return `(name, kind_label, is_exported, decl_node, doc_anchor)` for all type/class declarations."""
    named_exports = _collect_named_exports(unit)
    results: list[tuple[str, str, bool, SgNode, SgNode]] = []
    for child in unit.root.children():
        target = child
        anchor = child
        if child.kind() == "export_statement":
            decl = child.field("declaration")
            if decl is None:
                continue
            target = decl
            anchor = child
        tkind = _TYPE_DECL_KINDS.get(target.kind())
        if tkind is None:
            continue
        name_node = target.field("name")
        if name_node is None:
            continue
        tname = name_node.text().strip()
        is_exp = anchor.kind() == "export_statement" or _is_exported_node(target, tname, named_exports)
        results.append((tname, tkind, is_exp, target, anchor))
    return results


def _iter_class_methods(
    class_node: SgNode,
    class_name: str,
    class_exported: bool,
) -> list[tuple[str, str, bool, SgNode, SgNode]]:
    """Return `(qualified_name, method_name, is_public_exported, method_node, doc_anchor)` for a class."""
    body = class_node.field("body")
    if body is None:
        return []
    methods: list[tuple[str, str, bool, SgNode, SgNode]] = []
    for member in body.children():
        if member.kind() != "method_definition":
            continue
        name_node = member.field("name")
        if name_node is None:
            continue
        mname = name_node.text().strip()
        member_text = member.text().lstrip()
        is_private = (
            mname.startswith(("_", "#"))
            or member_text.startswith(("private ", "protected "))
        )
        is_pub = class_exported and not is_private and mname != "constructor"
        methods.append((f"{class_name}.{mname}", mname, is_pub, member, member))
    return methods


def _iter_var_callables(
    target: SgNode,
    anchor: SgNode,
    is_exp_stmt: bool,
    named_exports: set[str],
) -> list[tuple[str, str, bool, SgNode, SgNode]]:
    """Extract arrow_function / function_expression variable declarators from a lexical/variable declaration."""
    found: list[tuple[str, str, bool, SgNode, SgNode]] = []
    for declarator in target.find_all(kind="variable_declarator"):
        if declarator.parent() != target:
            continue
        name_node = declarator.field("name")
        val_node = declarator.field("value")
        if name_node is None or val_node is None or val_node.kind() not in _FN_VALUE_KINDS:
            continue
        vname = name_node.text().strip()
        is_exp = is_exp_stmt or vname in named_exports
        found.append((vname, vname, is_exp, val_node, anchor))
    return found


def iter_ts_js_callables(unit: ParsedUnit) -> list[tuple[str, str, bool, SgNode, SgNode]]:
    """Return `(qualified_name, short_name, is_exported, fn_node, doc_anchor)` for functions and methods."""
    named_exports = _collect_named_exports(unit)
    callables: list[tuple[str, str, bool, SgNode, SgNode]] = []

    for child in unit.root.children():
        target = child
        anchor = child
        is_exp_stmt = False
        if child.kind() == "export_statement":
            is_exp_stmt = True
            decl = child.field("declaration")
            if decl is None:
                continue
            target = decl

        kind = target.kind()
        if kind in {"function_declaration", "generator_function_declaration"}:
            name_node = target.field("name")
            if name_node is None:
                continue
            fname = name_node.text().strip()
            is_exp = is_exp_stmt or fname in named_exports
            callables.append((fname, fname, is_exp, target, anchor))
        elif kind in {"lexical_declaration", "variable_declaration"}:
            callables.extend(_iter_var_callables(target, anchor, is_exp_stmt, named_exports))
        elif kind in {"class_declaration", "abstract_class_declaration"}:
            cname_node = target.field("name")
            cname = cname_node.text().strip() if cname_node is not None else "AnonymousClass"
            c_exp = is_exp_stmt or cname in named_exports
            callables.extend(_iter_class_methods(target, cname, c_exp))

    return callables


def get_ts_js_params(fn_node: SgNode) -> list[tuple[str, bool, str]]:
    """Return `(param_name, has_type_annotation, type_text)` for a TypeScript or JavaScript callable node."""
    params_node = fn_node.field("parameters")
    if params_node is None:
        single_param = fn_node.field("parameter")
        if single_param is not None:
            return [(single_param.text().strip(), False, "")]
        return []

    results: list[tuple[str, bool, str]] = []
    for child in params_node.children():
        ckind = child.kind()
        if ckind in {"(", ")", ","}:
            continue
        type_ann = child.field("type") or child.find(kind="type_annotation")
        type_text = type_ann.text().lstrip(":").strip() if type_ann is not None else ""
        has_type = bool(type_text)
        pat_node = child.field("pattern") or child.field("name")
        if pat_node is not None:
            pname = pat_node.text().strip().lstrip(".")
        else:
            raw = child.text().split(":", 1)[0].split("=", 1)[0].strip().lstrip(".").rstrip("?")
            pname = raw or "_"
        if pname == "this":
            continue
        results.append((pname, has_type, type_text))
    return results


def has_ts_return_type(fn_node: SgNode) -> tuple[bool, str]:
    """Return `(has_return_annotation, return_type_text)` for a TypeScript callable node."""
    ret_node = fn_node.field("return_type")
    if ret_node is not None:
        txt = ret_node.text().lstrip(":").strip()
        return bool(txt), txt
    parent = fn_node.parent()
    if parent is not None and parent.kind() == "variable_declarator":
        var_type = parent.field("type") or parent.find(kind="type_annotation")
        if var_type is not None:
            txt = var_type.text().lstrip(":").strip()
            return bool(txt), txt
    return False, ""


def extract_preceding_jsdoc(anchor_node: SgNode) -> Optional[str]:
    """Return the `/** ... */` JSDoc/TSDoc comment immediately preceding `anchor_node` if present."""
    curr = anchor_node
    prev = curr.prev()
    while prev is not None and prev.kind() == "decorator":
        curr = prev
        prev = curr.prev()
    if prev is not None and prev.kind() == "comment":
        text = prev.text().strip()
        if text.startswith("/**") and prev.range().end.line + 2 >= curr.range().start.line:
            return text
    return None


def parse_jsdoc_block(raw_jsdoc: str) -> tuple[str, dict[str, str], Optional[str], bool]:
    """Return `(summary_text, param_types_by_name, return_type, has_type_tag)` from a `/** ... */` block."""
    inner = re.sub(r"^/\*\*+|\*+/$", "", raw_jsdoc.strip()).strip()
    lines: list[str] = []
    for raw_ln in inner.splitlines():
        clean = raw_ln.strip().lstrip("*").strip()
        if clean:
            lines.append(clean)
    summary_lines = [ln for ln in lines if not ln.startswith("@")]
    summary = " ".join(summary_lines).strip()

    param_types: dict[str, str] = {}
    for m in _JSDOC_PARAM_RE.finditer(inner):
        ptype = (m.group(1) or "").strip()
        pname = (m.group(2) or "").strip()
        if pname:
            param_types[pname] = ptype

    ret_match = _JSDOC_RETURN_RE.search(inner)
    ret_type = ret_match.group(1).strip() if ret_match is not None else None
    has_type_tag = _JSDOC_TYPE_RE.search(inner) is not None
    return summary, param_types, ret_type, has_type_tag
