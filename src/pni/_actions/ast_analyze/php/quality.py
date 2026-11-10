# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP complexity, superglobal/global state coupling, `@` error suppression, and spaghetti script checker."""

from __future__ import annotations

import re
from typing import ClassVar, Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseQualityChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit
from pni._actions.ast_analyze.php._helpers import (
    SUPERGLOBALS,
    enclosing_callable_symbol,
    extract_formal_param_nodes,
    extract_node_name,
    get_visibility,
    iter_direct_type_methods,
    iter_php_callables,
    iter_php_types,
)

_HTML_CLOSE_TAG_RE: Final[re.Pattern[str]] = re.compile(r"\?>")
_SQL_KEYWORD_RE: Final[re.Pattern[str]] = re.compile(
    r"(?i)\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b"
)


class PhpQualityChecker(BaseQualityChecker):
    """Evaluate PHP LOC, complexity, superglobals, `@` error suppression, `die`/`exit`, and HTML+SQL mixing."""

    branch_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "else_if_clause",
            "for_statement",
            "foreach_statement",
            "while_statement",
            "do_statement",
            "case_statement",
            "catch_clause",
            "conditional_expression",
            "match_conditional_expression",
        }
    )
    nesting_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "foreach_statement",
            "while_statement",
            "do_statement",
            "switch_statement",
            "try_statement",
            "anonymous_function",
        }
    )

    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment PHP/template lines in unit."""
        loc = 0
        in_block_comment = False
        for raw_line in unit.source.splitlines():
            s = raw_line.strip()
            if not s:
                continue
            if in_block_comment:
                if "*/" in s:
                    in_block_comment = False
                continue
            if s.startswith("/*"):
                if "*/" not in s:
                    in_block_comment = True
                continue
            if s.startswith("//") or (s.startswith("#") and not s.startswith("#[")):
                continue
            loc += 1
        return loc

    def count_classes(self, unit: ParsedUnit) -> int:
        """Count class, interface, trait, and enum declarations in unit."""
        return len(iter_php_types(unit.root))

    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, SgNode]]:
        """Return (symbol, cst_node) pairs for all functions and methods in unit."""
        return iter_php_callables(unit.root)

    def count_callable_params(self, node: SgNode) -> int:
        """Count formal parameters on a PHP function or method."""
        return len(extract_formal_param_nodes(node))

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Extract public types and public functions/methods for module_inventory."""
        pub_types = sorted({name for name, _ in iter_php_types(unit.root)})
        pub_callables: list[str] = [
            extract_node_name(fn) for fn in unit.root.find_all(kind="function_definition")
        ]
        for type_name, tnode in iter_php_types(unit.root):
            for mnode in iter_direct_type_methods(tnode):
                if get_visibility(mnode) == "public":
                    pub_callables.append(f"{type_name}::{extract_node_name(mnode)}")
        return pub_types, sorted(set(pub_callables))

    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect superglobal reads (`$_GET`, `$_POST`), `global $x`, and mutable public static properties."""
        findings: list[CodeLocation] = []
        seen_lines: set[tuple[int, str]] = set()

        for gdecl in unit.root.find_all(kind="global_declaration"):
            line = gdecl.range().start.line + 1
            sym = enclosing_callable_symbol(gdecl) or "<script>"
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line,
                    symbol=sym,
                    detail=f"Global state coupling via '{gdecl.text().strip()}'",
                )
            )

        for vnode in unit.root.find_all(kind="variable_name"):
            vtext = vnode.text().strip()
            if vtext == "$_ENV":
                continue
            if vtext in SUPERGLOBALS:
                line = vnode.range().start.line + 1
                key = (line, vtext)
                if key in seen_lines:
                    continue
                seen_lines.add(key)
                sym = enclosing_callable_symbol(vnode) or "<script>"
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=sym,
                        detail=(
                            f"Direct superglobal '{vtext}' access — "
                            "encapsulate via typed Request/Session abstraction"
                        ),
                    )
                )

        for _, tnode in iter_php_types(unit.root):
            for prop in tnode.find_all(kind="property_declaration"):
                prop_txt = prop.text()
                if "static" in prop_txt and "readonly" not in prop_txt and get_visibility(prop) == "public":
                    vnode = prop.find(kind="variable_name")
                    pname = vnode.text().strip() if vnode is not None else "static_property"
                    findings.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=prop.range().start.line + 1,
                            symbol=pname,
                            detail="Mutable 'public static' property introduces shared global state",
                        )
                    )
        return findings

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `@` error suppression, empty catch blocks, abrupt `die`/`exit`, and mixed HTML+SQL scripts."""
        idioms: list[CodeLocation] = []

        for sup in unit.root.find_all(kind="error_suppression_expression"):
            line = sup.range().start.line + 1
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line,
                    symbol=enclosing_callable_symbol(sup) or "@",
                    detail=f"Error-suppression operator '{sup.text().strip()[:45]}' hides runtime failures",
                )
            )

        for catch_node in unit.root.find_all(kind="catch_clause"):
            body = catch_node.find(kind="compound_statement")
            if body is not None:
                stmts = [c for c in body.children() if c.kind() not in {"{", "}", "comment"}]
                if not stmts:
                    idioms.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=catch_node.range().start.line + 1,
                            symbol=enclosing_callable_symbol(catch_node) or "catch",
                            detail="Empty catch block silently swallows exceptions",
                        )
                    )

        for exit_node in unit.root.find_all(kind="exit_statement"):
            line = exit_node.range().start.line + 1
            if line <= 25 and "ABSPATH" in "\n".join(unit.source.splitlines()[:25]):
                continue
            exit_snip = exit_node.text().strip()[:35]
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line,
                    symbol=enclosing_callable_symbol(exit_node) or "exit",
                    detail=f"Abrupt process termination '{exit_snip}' — throw domain exception or return Response",
                )
            )

        # Mixed HTML + SQL + logic "spaghetti script" detection
        close_tags = len(_HTML_CLOSE_TAG_RE.findall(unit.source))
        if close_tags >= 1 and _SQL_KEYWORD_RE.search(unit.source):
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=1,
                    symbol=unit.file_path.name,
                    detail="Spaghetti script mixes inline HTML markup ('?>') and raw SQL queries in the same file",
                )
            )
        return idioms
