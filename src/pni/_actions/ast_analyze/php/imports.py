# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP namespace `use` sorting and legacy `include`/`require` coupling checker."""

from __future__ import annotations

from pathlib import Path

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseImportChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitImportStats
from pni._actions.ast_analyze.php._helpers import (
    CALLABLE_DECL_KINDS,
    INCLUDE_EXPR_KINDS,
    TYPE_DECL_KINDS,
    extract_php_namespace,
)

_NESTED_SCOPE_KINDS = frozenset(
    {
        *CALLABLE_DECL_KINDS,
        "if_statement",
        "for_statement",
        "foreach_statement",
        "while_statement",
        "switch_statement",
        "try_statement",
    }
)


def _extract_use_targets(use_node: SgNode) -> list[str]:
    """Extract normalized fully qualified symbol names from a `namespace_use_declaration`."""
    group = use_node.find(kind="namespace_use_group")
    if group is not None:
        prefix_node = use_node.find(kind="namespace_name")
        prefix_base = prefix_node.text().strip().lstrip("\\") if prefix_node is not None else ""
        prefix = f"{prefix_base}\\" if prefix_base else ""
        items: list[str] = []
        for clause in group.find_all(kind="namespace_use_clause"):
            items.append(f"{prefix}{clause.text().strip()}")
        return items

    clauses = use_node.find_all(kind="namespace_use_clause")
    return [c.text().strip().lstrip("\\") for c in clauses if c.text().strip()]


def _is_inside_nested_scope(node: SgNode) -> bool:
    """Return True if node sits inside a function, method, or conditional/loop block."""
    curr = node.parent()
    while curr is not None:
        if curr.kind() in _NESTED_SCOPE_KINDS:
            return True
        curr = curr.parent()
    return False


def _is_trait_use_inside_class(node: SgNode) -> bool:
    """Return True if node is inside a class/trait body rather than top-level namespace imports."""
    curr = node.parent()
    while curr is not None:
        if curr.kind() in TYPE_DECL_KINDS:
            return True
        curr = curr.parent()
    return False


class PhpImportChecker(BaseImportChecker):
    """Evaluate PSR-12 `use` ordering and flag procedural `include`/`require` coupling."""

    def discover_root_packages(self, units: list[ParsedUnit], project_root: Path) -> set[str]:
        """Discover internal root namespace prefixes (e.g. 'App', 'Domain') across parsed units."""
        _ = project_root
        roots: set[str] = set()
        for unit in units:
            ns = extract_php_namespace(unit.root)
            if ns:
                roots.add(ns.split("\\", maxsplit=1)[0])
        return roots

    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Check top-level `use` alphabetical order and flag manual or nested `include`/`require` calls."""
        _ = root_packages
        unsorted: list[CodeLocation] = []
        late: list[CodeLocation] = []

        use_nodes = [
            u for u in unit.root.find_all(kind="namespace_use_declaration") if not _is_trait_use_inside_class(u)
        ]
        seen_keys: list[tuple[str, int, str]] = []
        for unode in use_nodes:
            targets = _extract_use_targets(unode)
            if not targets:
                continue
            line = unode.range().start.line + 1
            primary = targets[0]
            # Separate `use function` / `use const` groups from class `use` declarations
            raw_text = unode.text().strip()
            group_prefix = (
                "2_const:"
                if raw_text.lower().startswith("use const ")
                else ("1_func:" if raw_text.lower().startswith("use function ") else "0_class:")
            )
            seen_keys.append((f"{group_prefix}{primary.lower()}", line, primary))

        for idx in range(1, len(seen_keys)):
            prev_key, _, prev_sym = seen_keys[idx - 1]
            curr_key, curr_line, curr_sym = seen_keys[idx]
            if curr_key < prev_key:
                unsorted.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=curr_line,
                        symbol=curr_sym,
                        detail=f"Out-of-order PHP 'use {curr_sym}' after '{prev_sym}' (PSR-12 alphabetical order)",
                    )
                )
                break

        has_namespace = bool(extract_php_namespace(unit.root))
        for inc_kind in INCLUDE_EXPR_KINDS:
            for inc_node in unit.root.find_all(kind=inc_kind):
                inc_text = inc_node.text().strip()
                # Allow Composer's standard `require __DIR__ . '/vendor/autoload.php'` in entrypoints
                if "vendor/autoload.php" in inc_text:
                    continue
                line = inc_node.range().start.line + 1
                if _is_inside_nested_scope(inc_node) or has_namespace:
                    late.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line,
                            symbol=inc_kind.removesuffix("_expression"),
                            detail=f"Manual '{inc_text[:60]}' inside scoped/namespaced code — prefer PSR-4 autoload",
                        )
                    )
                else:
                    late.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line,
                            symbol=inc_kind.removesuffix("_expression"),
                            detail=f"Procedural file include '{inc_text[:60]}' — migrate to Composer PSR-4 autoloading",
                        )
                    )

        is_clean = not unsorted and not late
        return UnitImportStats(
            is_clean=is_clean,
            unsorted_imports=unsorted,
            wildcard_imports=[],
            late_imports=late,
        )
