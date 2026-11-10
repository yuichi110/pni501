# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHPUnit and Pest test-suite AST checker for test counts, module coverage, and assertion density."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseTestChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, TestAstResult
from pni._actions.ast_analyze.php._helpers import (
    extract_node_name,
    find_preceding_phpdoc,
    get_visibility,
    iter_direct_type_methods,
    iter_php_types,
)

_ASSERTION_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:\bassert[A-Z_][A-Za-z0-9_]*\s*\("
    r"|\bexpectException[A-Za-z]*\s*\("
    r"|\bexpectOutput(?:String|Regex)\s*\("
    r"|\bexpectNotToPerformAssertions\s*\("
    r"|->\s*expects\s*\("
    r"|\bexpect\s*\("
    r"|\bassertDatabase[A-Za-z]*\s*\("
    r"|\bassertStatus\s*\("
    r"|\bassertJson[A-Za-z]*\s*\("
    r"|\bmock\s*\("
    r"|\bshouldReceive\s*\("
    r"|\bshouldHaveReceived[A-Za-z]*\s*\("
    r"|\bshould(?:Not)?(?:Be|HaveBeen)Called[A-Za-z]*\s*\()"
)
_PEST_TEST_CALL_NAMES: Final[frozenset[str]] = frozenset({"test", "it"})


def _is_phpunit_test_method(mnode: SgNode) -> bool:
    """Return True if a PHP method is a public `test*` method or carries `#[Test]` / `@test`."""
    if get_visibility(mnode) != "public":
        return False
    mname = extract_node_name(mnode)
    if mname.startswith("test") and len(mname) > 4:
        return True
    for child in mnode.children():
        if child.kind() == "attribute_list" and re.search(r"#\[\s*Test\b", child.text()):
            return True
    doc = find_preceding_phpdoc(mnode)
    return bool(doc and re.search(r"@test\b", doc))


class PhpTestChecker(BaseTestChecker):
    """Evaluate PHPUnit (`TestCase`) and Pest (`test()`/`it()`) test methods and assertion presence."""

    def _inspect_test_unit(self, tunit: ParsedUnit, assertion_free: list[CodeLocation]) -> int:
        """Count PHPUnit/Pest test callables in a single test file and append assertion-free cases."""
        unit_count = 0
        for type_name, tnode in iter_php_types(tunit.root):
            for mnode in iter_direct_type_methods(tnode):
                if not _is_phpunit_test_method(mnode):
                    continue
                unit_count += 1
                mname = extract_node_name(mnode)
                body = mnode.find(kind="compound_statement")
                body_text = body.text() if body is not None else ""
                if not _ASSERTION_RE.search(body_text):
                    assertion_free.append(
                        CodeLocation(
                            file=tunit.rel_path,
                            line=mnode.range().start.line + 1,
                            symbol=f"{type_name}::{mname}",
                            detail="PHPUnit test method contains no assertion or expectation calls",
                        )
                    )

        for fcall in tunit.root.find_all(kind="function_call_expression"):
            children = fcall.children()
            callee = children[0].text().strip() if children else ""
            if callee in _PEST_TEST_CALL_NAMES:
                unit_count += 1
                if not _ASSERTION_RE.search(fcall.text()):
                    assertion_free.append(
                        CodeLocation(
                            file=tunit.rel_path,
                            line=fcall.range().start.line + 1,
                            symbol=callee,
                            detail=f"Pest '{callee}(...)' block contains no expect()/assert*() calls",
                        )
                    )
        return unit_count

    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Count PHPUnit/Pest test callables, detect assertion-free tests, and estimate module coverage."""
        _ = project_root
        assertion_free: list[CodeLocation] = []
        test_count = sum(self._inspect_test_unit(tu, assertion_free) for tu in test_units)
        combined_test_text = "\n".join(tu.source for tu in test_units)

        covered_modules = 0
        eligible_modules = 0
        for sunit in source_units:
            stem = sunit.file_path.stem
            if stem in {"index", "routes", "api", "web", "console"}:
                continue
            eligible_modules += 1
            type_names = [tname for tname, _ in iter_php_types(sunit.root)]
            tokens = [stem, *type_names]
            if any(re.search(rf"\b{re.escape(tok)}\b", combined_test_text) for tok in tokens if tok):
                covered_modules += 1

        mod_cov = round((covered_modules / eligible_modules) * 100.0, 1) if eligible_modules > 0 else 100.0
        return TestAstResult(
            test_functions_count=test_count,
            module_test_coverage_pct=mod_cov,
            assertion_free_tests=assertion_free,
        )
