# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unified Tree-sitter CST abstraction with lazy loading and 1-pass indexed traversal."""

from __future__ import annotations

import bisect
import importlib
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from pni._languages.registry import GrammarProviderSpec, get_grammar_provider

if TYPE_CHECKING:
    from tree_sitter import Language, Node, Parser, Tree

_LANGUAGE_CACHE: dict[str, Language] = {}
_PARSER_CACHE: dict[str, Parser] = {}


@dataclass(frozen=True, slots=True)
class CstPos:
    """Zero-based line/column and byte offset position inside a parsed source document."""

    line: int
    column: int
    index: int


@dataclass(frozen=True, slots=True)
class CstRange:
    """Start and end source positions of a CST node."""

    start: CstPos
    end: CstPos


def _is_same_or_descendant(candidate: Node, ancestor: Node) -> bool:
    """Return True if candidate is ancestor itself or a descendant of ancestor."""
    curr: Node | None = candidate
    target_start = ancestor.start_byte
    target_end = ancestor.end_byte
    while curr is not None:
        if curr == ancestor:
            return True
        if curr.start_byte < target_start or curr.end_byte > target_end:
            return False
        curr = curr.parent
    return False


class _CstDocument:
    """Parsed Tree-sitter document owning raw UTF-8 bytes, CST tree, and lazy kind index."""

    __slots__ = ("_index", "grammar", "source_bytes", "tree")

    def __init__(self, grammar: str, source_bytes: bytes, tree: Tree) -> None:
        """Initialize parsed document wrapper."""
        self.grammar = grammar
        self.source_bytes = source_bytes
        self.tree = tree
        self._index: dict[str, tuple[list[int], list[Node]]] | None = None

    def _ensure_index(self) -> dict[str, tuple[list[int], list[Node]]]:
        """Build a 1-pass TreeCursor kind->(start_bytes, nodes) index lazily on first search."""
        if self._index is not None:
            return self._index

        by_kind: dict[str, list[Node]] = {}
        cursor = self.tree.walk()
        visited_children = False
        while True:
            if not visited_children:
                node = cursor.node
                if node is not None:
                    node_type = node.type
                    if node.is_named or (node_type and node_type[0].isalpha()):
                        by_kind.setdefault(node_type, []).append(node)
                if cursor.goto_first_child():
                    continue
            if cursor.goto_next_sibling():
                visited_children = False
            elif cursor.goto_parent():
                visited_children = True
            else:
                break

        self._index = {k: ([n.start_byte for n in ns], ns) for k, ns in by_kind.items()}
        return self._index

    def find_all_in_subtree(self, anchor: Node, kind: str) -> list[CstNode]:
        """Return all CST nodes matching kind inside anchor's subtree (including anchor itself)."""
        idx = self._ensure_index()
        pair = idx.get(kind)
        if pair is None:
            if not kind or kind[0].isalpha():
                return []
            return self._fallback_scan(anchor, kind)

        starts, nodes = pair
        start_b = anchor.start_byte
        end_b = anchor.end_byte
        lo = bisect.bisect_left(starts, start_b)
        hi = bisect.bisect_right(starts, end_b)

        matches: list[CstNode] = []
        for pos in range(lo, hi):
            cand = nodes[pos]
            cand_end = cand.end_byte
            if cand_end > end_b:
                continue
            if cand.start_byte == start_b and cand_end == end_b and not _is_same_or_descendant(cand, anchor):
                continue
            matches.append(CstNode(self, cand))
        return matches

    def find_first_in_subtree(self, anchor: Node, kind: str) -> CstNode | None:
        """Return the first pre-order CST node matching kind inside anchor's subtree (including anchor)."""
        idx = self._ensure_index()
        pair = idx.get(kind)
        if pair is None:
            if not kind or kind[0].isalpha():
                return None
            found = self._fallback_scan(anchor, kind, first_only=True)
            return found[0] if found else None

        starts, nodes = pair
        start_b = anchor.start_byte
        end_b = anchor.end_byte
        lo = bisect.bisect_left(starts, start_b)
        hi = bisect.bisect_right(starts, end_b)

        for pos in range(lo, hi):
            cand = nodes[pos]
            cand_end = cand.end_byte
            if cand_end > end_b:
                continue
            if cand.start_byte == start_b and cand_end == end_b and not _is_same_or_descendant(cand, anchor):
                continue
            return CstNode(self, cand)
        return None

    def _fallback_scan(self, anchor: Node, kind: str, *, first_only: bool = False) -> list[CstNode]:
        """Fallback stack scan for unnamed punctuation/symbol kinds omitted from the fast index."""
        out: list[CstNode] = []
        stack: list[Node] = [anchor]
        while stack:
            curr = stack.pop()
            if curr.type == kind:
                out.append(CstNode(self, curr))
                if first_only:
                    return out
            children = curr.children
            if children:
                stack.extend(reversed(children))
        return out


class CstNode:
    """High-performance Tree-sitter CST node wrapper with ergonomic traversal helpers."""

    __slots__ = ("_doc", "_node")

    def __init__(self, doc: _CstDocument, node: Node) -> None:
        """Wrap a raw tree_sitter.Node bound to its parsed document."""
        self._doc = doc
        self._node = node

    def _wrap(self, raw: Node) -> CstNode:
        """Wrap a sibling/child/parent raw tree_sitter.Node in the same document."""
        return CstNode(self._doc, raw)

    def kind(self) -> str:
        """Return the grammar node type string."""
        return self._node.type

    def is_named(self) -> bool:
        """Return True if this node is a named grammar rule rather than anonymous punctuation."""
        return self._node.is_named

    def is_leaf(self) -> bool:
        """Return True if this node has zero children."""
        return self._node.child_count == 0

    def child(self, nth: int) -> CstNode | None:
        """Return the nth direct child node (0-based), or None if out of bounds."""
        child = self._node.child(nth)
        return self._wrap(child) if child is not None else None

    def text(self) -> str:
        """Return the UTF-8 decoded source text spanned by this node."""
        return self._doc.source_bytes[self._node.start_byte : self._node.end_byte].decode(
            "utf-8",
            errors="replace",
        )

    def range(self) -> CstRange:
        """Return zero-based start/end line, column, and byte offset positions."""
        sp = self._node.start_point
        ep = self._node.end_point
        return CstRange(
            start=CstPos(line=sp.row, column=sp.column, index=self._node.start_byte),
            end=CstPos(line=ep.row, column=ep.column, index=self._node.end_byte),
        )

    def children(self) -> list[CstNode]:
        """Return all direct child nodes (named and unnamed)."""
        return [self._wrap(c) for c in self._node.children]

    def named_children(self) -> list[CstNode]:
        """Return direct named child nodes."""
        return [self._wrap(c) for c in self._node.named_children]

    def field(self, name: str) -> CstNode | None:
        """Return the first direct child bound to grammar field `name`, if present."""
        child = self._node.child_by_field_name(name)
        return self._wrap(child) if child is not None else None

    def field_children(self, name: str) -> list[CstNode]:
        """Return all direct children bound to grammar field `name`."""
        return [self._wrap(c) for c in self._node.children_by_field_name(name)]

    def parent(self) -> CstNode | None:
        """Return the immediate parent CST node, or None for the root node."""
        p = self._node.parent
        return self._wrap(p) if p is not None else None

    def prev(self) -> CstNode | None:
        """Return the immediately preceding sibling CST node (named or unnamed), if any."""
        p = self._node.prev_sibling
        return self._wrap(p) if p is not None else None

    def inside(self, *, kind: str) -> bool:
        """Return True if any strict ancestor node has node type equal to `kind`."""
        curr = self._node.parent
        while curr is not None:
            if curr.type == kind:
                return True
            curr = curr.parent
        return False

    def has(self, *, kind: str) -> bool:
        """Return True if any node in this subtree matches `kind` (fast C check for 'ERROR')."""
        if kind == "ERROR":
            return self._node.has_error
        return self._doc.find_first_in_subtree(self._node, kind) is not None

    def find(self, *, kind: str) -> CstNode | None:
        """Return the first pre-order node matching `kind` within this subtree (including self)."""
        return self._doc.find_first_in_subtree(self._node, kind)

    def find_all(self, *, kind: str) -> list[CstNode]:
        """Return all pre-order nodes matching `kind` within this subtree (including self)."""
        return self._doc.find_all_in_subtree(self._node, kind)

    def __eq__(self, other: object) -> bool:
        """Return True when two wrappers reference the exact same underlying CST node."""
        if not isinstance(other, CstNode):
            return NotImplemented
        return self._doc is other._doc and self._node == other._node

    def __hash__(self) -> int:
        """Hash by document identity, byte span, and kind."""
        return hash((id(self._doc), self._node.start_byte, self._node.end_byte, self._node.type))


def _load_language_from_spec(spec: GrammarProviderSpec) -> Language:
    """Lazily import tree-sitter and build a cached Language instance for spec."""
    ts_mod = importlib.import_module("tree_sitter")
    language_ctor = getattr(ts_mod, "Language")

    if spec.source == "language_pack":
        pack_mod = importlib.import_module(spec.module_name)
        pack_loader = getattr(pack_mod, spec.callable_name)
        return cast("Language", pack_loader(spec.grammar_id))

    grammar_mod = importlib.import_module(spec.module_name)
    loader = getattr(grammar_mod, spec.callable_name)
    raw = loader()
    if isinstance(raw, language_ctor):
        return cast("Language", raw)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return cast("Language", language_ctor(raw))


def get_tree_sitter_language(grammar: str) -> Language:
    """Return a cached tree_sitter.Language instance for `grammar`."""
    key = grammar.strip().lower()
    cached = _LANGUAGE_CACHE.get(key)
    if cached is not None:
        return cached

    spec = get_grammar_provider(key)
    if spec is None:
        msg = f"Unsupported Tree-sitter grammar '{grammar}'."
        raise ValueError(msg)

    lang = _load_language_from_spec(spec)
    _LANGUAGE_CACHE[key] = lang
    return lang


def _get_parser(grammar: str) -> Parser:
    """Return a cached tree_sitter.Parser configured for `grammar`."""
    key = grammar.strip().lower()
    cached = _PARSER_CACHE.get(key)
    if cached is not None:
        return cached

    ts_mod = importlib.import_module("tree_sitter")
    parser = ts_mod.Parser(get_tree_sitter_language(key))
    _PARSER_CACHE[key] = parser
    return parser


def parse_cst(source: str, grammar: str) -> CstNode:
    """Parse source text with the cached Tree-sitter parser for `grammar` and return its root CstNode.

    Args:
        source: UTF-8 source text to parse.
        grammar: Registered grammar identifier (e.g. 'python', 'java', 'php', 'go', 'typescript', 'tsx').

    Returns:
        CstNode: Root CST node bound to a lazily indexed parsed document.
    """
    source_bytes = source.encode("utf-8")
    parser = _get_parser(grammar)
    tree = parser.parse(source_bytes)
    doc = _CstDocument(grammar=grammar, source_bytes=source_bytes, tree=tree)
    return CstNode(doc, tree.root_node)
