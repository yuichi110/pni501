# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python internal import graph, deptry-style manifest check, and private boundary checker."""

from __future__ import annotations

import contextlib
import csv
import importlib.metadata
import sys
from pathlib import Path, PurePosixPath
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseDependencyChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit
from pni._actions.ast_analyze.python._helpers import (
    is_in_type_checking_guard,
    module_name_from_path,
)
from pni._actions.project_inspect import normalize_python_dep_name, run_project_inspect

_STDLIB_MODULES: Final[frozenset[str]] = frozenset({*sys.stdlib_module_names, "__future__"})
_DIST_TO_IMPORT_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "pyyaml": ("yaml",),
    "pillow": ("pil",),
    "python_multipart": ("python_multipart", "multipart"),
    "beautifulsoup4": ("bs4",),
    "scikit_learn": ("sklearn",),
    "scikit_image": ("skimage",),
    "opencv_python": ("cv2",),
    "opencv_python_headless": ("cv2",),
    "python_dotenv": ("dotenv",),
    "attrs": ("attr", "attrs"),
    "pyjwt": ("jwt",),
    "protobuf": ("google",),
    "python_dateutil": ("dateutil",),
    "msgpack_python": ("msgpack",),
    "python_docx": ("docx",),
    "python_pptx": ("pptx",),
    "markdown_it_py": ("markdown_it",),
    "ruamel_yaml": ("ruamel",),
    "grpcio": ("grpc",),
    "pyopenssl": ("openssl",),
    "gitpython": ("git",),
    "pynacl": ("nacl",),
    "pycryptodome": ("crypto",),
    "pycryptodomex": ("cryptodome",),
    "python_jose": ("jose",),
    "python_magic": ("magic",),
    "python_slugify": ("slugify",),
    "pyserial": ("serial",),
    "pyzmq": ("zmq",),
    "graphql_core": ("graphql",),
    "psycopg_binary": ("psycopg",),
    "pygments": ("pygments",),
    "xlsxwriter": ("xlsxwriter",),
    "lxml": ("lxml",),
}
_NAMESPACE_DIST_PREFIXES: Final[dict[str, tuple[str, ...]]] = {
    "opentelemetry": ("opentelemetry_",),
    "google": ("google_", "googleapis_"),
    "azure": ("azure_",),
    "sphinxcontrib": ("sphinxcontrib_",),
    "zope": ("zope_",),
    "jaraco": ("jaraco_",),
    "mpl_toolkits": ("matplotlib", "mpl_toolkits_"),
}
_RUNTIME_DRIVER_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        "playwright",
        "uvicorn",
        "gunicorn",
        "hypercorn",
        "psycopg2",
        "psycopg2_binary",
        "asyncpg",
        "pymysql",
        "aiosqlite",
        "uv_build",
        "hatchling",
        "setuptools",
        "wheel",
    }
)


def _resolve_from_import(
    stmt: SgNode,
    current_mod: str,
    root_packages: set[str],
    known_modules: set[str],
) -> set[str]:
    """Resolve internal modules referenced by a Python import_from_statement."""
    resolved: set[str] = set()
    mod_node = stmt.field("module_name")
    base_mod = ""
    if mod_node is not None:
        raw_mod = mod_node.text()
        if raw_mod.startswith("."):
            dots = len(raw_mod) - len(raw_mod.lstrip("."))
            suffix = raw_mod.lstrip(".")
            pkg_parts = current_mod.split(".")[:-dots] if dots <= len(current_mod.split(".")) else []
            base_mod = ".".join([*pkg_parts, suffix]) if suffix else ".".join(pkg_parts)
        else:
            base_mod = raw_mod

    if not base_mod or base_mod.split(".")[0] not in root_packages:
        return resolved

    for imported in stmt.field_children("name"):
        sub_candidate = f"{base_mod}.{imported.text().split(' as ')[0].strip()}"
        if sub_candidate in known_modules:
            resolved.add(sub_candidate)
    if not resolved:
        resolved.add(base_mod)
    return resolved


def _extract_unit_imports(
    root: SgNode,
    current_mod: str,
    root_packages: set[str],
    known_modules: set[str],
    *,
    include_type_checking: bool = False,
) -> list[str]:
    """Extract sorted internal module dependencies from a single Python CST root."""
    imports: set[str] = set()
    for stmt in root.find_all(kind="import_statement"):
        if not include_type_checking and is_in_type_checking_guard(stmt):
            continue
        for name_node in stmt.field_children("name"):
            target = name_node.text().split(" as ")[0].strip()
            if target.split(".")[0] in root_packages and target != current_mod:
                imports.add(target)

    for stmt in root.find_all(kind="import_from_statement"):
        if not include_type_checking and is_in_type_checking_guard(stmt):
            continue
        for target in _resolve_from_import(stmt, current_mod, root_packages, known_modules):
            if target != current_mod:
                imports.add(target)

    return sorted(imports)


def _discover_venv_site_packages(project_root: Path) -> list[str]:
    """Locate site-packages directories inside target project's .venv/ or venv/ if present."""
    candidates: list[Path] = []
    for venv_name in (".venv", "venv"):
        vdir = project_root / venv_name
        if not vdir.is_dir():
            continue
        candidates.extend(sorted(vdir.glob("lib/python*/site-packages")))
        win_sp = vdir / "Lib" / "site-packages"
        if win_sp.is_dir():
            candidates.append(win_sp)
    return [str(p) for p in candidates if p.is_dir()]


def _add_record_path_top_import(top_names: set[str], raw_rel_path: str) -> None:
    """Record a top-level importable package/module name from a single PEP 376 RECORD path."""
    parts = PurePosixPath(raw_rel_path).parts
    if not parts or parts[0].startswith("..") or parts[0].endswith((".dist-info", ".data", ".egg-info")):
        return
    head = parts[0]
    if len(parts) > 1 and head.isidentifier() and head != "__pycache__":
        top_names.add(normalize_python_dep_name(head))
    elif len(parts) == 1 and head.endswith(".py"):
        stem = head[:-3]
        if stem.isidentifier() and not stem.startswith("_"):
            top_names.add(normalize_python_dep_name(stem))


def _extract_dist_top_imports(dist: importlib.metadata.Distribution) -> set[str]:
    """Extract top-level importable package/module names from top_level.txt and RECORD."""
    top_names: set[str] = set()
    raw_top = dist.read_text("top_level.txt")
    if raw_top:
        for line in raw_top.splitlines():
            clean = line.strip().split("/", maxsplit=1)[0]
            if clean and clean.isidentifier():
                top_names.add(normalize_python_dep_name(clean))

    raw_record = dist.read_text("RECORD")
    if raw_record:
        for row in csv.reader(raw_record.splitlines()):
            if row and row[0]:
                _add_record_path_top_import(top_names, row[0])
        return top_names

    for pkg_file in dist.files or ():
        _add_record_path_top_import(top_names, str(pkg_file))
    return top_names


def _merge_target_venv_distributions(mapping: dict[str, set[str]], project_root: Path) -> None:
    """Merge installed package -> import mappings from target project's .venv site-packages."""
    sp_paths = _discover_venv_site_packages(project_root)
    if not sp_paths:
        return
    with contextlib.suppress(Exception):
        for dist in importlib.metadata.distributions(path=sp_paths):
            with contextlib.suppress(Exception):
                raw_name = dist.name
                if not raw_name:
                    continue
                dist_norm = normalize_python_dep_name(raw_name)
                for imp_norm in _extract_dist_top_imports(dist):
                    mapping.setdefault(imp_norm, set()).add(dist_norm)


def _build_env_import_to_dist_map(project_root: Path | None = None) -> dict[str, set[str]]:
    """Build normalized top-level import -> normalized distribution names from env and target .venv."""
    mapping: dict[str, set[str]] = {}
    with contextlib.suppress(Exception):
        for pkg_mod, dists in importlib.metadata.packages_distributions().items():
            norm_mod = normalize_python_dep_name(pkg_mod)
            mapping.setdefault(norm_mod, set()).update(normalize_python_dep_name(d) for d in dists)
    if project_root is not None:
        _merge_target_venv_distributions(mapping, project_root)
    for dist_name, import_names in _DIST_TO_IMPORT_ALIASES.items():
        for imp in import_names:
            mapping.setdefault(imp, set()).add(dist_name)
    return mapping


def _collect_dynamic_third_party_imports(
    unit: ParsedUnit,
    root_packages: set[str],
) -> list[tuple[str, str, int, bool]]:
    """Extract string-literal package names passed to importlib.import_module() or __import__()."""
    dyn: list[tuple[str, str, int, bool]] = []
    for call in unit.root.find_all(kind="call"):
        fn = call.field("function")
        if fn is None or fn.text().strip() not in {"importlib.import_module", "import_module", "__import__"}:
            continue
        args = call.field("arguments")
        arg_nodes = args.named_children() if args is not None else []
        if not arg_nodes or arg_nodes[0].kind() != "string":
            continue
        raw_lit = arg_nodes[0].text().strip("\"'")
        if not raw_lit or raw_lit.startswith("."):
            continue
        top = raw_lit.split(".")[0]
        if top.isidentifier() and top not in _STDLIB_MODULES and top not in root_packages:
            dyn.append((top, unit.rel_path, call.range().start.line + 1, is_in_type_checking_guard(call)))
    return dyn


def _collect_third_party_imports(
    units: list[ParsedUnit],
    root_packages: set[str],
) -> list[tuple[str, str, int, bool]]:
    """Return (top_module_name, rel_path, line, is_type_checking) tuples for third-party imports."""
    found: list[tuple[str, str, int, bool]] = []
    for unit in units:
        for stmt in unit.root.find_all(kind="import_statement"):
            tc_only = is_in_type_checking_guard(stmt)
            for nnode in stmt.field_children("name"):
                top = nnode.text().split(" as ")[0].strip().split(".")[0]
                if top and top not in _STDLIB_MODULES and top not in root_packages:
                    found.append((top, unit.rel_path, stmt.range().start.line + 1, tc_only))
        for stmt in unit.root.find_all(kind="import_from_statement"):
            mod_node = stmt.field("module_name")
            if mod_node is None:
                continue
            raw_mod = mod_node.text().strip()
            if raw_mod.startswith("."):
                continue
            top = raw_mod.split(".")[0]
            if top and top not in _STDLIB_MODULES and top not in root_packages:
                found.append((top, unit.rel_path, stmt.range().start.line + 1, is_in_type_checking_guard(stmt)))
        found.extend(_collect_dynamic_third_party_imports(unit, root_packages))
    return found


def _matches_declared(
    imp_norm: str,
    declared_set: set[str],
    imp_to_dists: dict[str, set[str]],
) -> set[str]:
    """Return matching declared distribution names for an imported top-level package."""
    matched: set[str] = set()
    if imp_norm in declared_set:
        matched.add(imp_norm)
    matched.update(imp_to_dists.get(imp_norm, set()) & declared_set)
    ns_prefixes = _NAMESPACE_DIST_PREFIXES.get(imp_norm, ())
    if ns_prefixes:
        matched.update(d for d in declared_set if d.startswith(ns_prefixes))
    return matched


class PythonDependencyChecker(BaseDependencyChecker):
    """Build internal Python import graph, cross-check pyproject dependencies, and check boundaries."""

    def _build_python_graph(
        self,
        units: list[ParsedUnit],
        project_root: Path,
        *,
        include_type_checking: bool,
    ) -> dict[str, list[str]]:
        """Build internal Python module dependency graph with optional TYPE_CHECKING imports."""
        unit_modules = [(u, module_name_from_path(u.file_path, project_root)) for u in units]
        known_modules = {mod for _, mod in unit_modules if mod}
        root_packages = {mod.split(".")[0] for mod in known_modules}

        graph: dict[str, list[str]] = {}
        for unit, mod_name in unit_modules:
            if mod_name:
                graph[mod_name] = _extract_unit_imports(
                    unit.root,
                    mod_name,
                    root_packages,
                    known_modules,
                    include_type_checking=include_type_checking,
                )
        return graph

    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Index known Python modules (Pass 1) and resolve runtime internal imports (Pass 2)."""
        return self._build_python_graph(units, project_root, include_type_checking=False)

    def detect_type_checking_cycles(
        self,
        units: list[ParsedUnit],
        project_root: Path,
        runtime_cycles: list[list[str]],
    ) -> list[list[str]]:
        """Detect internal cycles that occur only when `if TYPE_CHECKING:` imports are included."""
        full_graph = self._build_python_graph(units, project_root, include_type_checking=True)
        runtime_set = {tuple(c) for c in runtime_cycles}
        return [c for c in self.detect_cycles(full_graph) if tuple(c) not in runtime_set]

    def check_manifest_dependencies(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> tuple[list[str], list[CodeLocation]]:
        """Cross-check declared dependencies in manifests against third-party imports (deptry style)."""
        pf = run_project_inspect(project_root, lang="python")
        if not pf.manifest_files:
            return [], []

        declared_runtime = {normalize_python_dep_name(d) for d in pf.dependencies if d.strip()}
        declared_dev = {normalize_python_dep_name(d) for d in pf.dev_dependencies if d.strip()}
        local_stems = {u.file_path.stem for u in units}
        root_packages = {
            *{module_name_from_path(u.file_path, project_root).split(".")[0] for u in units},
            *local_stems,
        }
        imp_to_dists = _build_env_import_to_dist_map(project_root)

        used_runtime_dists: set[str] = set()
        undeclared: list[CodeLocation] = []
        seen_undeclared: set[tuple[str, str]] = set()

        for top_mod, rel_path, lineno, tc_only in _collect_third_party_imports(units, root_packages):
            imp_norm = normalize_python_dep_name(top_mod)
            matched = _matches_declared(imp_norm, declared_runtime, imp_to_dists)
            if matched:
                used_runtime_dists.update(matched)
                continue
            dev_match = _matches_declared(imp_norm, declared_dev, imp_to_dists)
            if tc_only and (dev_match or imp_norm.startswith("types_")):
                continue
            if (rel_path, top_mod) in seen_undeclared:
                continue
            seen_undeclared.add((rel_path, top_mod))
            detail = (
                f"Dev-only dependency '{top_mod}' imported in production code (DEP004)"
                if dev_match
                else f"Third-party module '{top_mod}' not declared in runtime dependencies (DEP001)"
            )
            undeclared.append(CodeLocation(file=rel_path, line=lineno, symbol=top_mod, detail=detail))

        unused = sorted(
            d for d in (declared_runtime - used_runtime_dists) if d and d not in _RUNTIME_DRIVER_ALLOWLIST
        )
        return unused, undeclared

    def check_boundary_violations(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> list[CodeLocation]:
        """Detect cross-subpackage private module imports and domain -> adapter layer inversions."""
        unit_modules = [(u, module_name_from_path(u.file_path, project_root)) for u in units]
        known_modules = {mod for _, mod in unit_modules if mod}
        root_packages = {mod.split(".")[0] for mod in known_modules}
        outer_layers = {"api", "cli", "views", "controllers", "presentation"}
        violations: list[CodeLocation] = []

        for unit, src_mod in unit_modules:
            src_parts = src_mod.split(".")
            in_domain = "domain" in src_parts[1:-1] or (len(src_parts) >= 2 and src_parts[1] == "domain")
            for target in _extract_unit_imports(unit.root, src_mod, root_packages, known_modules):
                tgt_parts = target.split(".")
                if len(tgt_parts) >= 3 and tgt_parts[-1].startswith("_") and src_parts[:2] != tgt_parts[:2]:
                    violations.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=1,
                            symbol=f"{src_mod} -> {target}",
                            detail=f"Cross-domain import of private module '{target}' from '{'.'.join(src_parts[:2])}'",
                        )
                    )
                elif in_domain and any(seg in outer_layers for seg in tgt_parts[1:]):
                    violations.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=1,
                            symbol=f"{src_mod} -> {target}",
                            detail=f"Architectural layer inversion: domain module '{src_mod}' imports '{target}'",
                        )
                    )
        return violations
