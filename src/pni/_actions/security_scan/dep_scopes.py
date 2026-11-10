# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic lockfile/manifest dependency scope resolver (core runtime vs dev/optional)."""

from __future__ import annotations

import collections
import contextlib
import json
import re
import tomllib
from pathlib import Path

_REQ_SPLIT_RE = re.compile(r"[<>=!~@;\s]")
_EXTRAS_RE = re.compile(r"^([^\[\s<>=!~@;]+)\[([^\]]+)\]")


def normalize_vuln_pkg_key(pkg_name: str) -> str:
    """Normalize a package identifier for cross-matching Trivy records against manifests and lockfiles."""
    clean = pkg_name.strip()
    if "/" in clean or clean.startswith("@"):
        return clean.lower()
    return re.sub(r"[-_.]+", "_", clean).lower().strip("_")


def _parse_pep508_name_and_extras(raw_spec: str) -> tuple[str, set[str]]:
    """Extract `(normalized_pkg_name, normalized_extras)` from a PEP 508 requirement string."""
    stripped = raw_spec.strip()
    ext_match = _EXTRAS_RE.match(stripped)
    if ext_match:
        name = normalize_vuln_pkg_key(ext_match.group(1))
        extras = {normalize_vuln_pkg_key(e) for e in ext_match.group(2).split(",") if e.strip()}
        return name, extras
    head = _REQ_SPLIT_RE.split(stripped, maxsplit=1)[0].split("[", maxsplit=1)[0]
    return normalize_vuln_pkg_key(head), set()


def _load_toml_dict(path: Path) -> dict[str, object]:
    """Safely parse a TOML file into a dictionary, returning empty dict on failure."""
    if not path.is_file():
        return {}
    with contextlib.suppress(Exception):
        parsed = tomllib.loads(path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            return parsed
    return {}


def _iter_group_req_strings(table: object) -> list[str]:
    """Flatten string requirement entries across a dict-of-lists TOML table."""
    if not isinstance(table, dict):
        return []
    out: list[str] = []
    for items in table.values():
        if isinstance(items, list):
            out.extend(item for item in items if isinstance(item, str) and item.strip())
    return out


def _collect_core_seeds(project_sec: dict[str, object]) -> dict[str, set[str]]:
    """Parse `[project.dependencies]` into a `{pkg_norm: extras_set}` dictionary."""
    seeds: dict[str, set[str]] = {}
    raw_deps = project_sec.get("dependencies", [])
    if not isinstance(raw_deps, list):
        return seeds
    for item in raw_deps:
        if isinstance(item, str) and item.strip():
            p_norm, exts = _parse_pep508_name_and_extras(item)
            if p_norm:
                seeds.setdefault(p_norm, set()).update(exts)
    return seeds


def _extract_pyproject_seed_info(pyproject_path: Path) -> tuple[bool, str, dict[str, set[str]], set[str]]:
    """Return `(has_project_table, root_norm, core_seeds_with_extras, explicit_non_core_direct)`."""
    data = _load_toml_dict(pyproject_path)
    project_sec = data.get("project")
    if not isinstance(project_sec, dict):
        non_core_groups = {
            _parse_pep508_name_and_extras(s)[0] for s in _iter_group_req_strings(data.get("dependency-groups"))
        }
        return False, "", {}, {n for n in non_core_groups if n}

    root_norm = normalize_vuln_pkg_key(str(project_sec.get("name", "")))
    core_seeds = _collect_core_seeds(project_sec)
    raw_non_core = [
        *_iter_group_req_strings(project_sec.get("optional-dependencies")),
        *_iter_group_req_strings(data.get("dependency-groups")),
    ]
    non_core_direct = {
        p_norm
        for item in raw_non_core
        if (p_norm := _parse_pep508_name_and_extras(item)[0]) and p_norm not in core_seeds
    }
    return True, root_norm, core_seeds, non_core_direct


def _extract_uv_dep_edges(raw_list: object) -> list[tuple[str, tuple[str, ...]]]:
    """Parse a uv.lock dependency array of tables into `(dep_norm, extras_tuple)` edges."""
    if not isinstance(raw_list, list):
        return []
    edges: list[tuple[str, tuple[str, ...]]] = []
    for entry in raw_list:
        if not isinstance(entry, dict):
            continue
        raw_name = entry.get("name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            continue
        dep_norm = normalize_vuln_pkg_key(raw_name)
        raw_extra = entry.get("extra")
        extras = (
            tuple(normalize_vuln_pkg_key(str(x)) for x in raw_extra if str(x).strip())
            if isinstance(raw_extra, list)
            else ()
        )
        edges.append((dep_norm, extras))
    return edges


def _build_uv_lock_graphs(
    raw_pkgs: list[object],
) -> tuple[
    set[str],
    dict[str, list[tuple[str, tuple[str, ...]]]],
    dict[tuple[str, str], list[tuple[str, tuple[str, ...]]]],
]:
    """Index locked package names, base dependency edges, and optional-dependency edges from `uv.lock`."""
    all_locked: set[str] = set()
    base_graph: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
    opt_graph: dict[tuple[str, str], list[tuple[str, tuple[str, ...]]]] = {}

    for pkg in raw_pkgs:
        if not isinstance(pkg, dict):
            continue
        name = normalize_vuln_pkg_key(str(pkg.get("name", "")))
        if not name:
            continue
        all_locked.add(name)
        base_graph.setdefault(name, []).extend(_extract_uv_dep_edges(pkg.get("dependencies")))
        raw_opt = pkg.get("optional-dependencies")
        if isinstance(raw_opt, dict):
            for ext_key, ext_deps in raw_opt.items():
                ext_norm = normalize_vuln_pkg_key(str(ext_key))
                opt_graph.setdefault((name, ext_norm), []).extend(_extract_uv_dep_edges(ext_deps))
    return all_locked, base_graph, opt_graph


def _resolve_uv_lock_non_core(
    uv_lock_path: Path,
    root_norm: str,
    core_seeds: dict[str, set[str]],
) -> set[str]:
    """Compute locked packages unreachable from `[project.dependencies]` in `uv.lock`."""
    data = _load_toml_dict(uv_lock_path)
    raw_pkgs = data.get("package")
    if not isinstance(raw_pkgs, list):
        return set()

    all_locked, base_graph, opt_graph = _build_uv_lock_graphs(raw_pkgs)
    reachable: set[str] = set()
    visited_extras: set[tuple[str, str]] = set()
    queue: collections.deque[tuple[str, tuple[str, ...]]] = collections.deque()

    if root_norm:
        reachable.add(root_norm)
        queue.extend(base_graph.get(root_norm, ()))
    for seed_pkg, seed_exts in core_seeds.items():
        queue.append((seed_pkg, tuple(sorted(seed_exts))))

    while queue:
        curr, exts = queue.popleft()
        if curr not in reachable:
            reachable.add(curr)
            queue.extend(base_graph.get(curr, ()))
        for ext in exts:
            if (curr, ext) not in visited_extras:
                visited_extras.add((curr, ext))
                queue.extend(opt_graph.get((curr, ext), ()))

    return all_locked - reachable


def _resolve_poetry_lock_non_core(poetry_lock_path: Path, core_seeds: dict[str, set[str]]) -> set[str]:
    """Identify dev/optional-only packages in `poetry.lock`."""
    data: dict[str, object] = {}
    with contextlib.suppress(Exception):
        parsed = tomllib.loads(poetry_lock_path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            data = parsed
    raw_pkgs = data.get("package")
    if not isinstance(raw_pkgs, list):
        return set()

    non_core: set[str] = set()
    for pkg in raw_pkgs:
        if not isinstance(pkg, dict):
            continue
        name = normalize_vuln_pkg_key(str(pkg.get("name", "")))
        if not name or name in core_seeds:
            continue
        category = str(pkg.get("category", "")).strip().lower()
        groups = pkg.get("groups")
        is_dev_group = isinstance(groups, list) and "main" not in [str(g).lower() for g in groups]
        if category == "dev" or is_dev_group:
            non_core.add(name)
    return non_core


def _resolve_composer_lock_non_core(composer_lock_path: Path) -> set[str]:
    """Extract `packages-dev` entries not present in production `packages` from `composer.lock`."""
    if not composer_lock_path.is_file():
        return set()
    payload: object = None
    with contextlib.suppress(Exception):
        payload = json.loads(composer_lock_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return set()
    prod_pkgs = {
        normalize_vuln_pkg_key(str(p.get("name", "")))
        for p in (payload.get("packages") or [])
        if isinstance(p, dict) and p.get("name")
    }
    dev_pkgs = {
        normalize_vuln_pkg_key(str(p.get("name", "")))
        for p in (payload.get("packages-dev") or [])
        if isinstance(p, dict) and p.get("name")
    }
    return dev_pkgs - prod_pkgs


def _resolve_npm_lock_non_core(npm_lock_path: Path) -> set[str]:
    """Extract dev-only packages from `package-lock.json`."""
    if not npm_lock_path.is_file():
        return set()
    payload: object = None
    with contextlib.suppress(Exception):
        payload = json.loads(npm_lock_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return set()
    packages = payload.get("packages")
    if not isinstance(packages, dict):
        return set()
    prod_names: set[str] = set()
    dev_names: set[str] = set()
    for path_key, meta in packages.items():
        if not path_key or not isinstance(meta, dict):
            continue
        pkg_name = str(meta.get("name") or path_key.rsplit("node_modules/", maxsplit=1)[-1]).strip()
        if not pkg_name:
            continue
        norm = normalize_vuln_pkg_key(pkg_name)
        if meta.get("dev") is True or meta.get("devOptional") is True:
            dev_names.add(norm)
        else:
            prod_names.add(norm)
    return dev_names - prod_names


def _resolve_maven_pom_non_core(pom_path: Path) -> set[str]:
    """Extract test, provided, and optional-only Maven dependencies from `pom.xml`."""
    if not pom_path.is_file():
        return set()
    cleaned = ""
    with contextlib.suppress(Exception):
        raw = pom_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = re.sub(
            r"<!--.*?-->|<(dependencyManagement|build|profiles|reporting)>.*?</\1>",
            "",
            raw,
            flags=re.DOTALL,
        )
    if not cleaned:
        return set()
    prod_keys: set[str] = set()
    non_core_keys: set[str] = set()
    for dep_match in re.finditer(r"<dependency>(.*?)</dependency>", cleaned, flags=re.DOTALL):
        block = dep_match.group(1)
        g_match = re.search(r"<groupId>\s*([^<]*?)\s*</groupId>", block, flags=re.DOTALL)
        a_match = re.search(r"<artifactId>\s*([^<]*?)\s*</artifactId>", block, flags=re.DOTALL)
        s_match = re.search(r"<scope>\s*([^<]*?)\s*</scope>", block, flags=re.DOTALL)
        o_match = re.search(r"<optional>\s*([^<]*?)\s*</optional>", block, flags=re.DOTALL)
        if not a_match:
            continue
        gid = g_match.group(1).strip() if g_match else ""
        aid = a_match.group(1).strip()
        scope = s_match.group(1).strip().lower() if s_match else ""
        is_opt = (o_match.group(1).strip().lower() == "true") if o_match else False
        keys = {normalize_vuln_pkg_key(aid)}
        if gid:
            keys.add(normalize_vuln_pkg_key(f"{gid}:{aid}"))
        if scope in {"test", "provided"} or is_opt:
            non_core_keys.update(keys)
        else:
            prod_keys.update(keys)
    return non_core_keys - prod_keys


def _resolve_package_json_non_core(pkg_json_path: Path) -> set[str]:
    """Extract direct `devDependencies` not declared in `dependencies` from `package.json`."""
    if not pkg_json_path.is_file():
        return set()
    payload: object = None
    with contextlib.suppress(Exception):
        payload = json.loads(pkg_json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return set()
    deps = payload.get("dependencies")
    dev_deps = payload.get("devDependencies")
    prod_set = {normalize_vuln_pkg_key(str(k)) for k in deps} if isinstance(deps, dict) else set()
    dev_set = {normalize_vuln_pkg_key(str(k)) for k in dev_deps} if isinstance(dev_deps, dict) else set()
    return dev_set - prod_set


def discover_non_core_packages(target_dir: Path) -> set[str]:
    """Discover normalized package names proven to belong only to dev/optional dependency groups."""
    non_core: set[str] = set()
    pyproject_path = target_dir / "pyproject.toml"
    has_proj, root_norm, core_seeds, non_core_direct = _extract_pyproject_seed_info(pyproject_path)
    non_core.update(non_core_direct)

    uv_lock = target_dir / "uv.lock"
    if has_proj and uv_lock.is_file():
        non_core.update(_resolve_uv_lock_non_core(uv_lock, root_norm, core_seeds))

    poetry_lock = target_dir / "poetry.lock"
    if poetry_lock.is_file():
        non_core.update(_resolve_poetry_lock_non_core(poetry_lock, core_seeds))

    non_core.update(_resolve_composer_lock_non_core(target_dir / "composer.lock"))
    non_core.update(_resolve_npm_lock_non_core(target_dir / "package-lock.json"))
    non_core.update(_resolve_package_json_non_core(target_dir / "package.json"))
    non_core.update(_resolve_maven_pom_non_core(target_dir / "pom.xml"))
    return non_core
