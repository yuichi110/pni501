# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python pytest / unittest AST test-suite health and assertion-free test checker."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Final

from ast_grep_py import SgNode, SgRoot

from pni._actions.ast_analyze.base import BaseTestChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, TestAstResult
from pni._actions.ast_analyze.python._helpers import (
    function_symbol_name,
    module_name_from_path,
)

_ASSERT_CALL_TOKENS: Final[tuple[str, ...]] = (
    "pytest.raises",
    "pytest.warns",
    "pytest.fail",
    "raises(",
    ".assert",
    "self.assert",
    "self.fail",
    "assert_",
    "check_",
    "verify_",
)
_PYTEST_ASSERTION_HOOKS: Final[frozenset[str]] = frozenset(
    {
        "pytest_runtest_call",
        "pytest_runtest_makereport",
        "pytest_pyfunc_call",
    }
)


def _has_test_assertion(fn_node: SgNode) -> bool:
    """Return True if a Python test function contains an assert statement or assertion helper call."""
    if fn_node.find_all(kind="assert_statement"):
        return True
    body_text = fn_node.text()
    return any(tok in body_text for tok in _ASSERT_CALL_TOKENS)


def _is_autouse_post_yield_assertion_fixture(fn_node: SgNode) -> bool:
    """Return True if fn_node is an @pytest.fixture(..., autouse=True) with post-yield verification."""
    parent = fn_node.parent()
    if parent is None or parent.kind() != "decorated_definition":
        return False
    is_autouse = any(
        child.kind() == "decorator" and "fixture" in child.text() and "autouse=True" in child.text().replace(" ", "")
        for child in parent.named_children()
    )
    if not is_autouse:
        return False
    yields = fn_node.find_all(kind="yield")
    if not yields:
        return _has_test_assertion(fn_node)
    first_yield_end = yields[0].range().end.index
    for assert_node in fn_node.find_all(kind="assert_statement"):
        if assert_node.range().start.index > first_yield_end:
            return True
    tail_text = fn_node.text()[first_yield_end - fn_node.range().start.index :]
    return any(tok in tail_text for tok in _ASSERT_CALL_TOKENS)


def _inspect_conftest_root(root: SgNode, rel_path: str) -> list[str]:
    """Return harness notes if a conftest.py CST defines automated test-verification hooks/fixtures."""
    notes: list[str] = []
    for fn_node in root.find_all(kind="function_definition"):
        fn_name = function_symbol_name(fn_node)
        if fn_name in _PYTEST_ASSERTION_HOOKS and _has_test_assertion(fn_node):
            notes.append(f"{rel_path}: '{fn_name}' hook performs automated test assertions")
        elif _is_autouse_post_yield_assertion_fixture(fn_node):
            notes.append(f"{rel_path}: autouse fixture '{fn_name}' performs automated post-test assertions")
    return notes


def _discover_conftest_assertion_scopes(
    test_units: list[ParsedUnit],
    project_root: Path,
) -> tuple[list[Path], list[str]]:
    """Discover directory scopes governed by conftest.py automated assertion hooks or autouse fixtures."""
    checked_paths: set[Path] = set()
    scope_dirs: list[Path] = []
    notes: list[str] = []

    for unit in test_units:
        if unit.file_path.name != "conftest.py":
            continue
        checked_paths.add(unit.file_path.resolve())
        unit_notes = _inspect_conftest_root(unit.root, unit.rel_path)
        if unit_notes:
            scope_dirs.append(unit.file_path.parent.resolve())
            notes.extend(unit_notes)

    root_resolved = project_root.resolve()
    ancestor_dirs: set[Path] = set()
    for unit in test_units:
        curr = unit.file_path.resolve().parent
        while curr == root_resolved or curr.is_relative_to(root_resolved):
            ancestor_dirs.add(curr)
            if curr == root_resolved:
                break
            curr = curr.parent

    for adir in sorted(ancestor_dirs):
        cfile = (adir / "conftest.py").resolve()
        if cfile in checked_paths or not cfile.is_file():
            continue
        checked_paths.add(cfile)
        with contextlib.suppress(Exception):
            src = cfile.read_text(encoding="utf-8")
            root = SgRoot(src, "python").root()
            rel = cfile.relative_to(root_resolved).as_posix() if cfile.is_relative_to(root_resolved) else cfile.name
            extra_notes = _inspect_conftest_root(root, rel)
            if extra_notes:
                scope_dirs.append(adir)
                notes.extend(extra_notes)

    return scope_dirs, notes


def _compute_module_test_coverage(
    test_units: list[ParsedUnit],
    source_units: list[ParsedUnit],
    project_root: Path,
) -> float | None:
    """Compute percentage of non-__init__ public source modules referenced or matched by tests."""
    public_mods: list[tuple[str, str]] = []
    for su in source_units:
        stem = su.file_path.stem
        if stem == "__init__" or stem.startswith("_"):
            continue
        mod_full = module_name_from_path(su.file_path, project_root)
        public_mods.append((stem, mod_full))

    if not public_mods:
        return None

    combined_test_src = "\n".join(tu.source for tu in test_units)
    test_stems = {tu.file_path.stem for tu in test_units}
    covered = 0
    for stem, mod_full in public_mods:
        top_pkg = mod_full.split(".")[0]
        if (
            f"test_{stem}" in test_stems
            or f"{stem}_test" in test_stems
            or mod_full in combined_test_src
            or stem in combined_test_src
            or top_pkg in combined_test_src
        ):
            covered += 1
    return round((covered / len(public_mods)) * 100.0, 1)


class PythonTestChecker(BaseTestChecker):
    """Inspect Python test files for test function counts, assertion presence, and module coverage."""

    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Analyze test_* functions across Python test units, respecting conftest assertion hooks."""
        total_tests = 0
        assertion_free: list[CodeLocation] = []
        hook_scope_dirs, harness_notes = _discover_conftest_assertion_scopes(test_units, project_root)

        for unit in test_units:
            unit_resolved = unit.file_path.resolve()
            covered_by_hook = any(unit_resolved.is_relative_to(sdir) for sdir in hook_scope_dirs)
            for fn_node in unit.root.find_all(kind="function_definition"):
                fn_name = function_symbol_name(fn_node)
                is_nested = fn_node.parent() is not None and fn_node.inside(kind="function_definition")
                if is_nested or not fn_name.startswith("test"):
                    continue
                total_tests += 1
                if not covered_by_hook and not _has_test_assertion(fn_node):
                    assertion_free.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=fn_node.range().start.line + 1,
                            symbol=fn_name,
                            detail="Test function has no 'assert' or 'pytest.raises' verification",
                        )
                    )

        cov_pct = _compute_module_test_coverage(test_units, source_units, project_root)
        return TestAstResult(
            test_functions_count=total_tests,
            module_test_coverage_pct=cov_pct,
            assertion_free_tests=assertion_free,
            test_harness_notes=harness_notes,
        )
