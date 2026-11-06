# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java-specific CST helper utilities shared across Java AST checkers."""

from __future__ import annotations

from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.models import ParsedUnit

JAVA_TYPE_KINDS: Final[tuple[str, ...]] = (
    "class_declaration",
    "interface_declaration",
    "enum_declaration",
    "record_declaration",
)
JAVA_CALLABLE_KINDS: Final[tuple[str, ...]] = (
    "method_declaration",
    "constructor_declaration",
)


def extract_java_package(root: SgNode) -> str:
    """Extract the package name from a Java compilation unit CST root."""
    pkg_decl = root.find(kind="package_declaration")
    if pkg_decl is None:
        return ""
    for child in pkg_decl.named_children():
        if child.kind() in {"scoped_identifier", "identifier"}:
            return child.text().strip()
    return ""


def unit_fqn(unit: ParsedUnit) -> tuple[str, str]:
    """Return (package_name, primary_fqn) for a parsed Java compilation unit."""
    pkg = extract_java_package(unit.root)
    primary = unit.file_path.stem
    fqn = f"{pkg}.{primary}" if pkg else primary
    return pkg, fqn


def get_modifiers_node(decl: SgNode) -> SgNode | None:
    """Return the modifiers child node of a Java declaration if present."""
    for child in decl.children():
        if child.kind() == "modifiers":
            return child
    return None


def modifier_tokens(decl: SgNode) -> set[str]:
    """Return modifier keywords ('public', 'static', 'final', etc.) on a Java declaration."""
    mods = get_modifiers_node(decl)
    if mods is None:
        return set()
    return {c.kind() for c in mods.children() if c.is_leaf()}


def has_override_annotation(decl: SgNode) -> bool:
    """Return True if a method declaration carries @Override."""
    mods = get_modifiers_node(decl)
    if mods is None:
        return False
    return any("@Override" in c.text() for c in mods.named_children())


def find_unchecked_suppress(decl: SgNode) -> str | None:
    """Return matched suppression token if @SuppressWarnings suppresses unchecked or rawtypes."""
    mods = get_modifiers_node(decl)
    if mods is None:
        return None
    for child in mods.named_children():
        txt = child.text()
        if "SuppressWarnings" in txt and ("unchecked" in txt or "rawtypes" in txt):
            return txt.strip()
    return None


def callable_symbol_name(m_node: SgNode) -> str:
    """Return method or constructor name for a Java callable CST node."""
    name_node = m_node.field("name")
    return name_node.text() if name_node is not None else "<init>"
