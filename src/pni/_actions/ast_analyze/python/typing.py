# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python static type annotation, bare generic, Any usage, and unscoped type:ignore AST checker."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTypingChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitTypingStats
from pni._actions.ast_analyze.python._helpers import (
    VALID_PARAM_KINDS,
    extract_param_name,
    function_symbol_name,
)

_UNTYPED_PARAM_KINDS: Final[frozenset[str]] = frozenset(
    {"identifier", "default_parameter", "list_splat_pattern", "dictionary_splat_pattern"}
)
_TYPED_PARAM_KINDS: Final[frozenset[str]] = frozenset({"typed_parameter", "typed_default_parameter"})
_BARE_GENERIC_BUILTINS: Final[frozenset[str]] = frozenset({"list", "dict", "tuple", "set"})
_EXEMPT_CLASS_ATTRS: Final[frozenset[str]] = frozenset({"model_config", "__all__", "__slots__"})
_UNSCOPED_IGNORE_RE = re.compile(r"#\s*(type|pyright)\s*:\s*ignore(?!\s*\[)")


def _node_uses_any(type_node: SgNode | None) -> bool:
    """Return True if a type annotation node references typing.Any or Any."""
    if type_node is None:
        return False
    return any(ident.text() == "Any" for ident in type_node.find_all(kind="identifier"))


def _find_bare_generics(type_node: SgNode | None) -> list[str]:
    """Find unparameterized builtin container types (e.g. bare 'list' instead of 'list[T]')."""
    if type_node is None:
        return []
    found: list[str] = []
    for ident in type_node.find_all(kind="identifier"):
        name = ident.text()
        if name not in _BARE_GENERIC_BUILTINS:
            continue
        parent = ident.parent()
        is_generic_head = (
            parent is not None
            and parent.kind() == "generic_type"
            and (first := parent.child(0)) is not None
            and first.range().start.index == ident.range().start.index
        )
        if not is_generic_head and name not in found:
            found.append(name)
    return found


def _collect_type_weaknesses(
    type_node: SgNode | None,
    rel_file: str,
    lineno: int,
    symbol: str,
    target_label: str,
) -> list[CodeLocation]:
    """Collect 'Any' and bare-generic findings for a single parameter or return type node."""
    weak: list[CodeLocation] = []
    if _node_uses_any(type_node):
        weak.append(CodeLocation(file=rel_file, line=lineno, symbol=symbol, detail=f"{target_label} uses 'Any'"))
    for bare in _find_bare_generics(type_node):
        weak.append(
            CodeLocation(
                file=rel_file,
                line=lineno,
                symbol=symbol,
                detail=f"{target_label} uses unparameterized '{bare}' (missing type arguments)",
            )
        )
    return weak


def _inspect_function_typing(
    fn_node: SgNode,
    rel_file: str,
) -> tuple[bool, list[CodeLocation], list[CodeLocation]]:
    """Inspect a Python function_definition node for missing annotations and weak types."""
    missing: list[CodeLocation] = []
    weak_locs: list[CodeLocation] = []
    missing_params: list[str] = []
    lineno = fn_node.range().start.line + 1
    fn_name = function_symbol_name(fn_node)

    params_node = fn_node.field("parameters")
    if params_node is not None:
        for param in params_node.named_children():
            pkind = param.kind()
            if pkind not in VALID_PARAM_KINDS:
                continue
            pname = extract_param_name(param)
            if pname in {"self", "cls", ""}:
                continue
            if pkind in _UNTYPED_PARAM_KINDS:
                missing_params.append(pname)
            elif pkind in _TYPED_PARAM_KINDS:
                weak_locs.extend(
                    _collect_type_weaknesses(param.field("type"), rel_file, lineno, fn_name, f"Parameter '{pname}'")
                )

    ret_node = fn_node.field("return_type")
    if ret_node is None:
        missing_params.append("return")
    else:
        weak_locs.extend(_collect_type_weaknesses(ret_node, rel_file, lineno, fn_name, "Return annotation"))

    is_typed = len(missing_params) == 0
    if not is_typed:
        missing.append(
            CodeLocation(
                file=rel_file,
                line=lineno,
                symbol=fn_name,
                detail=f"Missing annotations: {', '.join(missing_params)}",
            )
        )
    return is_typed, missing, weak_locs


def _is_enum_class(cls_node: SgNode) -> bool:
    """Return True if cls_node inherits from Enum / StrEnum / IntEnum."""
    superclasses = cls_node.field("superclasses")
    if superclasses is None:
        return False
    text = superclasses.text()
    return any(base in text for base in ("Enum", "StrEnum", "IntEnum", "Flag"))


def _inspect_class_attributes(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect untyped public class attribute assignments on non-Enum classes."""
    issues: list[CodeLocation] = []
    for cls_node in unit.root.find_all(kind="class_definition"):
        if _is_enum_class(cls_node):
            continue
        cname_node = cls_node.field("name")
        cname = cname_node.text() if cname_node is not None else "<class>"
        body = cls_node.field("body")
        if body is None:
            continue
        for stmt in body.named_children():
            if stmt.kind() != "expression_statement":
                continue
            children = stmt.named_children()
            if not children or children[0].kind() != "assignment":
                continue
            assign = children[0]
            left = assign.field("left")
            if left is None or left.kind() != "identifier" or assign.field("type") is not None:
                continue
            attr_name = left.text()
            if attr_name in _EXEMPT_CLASS_ATTRS or (attr_name.startswith("__") and attr_name.endswith("__")):
                continue
            issues.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=assign.range().start.line + 1,
                    symbol=f"{cname}.{attr_name}",
                    detail=f"Untyped class attribute '{attr_name}'",
                )
            )
    return issues


def _inspect_unscoped_ignores(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect bare '# type: ignore' or '# pyright: ignore' comments without specific error codes."""
    ignores: list[CodeLocation] = []
    for cnode in unit.root.find_all(kind="comment"):
        text = cnode.text().strip()
        if _UNSCOPED_IGNORE_RE.search(text):
            ignores.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=cnode.range().start.line + 1,
                    symbol="type: ignore",
                    detail=f"Unscoped type ignore without '[error-code]': {text} (PGH003)",
                )
            )
    return ignores


class PythonTypingChecker(BaseTypingChecker):
    """Check Python callable/attribute type annotations, bare generics, Any, and unscoped ignores."""

    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect all callables, class attributes, and ignore comments in a Python unit."""
        functions = unit.root.find_all(kind="function_definition")
        safe_count = 0
        issues: list[CodeLocation] = []
        weak_usages: list[CodeLocation] = []

        for fn_node in functions:
            is_typed, fn_issues, fn_weak = _inspect_function_typing(fn_node, unit.rel_path)
            if is_typed:
                safe_count += 1
            issues.extend(fn_issues)
            weak_usages.extend(fn_weak)

        issues.extend(_inspect_class_attributes(unit))
        ignores = _inspect_unscoped_ignores(unit)

        return UnitTypingStats(
            total_callables=len(functions),
            type_safe_callables=safe_count,
            type_safety_issues=issues,
            weak_type_usages=weak_usages,
            unscoped_type_ignores=ignores,
        )
