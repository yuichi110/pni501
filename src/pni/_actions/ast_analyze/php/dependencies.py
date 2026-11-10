# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP namespace and file-include dependency graph, cycle, Composer manifest, and boundary checker."""

from __future__ import annotations

import contextlib
import json
import re
from pathlib import Path
from typing import Final

from pni._actions.ast_analyze.base import BaseDependencyChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit
from pni._actions.ast_analyze.php._helpers import (
    INCLUDE_EXPR_KINDS,
    extract_php_namespace,
    iter_php_types,
    strip_php_quotes,
)

_VENDOR_PREFIX_MAP: Final[dict[str, str]] = {
    "illuminate": "laravel/framework",
    "laravel": "laravel/framework",
    "guzzlehttp": "guzzlehttp/guzzle",
    "monolog": "monolog/monolog",
    "carbon": "nesbot/carbon",
    "ramsey": "ramsey/uuid",
    "psr": "psr/",
    "symfony": "symfony/",
    "doctrine": "doctrine/",
}
_INCLUDE_LITERAL_RE: Final[re.Pattern[str]] = re.compile(r"['\"]([^'\"]+\.(?:php|phtml|inc))['\"]")


def _unit_symbols(unit: ParsedUnit) -> tuple[str, list[str]]:
    """Return (primary_node_id, exported_fqns) for a PHP unit."""
    ns = extract_php_namespace(unit.root)
    types = [tname for tname, _ in iter_php_types(unit.root)]
    if ns and types:
        fqns = [f"{ns}\\{t}" for t in types]
        return fqns[0], fqns
    if ns:
        return ns, [ns]
    return unit.rel_path, [unit.rel_path]


def _extract_use_fqns(unit: ParsedUnit) -> list[tuple[str, int]]:
    """Return `(imported_fqn, line_1based)` pairs from top-level `use` declarations."""
    imports: list[tuple[str, int]] = []
    for unode in unit.root.find_all(kind="namespace_use_declaration"):
        line = unode.range().start.line + 1
        group = unode.find(kind="namespace_use_group")
        if group is not None:
            pnode = unode.find(kind="namespace_name")
            pbase = pnode.text().strip().lstrip("\\") if pnode is not None else ""
            prefix = f"{pbase}\\" if pbase else ""
            for clause in group.find_all(kind="namespace_use_clause"):
                raw = clause.text().strip().split(" as ", maxsplit=1)[0].strip()
                imports.append((f"{prefix}{raw}", line))
        else:
            for clause in unode.find_all(kind="namespace_use_clause"):
                raw = clause.text().strip().split(" as ", maxsplit=1)[0].strip().lstrip("\\")
                if raw:
                    imports.append((raw, line))
    return imports


def _extract_included_resolved_paths(unit: ParsedUnit, project_root: Path) -> list[Path]:
    """Resolve static `.php` targets referenced by `include`/`require` expressions."""
    targets: list[Path] = []
    base_dir = unit.file_path.parent
    proj_resolved = project_root.resolve()
    for inc_kind in INCLUDE_EXPR_KINDS:
        for inc_node in unit.root.find_all(kind=inc_kind):
            txt = inc_node.text()
            for match in _INCLUDE_LITERAL_RE.finditer(txt):
                rel_lit = strip_php_quotes(match.group(0)).lstrip("/")
                for cand in (base_dir / rel_lit, project_root / rel_lit):
                    resolved = cand.resolve()
                    if resolved.is_file() and resolved.is_relative_to(proj_resolved):
                        targets.append(resolved)
                        break
    return targets


def _extract_psr4_heads(autoload_obj: object) -> set[str]:
    """Extract top-level namespace prefixes from a Composer `autoload` or `autoload-dev` object."""
    heads: set[str] = set()
    if not isinstance(autoload_obj, dict):
        return heads
    for section_key in ("psr-4", "psr-0"):
        mapping = autoload_obj.get(section_key)
        if isinstance(mapping, dict):
            for ns_prefix in mapping:
                head = str(ns_prefix).strip("\\").split("\\", maxsplit=1)[0]
                if head:
                    heads.add(head)
    return heads


def _load_lock_namespace_map(lock_path: Path) -> dict[str, str]:
    """Map lowercase PSR-4 top-level namespaces to package names from `composer.lock` if present."""
    ns_to_pkg: dict[str, str] = {}
    if not lock_path.is_file():
        return ns_to_pkg
    with contextlib.suppress(Exception):
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return ns_to_pkg
        for key in ("packages", "packages-dev"):
            pkgs = data.get(key)
            if not isinstance(pkgs, list):
                continue
            for entry in pkgs:
                if not isinstance(entry, dict):
                    continue
                pkg_name = str(entry.get("name", "")).strip().lower()
                if "/" not in pkg_name:
                    continue
                for head in _extract_psr4_heads(entry.get("autoload")):
                    ns_to_pkg.setdefault(head.lower(), pkg_name)
    return ns_to_pkg


def _matches_declared_composer_pkg(
    top_low: str,
    top_clean: str,
    mapped: str,
    declared_pkgs: set[str],
) -> bool:
    """Return True if an imported top-level namespace matches any declared Composer package."""
    for pkg in declared_pkgs:
        if pkg.startswith(mapped):
            return True
        parts = pkg.split("/")
        if top_low in parts or any(top_clean == part.replace("-", "").replace("_", "") for part in parts):
            return True
        if top_clean == pkg.replace("/", "").replace("-", "").replace("_", ""):
            return True
    return False


class PhpDependencyChecker(BaseDependencyChecker):
    """Build PHP namespace + procedural include graphs, detect cycles, and audit Composer dependencies."""

    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Build an adjacency list across internal PHP namespaces/classes and relative file includes."""
        fqn_to_owner: dict[str, str] = {}
        resolved_to_owner: dict[Path, str] = {}
        unit_owners: dict[str, str] = {}

        for unit in units:
            owner, exported = _unit_symbols(unit)
            unit_owners[unit.rel_path] = owner
            resolved_to_owner[unit.file_path.resolve()] = owner
            for fqn in exported:
                fqn_to_owner[fqn] = owner

        graph: dict[str, set[str]] = {owner: set() for owner in unit_owners.values()}
        for unit in units:
            src_owner = unit_owners[unit.rel_path]
            for imp_fqn, _ in _extract_use_fqns(unit):
                target_owner = fqn_to_owner.get(imp_fqn)
                if target_owner and target_owner != src_owner:
                    graph[src_owner].add(target_owner)
            for inc_resolved in _extract_included_resolved_paths(unit, project_root):
                target_owner = resolved_to_owner.get(inc_resolved)
                if target_owner and target_owner != src_owner:
                    graph[src_owner].add(target_owner)

        return {k: sorted(v) for k, v in sorted(graph.items())}

    def _load_composer_manifest_info(
        self,
        composer_path: Path,
        units: list[ParsedUnit],
    ) -> tuple[set[str], set[str]]:
        """Return (declared_vendor_packages, internal_namespace_roots) from composer.json and CST units."""
        declared_pkgs: set[str] = set()
        internal_roots: set[str] = {"App", "Database", "Tests"}
        with contextlib.suppress(Exception):
            data = json.loads(composer_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                req = data.get("require")
                if isinstance(req, dict):
                    declared_pkgs.update(str(p).strip().lower() for p in req if "/" in str(p))
                internal_roots.update(_extract_psr4_heads(data.get("autoload")))
                internal_roots.update(_extract_psr4_heads(data.get("autoload-dev")))

        for unit in units:
            ns = extract_php_namespace(unit.root)
            if ns:
                internal_roots.add(ns.split("\\", maxsplit=1)[0])
        return declared_pkgs, internal_roots

    def check_manifest_dependencies(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> tuple[list[str], list[CodeLocation]]:
        """Cross-check declared `composer.json` runtime packages against third-party `use` namespaces."""
        composer_path = project_root / "composer.json"
        if not composer_path.is_file():
            return [], []

        declared_pkgs, internal_roots = self._load_composer_manifest_info(composer_path, units)
        lock_ns_to_pkg = _load_lock_namespace_map(project_root / "composer.lock")
        used_vendors: set[str] = set()
        undeclared: list[CodeLocation] = []
        for unit in units:
            for imp_fqn, line in _extract_use_fqns(unit):
                if "\\" not in imp_fqn:
                    continue
                top_ns = imp_fqn.split("\\", maxsplit=1)[0]
                if top_ns in internal_roots:
                    continue
                top_low = top_ns.lower()
                top_clean = top_low.replace("-", "").replace("_", "")
                used_vendors.add(top_low)
                used_vendors.add(top_clean)
                mapped = _VENDOR_PREFIX_MAP.get(top_low, lock_ns_to_pkg.get(top_low, top_low))
                used_vendors.add(mapped)
                if declared_pkgs and not _matches_declared_composer_pkg(
                    top_low, top_clean, mapped, declared_pkgs
                ):
                    undeclared.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line,
                            symbol=imp_fqn,
                            detail=f"External namespace '{imp_fqn}' imported without matching composer.json 'require'",
                        )
                    )

        unused: list[str] = []
        all_source_lower = "\n".join(u.source.lower() for u in units)
        framework_meta_pkgs = {"laravel/framework", "laravel/sanctum", "laravel/tinker", "guzzlehttp/guzzle"}
        for pkg in sorted(declared_pkgs):
            if pkg in framework_meta_pkgs or pkg.startswith(("ext-", "psr/")):
                continue
            vendor, short = pkg.split("/", maxsplit=1)
            short_clean = short.replace("-", "").replace("_", "")
            if (
                pkg not in used_vendors
                and vendor not in used_vendors
                and short_clean not in used_vendors
                and vendor not in all_source_lower
                and short_clean not in all_source_lower.replace("_", "")
            ):
                unused.append(pkg)

        return unused, undeclared

    def check_boundary_violations(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> list[CodeLocation]:
        """Flag Domain/Model units importing HTTP/Controller or Admin presentation layers."""
        _ = project_root
        violations: list[CodeLocation] = []
        for unit in units:
            ns = extract_php_namespace(unit.root)
            is_domain = any(seg in ns for seg in ("\\Domain", "\\Models", "\\Entities"))
            if not is_domain:
                continue
            for imp_fqn, line in _extract_use_fqns(unit):
                if any(seg in imp_fqn for seg in ("\\Http\\Controllers", "\\Console\\", "\\Admin\\")):
                    violations.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line,
                            symbol=imp_fqn,
                            detail=f"Domain/Model layer '{ns}' depends upward on presentation/controller '{imp_fqn}'",
                        )
                    )
        return violations
