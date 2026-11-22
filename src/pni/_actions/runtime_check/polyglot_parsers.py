# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic test-output and coverage parsers for extended polyglot container harnesses."""

from __future__ import annotations

import contextlib
import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Final, Optional

from pni._actions.runtime_check.models import (
    CoverageResult,
    FailedTestCase,
    ModuleCoverageItem,
)
from pni._actions.runtime_check.parsers import (
    parse_clover_xml,
    parse_istanbul_coverage_summary,
    parse_jacoco_xml,
    parse_lcov_info,
    parse_node_test_output,
)

_MAX_FAILURE_ITEMS: Final[int] = 25
_MAX_LOWEST_MODULES: Final[int] = 15
_MAX_MISSING_LINES: Final[int] = 10
_ANSI_ESCAPE_RE: Final[re.Pattern[str]] = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_BENIGN_DOCTYPE_RE: Final[re.Pattern[str]] = re.compile(r"<!DOCTYPE\s+[^>\[\]]+>", re.IGNORECASE)

_RUST_SUMMARY_RE: Final[re.Pattern[str]] = re.compile(
    r"test result:\s+(?:ok|FAILED)\.\s+(\d+)\s+passed;\s+(\d+)\s+failed;\s+(\d+)\s+ignored;",
)
_RUST_FAIL_CASE_RE: Final[re.Pattern[str]] = re.compile(r"^test\s+(\S+)\s+\.\.\.\s+FAILED\s*$")
_DOTNET_SUMMARY_RE: Final[re.Pattern[str]] = re.compile(
    r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)",
)
_RSPEC_SUMMARY_RE: Final[re.Pattern[str]] = re.compile(
    r"(\d+)\s+examples?,\s+(\d+)\s+failures?(?:,\s+(\d+)\s+pending)?",
)
_MINITEST_SUMMARY_RE: Final[re.Pattern[str]] = re.compile(
    r"(\d+)\s+runs?,\s+\d+\s+assertions?,\s+(\d+)\s+failures?,\s+(\d+)\s+errors?,\s+(\d+)\s+skips?",
)
_SWIFT_XCTEST_RE: Final[re.Pattern[str]] = re.compile(
    r"Executed\s+(\d+)\s+tests?,\s+with\s+(\d+)\s+failures?",
)
_SWIFT_TESTING_RE: Final[re.Pattern[str]] = re.compile(
    r"Test run with\s+(\d+)\s+tests?.*?(passed|failed)",
    re.IGNORECASE,
)
_ELIXIR_SUMMARY_RE: Final[re.Pattern[str]] = re.compile(
    r"(\d+)\s+tests?,\s+(\d+)\s+failures?(?:,\s+(\d+)\s+(?:skipped|excluded))?",
)
_DART_COUNT_RE: Final[re.Pattern[str]] = re.compile(r"\+(\d+)(?:\s+~(\d+))?(?:\s+-(\d+))?:")
_R_TESTTHAT_RE: Final[re.Pattern[str]] = re.compile(
    r"\[\s*FAIL\s+(\d+)\s*\|\s*WARN\s+\d+\s*\|\s*SKIP\s+(\d+)\s*\|\s*PASS\s+(\d+)\s*\]",
)
_SCALA_SBT_RE: Final[re.Pattern[str]] = re.compile(
    r"Total\s+(\d+),\s+Failed\s+(\d+),\s+Errors\s+(\d+),\s+Passed\s+(\d+)(?:,\s+(?:Skipped|Ignored)\s+(\d+))?",
)
_SCALATEST_RE: Final[re.Pattern[str]] = re.compile(
    r"Tests:\s+succeeded\s+(\d+),\s+failed\s+(\d+),\s+canceled\s+(\d+),\s+ignored\s+(\d+),\s+pending\s+(\d+)",
)
_TAP_OK_RE: Final[re.Pattern[str]] = re.compile(r"^(ok|not ok)\s+\d*(?:\s*-\s*(.*))?$", re.IGNORECASE)
_GENERIC_PASSED_FAILED_RE: Final[re.Pattern[str]] = re.compile(
    r"(\d+)\s+passed.*?(\d+)\s+failed",
    re.IGNORECASE,
)

ParsedTestTuple = tuple[int, int, int, int, int, list[FailedTestCase]]
_EMPTY_RESULT: Final[ParsedTestTuple] = (0, 0, 0, 0, 0, [])


def _read_clean_text(path: Path) -> str:
    """Read UTF-8 text from path with ANSI escape sequences stripped."""
    if not path.is_file():
        return ""
    with contextlib.suppress(Exception):
        raw = path.read_text(encoding="utf-8", errors="replace")
        return _ANSI_ESCAPE_RE.sub("", raw)
    return ""


def _safe_parse_xml(xml_path: Path) -> Optional[ET.Element]:
    """Parse an XML file after rejecting ENTITY / internal-subset DTD declarations."""
    if not xml_path.is_file():
        return None
    with contextlib.suppress(Exception):
        raw = xml_path.read_text(encoding="utf-8", errors="replace")
        if "<!ENTITY" in raw.upper():
            return None
        cleaned = _BENIGN_DOCTYPE_RE.sub("", raw, count=1)
        if "<!DOCTYPE" in cleaned.upper():
            return None
        return ET.fromstring(cleaned)  # noqa: S314
    return None


def _compute_pct(covered: int, total: int) -> float:
    """Compute percentage rounded to one decimal place (100.0 when total <= 0)."""
    if total <= 0:
        return 100.0
    return round((covered / total) * 100.0, 1)


def _strip_xml_ns(tag: str) -> str:
    """Strip Clark-notation XML namespace prefix from an Element tag."""
    if "}" in tag:
        return tag.rsplit("}", maxsplit=1)[-1]
    return tag


def parse_rust_test_output(path: Path) -> ParsedTestTuple:
    """Parse `cargo test` output aggregating counts across all test binaries."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    passed = 0
    failed = 0
    skipped = 0
    failures: list[FailedTestCase] = []
    for line in clean.splitlines():
        m = _RUST_SUMMARY_RE.search(line)
        if m:
            passed += int(m.group(1))
            failed += int(m.group(2))
            skipped += int(m.group(3))
            continue
        fm = _RUST_FAIL_CASE_RE.match(line.strip())
        if fm:
            failures.append(
                FailedTestCase(
                    classname="cargo.test",
                    name=fm.group(1),
                    kind="failure",
                    message=line.strip()[:240],
                )
            )
    total = passed + failed + skipped
    return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]


def parse_dotnet_trx_xml(trx_path: Path) -> ParsedTestTuple:
    """Parse Microsoft Visual Studio TRX XML report emitted by `dotnet test --logger trx`."""
    root = _safe_parse_xml(trx_path)
    if root is None:
        return _EMPTY_RESULT

    passed = 0
    failed = 0
    skipped = 0
    failures: list[FailedTestCase] = []

    for elem in root.iter():
        if _strip_xml_ns(elem.tag) != "UnitTestResult":
            continue
        outcome = elem.attrib.get("outcome", "").strip().lower()
        name = elem.attrib.get("testName", "unknown")
        if outcome == "passed":
            passed += 1
        elif outcome in {"notexecuted", "skipped", "inconclusive"}:
            skipped += 1
        elif outcome:
            failed += 1
            msg = ""
            for child in elem.iter():
                if _strip_xml_ns(child.tag) == "Message" and child.text:
                    msg = child.text.strip().splitlines()[0][:240]
                    break
            failures.append(
                FailedTestCase(
                    classname="dotnet.test",
                    name=name,
                    kind="failure",
                    message=msg or f"Test {outcome}",
                )
            )

    total = passed + failed + skipped
    return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]


def parse_dotnet_test_output(path: Path) -> ParsedTestTuple:
    """Parse `dotnet test` console summary when TRX XML is absent."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    passed = 0
    failed = 0
    skipped = 0
    total = 0
    for m in _DOTNET_SUMMARY_RE.finditer(clean):
        failed += int(m.group(1))
        passed += int(m.group(2))
        skipped += int(m.group(3))
        total += int(m.group(4))
    if total == 0:
        return _EMPTY_RESULT

    failures: list[FailedTestCase] = []
    if failed > 0:
        for line in clean.splitlines():
            s = line.strip()
            if s.startswith("Failed ") and "[" in s:
                name = s.removeprefix("Failed ").split("[", maxsplit=1)[0].strip()
                failures.append(
                    FailedTestCase(classname="dotnet.test", name=name[:80], kind="failure", message=s[:240])
                )
    return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]


def _accumulate_cobertura_class(
    cls_el: ET.Element,
    workspace_prefix: str,
    seen_files: dict[str, tuple[int, int, int, int, list[int]]],
) -> None:
    """Fold one Cobertura `<class>` element's line and branch hits into seen_files."""
    raw_fn = cls_el.attrib.get("filename", "").replace("\\", "/")
    if not raw_fn:
        return
    rel_fn = raw_fn.removeprefix(workspace_prefix).lstrip("/")
    cov_l, tot_l, cov_b, tot_b, missed = seen_files.get(rel_fn, (0, 0, 0, 0, []))
    for line_el in cls_el.findall("./lines/line"):
        hits = int(line_el.attrib.get("hits", "0") or 0)
        tot_l += 1
        if hits > 0:
            cov_l += 1
        else:
            num = int(line_el.attrib.get("number", "0") or 0)
            if num > 0 and num not in missed and len(missed) < _MAX_MISSING_LINES:
                missed.append(num)
        cond = line_el.attrib.get("condition-coverage", "")
        bm = re.search(r"\((\d+)/(\d+)\)", cond)
        if bm:
            cov_b += int(bm.group(1))
            tot_b += int(bm.group(2))
    seen_files[rel_fn] = (cov_l, tot_l, cov_b, tot_b, missed)


def parse_cobertura_xml(
    cobertura_path: Path,
    workspace_prefix: str = "/workspace/",
) -> CoverageResult:
    """Parse Cobertura XML coverage report (Coverlet, Tarpaulin, llvm-cov, etc.)."""
    root = _safe_parse_xml(cobertura_path)
    if root is None:
        return CoverageResult()

    seen_files: dict[str, tuple[int, int, int, int, list[int]]] = {}
    for cls_el in root.findall(".//class"):
        _accumulate_cobertura_class(cls_el, workspace_prefix, seen_files)

    items: list[ModuleCoverageItem] = []
    total_cov = 0
    total_stmts = 0
    total_bcov = 0
    total_btotal = 0
    for rel_fn, (cov_l, tot_l, cov_b, tot_b, missed) in seen_files.items():
        total_cov += cov_l
        total_stmts += tot_l
        total_bcov += cov_b
        total_btotal += tot_b
        items.append(
            ModuleCoverageItem(
                file_path=rel_fn,
                line_coverage_pct=_compute_pct(cov_l, tot_l),
                branch_coverage_pct=_compute_pct(cov_b, tot_b) if tot_b > 0 else None,
                covered_lines=cov_l,
                total_statements=tot_l,
                missing_lines_preview=missed,
            )
        )

    if total_stmts == 0:
        lines_valid = int(root.attrib.get("lines-valid", "0") or 0)
        lines_cov = int(root.attrib.get("lines-covered", "0") or 0)
        if lines_valid <= 0:
            return CoverageResult()
        total_cov, total_stmts = lines_cov, lines_valid

    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="cobertura",
        line_coverage_pct=_compute_pct(total_cov, total_stmts),
        branch_coverage_pct=_compute_pct(total_bcov, total_btotal) if total_btotal > 0 else None,
        covered_lines=total_cov,
        total_statements=total_stmts,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


def parse_ruby_test_output(path: Path) -> ParsedTestTuple:
    """Parse Ruby RSpec or Minitest console output."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    rspec_m = _RSPEC_SUMMARY_RE.search(clean)
    if rspec_m:
        total = int(rspec_m.group(1))
        failed = int(rspec_m.group(2))
        skipped = int(rspec_m.group(3) or 0)
        passed = max(0, total - failed - skipped)
        failures: list[FailedTestCase] = []
        if failed > 0:
            for line in clean.splitlines():
                s = line.strip()
                if s.startswith("rspec ") and ":" in s:
                    failures.append(FailedTestCase(classname="rspec", name=s[:80], kind="failure", message=s[:240]))
        return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]

    mini_m = _MINITEST_SUMMARY_RE.search(clean)
    if mini_m:
        total = int(mini_m.group(1))
        failed = int(mini_m.group(2))
        errors = int(mini_m.group(3))
        skipped = int(mini_m.group(4))
        passed = max(0, total - failed - errors - skipped)
        return total, passed, failed, errors, skipped, []

    return _EMPTY_RESULT


def parse_swift_test_output(path: Path) -> ParsedTestTuple:
    """Parse Swift XCTest or Swift Testing output."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    total = 0
    failed = 0
    for line in clean.splitlines():
        if "Test Suite 'All tests'" in line or "Test Suite 'Selected tests'" in line:
            continue
        m = _SWIFT_XCTEST_RE.search(line)
        if m and "Executed " in line:
            total = int(m.group(1))
            failed = int(m.group(2))
    if total > 0:
        failures = [
            FailedTestCase(classname="swift.test", name=ln.strip()[:80], kind="failure", message=ln.strip()[:240])
            for ln in clean.splitlines()
            if " failed (" in ln and "Test Case" in ln
        ]
        return total, max(0, total - failed), failed, 0, 0, failures[:_MAX_FAILURE_ITEMS]

    st_m = _SWIFT_TESTING_RE.search(clean)
    if st_m:
        total = int(st_m.group(1))
        is_failed = st_m.group(2).lower() == "failed"
        failed_cnt = 1 if is_failed else 0
        return total, max(0, total - failed_cnt), failed_cnt, 0, 0, []

    return _EMPTY_RESULT


def parse_elixir_test_output(path: Path) -> ParsedTestTuple:
    """Parse Elixir ExUnit summary output."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    matches = list(_ELIXIR_SUMMARY_RE.finditer(clean))
    if not matches:
        return _EMPTY_RESULT
    m = matches[-1]
    total = int(m.group(1))
    failed = int(m.group(2))
    skipped = int(m.group(3) or 0)
    passed = max(0, total - failed - skipped)
    failures: list[FailedTestCase] = []
    if failed > 0:
        for line in clean.splitlines():
            s = line.strip()
            if re.match(r"^\d+\)\s+test\s+", s):
                failures.append(FailedTestCase(classname="exunit", name=s[:80], kind="failure", message=s[:240]))
    return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]


def parse_dart_test_output(path: Path) -> ParsedTestTuple:
    """Parse `dart test --reporter expanded` summary lines."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    matches = list(_DART_COUNT_RE.finditer(clean))
    if not matches:
        return parse_tap_output(path)
    last = matches[-1]
    passed = int(last.group(1))
    skipped = int(last.group(2) or 0)
    failed = int(last.group(3) or 0)
    total = passed + failed + skipped
    failures: list[FailedTestCase] = []
    if failed > 0:
        for line in clean.splitlines():
            if "[E]" in line:
                s = line.strip()
                failures.append(FailedTestCase(classname="dart.test", name=s[:80], kind="failure", message=s[:240]))
    return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]


def parse_tap_output(path: Path) -> ParsedTestTuple:
    """Parse Test Anything Protocol (TAP) output (Perl prove, Bash bats, C/C++/COBOL harnesses)."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    passed = 0
    failed = 0
    skipped = 0
    failures: list[FailedTestCase] = []
    for line in clean.splitlines():
        s = line.strip()
        m = _TAP_OK_RE.match(s)
        if not m:
            continue
        status = m.group(1).lower()
        desc = (m.group(2) or "").strip()
        if "# skip" in s.lower() or "# todo" in s.lower():
            skipped += 1
        elif status == "ok":
            passed += 1
        else:
            failed += 1
            failures.append(
                FailedTestCase(
                    classname="tap.test",
                    name=(desc or s)[:80],
                    kind="failure",
                    message=s[:240],
                )
            )
    total = passed + failed + skipped
    return total, passed, failed, 0, skipped, failures[:_MAX_FAILURE_ITEMS]


def parse_r_test_output(path: Path) -> ParsedTestTuple:
    """Parse R `testthat` summary output (`[ FAIL X | WARN Y | SKIP Z | PASS N ]`)."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    passed = 0
    failed = 0
    skipped = 0
    for m in _R_TESTTHAT_RE.finditer(clean):
        failed += int(m.group(1))
        skipped += int(m.group(2))
        passed += int(m.group(3))
    total = passed + failed + skipped
    if total == 0:
        return parse_tap_output(path)
    return total, passed, failed, 0, skipped, []


def parse_scala_test_output(path: Path) -> ParsedTestTuple:
    """Parse sbt / ScalaTest / MUnit console summary when JUnit XML is absent."""
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT

    sbt_m = _SCALA_SBT_RE.search(clean)
    if sbt_m:
        total = int(sbt_m.group(1))
        failed = int(sbt_m.group(2))
        errors = int(sbt_m.group(3))
        passed = int(sbt_m.group(4))
        skipped = int(sbt_m.group(5) or 0)
        return total, passed, failed, errors, skipped, []

    st_m = _SCALATEST_RE.search(clean)
    if st_m:
        passed = int(st_m.group(1))
        failed = int(st_m.group(2))
        skipped = int(st_m.group(3)) + int(st_m.group(4)) + int(st_m.group(5))
        return passed + failed + skipped, passed, failed, 0, skipped, []

    return _EMPTY_RESULT


def parse_generic_test_output(path: Path) -> ParsedTestTuple:
    """Parse generic TAP or `N passed, M failed` summary output for Tier B runtimes."""
    tap = parse_tap_output(path)
    if tap[0] > 0:
        return tap
    clean = _read_clean_text(path)
    if not clean.strip():
        return _EMPTY_RESULT
    m = _GENERIC_PASSED_FAILED_RE.search(clean)
    if m:
        passed = int(m.group(1))
        failed = int(m.group(2))
        return passed + failed, passed, failed, 0, 0, []
    return _EMPTY_RESULT


_LANG_TEST_PARSERS: Final[dict[str, tuple[str, Callable[[Path], ParsedTestTuple]]]] = {
    "rust": ("rust_test.txt", parse_rust_test_output),
    "ruby": ("ruby_test.txt", parse_ruby_test_output),
    "swift": ("swift_test.txt", parse_swift_test_output),
    "elixir": ("elixir_test.txt", parse_elixir_test_output),
    "dart": ("dart_test.txt", parse_dart_test_output),
    "vue": ("node_test.txt", parse_node_test_output),
    "svelte": ("node_test.txt", parse_node_test_output),
    "r": ("r_test.txt", parse_r_test_output),
    "scala": ("scala_test.txt", parse_scala_test_output),
}


def parse_polyglot_test_results(language: str, out_dir: Path) -> ParsedTestTuple:
    """Dispatch Stage 2 test result parsing for all extended polyglot harness languages."""
    if language in {"csharp", "fsharp"}:
        trx = parse_dotnet_trx_xml(out_dir / "results.trx")
        return trx if trx[0] > 0 else parse_dotnet_test_output(out_dir / "dotnet_test.txt")

    entry = _LANG_TEST_PARSERS.get(language)
    if entry is not None:
        filename, parser_fn = entry
        parsed = parser_fn(out_dir / filename)
        if parsed[0] > 0:
            return parsed

    if (out_dir / "tap_test.txt").is_file():
        return parse_tap_output(out_dir / "tap_test.txt")
    return parse_generic_test_output(out_dir / "generic_test.txt")


def _parse_frontend_coverage(out_dir: Path) -> CoverageResult:
    """Parse Istanbul, LCOV, or Clover coverage artifacts produced by Vue/Svelte Node runs."""
    cov = parse_istanbul_coverage_summary(out_dir / "coverage-summary.json")
    if not cov.measured and (out_dir / "lcov.info").is_file():
        cov = parse_lcov_info(out_dir / "lcov.info")
    if not cov.measured and (out_dir / "clover.xml").is_file():
        cov = parse_clover_xml(out_dir / "clover.xml")
    return cov


def parse_polyglot_coverage(
    language: str,
    source_targets: list[str],
    out_dir: Path,
) -> CoverageResult:
    """Dispatch Stage 2 coverage report parsing for all extended polyglot harness languages."""
    if language in {"kotlin", "scala", "groovy"}:
        src_prefix = source_targets[0] if source_targets else f"src/main/{language}"
        return parse_jacoco_xml(out_dir / "jacoco.xml", source_root_prefix=src_prefix)
    if language in {"vue", "svelte"}:
        return _parse_frontend_coverage(out_dir)

    result = CoverageResult()
    if (out_dir / "cobertura.xml").is_file():
        result = parse_cobertura_xml(out_dir / "cobertura.xml")
    elif (out_dir / "lcov.info").is_file():
        result = parse_lcov_info(out_dir / "lcov.info")
    elif (out_dir / "clover.xml").is_file():
        result = parse_clover_xml(out_dir / "clover.xml")
    return result
