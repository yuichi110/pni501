# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python deterministic isort / PEP 8 import grouping, sorting, wildcard, and late-import checker."""

from __future__ import annotations

import contextlib
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseImportChecker
from pni._actions.ast_analyze.models import CodeLocation, ImportResult, ParsedUnit, UnitImportStats
from pni._actions.ast_analyze.python._helpers import module_name_from_path

_STDLIB_MODULES: Final[frozenset[str]] = frozenset(sys.stdlib_module_names)
_IMPORT_KINDS: Final[frozenset[str]] = frozenset(
    {"future_import_statement", "import_statement", "import_from_statement"}
)
_GROUP_LABELS: Final[dict[int, str]] = {
    0: "__future__",
    1: "stdlib",
    2: "third-party",
    3: "first-party",
}


@dataclass(frozen=True)
class _IsortConfig:
    """Explicit module classification overrides parsed from pyproject.toml isort sections."""

    known_first_party: frozenset[str] = frozenset()
    known_third_party: frozenset[str] = frozenset()
    known_local_folder: frozenset[str] = frozenset()
    extra_standard_library: frozenset[str] = frozenset()


def _extract_isort_names(section: dict[str, object], keys: tuple[str, ...]) -> set[str]:
    """Extract normalized module/package identifiers from an isort TOML table for candidate keys."""
    names: set[str] = set()
    for key in keys:
        raw = section.get(key)
        if isinstance(raw, list):
            names.update(str(item).strip() for item in raw if str(item).strip())
        elif isinstance(raw, str):
            names.update(part.strip() for part in raw.split(",") if part.strip())
    return names


def _collect_isort_tables(data: dict[str, object]) -> list[dict[str, object]]:
    """Return candidate isort TOML dictionaries from Ruff and standalone isort sections."""
    tool = data.get("tool")
    if not isinstance(tool, dict):
        return []
    tables: list[dict[str, object]] = []
    ruff = tool.get("ruff")
    if isinstance(ruff, dict):
        lint = ruff.get("lint")
        if isinstance(lint, dict) and isinstance(lint.get("isort"), dict):
            tables.append(lint["isort"])
        if isinstance(ruff.get("isort"), dict):
            tables.append(ruff["isort"])
    if isinstance(tool.get("isort"), dict):
        tables.append(tool["isort"])
    return tables


def _load_isort_config(project_root: Path) -> _IsortConfig:
    """Load explicit isort package grouping overrides from pyproject.toml if present."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        return _IsortConfig()
    data: dict[str, object] = {}
    with contextlib.suppress(Exception):
        parsed = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            data = parsed
    tables = _collect_isort_tables(data)
    if not tables:
        return _IsortConfig()

    first_party: set[str] = set()
    third_party: set[str] = set()
    local_folder: set[str] = set()
    extra_stdlib: set[str] = set()
    for tbl in tables:
        first_party.update(_extract_isort_names(tbl, ("known-first-party", "known_first_party", "src-paths")))
        third_party.update(_extract_isort_names(tbl, ("known-third-party", "known_third_party")))
        local_folder.update(_extract_isort_names(tbl, ("known-local-folder", "known_local_folder")))
        extra_stdlib.update(
            _extract_isort_names(
                tbl,
                (
                    "extra-standard-library",
                    "extra_standard_library",
                    "known-standard-library",
                    "known_standard_library",
                ),
            )
        )
    return _IsortConfig(
        known_first_party=frozenset(first_party),
        known_third_party=frozenset(third_party),
        known_local_folder=frozenset(local_folder),
        extra_standard_library=frozenset(extra_stdlib),
    )


def _matches_isort_spec(raw_mod: str, specs: frozenset[str]) -> bool:
    """Return True if raw_mod matches a top-level package or dotted prefix in specs."""
    if not specs:
        return False
    top = raw_mod.split(".", maxsplit=1)[0]
    if top in specs:
        return True
    return any(raw_mod == s or raw_mod.startswith(f"{s}.") for s in specs if "." in s)


@dataclass(frozen=True)
class _ImportEntry:
    """Normalized top-level import statement metadata for isort validation."""

    node: SgNode
    start_line: int
    end_line: int
    group: int
    sort_key: tuple[int, int, str, str]
    unsorted_members: bool
    summary: str


def _member_type_rank(symbol: str) -> tuple[int, str, str]:
    """Compute Ruff/isort order-by-type rank: CONSTANT (0) < Class (1) < variable/func (2)."""
    clean = symbol.split(" as ", maxsplit=1)[0].strip()
    stripped = clean.lstrip("_")
    alpha = "".join(ch for ch in stripped if ch.isalpha())
    if alpha and alpha.isupper():
        rank = 0
    elif stripped and stripped[0].isupper():
        rank = 1
    else:
        rank = 2
    return (rank, clean.lower(), clean)


def _are_imported_members_sorted(stmt: SgNode) -> bool:
    """Check whether imported names inside a single statement follow isort order-by-type."""
    members = [n.text().strip() for n in stmt.field_children("name") if n.kind() != "wildcard_import"]
    if len(members) <= 1:
        return True
    keys = [_member_type_rank(m) for m in members]
    return keys == sorted(keys)


def _classify_isort_override(raw_mod: str, isort_cfg: _IsortConfig) -> int | None:
    """Return explicit isort group override (1, 2, or 3) when configured, otherwise None."""
    if _matches_isort_spec(raw_mod, isort_cfg.known_first_party) or _matches_isort_spec(
        raw_mod, isort_cfg.known_local_folder
    ):
        return 3
    if _matches_isort_spec(raw_mod, isort_cfg.known_third_party):
        return 2
    if _matches_isort_spec(raw_mod, isort_cfg.extra_standard_library):
        return 1
    return None


def _classify_group(
    raw_mod: str,
    root_packages: set[str],
    isort_cfg: _IsortConfig | None = None,
) -> int:
    """Classify a module path into isort group 0 (__future__), 1 (stdlib), 2 (3rd-party), or 3 (local)."""
    if raw_mod == "__future__":
        return 0
    if raw_mod.startswith("."):
        return 3
    override = _classify_isort_override(raw_mod, isort_cfg) if isort_cfg is not None else None
    if override is not None:
        return override
    top = raw_mod.split(".", maxsplit=1)[0]
    if top in root_packages:
        return 3
    return 1 if top in _STDLIB_MODULES else 2


def _has_skip_comment(source_lines: list[str], start_line: int, end_line: int) -> bool:
    """Return True if an import statement carries an explicit isort/ruff skip directive."""
    for idx in range(start_line, min(end_line + 1, len(source_lines))):
        lower = source_lines[idx].lower()
        if "isort: skip" in lower or "isort:skip" in lower or "noqa: i001" in lower or "noqa" in lower:
            return True
    return False


def _build_import_entry(
    stmt: SgNode,
    root_packages: set[str],
    isort_cfg: _IsortConfig | None = None,
) -> _ImportEntry:
    """Construct an _ImportEntry with isort group and statement sort key."""
    start_ln = stmt.range().start.line
    end_ln = stmt.range().end.line
    first_line = stmt.text().splitlines()[0].strip()

    if stmt.kind() == "future_import_statement":
        skey = (1, 0, "__future__", "__future__")
        return _ImportEntry(stmt, start_ln, end_ln, 0, skey, not _are_imported_members_sorted(stmt), first_line)

    if stmt.kind() == "import_statement":
        names = [n.text().split(" as ")[0].strip() for n in stmt.field_children("name")]
        primary = names[0] if names else ""
        grp = _classify_group(primary, root_packages, isort_cfg)
        skey = (0, 0, primary.lower(), primary)
        return _ImportEntry(stmt, start_ln, end_ln, grp, skey, not _are_imported_members_sorted(stmt), first_line)

    mod_node = stmt.field("module_name")
    raw_mod = mod_node.text().strip() if mod_node is not None else ""
    grp = _classify_group(raw_mod, root_packages, isort_cfg)
    if raw_mod.startswith("."):
        dots = len(raw_mod) - len(raw_mod.lstrip("."))
        suffix = raw_mod.lstrip(".")
        skey = (1, 1 + dots, suffix.lower(), suffix)
    else:
        skey = (1, 0, raw_mod.lower(), raw_mod)
    return _ImportEntry(stmt, start_ln, end_ln, grp, skey, not _are_imported_members_sorted(stmt), first_line)


def _has_blank_line_between(source_lines: list[str], prev_end: int, curr_start: int) -> bool:
    """Return True if at least one empty line separates prev_end and curr_start."""
    if curr_start <= prev_end + 1:
        return False
    return any(not source_lines[idx].strip() for idx in range(prev_end + 1, min(curr_start, len(source_lines))))


def _validate_import_block(
    stmts: list[SgNode],
    root_packages: set[str],
    source_lines: list[str],
    rel_path: str,
    isort_cfg: _IsortConfig | None = None,
) -> list[CodeLocation]:
    """Validate isort group ordering, blank-line separation, and alphabetical sorting in one block."""
    issues: list[CodeLocation] = []
    entries = [
        _build_import_entry(s, root_packages, isort_cfg)
        for s in stmts
        if not _has_skip_comment(source_lines, s.range().start.line, s.range().end.line)
    ]

    for idx, entry in enumerate(entries):
        if entry.unsorted_members:
            issues.append(
                CodeLocation(
                    file=rel_path,
                    line=entry.start_line + 1,
                    symbol=entry.summary,
                    detail="Unsorted imported members within 'from ... import ...' (isort I001)",
                )
            )
        if idx == 0:
            continue
        prev = entries[idx - 1]
        if entry.group < prev.group:
            issues.append(
                CodeLocation(
                    file=rel_path,
                    line=entry.start_line + 1,
                    symbol=entry.summary,
                    detail=(
                        f"Import group '{_GROUP_LABELS[entry.group]}' appears after "
                        f"'{_GROUP_LABELS[prev.group]}' (isort I001)"
                    ),
                )
            )
        elif entry.group > prev.group:
            if not _has_blank_line_between(source_lines, prev.end_line, entry.start_line):
                issues.append(
                    CodeLocation(
                        file=rel_path,
                        line=entry.start_line + 1,
                        symbol=entry.summary,
                        detail=(
                            f"Missing blank line between '{_GROUP_LABELS[prev.group]}' and "
                            f"'{_GROUP_LABELS[entry.group]}' import groups (isort I001)"
                        ),
                    )
                )
        elif entry.sort_key < prev.sort_key:
            issues.append(
                CodeLocation(
                    file=rel_path,
                    line=entry.start_line + 1,
                    symbol=entry.summary,
                    detail=f"Out-of-order import within '{_GROUP_LABELS[entry.group]}' group (isort I001)",
                )
            )
    return issues


def _is_type_checking_if(node: SgNode) -> bool:
    """Return True if node is an `if TYPE_CHECKING:` or `if typing.TYPE_CHECKING:` block."""
    if node.kind() != "if_statement":
        return False
    cond = node.field("condition")
    if cond is None:
        return False
    cond_text = cond.text().strip()
    return "TYPE_CHECKING" in cond_text and "not" not in cond_text.split()


def _is_generated_facade_wildcard(wnode: SgNode, unit: ParsedUnit) -> bool:
    """Return True if wildcard import re-exports a *_generated module inside __init__.py or an __all__ facade."""
    if unit.file_path.name != "__init__.py" and "__all__" not in unit.source:
        return False
    parent = wnode.parent()
    if parent is None or parent.kind() != "import_from_statement":
        return False
    mod_node = parent.field("module_name")
    if mod_node is None:
        return False
    raw_mod = mod_node.text().strip().lstrip(".")
    leaf = raw_mod.rsplit(".", maxsplit=1)[-1] if raw_mod else ""
    return leaf == "_generated" or leaf.endswith("_generated")


def _is_docstring_expr(child: SgNode) -> bool:
    """Return True if child is a string literal expression_statement."""
    if child.kind() != "expression_statement":
        return False
    sub = child.named_children()
    return bool(sub and sub[0].kind() == "string")


def _collect_nested_late_imports(root: SgNode, rel_path: str, seen_stmt_ids: set[int]) -> list[CodeLocation]:
    """Collect non-top-level imports inside function or class bodies (excluding top-level try blocks)."""
    late: list[CodeLocation] = []
    for ikind in _IMPORT_KINDS:
        for stmt in root.find_all(kind=ikind):
            if stmt.range().start.index in seen_stmt_ids:
                continue
            if stmt.inside(kind="try_statement") and not stmt.inside(kind="function_definition"):
                continue
            late.append(
                CodeLocation(
                    file=rel_path,
                    line=stmt.range().start.line + 1,
                    symbol=stmt.text().splitlines()[0].strip(),
                    detail="Non-top-level / lazy import inside function or class body (PLC0415)",
                )
            )
    return late


def _extract_import_blocks_and_late_imports(
    root: SgNode,
    rel_path: str,
) -> tuple[list[list[SgNode]], list[CodeLocation]]:
    """Partition module imports into top-level/TYPE_CHECKING blocks vs late/nested imports."""
    blocks: list[list[SgNode]] = []
    top_imports: list[SgNode] = []
    late: list[CodeLocation] = []
    seen_stmt_ids: set[int] = set()
    seen_non_comment = False
    seen_executable = False

    for child in root.named_children():
        ckind = child.kind()
        if ckind == "comment":
            continue
        if not seen_non_comment and _is_docstring_expr(child):
            seen_non_comment = True
            continue
        seen_non_comment = True
        if ckind in _IMPORT_KINDS:
            seen_stmt_ids.add(child.range().start.index)
            if not seen_executable:
                top_imports.append(child)
            else:
                late.append(
                    CodeLocation(
                        file=rel_path,
                        line=child.range().start.line + 1,
                        symbol=child.text().splitlines()[0].strip(),
                        detail="Module-level import placed after executable statements (E402)",
                    )
                )
        elif _is_type_checking_if(child):
            conseq = child.field("consequence")
            tc_imports = [c for c in (conseq.named_children() if conseq else []) if c.kind() in _IMPORT_KINDS]
            seen_stmt_ids.update(tci.range().start.index for tci in tc_imports)
            if tc_imports:
                blocks.append(tc_imports)
        else:
            seen_executable = True

    if top_imports:
        blocks.insert(0, top_imports)
    late.extend(_collect_nested_late_imports(root, rel_path, seen_stmt_ids))
    return blocks, late


class PythonImportChecker(BaseImportChecker):
    """Validate PEP 8 / Ruff isort import grouping, blank lines, sorting, wildcards, and late imports."""

    def check(self, units: list[ParsedUnit], project_root: Path) -> ImportResult:
        """Aggregate Python import hygiene checks honoring pyproject.toml isort overrides."""
        if not self.applicable:
            return ImportResult(import_hygiene_coverage_pct=None)

        isort_cfg = _load_isort_config(project_root)
        root_packages = self.discover_root_packages(units, project_root)
        clean_units = 0
        unsorted: list[CodeLocation] = []
        wildcards: list[CodeLocation] = []
        late: list[CodeLocation] = []

        for unit in units:
            stats = self._inspect_unit_with_config(unit, root_packages, isort_cfg)
            if stats.is_clean and not stats.unsorted_imports and not stats.wildcard_imports:
                clean_units += 1
            unsorted.extend(stats.unsorted_imports)
            wildcards.extend(stats.wildcard_imports)
            late.extend(stats.late_imports)

        pct = round((clean_units / len(units)) * 100.0, 1) if units else 100.0
        return ImportResult(
            import_hygiene_coverage_pct=pct,
            unsorted_imports=unsorted,
            wildcard_imports=wildcards,
            late_imports=late,
        )

    def discover_root_packages(self, units: list[ParsedUnit], project_root: Path) -> set[str]:
        """Discover internal Python package root names adjusted by pyproject.toml isort overrides."""
        isort_cfg = _load_isort_config(project_root)
        pkgs: set[str] = set()
        for unit in units:
            mod = module_name_from_path(unit.file_path, project_root)
            if mod:
                pkgs.add(mod.split(".")[0])
        pkgs.update(p.split(".")[0] for p in isort_cfg.known_first_party if "." not in p)
        pkgs.update(p.split(".")[0] for p in isort_cfg.known_local_folder if "." not in p)
        pkgs.difference_update(p for p in isort_cfg.known_third_party if "." not in p)
        pkgs.difference_update(p for p in isort_cfg.extra_standard_library if "." not in p)
        return pkgs

    def _inspect_unit_with_config(
        self,
        unit: ParsedUnit,
        root_packages: set[str],
        isort_cfg: _IsortConfig | None = None,
    ) -> UnitImportStats:
        """Inspect a Python module for isort compliance, wildcard imports, and non-top-level imports."""
        source_lines = unit.source.splitlines()
        wildcards: list[CodeLocation] = []
        for wnode in unit.root.find_all(kind="wildcard_import"):
            if _is_generated_facade_wildcard(wnode, unit):
                continue
            parent = wnode.parent()
            sym = parent.text().strip() if parent is not None else "from ... import *"
            wildcards.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=wnode.range().start.line + 1,
                    symbol=sym,
                    detail="Wildcard import pollutes module namespace (F403)",
                )
            )

        blocks, late = _extract_import_blocks_and_late_imports(unit.root, unit.rel_path)
        unsorted: list[CodeLocation] = []
        for blk in blocks:
            unsorted.extend(_validate_import_block(blk, root_packages, source_lines, unit.rel_path, isort_cfg))

        return UnitImportStats(
            is_clean=not unsorted and not wildcards,
            unsorted_imports=unsorted,
            wildcard_imports=wildcards,
            late_imports=late,
        )

    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Inspect a Python module for isort compliance using default group classification."""
        return self._inspect_unit_with_config(unit, root_packages, None)
