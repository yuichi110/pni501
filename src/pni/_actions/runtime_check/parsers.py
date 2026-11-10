# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic parsers for JUnit XML, pytest-cov JSON, and JaCoCo XML reports."""

from __future__ import annotations

import contextlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Final, Optional

from pni._actions.runtime_check.models import (
    CoverageResult,
    FailedTestCase,
    ModuleCoverageItem,
)

_MAX_FAILURE_ITEMS: Final[int] = 25
_MAX_LOWEST_MODULES: Final[int] = 15
_MAX_MISSING_LINES: Final[int] = 10
_BENIGN_DOCTYPE_RE: Final[re.Pattern[str]] = re.compile(r"<!DOCTYPE\s+[^>\[\]]+>", re.IGNORECASE)


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


def _extract_case_failure(case_elem: ET.Element) -> Optional[FailedTestCase]:
    """Extract FailedTestCase if a <testcase> contains <failure> or <error>."""
    classname = case_elem.attrib.get("classname", "")
    name = case_elem.attrib.get("name", "unknown")
    for kind in ("failure", "error"):
        child = case_elem.find(kind)
        if child is not None:
            msg = (child.attrib.get("message") or (child.text or "")).strip()
            first_line = msg.splitlines()[0][:240] if msg else f"Test {kind}"
            lit_kind = "error" if kind == "error" else "failure"
            return FailedTestCase(classname=classname, name=name, kind=lit_kind, message=first_line)
    return None


def _collect_suites(root: ET.Element) -> list[ET.Element]:
    """Return all <testsuite> elements whether root is <testsuite> or <testsuites>."""
    if root.tag == "testsuite":
        return [root, *root.findall(".//testsuite")]
    return list(root.findall(".//testsuite"))


def parse_junit_xml_files(
    xml_paths: list[Path],
) -> tuple[int, int, int, int, int, list[FailedTestCase]]:
    """Aggregate test counts and failures across one or more JUnit / Surefire XML files.

    Returns:
        tuple[int, int, int, int, int, list[FailedTestCase]]:
            (total, passed, failed, errors, skipped, failures)
    """
    total = 0
    failed = 0
    errors = 0
    skipped = 0
    failures: list[FailedTestCase] = []

    for path in sorted(xml_paths):
        root = _safe_parse_xml(path)
        if root is None:
            continue
        for suite in _collect_suites(root):
            cases = suite.findall("testcase")
            if cases:
                for case in cases:
                    total += 1
                    if case.find("skipped") is not None:
                        skipped += 1
                        continue
                    fail_item = _extract_case_failure(case)
                    if fail_item is not None:
                        if fail_item.kind == "error":
                            errors += 1
                        else:
                            failed += 1
                        failures.append(fail_item)
            elif suite.find("testsuite") is None:
                total += int(suite.attrib.get("tests", "0") or 0)
                failed += int(suite.attrib.get("failures", "0") or 0)
                errors += int(suite.attrib.get("errors", "0") or 0)
                skipped += int(suite.attrib.get("skipped", "0") or 0)

    passed = max(0, total - failed - errors - skipped)
    sorted_failures = sorted(failures, key=lambda f: (0 if f.kind == "error" else 1, f.classname, f.name))
    return total, passed, failed, errors, skipped, sorted_failures[:_MAX_FAILURE_ITEMS]


def _as_int(val: object) -> int:
    """Safely coerce JSON scalar values into an integer."""
    if isinstance(val, bool):
        return 0
    if isinstance(val, int):
        return val
    if isinstance(val, (float, str)):
        with contextlib.suppress(ValueError):
            return int(val)
    return 0


def _compute_branch_pct(summary_dict: dict[str, object]) -> Optional[float]:
    """Compute branch coverage percentage from coverage.py summary dict when branches exist."""
    num_branches = _as_int(summary_dict.get("num_branches"))
    if num_branches <= 0:
        return None
    cov_branches = _as_int(summary_dict.get("covered_branches"))
    return round((cov_branches / num_branches) * 100.0, 1)


def _compute_line_pct(covered: int, total: int) -> float:
    """Compute line coverage percentage (100.0 for empty statement files)."""
    if total <= 0:
        return 100.0
    return round((covered / total) * 100.0, 1)


def parse_pytest_coverage_json(cov_json_path: Path) -> CoverageResult:
    """Parse coverage.py / pytest-cov JSON report into a canonical CoverageResult."""
    if not cov_json_path.is_file():
        return CoverageResult()

    try:
        raw = json.loads(cov_json_path.read_text(encoding="utf-8"))
    except Exception:
        return CoverageResult()
    if not isinstance(raw, dict):
        return CoverageResult()

    totals = raw.get("totals")
    if not isinstance(totals, dict):
        return CoverageResult()

    covered_lines = _as_int(totals.get("covered_lines"))
    total_stmts = _as_int(totals.get("num_statements"))
    line_pct = _compute_line_pct(covered_lines, total_stmts)
    branch_pct = _compute_branch_pct(totals)

    items: list[ModuleCoverageItem] = []
    files_map = raw.get("files")
    if isinstance(files_map, dict):
        for rel_file, fdata in files_map.items():
            if not isinstance(fdata, dict):
                continue
            summary = fdata.get("summary")
            if not isinstance(summary, dict):
                continue
            fcov = _as_int(summary.get("covered_lines"))
            fstmts = _as_int(summary.get("num_statements"))
            missing_raw = fdata.get("missing_lines")
            missing = [_as_int(x) for x in missing_raw[:_MAX_MISSING_LINES]] if isinstance(missing_raw, list) else []
            items.append(
                ModuleCoverageItem(
                    file_path=str(rel_file).replace("\\", "/"),
                    line_coverage_pct=_compute_line_pct(fcov, fstmts),
                    branch_coverage_pct=_compute_branch_pct(summary),
                    covered_lines=fcov,
                    total_statements=fstmts,
                    missing_lines_preview=missing,
                )
            )

    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="pytest-cov",
        line_coverage_pct=line_pct,
        branch_coverage_pct=branch_pct,
        covered_lines=covered_lines,
        total_statements=total_stmts,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


def _jacoco_counter(elem: ET.Element, counter_type: str) -> tuple[int, int]:
    """Return (covered, total) from a direct child <counter type='...'> of elem."""
    for child in elem.findall("counter"):
        if child.attrib.get("type") == counter_type:
            missed = int(child.attrib.get("missed", "0") or 0)
            covered = int(child.attrib.get("covered", "0") or 0)
            return covered, covered + missed
    return 0, 0


def _jacoco_missing_lines(sf_elem: ET.Element) -> list[int]:
    """Collect up to _MAX_MISSING_LINES missed source line numbers from JaCoCo <sourcefile>."""
    missed_lines: list[int] = []
    for line_el in sf_elem.findall("line"):
        mi = int(line_el.attrib.get("mi", "0") or 0)
        ci = int(line_el.attrib.get("ci", "0") or 0)
        if mi > 0 and ci == 0:
            nr = int(line_el.attrib.get("nr", "0") or 0)
            if nr > 0:
                missed_lines.append(nr)
            if len(missed_lines) >= _MAX_MISSING_LINES:
                break
    return missed_lines


def parse_jacoco_xml(
    jacoco_xml_path: Path,
    source_root_prefix: str = "src/main/java",
) -> CoverageResult:
    """Parse JaCoCo XML report into a canonical CoverageResult."""
    root = _safe_parse_xml(jacoco_xml_path)
    if root is None:
        return CoverageResult()

    cov_lines, total_lines = _jacoco_counter(root, "LINE")
    cov_branches, total_branches = _jacoco_counter(root, "BRANCH")
    if total_lines == 0 and not root.findall(".//sourcefile"):
        return CoverageResult()

    prefix = source_root_prefix.strip("/")
    items: list[ModuleCoverageItem] = []
    for pkg_el in root.findall(".//package"):
        pkg_name = pkg_el.attrib.get("name", "").strip("/")
        for sf_el in pkg_el.findall("sourcefile"):
            sf_name = sf_el.attrib.get("name", "")
            if not sf_name:
                continue
            fcov, ftotal = _jacoco_counter(sf_el, "LINE")
            bcov, btotal = _jacoco_counter(sf_el, "BRANCH")
            rel_parts = [seg for seg in (prefix, pkg_name, sf_name) if seg]
            items.append(
                ModuleCoverageItem(
                    file_path="/".join(rel_parts),
                    line_coverage_pct=_compute_line_pct(fcov, ftotal),
                    branch_coverage_pct=_compute_line_pct(bcov, btotal) if btotal > 0 else None,
                    covered_lines=fcov,
                    total_statements=ftotal,
                    missing_lines_preview=_jacoco_missing_lines(sf_el),
                )
            )

    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="jacoco",
        line_coverage_pct=_compute_line_pct(cov_lines, total_lines),
        branch_coverage_pct=_compute_line_pct(cov_branches, total_branches) if total_branches > 0 else None,
        covered_lines=cov_lines,
        total_statements=total_lines,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


def _clover_missing_lines(file_elem: ET.Element) -> list[int]:
    """Collect up to _MAX_MISSING_LINES uncovered statement line numbers from Clover <file>."""
    missed: list[int] = []
    for line_el in file_elem.findall("line"):
        if line_el.attrib.get("type") != "stmt":
            continue
        cnt = int(line_el.attrib.get("count", "0") or 0)
        if cnt == 0:
            num = int(line_el.attrib.get("num", "0") or 0)
            if num > 0:
                missed.append(num)
            if len(missed) >= _MAX_MISSING_LINES:
                break
    return missed


def parse_clover_xml(
    clover_xml_path: Path,
    workspace_prefix: str = "/workspace/",
) -> CoverageResult:
    """Parse PHPUnit / PCOV Clover XML report into a canonical CoverageResult."""
    root = _safe_parse_xml(clover_xml_path)
    if root is None:
        return CoverageResult()

    proj_el = root.find("project") if root.tag != "project" else root
    if proj_el is None:
        return CoverageResult()

    proj_metrics = proj_el.find("metrics")
    file_elems = list(proj_el.findall(".//file"))
    if proj_metrics is None and not file_elems:
        return CoverageResult()

    items: list[ModuleCoverageItem] = []
    sum_cov = 0
    sum_stmts = 0
    sum_bcov = 0
    sum_btotal = 0

    for f_el in file_elems:
        raw_name = f_el.attrib.get("name", "").replace("\\", "/")
        if not raw_name or "/vendor/" in raw_name:
            continue
        rel_name = raw_name.removeprefix(workspace_prefix).lstrip("/")
        f_metrics = f_el.find("metrics")
        if f_metrics is None:
            continue
        fcov = int(f_metrics.attrib.get("coveredstatements", "0") or 0)
        fstmts = int(f_metrics.attrib.get("statements", "0") or 0)
        bcov = int(f_metrics.attrib.get("coveredconditionals", "0") or 0)
        btotal = int(f_metrics.attrib.get("conditionals", "0") or 0)
        sum_cov += fcov
        sum_stmts += fstmts
        sum_bcov += bcov
        sum_btotal += btotal
        items.append(
            ModuleCoverageItem(
                file_path=rel_name,
                line_coverage_pct=_compute_line_pct(fcov, fstmts),
                branch_coverage_pct=_compute_line_pct(bcov, btotal) if btotal > 0 else None,
                covered_lines=fcov,
                total_statements=fstmts,
                missing_lines_preview=_clover_missing_lines(f_el),
            )
        )

    if proj_metrics is not None and not items:
        sum_cov = int(proj_metrics.attrib.get("coveredstatements", "0") or 0)
        sum_stmts = int(proj_metrics.attrib.get("statements", "0") or 0)
        sum_bcov = int(proj_metrics.attrib.get("coveredconditionals", "0") or 0)
        sum_btotal = int(proj_metrics.attrib.get("conditionals", "0") or 0)

    if sum_stmts == 0 and not items:
        return CoverageResult()

    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="phpunit-pcov",
        line_coverage_pct=_compute_line_pct(sum_cov, sum_stmts),
        branch_coverage_pct=_compute_line_pct(sum_bcov, sum_btotal) if sum_btotal > 0 else None,
        covered_lines=sum_cov,
        total_statements=sum_stmts,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


_GO_TEST_OUTCOME_RE: Final[re.Pattern[str]] = re.compile(r"^\s*---\s+(PASS|FAIL|SKIP):\s+([^\s(]+)")
_GO_PKG_FAIL_RE: Final[re.Pattern[str]] = re.compile(r"^FAIL\s+(\S+)\s+.*\[(build|setup)\s+failed\]")
_GO_COVER_LINE_RE: Final[re.Pattern[str]] = re.compile(r"^(.+):(\d+)\.\d+,(\d+)\.\d+\s+(\d+)\s+(\d+)\s*$")
_ANSI_ESCAPE_RE: Final[re.Pattern[str]] = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def parse_go_test_output(
    go_test_path: Path,
) -> tuple[int, int, int, int, int, list[FailedTestCase]]:
    """Parse `go test -v` output into (total, passed, failed, errors, skipped, failures)."""
    if not go_test_path.is_file():
        return 0, 0, 0, 0, 0, []

    with contextlib.suppress(Exception):
        lines = go_test_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return 0, 0, 0, 0, 0, []

    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    failures: list[FailedTestCase] = []

    for line in lines:
        m = _GO_TEST_OUTCOME_RE.match(line)
        if m:
            status_tok, test_name = m.group(1), m.group(2)
            if status_tok == "PASS":
                passed += 1
            elif status_tok == "SKIP":
                skipped += 1
            elif status_tok == "FAIL":
                failed += 1
                failures.append(
                    FailedTestCase(
                        classname="go.test",
                        name=test_name,
                        kind="failure",
                        message=line.strip()[:240],
                    )
                )
            continue

        pkg_fail = _GO_PKG_FAIL_RE.match(line)
        if pkg_fail:
            errors += 1
            failures.append(
                FailedTestCase(
                    classname=pkg_fail.group(1),
                    name="build",
                    kind="error",
                    message=line.strip()[:240],
                )
            )

    total = passed + failed + errors + skipped
    return total, passed, failed, errors, skipped, failures[:_MAX_FAILURE_ITEMS]


def _normalize_go_cover_path(raw_path: str, module_prefix: str) -> str:
    """Strip Go module prefix from coverprofile file path when present."""
    clean = raw_path.strip().replace("\\", "/")
    if module_prefix:
        pref = module_prefix.strip().rstrip("/") + "/"
        if clean.startswith(pref):
            return clean[len(pref) :]
    return clean


def _parse_go_cover_blocks(
    lines: list[str],
    module_prefix: str,
) -> dict[tuple[str, int, int], tuple[int, int]]:
    """Deduplicate Go coverprofile blocks by (file_path, start_line, end_line) keeping max count."""
    blocks: dict[tuple[str, int, int], tuple[int, int]] = {}
    for line in lines:
        if line.startswith("mode:") or not line.strip():
            continue
        m = _GO_COVER_LINE_RE.match(line)
        if not m:
            continue
        rel_file = _normalize_go_cover_path(m.group(1), module_prefix)
        key = (rel_file, int(m.group(2)), int(m.group(3)))
        num_stmt, cnt = int(m.group(4)), int(m.group(5))
        prev = blocks.get(key)
        if prev is None or cnt > prev[1]:
            blocks[key] = (num_stmt, cnt)
    return blocks


def parse_go_coverprofile(
    coverprofile_path: Path,
    module_prefix: str = "",
) -> CoverageResult:
    """Parse Go `-coverprofile=/out/coverage.out` report into a canonical CoverageResult."""
    if not coverprofile_path.is_file():
        return CoverageResult()

    lines: list[str] = []
    with contextlib.suppress(Exception):
        lines = coverprofile_path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks = _parse_go_cover_blocks(lines, module_prefix)
    if not blocks:
        return CoverageResult()

    file_stats: dict[str, list[int]] = {}
    file_missing: dict[str, list[int]] = {}
    for (rel_file, start_ln, _end_ln), (num_stmt, cnt) in sorted(blocks.items()):
        stats = file_stats.setdefault(rel_file, [0, 0])
        stats[1] += num_stmt
        if cnt > 0:
            stats[0] += num_stmt
        else:
            missed = file_missing.setdefault(rel_file, [])
            if start_ln not in missed and len(missed) < _MAX_MISSING_LINES:
                missed.append(start_ln)

    total_cov = 0
    total_stmts = 0
    items: list[ModuleCoverageItem] = []
    for rel_file, (fcov, fstmts) in file_stats.items():
        total_cov += fcov
        total_stmts += fstmts
        items.append(
            ModuleCoverageItem(
                file_path=rel_file,
                line_coverage_pct=_compute_line_pct(fcov, fstmts),
                branch_coverage_pct=None,
                covered_lines=fcov,
                total_statements=fstmts,
                missing_lines_preview=file_missing.get(rel_file, []),
            )
        )

    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="go-cover",
        line_coverage_pct=_compute_line_pct(total_cov, total_stmts),
        branch_coverage_pct=None,
        covered_lines=total_cov,
        total_statements=total_stmts,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


def _parse_jest_vitest_counts(clean_text: str) -> Optional[tuple[int, int, int, int]]:
    """Extract (total, passed, failed, skipped) from Jest or Vitest `Tests:` summary line."""
    for line in reversed(clean_text.splitlines()):
        stripped = line.strip()
        if not stripped.startswith("Tests:"):
            continue
        passed_m = re.search(r"(\d+)\s+passed", stripped)
        failed_m = re.search(r"(\d+)\s+failed", stripped)
        skipped_m = re.search(r"(\d+)\s+(?:skipped|todo|pending)", stripped)
        total_m = re.search(r"(\d+)\s+total", stripped)
        passed = int(passed_m.group(1)) if passed_m else 0
        failed = int(failed_m.group(1)) if failed_m else 0
        skipped = int(skipped_m.group(1)) if skipped_m else 0
        total = int(total_m.group(1)) if total_m else (passed + failed + skipped)
        if total > 0:
            return total, passed, failed, skipped
    return None


def _parse_node_tap_counts(clean_text: str) -> Optional[tuple[int, int, int, int]]:
    """Extract (total, passed, failed, skipped) from `node --test` summary output."""
    tests_m = re.search(r"(?m)^(?:ℹ|#)\s+tests\s+(\d+)\b", clean_text)
    pass_m = re.search(r"(?m)^(?:ℹ|#)\s+pass\s+(\d+)\b", clean_text)
    fail_m = re.search(r"(?m)^(?:ℹ|#)\s+fail\s+(\d+)\b", clean_text)
    skip_m = re.search(r"(?m)^(?:ℹ|#)\s+skipped\s+(\d+)\b", clean_text)
    if tests_m or pass_m or fail_m:
        passed = int(pass_m.group(1)) if pass_m else 0
        failed = int(fail_m.group(1)) if fail_m else 0
        skipped = int(skip_m.group(1)) if skip_m else 0
        total = int(tests_m.group(1)) if tests_m else (passed + failed + skipped)
        return total, passed, failed, skipped
    return None


def _parse_wtr_or_mocha_counts(clean_text: str) -> Optional[tuple[int, int, int, int]]:
    """Extract (total, passed, failed, skipped) from `@web/test-runner` or Mocha summary output."""
    for line in reversed(clean_text.splitlines()):
        stripped = line.strip()
        if "|" in stripped or "failed" in stripped:
            pass_m = re.search(r"(\d+)\s+passed\b", stripped)
            if pass_m and not stripped.lower().startswith("tests:"):
                passed = int(pass_m.group(1))
                fail_m = re.search(r"(\d+)\s+failed\b", stripped)
                skip_m = re.search(r"(\d+)\s+(?:skipped|pending)\b", stripped)
                failed = int(fail_m.group(1)) if fail_m else 0
                skipped = int(skip_m.group(1)) if skip_m else 0
                total = passed + failed + skipped
                if total > 0:
                    return total, passed, failed, skipped
    mocha_pass = re.search(r"(?m)^\s*(\d+)\s+passing\b", clean_text)
    if mocha_pass:
        passed = int(mocha_pass.group(1))
        mocha_fail = re.search(r"(?m)^\s*(\d+)\s+failing\b", clean_text)
        mocha_pend = re.search(r"(?m)^\s*(\d+)\s+pending\b", clean_text)
        failed = int(mocha_fail.group(1)) if mocha_fail else 0
        skipped = int(mocha_pend.group(1)) if mocha_pend else 0
        return passed + failed + skipped, passed, failed, skipped
    return None


def parse_node_test_output(
    node_test_path: Path,
) -> tuple[int, int, int, int, int, list[FailedTestCase]]:
    """Parse Vitest / Jest / `@web/test-runner` / Mocha / `node --test` text output when JUnit XML is absent."""
    if not node_test_path.is_file():
        return 0, 0, 0, 0, 0, []

    with contextlib.suppress(Exception):
        raw = node_test_path.read_text(encoding="utf-8", errors="replace")
    if not raw.strip():
        return 0, 0, 0, 0, 0, []

    clean = _ANSI_ESCAPE_RE.sub("", raw)
    counts = (
        _parse_jest_vitest_counts(clean)
        or _parse_node_tap_counts(clean)
        or _parse_wtr_or_mocha_counts(clean)
    )
    if counts is None:
        return 0, 0, 0, 0, 0, []

    total, passed, failed, skipped = counts
    failures: list[FailedTestCase] = []
    suite_fails: list[FailedTestCase] = []
    if failed > 0:
        for line in clean.splitlines():
            s = line.strip()
            if s.startswith(("✕ ", "× ", "✖ ", "❌ ")):
                failures.append(
                    FailedTestCase(
                        classname="node.test",
                        name=s[:80],
                        kind="failure",
                        message=s[:240],
                    )
                )
            elif s.startswith("FAIL "):
                suite_fails.append(
                    FailedTestCase(
                        classname="node.test",
                        name=s[:80],
                        kind="failure",
                        message=s[:240],
                    )
                )
    eff_failures = failures or suite_fails
    return total, passed, failed, 0, skipped, eff_failures[:_MAX_FAILURE_ITEMS]


def parse_istanbul_coverage_summary(
    summary_json_path: Path,
    workspace_prefix: str = "/workspace/",
) -> CoverageResult:
    """Parse Istanbul / V8 `coverage-summary.json` into a canonical CoverageResult."""
    if not summary_json_path.is_file():
        return CoverageResult()

    try:
        raw = json.loads(summary_json_path.read_text(encoding="utf-8"))
    except Exception:
        return CoverageResult()
    if not isinstance(raw, dict):
        return CoverageResult()

    total_entry = raw.get("total")
    if not isinstance(total_entry, dict):
        return CoverageResult()

    lines_dict = total_entry.get("lines") if isinstance(total_entry.get("lines"), dict) else {}
    branches_dict = total_entry.get("branches") if isinstance(total_entry.get("branches"), dict) else {}
    cov_lines = _as_int(lines_dict.get("covered"))
    total_stmts = _as_int(lines_dict.get("total"))
    cov_branches = _as_int(branches_dict.get("covered"))
    total_branches = _as_int(branches_dict.get("total"))

    items: list[ModuleCoverageItem] = []
    sum_fcov = 0
    sum_ftotal = 0
    sum_fbcov = 0
    sum_fbtotal = 0
    for key, fdata in raw.items():
        if key == "total" or not isinstance(fdata, dict):
            continue
        flines = fdata.get("lines") if isinstance(fdata.get("lines"), dict) else {}
        fbranches = fdata.get("branches") if isinstance(fdata.get("branches"), dict) else {}
        fcov = _as_int(flines.get("covered"))
        ftotal = _as_int(flines.get("total"))
        fbcov = _as_int(fbranches.get("covered"))
        fbtotal = _as_int(fbranches.get("total"))
        sum_fcov += fcov
        sum_ftotal += ftotal
        sum_fbcov += fbcov
        sum_fbtotal += fbtotal
        rel_path = str(key).replace("\\", "/").removeprefix(workspace_prefix).lstrip("/")
        items.append(
            ModuleCoverageItem(
                file_path=rel_path,
                line_coverage_pct=_compute_line_pct(fcov, ftotal),
                branch_coverage_pct=_compute_line_pct(fbcov, fbtotal) if fbtotal > 0 else None,
                covered_lines=fcov,
                total_statements=ftotal,
                missing_lines_preview=[],
            )
        )

    if items and sum_ftotal > 0:
        cov_lines, total_stmts = sum_fcov, sum_ftotal
        cov_branches, total_branches = sum_fbcov, sum_fbtotal

    if total_stmts == 0 and not items:
        return CoverageResult()

    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="istanbul-summary",
        line_coverage_pct=_compute_line_pct(cov_lines, total_stmts),
        branch_coverage_pct=_compute_line_pct(cov_branches, total_branches) if total_branches > 0 else None,
        covered_lines=cov_lines,
        total_statements=total_stmts,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


def _finalize_lcov_record(
    sf_path: str,
    da_hits: dict[int, int],
    lf_val: int,
    lh_val: int,
    brda_hits: list[int],
    brf_val: int,
    brh_val: int,
    workspace_prefix: str,
) -> tuple[ModuleCoverageItem, int, int]:
    """Build a ModuleCoverageItem and (covered_branches, total_branches) from one LCOV `SF:` block."""
    rel_path = sf_path.replace("\\", "/").removeprefix(workspace_prefix).lstrip("/")
    ftotal = lf_val if lf_val > 0 else len(da_hits)
    fcov = lh_val if lf_val > 0 else sum(1 for h in da_hits.values() if h > 0)
    fbtotal = brf_val if brf_val > 0 else len(brda_hits)
    fbcov = brh_val if brf_val > 0 else sum(1 for h in brda_hits if h > 0)
    missing = sorted(ln for ln, h in da_hits.items() if h == 0)[:_MAX_MISSING_LINES]
    item = ModuleCoverageItem(
        file_path=rel_path,
        line_coverage_pct=_compute_line_pct(fcov, ftotal),
        branch_coverage_pct=_compute_line_pct(fbcov, fbtotal) if fbtotal > 0 else None,
        covered_lines=fcov,
        total_statements=ftotal,
        missing_lines_preview=missing,
    )
    return item, fbcov, fbtotal


def _apply_lcov_line(
    line: str,
    da_hits: dict[int, int],
    brda_hits: list[int],
    counters: list[int],
) -> None:
    """Apply a single DA/LF/LH/BRDA/BRF/BRH line into active LCOV record accumulators."""
    if line.startswith("DA:"):
        parts = line[3:].split(",")
        if len(parts) >= 2:
            with contextlib.suppress(ValueError):
                da_hits[int(parts[0])] = int(parts[1])
    elif line.startswith("LF:"):
        counters[0] = _as_int(line[3:])
    elif line.startswith("LH:"):
        counters[1] = _as_int(line[3:])
    elif line.startswith("BRDA:"):
        parts = line[5:].split(",")
        if len(parts) >= 4:
            taken = parts[3].strip()
            brda_hits.append(0 if taken in {"-", "0"} else _as_int(taken))
    elif line.startswith("BRF:"):
        counters[2] = _as_int(line[4:])
    elif line.startswith("BRH:"):
        counters[3] = _as_int(line[4:])


def parse_lcov_info(
    lcov_path: Path,
    workspace_prefix: str = "/workspace/",
) -> CoverageResult:
    """Parse LCOV `lcov.info` report into a canonical CoverageResult with unified module and total counts."""
    if not lcov_path.is_file():
        return CoverageResult()

    lines: list[str] = []
    with contextlib.suppress(Exception):
        lines = lcov_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return CoverageResult()

    items: list[ModuleCoverageItem] = []
    total_bcov = 0
    total_btotal = 0
    sf_path = ""
    da_hits: dict[int, int] = {}
    brda_hits: list[int] = []
    counters = [0, 0, 0, 0]  # [lf, lh, brf, brh]

    for raw in lines:
        line = raw.strip()
        if line.startswith("SF:"):
            sf_path = line[3:].strip()
            da_hits = {}
            brda_hits = []
            counters = [0, 0, 0, 0]
        elif line == "end_of_record" and sf_path:
            item, bcov, btotal = _finalize_lcov_record(
                sf_path,
                da_hits,
                counters[0],
                counters[1],
                brda_hits,
                counters[2],
                counters[3],
                workspace_prefix,
            )
            items.append(item)
            total_bcov += bcov
            total_btotal += btotal
            sf_path = ""
        elif sf_path:
            _apply_lcov_line(line, da_hits, brda_hits, counters)

    if not items:
        return CoverageResult()

    total_cov = sum(m.covered_lines for m in items)
    total_stmts = sum(m.total_statements for m in items)
    items.sort(key=lambda m: (m.line_coverage_pct, -m.total_statements, m.file_path))
    return CoverageResult(
        measured=True,
        tool="lcov",
        line_coverage_pct=_compute_line_pct(total_cov, total_stmts),
        branch_coverage_pct=_compute_line_pct(total_bcov, total_btotal) if total_btotal > 0 else None,
        covered_lines=total_cov,
        total_statements=total_stmts,
        lowest_covered_modules=items[:_MAX_LOWEST_MODULES],
    )


_NOISE_ERROR_PATTERNS: Final[tuple[str, ...]] = (
    "[help 1]",
    "to see the full stack trace",
    "re-run maven using",
    "for more information about the errors",
    "http://cwiki.apache.org/confluence",
)
_CORE_DIAGNOSTIC_MARKERS: Final[tuple[str, ...]] = (
    "bad class file",
    "wrong version",
    "cannot find symbol",
    "package ",
    "does not exist",
    "compilation failure",
    "syntaxerror",
    "fatal error",
    "parse error",
    "modulenotfounderror",
    "importerror",
    "traceback",
    "cannot use ",
    "undefined:",
    "error ts",
    "referenceerror",
    "typeerror",
    "err_module_not_found",
    "[error]",
    "error:",
)


def extract_verbatim_error_excerpt(lines: list[str], *, max_lines: int = 5) -> list[str]:
    """Extract up to max_lines high-signal verbatim compiler or container failure lines from log tails."""
    if not lines or max_lines <= 0:
        return []

    prioritized: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        low = stripped.lower()
        if any(noise in low for noise in _NOISE_ERROR_PATTERNS):
            continue
        if re.fullmatch(r"(?:\d+(?:\.\d+)?\s+)?\[error\]", low):
            continue
        if low.startswith("#") and "error: process \"/bin/sh -c" in low:
            continue
        if any(marker in low for marker in _CORE_DIAGNOSTIC_MARKERS):
            if stripped not in prioritized:
                prioritized.append(stripped)

    if prioritized:
        return prioritized[:max_lines]

    non_empty = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("---")]
    return non_empty[-max_lines:]
