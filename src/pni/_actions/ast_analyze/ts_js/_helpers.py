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

import contextlib
import json
import re
from pathlib import Path
from typing import Final, Optional

from ast_grep_py import SgNode, SgRoot

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


def _unwrap_parens_and_unary(node: Optional[SgNode]) -> Optional[SgNode]:
    """Unwrap `parenthesized_expression` and prefix `unary_expression` wrappers around an AST node."""
    curr = node
    for _ in range(4):
        if curr is None:
            return None
        kind = curr.kind()
        if kind == "parenthesized_expression":
            inner = next((c for c in curr.children() if c.kind() not in {"(", ")"}), None)
            if inner is None:
                return curr
            curr = inner
        elif kind == "unary_expression":
            operand = curr.field("argument")
            if operand is None:
                return curr
            curr = operand
        else:
            return curr
    return curr


def _extract_call_iife_bodies(call_node: SgNode) -> list[SgNode]:
    """Return `statement_block` bodies from an IIFE or UMD `call_expression`."""
    fn_node = _unwrap_parens_and_unary(call_node.field("function"))
    if fn_node is None or fn_node.kind() not in _FN_VALUE_KINDS:
        return []
    bodies: list[SgNode] = []
    fn_body = fn_node.field("body")
    if fn_body is not None and fn_body.kind() == "statement_block":
        bodies.append(fn_body)
    args_node = call_node.field("arguments")
    if args_node is not None:
        for arg in args_node.children():
            unwrapped_arg = _unwrap_parens_and_unary(arg)
            if unwrapped_arg is not None and unwrapped_arg.kind() in _FN_VALUE_KINDS:
                arg_body = unwrapped_arg.field("body")
                if arg_body is not None and arg_body.kind() == "statement_block":
                    bodies.append(arg_body)
    return bodies


def _extract_stmt_iife_bodies(stmt_node: SgNode) -> list[SgNode]:
    """Extract IIFE/UMD `statement_block` bodies from a top-level expression or variable statement."""
    kind = stmt_node.kind()
    if kind == "expression_statement":
        for child in stmt_node.children():
            unwrapped = _unwrap_parens_and_unary(child)
            if unwrapped is not None and unwrapped.kind() == "call_expression":
                return _extract_call_iife_bodies(unwrapped)
        return []
    if kind in {"lexical_declaration", "variable_declaration"}:
        bodies: list[SgNode] = []
        for declarator in stmt_node.find_all(kind="variable_declarator"):
            if declarator.parent() != stmt_node:
                continue
            val = _unwrap_parens_and_unary(declarator.field("value"))
            if val is not None and val.kind() == "call_expression":
                bodies.extend(_extract_call_iife_bodies(val))
        return bodies
    return []


def iter_top_level_statements(
    root: SgNode,
    *,
    _depth: int = 0,
    _in_iife: bool = False,
) -> list[tuple[SgNode, bool]]:
    """Yield `(statement_node, in_iife)` across module root and unwrapped IIFE/UMD bodies."""
    items: list[tuple[SgNode, bool]] = []
    for child in root.children():
        if _depth < 3:
            iife_bodies = _extract_stmt_iife_bodies(child)
            if iife_bodies:
                for body in iife_bodies:
                    items.extend(iter_top_level_statements(body, _depth=_depth + 1, _in_iife=True))
                continue
        items.append((child, _in_iife))
    return items


def _collect_named_exports(unit: ParsedUnit) -> set[str]:
    """Collect identifiers exported via ES `export`, CommonJS `exports`, or IIFE `return`/`window`."""
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
    for m in re.finditer(r"\breturn\s+new\s+([A-Za-z_$][\w$]*)\s*\(", unit.source):
        exported.add(m.group(1))
    for m in re.finditer(
        r"\b(?:window|globalThis|self)\.[A-Za-z_$][\w$]*\s*=\s*(?:new\s+)?([A-Za-z_$][\w$]*)",
        unit.source,
    ):
        exported.add(m.group(1))
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
    has_es_export = unit.root.find(kind="export_statement") is not None
    results: list[tuple[str, str, bool, SgNode, SgNode]] = []
    for child, in_iife in iter_top_level_statements(unit.root):
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
        is_iife_pub = in_iife and not has_es_export and not tname.startswith(("_", "#"))
        is_exp = (
            anchor.kind() == "export_statement"
            or _is_exported_node(target, tname, named_exports)
            or is_iife_pub
        )
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
    *,
    in_iife: bool = False,
    has_es_export: bool = True,
) -> list[tuple[str, str, bool, SgNode, SgNode]]:
    """Extract arrow_function / function_expression / class declarators from a lexical/variable declaration."""
    found: list[tuple[str, str, bool, SgNode, SgNode]] = []
    for declarator in target.find_all(kind="variable_declarator"):
        if declarator.parent() != target:
            continue
        name_node = declarator.field("name")
        val_node = declarator.field("value")
        if name_node is None or val_node is None:
            continue
        vname = name_node.text().strip()
        is_iife_pub = in_iife and not has_es_export and not vname.startswith(("_", "#"))
        is_exp = is_exp_stmt or vname in named_exports or is_iife_pub
        if val_node.kind() in _FN_VALUE_KINDS:
            found.append((vname, vname, is_exp, val_node, anchor))
        elif val_node.kind() == "class":
            found.extend(_iter_class_methods(val_node, vname, is_exp))
    return found


def iter_ts_js_callables(unit: ParsedUnit) -> list[tuple[str, str, bool, SgNode, SgNode]]:
    """Return `(qualified_name, short_name, is_exported, fn_node, doc_anchor)` for functions and methods."""
    named_exports = _collect_named_exports(unit)
    has_es_export = unit.root.find(kind="export_statement") is not None
    callables: list[tuple[str, str, bool, SgNode, SgNode]] = []

    for child, in_iife in iter_top_level_statements(unit.root):
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
            is_iife_pub = in_iife and not has_es_export and not fname.startswith(("_", "#"))
            is_exp = is_exp_stmt or fname in named_exports or is_iife_pub
            callables.append((fname, fname, is_exp, target, anchor))
        elif kind in {"lexical_declaration", "variable_declaration"}:
            callables.extend(
                _iter_var_callables(
                    target,
                    anchor,
                    is_exp_stmt,
                    named_exports,
                    in_iife=in_iife,
                    has_es_export=has_es_export,
                )
            )
        elif kind in {"class_declaration", "abstract_class_declaration"}:
            cname_node = target.field("name")
            cname = cname_node.text().strip() if cname_node is not None else "AnonymousClass"
            is_iife_pub = in_iife and not has_es_export and not cname.startswith(("_", "#"))
            c_exp = is_exp_stmt or cname in named_exports or is_iife_pub
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


def find_companion_dts_files(file_path: Path) -> list[Path]:
    """Locate companion `.d.ts` files for a JavaScript source file (same stem or package.json `types`/`typings`)."""
    if file_path.suffix.lower() in {".ts", ".tsx"}:
        return []
    found: list[Path] = []
    direct = file_path.with_suffix(".d.ts")
    if direct.is_file():
        found.append(direct)

    curr = file_path.parent
    stem_low = file_path.stem.lower()
    for _ in range(3):
        pkg_json = curr / "package.json"
        if pkg_json.is_file():
            with contextlib.suppress(Exception):
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    for key in ("types", "typings"):
                        raw_rel = data.get(key)
                        if isinstance(raw_rel, str) and raw_rel.strip():
                            cand = (curr / raw_rel.strip()).resolve()
                            dts_stem = cand.name[:-5].lower() if cand.name.lower().endswith(".d.ts") else ""
                            if cand.is_file() and cand not in found and stem_low in {dts_stem, "index"}:
                                found.append(cand)
            break
        if curr.parent == curr:
            break
        curr = curr.parent
    return found


def extract_companion_dts_types(unit: ParsedUnit) -> list[str]:
    """Extract exported interface, type, class, and enum names from companion `.d.ts` files."""
    dts_files = find_companion_dts_files(unit.file_path)
    if not dts_files:
        return []
    names: set[str] = set()
    for dts_path in dts_files:
        with contextlib.suppress(Exception):
            dts_src = dts_path.read_text(encoding="utf-8")
            root = SgRoot(dts_src, "typescript").root()
            for kind_key in _TYPE_DECL_KINDS:
                for node in root.find_all(kind=kind_key):
                    nm = node.field("name")
                    if nm is not None:
                        tname = nm.text().strip()
                        if tname and not tname.startswith("_"):
                            names.add(tname)
    return sorted(names)

