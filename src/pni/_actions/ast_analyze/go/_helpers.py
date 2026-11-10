# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Shared AST traversal and go.mod resolution helpers for Go checkers."""

from __future__ import annotations

import contextlib
import re
from pathlib import Path
from typing import Optional

from ast_grep_py import SgNode

from pni._actions.ast_analyze.models import ParsedUnit


def extract_package_name(unit: ParsedUnit) -> str:
    """Return the declared Go package name for a parsed unit."""
    pkg_clause = unit.root.find(kind="package_clause")
    if pkg_clause is None:
        return ""
    pkg_ident = pkg_clause.find(kind="package_identifier")
    if pkg_ident is not None:
        return pkg_ident.text().strip()
    return pkg_clause.text().removeprefix("package").strip()


def is_exported_go_name(name: str) -> bool:
    """Return True if a Go identifier is exported (starts with an uppercase ASCII/Unicode letter)."""
    clean = name.strip()
    return bool(clean) and clean[0].isupper()


def extract_receiver_type_name(method_node: SgNode) -> str:
    """Extract base receiver type name (stripping `*` and generic type arguments) from a method_declaration."""
    recv = method_node.field("receiver")
    if recv is None:
        return ""
    for pdecl in recv.children():
        if pdecl.kind() != "parameter_declaration":
            continue
        type_node = pdecl.field("type")
        if type_node is None:
            continue
        raw_type = type_node.text().strip().lstrip("*")
        if "[" in raw_type:
            raw_type = raw_type.split("[", 1)[0].strip()
        return raw_type
    return ""


def iter_go_type_specs(unit: ParsedUnit) -> list[tuple[str, str, SgNode, SgNode]]:
    """Return `(type_name, type_kind, spec_node, decl_node)` for all top-level type declarations."""
    results: list[tuple[str, str, SgNode, SgNode]] = []
    for child in unit.root.children():
        if child.kind() != "type_declaration":
            continue
        for spec in child.children():
            if spec.kind() not in {"type_spec", "type_alias"}:
                continue
            name_node = spec.field("name")
            if name_node is None:
                continue
            tname = name_node.text().strip()
            type_node = spec.field("type")
            tkind = "type"
            if type_node is not None:
                if type_node.kind() == "struct_type":
                    tkind = "struct"
                elif type_node.kind() == "interface_type":
                    tkind = "interface"
            results.append((tname, tkind, spec, child))
    return results


def iter_go_callables(unit: ParsedUnit) -> list[tuple[str, str, SgNode]]:
    """Return `(qualified_symbol, short_name, node)` for all top-level functions and methods in unit."""
    callables: list[tuple[str, str, SgNode]] = []
    for child in unit.root.children():
        kind = child.kind()
        if kind == "function_declaration":
            name_node = child.field("name")
            if name_node is None:
                continue
            fname = name_node.text().strip()
            callables.append((fname, fname, child))
        elif kind == "method_declaration":
            name_node = child.field("name")
            if name_node is None:
                continue
            mname = name_node.text().strip()
            recv_type = extract_receiver_type_name(child)
            qualified = f"{recv_type}.{mname}" if recv_type else mname
            callables.append((qualified, mname, child))
    return callables


def get_go_callable_params(node: SgNode) -> list[tuple[str, str]]:
    """Return `(param_name, param_type_text)` pairs for a Go function or method declaration."""
    params_node = node.field("parameters")
    if params_node is None:
        return []
    pairs: list[tuple[str, str]] = []
    for child in params_node.children():
        if child.kind() not in {"parameter_declaration", "variadic_parameter_declaration"}:
            continue
        type_node = child.field("type")
        type_text = type_node.text().strip() if type_node is not None else ""
        names = [
            sub.text().strip()
            for sub in child.children()
            if sub.kind() == "identifier"
            and (type_node is None or sub.range().start.index < type_node.range().start.index)
        ]
        if names:
            for nm in names:
                pairs.append((nm, type_text))
        else:
            pairs.append(("_", type_text))
    return pairs


def extract_preceding_godoc(target_node: SgNode, parent_decl: Optional[SgNode] = None) -> Optional[str]:
    """Extract contiguous GoDoc comment text immediately preceding target_node or its single-spec parent_decl."""
    anchor = target_node
    if parent_decl is not None:
        specs = [c for c in parent_decl.children() if c.kind() in {"type_spec", "type_alias"}]
        if len(specs) == 1:
            anchor = parent_decl

    comments: list[str] = []
    expected_end_line = anchor.range().start.line
    prev = anchor.prev()
    while prev is not None and prev.kind() == "comment":
        if prev.range().end.line + 1 < expected_end_line:
            break
        comments.append(prev.text())
        expected_end_line = prev.range().start.line
        prev = prev.prev()

    if not comments:
        return None
    comments.reverse()
    return "\n".join(comments)


def parse_go_module_info(project_root: Path) -> tuple[str, dict[str, str]]:
    """Parse `go.mod` in project_root and return `(module_path, direct_requires_map)`."""
    go_mod = project_root / "go.mod"
    if not go_mod.is_file():
        return "", {}

    module_path = ""
    direct_requires: dict[str, str] = {}
    in_require = False

    with contextlib.suppress(Exception):
        for raw_line in go_mod.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            is_indirect = bool(re.search(r"//\s*indirect\b", stripped))
            code_part = stripped.split("//", 1)[0].strip()
            if code_part.startswith("module "):
                module_path = code_part.removeprefix("module ").strip().strip('"')
            elif code_part.startswith("require ("):
                in_require = True
            elif in_require and code_part == ")":
                in_require = False
            elif in_require or code_part.startswith("require "):
                req_body = code_part.removeprefix("require ").strip()
                parts = req_body.split()
                if len(parts) >= 2 and not is_indirect:
                    direct_requires[parts[0]] = parts[1]

    return module_path, direct_requires
