# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Shared CST traversal helpers and mixed HTML+PHP line-preserving normalizer for PHP AST analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Optional

from ast_grep_py import SgNode

TYPE_DECL_KINDS: Final[tuple[str, ...]] = (
    "class_declaration",
    "interface_declaration",
    "trait_declaration",
    "enum_declaration",
)
CALLABLE_DECL_KINDS: Final[frozenset[str]] = frozenset({"function_definition", "method_declaration"})
PARAM_NODE_KINDS: Final[frozenset[str]] = frozenset(
    {"simple_parameter", "variadic_parameter", "property_promotion_parameter"}
)
INCLUDE_EXPR_KINDS: Final[tuple[str, ...]] = (
    "include_expression",
    "include_once_expression",
    "require_expression",
    "require_once_expression",
)
SUPERGLOBALS: Final[frozenset[str]] = frozenset(
    {"$_GET", "$_POST", "$_REQUEST", "$_COOKIE", "$_SESSION", "$_FILES", "$_SERVER", "$_ENV", "$GLOBALS"}
)
USER_INPUT_SUPERGLOBALS: Final[frozenset[str]] = frozenset(
    {"$_GET", "$_POST", "$_REQUEST", "$_COOKIE", "$_FILES"}
)
NON_TYPE_PARAM_CHILD_KINDS: Final[frozenset[str]] = frozenset(
    {
        "visibility_modifier",
        "readonly_modifier",
        "attribute_list",
        "reference_modifier",
        "variadic_placeholder",
        "&",
        "...",
    }
)


@dataclass
class _PhpNormState:
    """Mutable tokenizer state for line-preserving mixed HTML+PHP normalization."""

    in_php: bool = False
    quote: str = ""
    line_comment: bool = False
    block_comment: bool = False
    sig: str = ";"


def _step_outside_php(source: str, i: int, out: list[str]) -> tuple[int, bool, str]:
    """Advance one token while outside PHP tags; return (next_index, entered_php, sig_char_override)."""
    n = len(source)
    if source.startswith("<?php", i) and (i + 5 == n or source[i + 5].isspace()):
        return i + 5, True, ""
    if source.startswith("<?=", i):
        out.append(" echo ")
        return i + 3, True, "o"
    if source.startswith("<?", i) and not source.startswith("<?xml", i):
        return i + 2, True, ""
    if source[i] == "\n":
        out.append("\n")
    return i + 1, False, ""


def _step_inside_comment_or_quote(
    source: str,
    i: int,
    out: list[str],
    state: _PhpNormState,
) -> int:
    """Advance one token while inside a block comment, line comment, or string literal."""
    ch = source[i]
    if state.block_comment:
        if source.startswith("*/", i):
            out.append("*/")
            state.block_comment = False
            return i + 2
        out.append(ch)
        return i + 1

    if state.line_comment:
        if source.startswith("?>", i):
            if state.sig not in {";", ":", "{", "}"}:
                out.append("; ")
                state.sig = ";"
            state.line_comment = False
            state.in_php = False
            return i + 2
        out.append(ch)
        if ch == "\n":
            state.line_comment = False
        return i + 1

    out.append(ch)
    if ch == "\\" and i + 1 < len(source):
        out.append(source[i + 1])
        return i + 2
    if ch == state.quote:
        state.quote = ""
    return i + 1


def _step_inside_php_code(source: str, i: int, out: list[str], state: _PhpNormState) -> int:
    """Advance one token of active PHP code outside comments/strings."""
    ch = source[i]
    if ch in {"'", '"'}:
        state.quote = ch
        out.append(ch)
        state.sig = ch
        return i + 1
    if source.startswith("/*", i):
        state.block_comment = True
        out.append("/*")
        return i + 2
    if source.startswith("#[", i):
        out.append("#[")
        state.sig = "["
        return i + 2
    if source.startswith("//", i) or ch == "#":
        state.line_comment = True
        out.append("//" if ch == "/" else "#")
        return i + (2 if ch == "/" else 1)
    if source.startswith("?>", i):
        if state.sig not in {";", ":", "{", "}"}:
            out.append("; ")
            state.sig = ";"
        else:
            out.append(" ")
        state.in_php = False
        return i + 2
    out.append(ch)
    if not ch.isspace():
        state.sig = ch
    return i + 1


def normalize_php_source_for_cst(source: str) -> str:
    """Normalize mixed HTML+PHP templates into pure line-preserving PHP for tree-sitter-php CST parsing.

    Pure PSR-12 PHP files without closing tags (`?>`) or short echo tags (`<?=`) are returned untouched.
    For mixed HTML/PHP scripts, HTML regions outside PHP tags are replaced with exact newline counts and
    `<?= expr ?>` short echo tags are expanded into `echo expr;` while preserving 1:1 line numbers.
    """
    stripped = source.lstrip()
    if stripped.startswith("<?php") and "?>" not in source and "<?=" not in source:
        return source

    n = len(source)
    out: list[str] = ["<?php "]
    i = 0
    state = _PhpNormState()

    while i < n:
        if not state.in_php:
            i, entered, sig_override = _step_outside_php(source, i, out)
            if entered:
                state.in_php = True
                if sig_override:
                    state.sig = sig_override
        elif state.block_comment or state.line_comment or state.quote:
            i = _step_inside_comment_or_quote(source, i, out, state)
        else:
            i = _step_inside_php_code(source, i, out, state)

    if state.in_php and state.sig not in {";", ":", "{", "}"}:
        out.append(";")
    return "".join(out)


def extract_php_namespace(root: SgNode) -> str:
    r"""Return the declared PHP namespace in root (e.g. 'App\Services'), or empty string if global."""
    ns_def = root.find(kind="namespace_definition")
    if ns_def is None:
        return ""
    ns_name = ns_def.find(kind="namespace_name")
    return ns_name.text().strip() if ns_name is not None else ""


def extract_node_name(node: SgNode) -> str:
    """Extract the identifier child (`kind == 'name'`) of a PHP declaration node."""
    for child in node.children():
        if child.kind() == "name":
            return child.text().strip()
    return "<anonymous>"


def get_visibility(node: SgNode) -> str:
    """Return 'public', 'protected', or 'private' for a PHP member declaration (default 'public')."""
    for child in node.children():
        if child.kind() == "visibility_modifier":
            return child.text().strip().lower()
    return "public"


def iter_php_types(root: SgNode) -> list[tuple[str, SgNode]]:
    """Return (type_name, cst_node) pairs for all class/interface/trait/enum declarations in root."""
    found: list[tuple[str, SgNode]] = []
    for kind in TYPE_DECL_KINDS:
        for tnode in root.find_all(kind=kind):
            found.append((extract_node_name(tnode), tnode))
    found.sort(key=lambda item: item[1].range().start.index)
    return found


def enclosing_anon_class_node(node: SgNode) -> Optional[SgNode]:
    """Return the enclosing anonymous class CST node (`anonymous_class` or `object_creation_expression`), if any."""
    curr = node.parent()
    while curr is not None:
        ckind = curr.kind()
        if ckind in {"anonymous_class", "object_creation_expression"}:
            return curr
        if ckind in TYPE_DECL_KINDS:
            return None
        curr = curr.parent()
    return None


def iter_direct_type_methods(tnode: SgNode) -> list[SgNode]:
    """Return direct `method_declaration` nodes of `tnode`, excluding methods inside anonymous classes."""
    return [m for m in tnode.find_all(kind="method_declaration") if enclosing_anon_class_node(m) is None]


def format_method_symbol(mnode: SgNode) -> str:
    """Format a PHP `method_declaration` symbol, qualifying methods inside anonymous classes."""
    mname = extract_node_name(mnode)
    anon_line: Optional[int] = None
    outer_callable: Optional[str] = None
    owner_type: Optional[str] = None
    curr = mnode.parent()
    while curr is not None:
        ckind = curr.kind()
        if ckind in {"anonymous_class", "object_creation_expression"} and anon_line is None:
            parent = curr.parent()
            anchor = parent if parent is not None and parent.kind() == "object_creation_expression" else curr
            anon_line = anchor.range().start.line + 1
        elif ckind in {"method_declaration", "function_definition"} and outer_callable is None:
            outer_callable = extract_node_name(curr)
        elif ckind in TYPE_DECL_KINDS and owner_type is None:
            owner_type = extract_node_name(curr)
        curr = curr.parent()

    if anon_line is not None:
        anon_tag = f"<anon@L{anon_line}>"
        parts = [p for p in (owner_type, outer_callable, anon_tag, mname) if p]
        return "::".join(parts)
    return f"{owner_type}::{mname}" if owner_type else mname


def iter_php_callables(root: SgNode) -> list[tuple[str, SgNode]]:
    """Return (symbol, cst_node) pairs for all top-level functions and class/trait/anonymous methods in root."""
    callables: list[tuple[str, SgNode]] = [
        (extract_node_name(fn_node), fn_node) for fn_node in root.find_all(kind="function_definition")
    ]
    for mnode in root.find_all(kind="method_declaration"):
        callables.append((format_method_symbol(mnode), mnode))

    callables.sort(key=lambda item: item[1].range().start.index)
    return callables


def extract_formal_param_nodes(callable_node: SgNode) -> list[SgNode]:
    """Return parameter CST nodes inside `formal_parameters` of a function or method."""
    for child in callable_node.children():
        if child.kind() == "formal_parameters":
            return [p for p in child.children() if p.kind() in PARAM_NODE_KINDS]
    return []


def find_preceding_phpdoc(node: SgNode) -> Optional[str]:
    """Return the immediately preceding `/** ... */` PHPDoc comment text for node if present."""
    prev = node.prev()
    while prev is not None and prev.kind() == "attribute_list":
        prev = prev.prev()
    if prev is not None and prev.kind() == "comment":
        text = prev.text().strip()
        if text.startswith("/**") and not text.startswith("/***"):
            gap_lines = node.range().start.line - prev.range().end.line
            if gap_lines <= 2:
                return text
    return None


def enclosing_callable_symbol(node: SgNode) -> Optional[str]:
    """Return the enclosing function or `ClassName::method` symbol for node, if any."""
    curr = node.parent()
    while curr is not None:
        ckind = curr.kind()
        if ckind == "function_definition":
            return extract_node_name(curr)
        if ckind == "method_declaration":
            return format_method_symbol(curr)
        if ckind in TYPE_DECL_KINDS:
            return extract_node_name(curr)
        curr = curr.parent()
    return None


def strip_php_quotes(raw: str) -> str:
    """Strip surrounding single or double quotes from a PHP string literal."""
    text = raw.strip()
    if len(text) >= 2 and text[0] in {"'", '"'} and text[-1] == text[0]:
        return text[1:-1]
    return text
