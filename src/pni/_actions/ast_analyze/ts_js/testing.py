# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Vitest, Jest, Mocha, and Node test runner AST checker for TypeScript & JavaScript."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTestChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    TestAstResult,
)

_TEST_CALL_NAMES: Final[frozenset[str]] = frozenset(
    {"it", "test", "it.only", "test.only", "it.concurrent", "test.concurrent"}
)
_TS_JS_ASSERT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:expect|expectTypeOf|assert|assertType|expectType|expectNotType|expectAssignable)\s*(?:\.\w+\s*)?(?:\(|<)"
    r"|\b(?:[Aa]ssert|[Vv]erify|[Cc]heck)[A-Za-z0-9_$]*\s*\("
    r"|\.(?:toBe\w*|toEqual\w*|toStrictEqual|toMatch\w*|toThrow\w*|toHave\w*|resolves|rejects|should)\b"
    r"|\b(?:sinon\.assert|fc\.assert|td\.verify)\b"
    r"|@ts-expect-error"
)
_EXTERNAL_CDN_SCRIPT_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:<script[^>]+src\s*=\s*['\"]|['\"])https?://(?:unpkg\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com)/[^'\">\s]+",
    re.IGNORECASE,
)


def _extract_test_case_name(args_node: SgNode) -> str:
    """Extract the string description of an `it('...', fn)` or `test('...', fn)` call."""
    for child in args_node.children():
        if child.kind() in {"string", "template_string"}:
            return child.text().strip().strip("'\"`")[:60]
    return "<test>"


def _extract_test_callback(args_node: SgNode) -> SgNode | None:
    """Return the callback function node from an `it(...)` or `test(...)` argument list."""
    for child in reversed(list(args_node.children())):
        if child.kind() in {"arrow_function", "function_expression"}:
            return child
    return None


def _collect_test_helper_names(test_units: list[ParsedUnit]) -> set[str]:
    """Collect helper function names in test files that perform `expect`/`assert` checks."""
    helpers: set[str] = set()
    for unit in test_units:
        for fn_node in unit.root.find_all(kind="function_declaration"):
            nm = fn_node.field("name")
            if nm is not None and _TS_JS_ASSERT_RE.search(fn_node.text()):
                helpers.add(nm.text().strip())
        for decl in unit.root.find_all(kind="variable_declarator"):
            nm = decl.field("name")
            val = decl.field("value")
            if nm is not None and val is not None and _TS_JS_ASSERT_RE.search(val.text()):
                helpers.add(nm.text().strip())
    return helpers


_TEST_FILE_SUFFIXES: Final[tuple[str, ...]] = (
    ".test.tsx",
    ".spec.tsx",
    ".test.ts",
    ".spec.ts",
    "_test.ts",
    ".test.jsx",
    ".spec.jsx",
    ".test.mjs",
    ".spec.mjs",
    ".test.js",
    ".spec.js",
    "_test.js",
)


def _collect_unit_tested_stems(tu: ParsedUnit) -> set[str]:
    """Extract tested module stems from a single test unit's filename and import/require statements."""
    stems: set[str] = set()
    fname = tu.file_path.name
    base_stem = next(
        (fname[: -len(sfx)].lower() for sfx in _TEST_FILE_SUFFIXES if fname.endswith(sfx)),
        tu.file_path.stem.lower(),
    )
    stems.add(base_stem)
    if base_stem.startswith("hx-"):
        stems.add(base_stem.removeprefix("hx-"))
    for m in re.finditer(r"from\s+['\"]([^'\"]+)['\"]|require\(\s*['\"]([^'\"]+)['\"]\s*\)", tu.source):
        imp = (m.group(1) or m.group(2) or "").rsplit("/", 1)[-1]
        for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs"):
            imp = imp.removesuffix(ext)
        if imp:
            stems.add(imp.lower())
    return stems


def _compute_ts_js_module_coverage(
    test_units: list[ParsedUnit],
    source_units: list[ParsedUnit],
    test_count: int,
) -> float | None:
    """Compute percentage of TS/JS source modules covered by test files."""
    if not source_units:
        return 100.0 if test_count > 0 else None

    tested_stems: set[str] = set()
    for tu in test_units:
        tested_stems.update(_collect_unit_tested_stems(tu))

    src_stems = {
        su.file_path.stem.lower()
        for su in source_units
        if su.file_path.stem.lower() not in {"index", "types", "constants"}
    }
    if not src_stems:
        return 100.0 if test_count > 0 else None

    for missing_stem in list(src_stems - tested_stems):
        if len(missing_stem) >= 3 and any(
            re.search(rf"\b{re.escape(missing_stem)}\b", tu.source) for tu in test_units
        ):
            tested_stems.add(missing_stem)

    matched = len(src_stems & tested_stems)
    return round((matched / len(src_stems)) * 100.0, 1)


def _scan_external_cdn_test_refs(project_root: Path) -> list[str]:
    """Scan test configs and HTML fixtures for external CDN script URLs that break under --network=none."""
    candidates: list[Path] = []
    for pat in ("web-test-runner.config.*", "karma.conf.*", "playwright.config.*"):
        candidates.extend(sorted(project_root.glob(pat)))
    for tdir_name in ("test", "tests", "__tests__"):
        tdir = project_root / tdir_name
        if tdir.is_dir():
            candidates.extend(sorted(tdir.rglob("*.html"))[:30])
            candidates.extend(sorted(tdir.glob("*.config.*"))[:10])
    flagged: list[str] = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _EXTERNAL_CDN_SCRIPT_RE.search(text):
            rel = path.relative_to(project_root).as_posix() if path.is_relative_to(project_root) else path.name
            flagged.append(rel)
    return flagged


class TsJsTestChecker(BaseTestChecker):
    """Evaluate Vitest / Jest / Mocha / `node:test` test cases and assertion presence."""

    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Count `it`/`test` blocks, detect assertion-free tests, and compute module coverage."""
        helper_names = _collect_test_helper_names(test_units)
        test_count = 0
        assertion_free: list[CodeLocation] = []
        notes: list[str] = []
        only_count = 0
        overmock_count = 0

        for unit in test_units:
            for call in unit.root.find_all(kind="call_expression"):
                fn = call.field("function")
                args = call.field("arguments")
                if fn is None or args is None:
                    continue
                fn_text = fn.text().strip()
                only_count += int(fn_text in {"it.only", "test.only", "describe.only"})
                if fn_text not in _TEST_CALL_NAMES and not fn_text.startswith(("it.each", "test.each")):
                    continue
                cb = _extract_test_callback(args)
                if cb is None:
                    continue
                test_count += 1
                case_name = _extract_test_case_name(args)
                cb_text = cb.text()
                overmock_count += int(
                    len(re.findall(r"\b(?:vi|jest|sinon)\.(?:fn|spyOn|stub|mock)\s*\(", cb_text)) > 5
                )
                has_assert = bool(_TS_JS_ASSERT_RE.search(cb_text)) or any(
                    re.search(rf"\b{re.escape(h)}\s*\(", cb_text) for h in helper_names
                )
                if not has_assert:
                    assertion_free.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=call.range().start.line + 1,
                            symbol=case_name,
                            detail=f"Test case '{case_name}' has no `expect(...)` or `assert` verification",
                        )
                    )

        if only_count > 0:
            notes.append(f"{only_count} focused `.only(...)` test/suite call(s) detected")
        if overmock_count > 0:
            notes.append(f"{overmock_count} test case(s) create >5 mocks (`vi.fn`/`jest.fn`)")
        cdn_files = _scan_external_cdn_test_refs(project_root)
        if cdn_files:
            sample = ", ".join(cdn_files[:3])
            notes.append(
                f"External CDN `<script>` reference(s) in test harness ({sample}) — "
                "prefetch and rewrite to local files during Docker build so `--network=none` tests succeed"
            )

        return TestAstResult(
            test_functions_count=test_count,
            module_test_coverage_pct=_compute_ts_js_module_coverage(test_units, source_units, test_count),
            assertion_free_tests=assertion_free,
            test_harness_notes=notes,
        )
