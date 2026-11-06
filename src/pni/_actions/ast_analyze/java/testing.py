# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java JUnit test suite AST checker (test count, module coverage, assertion-free tests)."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTestChecker
from pni._actions.ast_analyze.java._helpers import callable_symbol_name, get_modifiers_node, unit_fqn
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, TestAstResult

_TEST_ANNOTATIONS: Final[tuple[str, ...]] = (
    "@Test",
    "@ParameterizedTest",
    "@RepeatedTest",
    "@TestFactory",
)
_ASSERTION_PREFIXES: Final[tuple[str, ...]] = (
    "assert",
    "verify",
    "expect",
    "fail",
    "check",
    "should",
    "assume",
)


def _is_junit_test_method(mnode: SgNode) -> bool:
    """Return True if a Java method carries a JUnit test annotation."""
    mods = get_modifiers_node(mnode)
    if mods is None:
        return False
    text = mods.text()
    return any(ann in text for ann in _TEST_ANNOTATIONS)


def _method_has_assertion(mnode: SgNode) -> bool:
    """Return True if a Java test method invokes an assertion/verification helper or @Test(expected=...)."""
    mods = get_modifiers_node(mnode)
    if mods is not None and "expected" in mods.text():
        return True
    if mnode.find(kind="assert_statement") is not None:
        return True
    for inv in mnode.find_all(kind="method_invocation"):
        name_node = inv.field("name")
        callee = (name_node.text() if name_node is not None else inv.text()).lower()
        if callee.startswith(_ASSERTION_PREFIXES):
            return True
    return False


def _collect_covered_source_fqns(
    test_units: list[ParsedUnit],
    source_fqns: set[str],
    simple_to_fqns: dict[str, set[str]],
) -> set[str]:
    """Identify source Java FQNs referenced by imports or type identifiers across test units."""
    covered: set[str] = set()
    for tunit in test_units:
        for imp in tunit.root.find_all(kind="import_declaration"):
            raw = imp.text().removeprefix("import").strip().removesuffix(";").removeprefix("static ").strip()
            if raw in source_fqns:
                covered.add(raw)
        for tid in tunit.root.find_all(kind="type_identifier"):
            tname = tid.text()
            if tname in simple_to_fqns:
                covered.update(simple_to_fqns[tname])
        stem = tunit.file_path.stem
        for suffix in ("Tests", "Test", "IT"):
            if stem.endswith(suffix) and len(stem) > len(suffix):
                target_simple = stem[: -len(suffix)]
                covered.update(simple_to_fqns.get(target_simple, set()))
    return covered


class JavaTestChecker(BaseTestChecker):
    """Inspect JUnit test methods for assertion presence and source type coverage."""

    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Analyze Java test units for @Test methods, assertions, and covered source types."""
        _ = project_root
        test_count = 0
        assertion_free: list[CodeLocation] = []

        for tunit in test_units:
            for mnode in tunit.root.find_all(kind="method_declaration"):
                if not _is_junit_test_method(mnode):
                    continue
                test_count += 1
                if not _method_has_assertion(mnode):
                    mname = callable_symbol_name(mnode)
                    assertion_free.append(
                        CodeLocation(
                            file=tunit.rel_path,
                            line=mnode.range().start.line + 1,
                            symbol=mname,
                            detail=f"JUnit test method '{mname}' has no assertion or verification call",
                        )
                    )

        source_fqns: set[str] = set()
        simple_to_fqns: dict[str, set[str]] = {}
        for sunit in source_units:
            if sunit.file_path.name == "package-info.java":
                continue
            _, fqn = unit_fqn(sunit)
            source_fqns.add(fqn)
            simple_to_fqns.setdefault(sunit.file_path.stem, set()).add(fqn)

        cov_pct: float | None = None
        if source_fqns:
            covered = _collect_covered_source_fqns(test_units, source_fqns, simple_to_fqns)
            cov_pct = round((len(covered) / len(source_fqns)) * 100.0, 1)

        return TestAstResult(
            test_functions_count=test_count,
            module_test_coverage_pct=cov_pct,
            assertion_free_tests=assertion_free,
        )
