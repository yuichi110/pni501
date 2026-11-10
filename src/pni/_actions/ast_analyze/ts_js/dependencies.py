# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript internal module import graph, `package.json` cross-check, and boundaries."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path, PurePosixPath
from typing import Final

from pni._actions.ast_analyze.base import BaseDependencyChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_NODE_BUILTINS: Final[frozenset[str]] = frozenset(
    {
        "assert",
        "async_hooks",
        "buffer",
        "child_process",
        "cluster",
        "console",
        "constants",
        "crypto",
        "dgram",
        "diagnostics_channel",
        "dns",
        "domain",
        "events",
        "fs",
        "http",
        "http2",
        "https",
        "inspector",
        "module",
        "net",
        "os",
        "path",
        "perf_hooks",
        "process",
        "punycode",
        "querystring",
        "readline",
        "repl",
        "stream",
        "string_decoder",
        "sys",
        "test",
        "timers",
        "tls",
        "trace_events",
        "tty",
        "url",
        "util",
        "v8",
        "vm",
        "wasi",
        "worker_threads",
        "zlib",
    }
)
_IMPLICIT_RUNTIME_PACKAGES: Final[frozenset[str]] = frozenset(
    {
        "typescript",
        "tslib",
        "dotenv",
        "reflect-metadata",
        "source-map-support",
    }
)


def _unit_module_id(unit: ParsedUnit, project_root: Path) -> str:
    """Return workspace-relative module path without extension for a TS/JS unit."""
    rel = (
        unit.file_path.relative_to(project_root).as_posix()
        if unit.file_path.is_relative_to(project_root)
        else unit.rel_path
    )
    for sfx in (".d.ts", ".tsx", ".ts", ".jsx", ".mjs", ".cjs", ".js"):
        if rel.endswith(sfx):
            return rel[: -len(sfx)]
    return rel


def _is_inline_type_only_clause(stmt_text: str) -> bool:
    """Return True if an `import { ... }` or `export { ... }` clause contains only `type` specifiers."""
    brace_start = stmt_text.find("{")
    brace_end = stmt_text.find("}", brace_start + 1)
    if brace_start < 0 or brace_end < 0:
        return False
    prefix = stmt_text[:brace_start].removeprefix("import").removeprefix("export").strip()
    if prefix:
        return False
    items = [part.strip() for part in stmt_text[brace_start + 1 : brace_end].split(",") if part.strip()]
    return bool(items) and all(item.startswith("type ") for item in items)


def _iter_unit_module_specifiers(unit: ParsedUnit) -> list[tuple[str, int, bool, bool]]:
    """Return `(specifier, line_1based, is_type_only, is_reexport)` for ES imports/exports and `require(...)`."""
    specs: list[tuple[str, int, bool, bool]] = []
    for kind_name in ("import_statement", "export_statement"):
        is_reexport = kind_name == "export_statement"
        for node in unit.root.find_all(kind=kind_name):
            src = node.field("source")
            if src is None:
                continue
            spec = src.text().strip().strip("'\"")
            if not spec:
                continue
            text = node.text().lstrip()
            is_type_only = text.startswith(("import type ", "export type ")) or _is_inline_type_only_clause(text)
            specs.append((spec, node.range().start.line + 1, is_type_only, is_reexport))

    for call in unit.root.find_all(kind="call_expression"):
        fn = call.field("function")
        if fn is None or fn.text().strip() != "require":
            continue
        args = call.field("arguments")
        if args is None:
            continue
        str_node = args.find(kind="string")
        if str_node is not None:
            spec = str_node.text().strip().strip("'\"")
            if spec:
                specs.append((spec, call.range().start.line + 1, False, False))
    return specs


def _normalize_posix_rel(from_id: str, spec: str) -> str:
    """Resolve relative `./` or `../` specifier against `from_id`'s parent directory."""
    parent_dir = PurePosixPath(from_id).parent
    joined = (parent_dir / spec).as_posix()
    parts: list[str] = []
    for seg in joined.split("/"):
        if seg in {"", "."}:
            continue
        if seg == "..":
            if parts:
                parts.pop()
        else:
            parts.append(seg)
    return "/".join(parts)


def _match_known_module_id(candidate_base: str, known_ids: set[str]) -> str | None:
    """Strip known TS/JS extensions and check `candidate_base` or `candidate_base/index` in `known_ids`."""
    for sfx in (".tsx", ".ts", ".jsx", ".mjs", ".cjs", ".js"):
        if candidate_base.endswith(sfx):
            candidate_base = candidate_base[: -len(sfx)]
            break
    if candidate_base in known_ids:
        return candidate_base
    if f"{candidate_base}/index" in known_ids:
        return f"{candidate_base}/index"
    return None


def _resolve_internal_target(
    from_id: str,
    spec: str,
    known_ids: set[str],
) -> str | None:
    """Resolve a relative `./` / `../` or `@/` specifier to a known internal module ID."""
    if spec.startswith("."):
        return _match_known_module_id(_normalize_posix_rel(from_id, spec), known_ids)
    if spec.startswith("@/"):
        sub = spec.removeprefix("@/")
        for cand in (f"src/{sub}", sub):
            matched = _match_known_module_id(cand, known_ids)
            if matched is not None:
                return matched
    return None


def _extract_bare_pkg_name(spec: str) -> str:
    """Extract npm package name (`@scope/pkg` or `pkg`) from a bare import specifier."""
    if spec.startswith("@"):
        parts = spec.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else spec
    return spec.split("/", 1)[0]


def _read_single_package_json_deps(pkg_json: Path) -> tuple[set[str], set[str]]:
    """Read `(prod_deps, dev_deps)` from a single `package.json` file."""
    if not pkg_json.is_file():
        return set(), set()
    with contextlib.suppress(Exception):
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            deps = data.get("dependencies")
            dev_deps = data.get("devDependencies")
            peer_deps = data.get("peerDependencies")
            prod_set = {str(k).strip() for k in deps} if isinstance(deps, dict) else set()
            if isinstance(peer_deps, dict):
                prod_set.update(str(k).strip() for k in peer_deps)
            dev_set = {str(k).strip() for k in dev_deps} if isinstance(dev_deps, dict) else set()
            return prod_set, dev_set
    return set(), set()


def _load_package_json_deps(
    project_root: Path,
    units: list[ParsedUnit] | tuple[ParsedUnit, ...] = (),
) -> tuple[set[str], set[str]]:
    """Return `(prod_deps, dev_deps)` from target package and workspace root `package.json` manifests."""
    resolved_root = project_root.resolve()
    prod_all: set[str] = set()
    dev_all: set[str] = set()
    seen_manifests: set[Path] = set()

    for unit in units:
        for parent in unit.file_path.resolve().parents:
            cand = parent / "package.json"
            if cand.is_file():
                if cand not in seen_manifests:
                    seen_manifests.add(cand)
                    p_set, d_set = _read_single_package_json_deps(cand)
                    prod_all.update(p_set)
                    dev_all.update(d_set)
                break
            if parent == resolved_root:
                break

    root_pkg = resolved_root / "package.json"
    if root_pkg.is_file() and root_pkg not in seen_manifests:
        r_prod, r_dev = _read_single_package_json_deps(root_pkg)
        if not seen_manifests:
            prod_all.update(r_prod)
        dev_all.update(r_prod | r_dev)
    return prod_all, dev_all


def _is_barrel_module_id(module_id: str) -> bool:
    """Return True if `module_id` represents an `index` barrel module."""
    return module_id == "index" or module_id.endswith("/index")


class TsJsDependencyChecker(BaseDependencyChecker):
    """Build TS/JS internal module graph, cross-check `package.json` dependencies, and check boundaries."""

    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Build adjacency list of internal TS/JS runtime implementation modules (excluding barrel re-exports)."""
        id_map = {u.rel_path: _unit_module_id(u, project_root) for u in units}
        known_ids = set(id_map.values())
        edges: dict[str, set[str]] = {mid: set() for mid in known_ids}

        for unit in units:
            src_id = id_map[unit.rel_path]
            is_barrel = _is_barrel_module_id(src_id)
            for spec, _line, is_type_only, is_reexport in _iter_unit_module_specifiers(unit):
                if is_type_only or (is_barrel and is_reexport):
                    continue
                target_id = _resolve_internal_target(src_id, spec, known_ids)
                if target_id and target_id != src_id:
                    edges.setdefault(src_id, set()).add(target_id)

        return {mid: sorted(targets) for mid, targets in sorted(edges.items())}

    def detect_type_checking_cycles(
        self,
        units: list[ParsedUnit],
        project_root: Path,
        runtime_cycles: list[list[str]],
    ) -> list[list[str]]:
        """Detect cycles introduced by `import type` statements or `index.ts` barrel re-exports."""
        id_map = {u.rel_path: _unit_module_id(u, project_root) for u in units}
        known_ids = set(id_map.values())
        edges: dict[str, set[str]] = {mid: set() for mid in known_ids}
        has_extra_edges = False

        for unit in units:
            src_id = id_map[unit.rel_path]
            is_barrel = _is_barrel_module_id(src_id)
            for spec, _line, is_type_only, is_reexport in _iter_unit_module_specifiers(unit):
                if is_type_only or (is_barrel and is_reexport):
                    has_extra_edges = True
                target_id = _resolve_internal_target(src_id, spec, known_ids)
                if target_id and target_id != src_id:
                    edges.setdefault(src_id, set()).add(target_id)

        if not has_extra_edges:
            return []
        full_graph = {mid: sorted(targets) for mid, targets in sorted(edges.items())}
        all_cycles = self.detect_cycles(full_graph)
        rt_set = {tuple(c) for c in runtime_cycles}
        return [c for c in all_cycles if tuple(c) not in rt_set]

    def check_manifest_dependencies(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> tuple[list[str], list[CodeLocation]]:
        """Cross-check external npm package imports against `package.json`."""
        prod_deps, dev_deps = _load_package_json_deps(project_root, units)
        all_declared = prod_deps | dev_deps
        if not all_declared:
            return [], []

        used_pkgs: set[str] = set()
        undeclared: list[CodeLocation] = []
        seen_undeclared: set[tuple[str, str]] = set()

        for unit in units:
            for spec, line_no, _is_type, _is_reexport in _iter_unit_module_specifiers(unit):
                if spec.startswith((".", "/", "@/", "~/", "#")) or spec.startswith("node:"):
                    continue
                pkg = _extract_bare_pkg_name(spec)
                if pkg in _NODE_BUILTINS or pkg.removeprefix("node:") in _NODE_BUILTINS:
                    continue
                used_pkgs.add(pkg)
                if pkg not in all_declared and f"@types/{pkg}" not in all_declared:
                    if (unit.rel_path, pkg) not in seen_undeclared:
                        seen_undeclared.add((unit.rel_path, pkg))
                        undeclared.append(
                            CodeLocation(
                                file=unit.rel_path,
                                line=line_no,
                                symbol=pkg,
                                detail=f"External package '{pkg}' imported but not declared in package.json",
                            )
                        )

        unused = sorted(
            pkg
            for pkg in prod_deps
            if pkg not in used_pkgs
            and not pkg.startswith("@types/")
            and pkg not in _IMPLICIT_RUNTIME_PACKAGES
        )
        return unused, undeclared

    def check_boundary_violations(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> list[CodeLocation]:
        """Flag deep parent directory traversal (`../../../`) or cross-directory private `_` module imports."""
        _ = project_root
        violations: list[CodeLocation] = []
        for unit in units:
            for spec, line_no, _is_type, _is_reexport in _iter_unit_module_specifiers(unit):
                if spec.startswith("../../.."):
                    violations.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=spec,
                            detail=(
                                f"Deep relative parent import '{spec}' (>= 3 levels) — "
                                "use path aliases or package exports"
                            ),
                        )
                    )
                elif spec.startswith("../"):
                    leaf = PurePosixPath(spec).name
                    if leaf.startswith("_") and not leaf.startswith("__"):
                        violations.append(
                            CodeLocation(
                                file=unit.rel_path,
                                line=line_no,
                                symbol=spec,
                                detail=f"Cross-directory import of private module '{spec}'",
                            )
                        )
        return violations
