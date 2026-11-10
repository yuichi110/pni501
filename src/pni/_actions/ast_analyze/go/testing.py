# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go `*_test.go` test suite AST checker for `TestXxx`, `BenchmarkXxx`, and `FuzzXxx`."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTestChecker
from pni._actions.ast_analyze.go._helpers import (
    get_go_callable_params,
    iter_go_callables,
)
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    TestAstResult,
)

_GO_ASSERT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:t|b|f|s)\.(?:Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b"
    r"|\b(?:assert|require|is)\.\w+\s*\("
    r"|\bcmp\.(?:Diff|Equal)\s*\("
    r"|\breflect\.DeepEqual\s*\("
)
_TESTING_PARAM_TYPES: Final[tuple[str, ...]] = ("testing.T", "testing.B", "testing.F", "testing.TB")
_PUNCTUATION_KINDS: Final[frozenset[str]] = frozenset({"(", ")", ","})


def _is_go_test_function(name: str) -> bool:
    """Return True if a Go function name is a `Test*`, `Benchmark*`, `Fuzz*`, or `Example*` entry point."""
    for prefix in ("Test", "Benchmark", "Fuzz", "Example"):
        if name.startswith(prefix) and (len(name) == len(prefix) or not name[len(prefix)].islower()):
            return name != "TestMain"
    return False


def _collect_helper_functions(test_units: list[ParsedUnit]) -> set[str]:
    """Return names of intra-package helper functions in `*_test.go` files that contain assertions or `t.Helper()`."""
    helpers: set[str] = set()
    for unit in test_units:
        for _qual, short, node in iter_go_callables(unit):
            if _is_go_test_function(short):
                continue
            body_text = node.text()
            if ".Helper()" in body_text or _GO_ASSERT_RE.search(body_text):
                helpers.add(short)
    return helpers


def _extract_testing_param_names(node: SgNode) -> set[str]:
    """Return `*testing.T` / `*testing.B` / `*testing.F` parameter names declared on a test callable."""
    names: set[str] = {"t", "b", "f"}
    for pname, ptype in get_go_callable_params(node):
        if pname != "_" and any(tok in ptype for tok in _TESTING_PARAM_TYPES):
            names.add(pname)
    return names


def _call_delegates_assertion(call: SgNode, helper_names: set[str], testing_params: set[str]) -> bool:
    """Return True if `call` invokes a known helper, passes `t` to a helper, or delegates `t.Run(name, fn)`."""
    fn = call.field("function")
    callee_short = ""
    if fn is not None:
        fn_text = fn.text().strip()
        callee_short = fn_text.rsplit(".", 1)[-1]
        if callee_short in helper_names:
            return True

    args_node = call.field("arguments")
    if args_node is None:
        return False
    arg_nodes = [c for c in args_node.children() if c.kind() not in _PUNCTUATION_KINDS]
    if callee_short == "Run" and len(arg_nodes) >= 2 and arg_nodes[1].kind() != "func_literal":
        return True
    return any(arg.kind() == "identifier" and arg.text().strip() in testing_params for arg in arg_nodes)


def _test_has_assertion(node: SgNode, short_name: str, helper_names: set[str]) -> bool:
    """Return True if a Go test function verifies outcomes via `testing.T`, `testify`, `Example` output, or helpers."""
    if short_name.startswith(("Benchmark", "Example")):
        return True
    text = node.text()
    if _GO_ASSERT_RE.search(text):
        return True
    testing_params = _extract_testing_param_names(node)
    return any(
        _call_delegates_assertion(call, helper_names, testing_params)
        for call in node.find_all(kind="call_expression")
    )


class GoTestChecker(BaseTestChecker):
    """Evaluate Go `*_test.go` test functions, assertion presence, and package test alignment."""

    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Count Go test functions, flag assertion-free tests, and compute package test coverage."""
        _ = project_root
        helper_names = _collect_helper_functions(test_units)
        test_count = 0
        assertion_free: list[CodeLocation] = []

        notes: list[str] = []
        sleep_count = 0
        for unit in test_units:
            for qual, short, node in iter_go_callables(unit):
                if not _is_go_test_function(short):
                    continue
                test_count += 1
                if "time.Sleep(" in node.text():
                    sleep_count += 1
                if not _test_has_assertion(node, short, helper_names):
                    assertion_free.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=node.range().start.line + 1,
                            symbol=qual,
                            detail=f"Go test '{qual}' has no t.Error*/t.Fatal* or assert/require verification",
                        )
                    )
        if sleep_count > 0:
            notes.append(f"{sleep_count} Go test function(s) use `time.Sleep(...)` synchronization")

        src_dirs = {u.file_path.parent for u in source_units}
        tst_dirs = {u.file_path.parent for u in test_units}
        if src_dirs:
            covered = len(src_dirs & tst_dirs)
            cov_pct: float | None = round((covered / len(src_dirs)) * 100.0, 1)
        else:
            cov_pct = 100.0 if test_units else None

        return TestAstResult(
            test_functions_count=test_count,
            module_test_coverage_pct=cov_pct,
            assertion_free_tests=assertion_free,
            test_harness_notes=notes,
        )
