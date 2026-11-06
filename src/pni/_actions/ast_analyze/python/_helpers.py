# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python-specific CST helper utilities shared across Python AST checkers."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

VALID_PARAM_KINDS: Final[frozenset[str]] = frozenset(
    {
        "identifier",
        "typed_parameter",
        "default_parameter",
        "typed_default_parameter",
        "list_splat_pattern",
        "dictionary_splat_pattern",
    }
)


def module_name_from_path(py_file: Path, project_root: Path) -> str:
    """Convert a Python file path inside project_root to a dotted module identifier."""
    if not py_file.is_relative_to(project_root):
        return py_file.stem
    rel = py_file.relative_to(project_root)
    parts = list(rel.parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__.py":
        parts = parts[:-1]
    elif parts:
        parts[-1] = parts[-1].removesuffix(".py")
    return ".".join(parts) if parts else py_file.stem


def function_symbol_name(fn_node: SgNode) -> str:
    """Extract the identifier of a Python function_definition CST node."""
    name_node = fn_node.field("name")
    return name_node.text() if name_node is not None else "<anonymous>"


def extract_python_docstring_text(container: SgNode | None) -> str | None:
    """Extract unquoted text of the leading docstring literal in container, or None if absent."""
    if container is None:
        return None
    children = [c for c in container.named_children() if c.kind() != "comment"]
    if not children or children[0].kind() != "expression_statement":
        return None
    stmt_children = children[0].named_children()
    if not stmt_children or stmt_children[0].kind() != "string":
        return None
    raw = stmt_children[0].text().lstrip("rRuUfFbB")
    for delim in ('"""', "'''", '"', "'"):
        if raw.startswith(delim) and raw.endswith(delim) and len(raw) >= 2 * len(delim):
            return raw[len(delim) : -len(delim)]
    return raw


def has_python_docstring(container: SgNode | None) -> bool:
    """Return True if the first statement inside container is a string literal docstring."""
    return extract_python_docstring_text(container) is not None


def is_overload_decorated(fn_node: SgNode) -> bool:
    """Return True if fn_node is decorated with @overload or @typing.overload."""
    parent = fn_node.parent()
    if parent is None or parent.kind() != "decorated_definition":
        return False
    for child in parent.named_children():
        if child.kind() == "decorator":
            dec_text = child.text().lstrip("@").strip()
            if dec_text in {"overload", "typing.overload"}:
                return True
    return False


def is_in_type_checking_guard(node: SgNode) -> bool:
    """Return True if node resides inside the consequence block of an `if TYPE_CHECKING:` guard."""
    node_start = node.range().start.index
    node_end = node.range().end.index
    curr: SgNode | None = node.parent()
    while curr is not None:
        if curr.kind() == "if_statement":
            cond = curr.field("condition")
            conseq = curr.field("consequence")
            cond_text = cond.text().strip() if cond is not None else ""
            is_tc_cond = "TYPE_CHECKING" in cond_text and "not" not in cond_text.split()
            if (
                is_tc_cond
                and conseq is not None
                and conseq.range().start.index <= node_start
                and node_end <= conseq.range().end.index
            ):
                return True
        curr = curr.parent()
    return False


def extract_param_name(param: SgNode) -> str:
    """Extract clean parameter identifier name (without leading '*') from a parameter CST node."""
    name_node = param.field("name")
    if name_node is not None:
        return name_node.text().lstrip("*")
    for child in param.named_children():
        if child.kind() in {"identifier", "list_splat_pattern", "dictionary_splat_pattern"}:
            return child.text().lstrip("*")
    return param.text().split(":")[0].split("=")[0].strip().lstrip("*")


def extract_callable_param_names(fn_node: SgNode) -> list[str]:
    """Return ordered parameter names of fn_node excluding 'self', 'cls', comments, and separators."""
    params_node = fn_node.field("parameters")
    if params_node is None:
        return []
    names: list[str] = []
    for param in params_node.named_children():
        if param.kind() not in VALID_PARAM_KINDS:
            continue
        pname = extract_param_name(param)
        if pname and pname not in {"self", "cls"}:
            names.append(pname)
    return names
