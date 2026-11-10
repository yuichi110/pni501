# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go internal package dependency graph, go.mod manifest cross-check, and boundary violations."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from pni._actions.ast_analyze.base import BaseDependencyChecker
from pni._actions.ast_analyze.go._helpers import (
    extract_package_name,
    parse_go_module_info,
)
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit


def _unit_pkg_key(unit: ParsedUnit, project_root: Path) -> str:
    """Return canonical internal package identifier (relative dir or package name) for a Go unit."""
    if unit.file_path.is_relative_to(project_root):
        rel_dir = unit.file_path.parent.relative_to(project_root).as_posix()
        if rel_dir and rel_dir != ".":
            return rel_dir
    return extract_package_name(unit) or "root"


def _iter_unit_import_paths(unit: ParsedUnit) -> list[tuple[str, int]]:
    """Return `(import_path, line_1based)` for all imports in a Go unit."""
    items: list[tuple[str, int]] = []
    for spec in unit.root.find_all(kind="import_spec"):
        path_node = spec.field("path")
        if path_node is None:
            continue
        imp_path = path_node.text().strip().strip('"`')
        if imp_path:
            items.append((imp_path, spec.range().start.line + 1))
    return items


class GoDependencyChecker(BaseDependencyChecker):
    """Build Go internal package graph, check `go.mod` direct requires, and verify `pkg/` vs `cmd/`/`internal/`."""

    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Build adjacency list of internal Go package dependencies."""
        mod_path, _ = parse_go_module_info(project_root)
        known_pkgs = {_unit_pkg_key(u, project_root) for u in units}
        edges: dict[str, set[str]] = {pkg: set() for pkg in known_pkgs}

        for unit in units:
            src_pkg = _unit_pkg_key(unit, project_root)
            for imp_path, _line in _iter_unit_import_paths(unit):
                target_pkg = ""
                if mod_path and imp_path == mod_path:
                    target_pkg = next((p for p in known_pkgs if "/" not in p), "root")
                elif mod_path and imp_path.startswith(f"{mod_path}/"):
                    sub = imp_path.removeprefix(f"{mod_path}/")
                    if sub in known_pkgs:
                        target_pkg = sub
                if target_pkg and target_pkg != src_pkg:
                    edges.setdefault(src_pkg, set()).add(target_pkg)

        return {pkg: sorted(targets) for pkg, targets in sorted(edges.items())}

    def check_manifest_dependencies(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> tuple[list[str], list[CodeLocation]]:
        """Cross-check third-party imports in Go files against direct `require` directives in `go.mod`."""
        mod_path, direct_requires = parse_go_module_info(project_root)
        if not mod_path and not direct_requires:
            return [], []

        used_requires: set[str] = set()
        undeclared: list[CodeLocation] = []
        seen_undeclared: set[tuple[str, str]] = set()

        for unit in units:
            for imp_path, line_no in _iter_unit_import_paths(unit):
                if mod_path and (imp_path == mod_path or imp_path.startswith(f"{mod_path}/")):
                    continue
                first_seg = imp_path.split("/", 1)[0]
                if "." not in first_seg:
                    continue
                matched_mods = [
                    req_mod
                    for req_mod in direct_requires
                    if imp_path == req_mod or imp_path.startswith(f"{req_mod}/")
                ]
                if matched_mods:
                    used_requires.update(matched_mods)
                elif direct_requires and (unit.rel_path, imp_path) not in seen_undeclared:
                    seen_undeclared.add((unit.rel_path, imp_path))
                    undeclared.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=imp_path,
                            detail=f"External import '{imp_path}' is not declared as a direct require in go.mod",
                        )
                    )

        unused = sorted(req for req in direct_requires if req not in used_requires)
        return unused, undeclared

    def check_boundary_violations(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> list[CodeLocation]:
        """Flag `pkg/...` importing `internal/...` or any non-`cmd` package importing `cmd/...`."""
        mod_path, _ = parse_go_module_info(project_root)
        if not mod_path:
            return []

        violations: list[CodeLocation] = []
        for unit in units:
            src_pkg = _unit_pkg_key(unit, project_root)
            src_parts = PurePosixPath(src_pkg).parts
            src_top = src_parts[0] if src_parts else ""
            for imp_path, line_no in _iter_unit_import_paths(unit):
                if not imp_path.startswith(f"{mod_path}/"):
                    continue
                target_sub = imp_path.removeprefix(f"{mod_path}/")
                target_top = PurePosixPath(target_sub).parts[0] if target_sub else ""
                if target_top == "cmd" and src_top != "cmd":
                    violations.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=imp_path,
                            detail=f"Package '{src_pkg}' imports entrypoint package '{target_sub}' under cmd/",
                        )
                    )
                elif src_top == "pkg" and target_top == "internal":
                    violations.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=imp_path,
                            detail=f"Public SDK package '{src_pkg}' under pkg/ imports private '{target_sub}'",
                        )
                    )
        return violations
