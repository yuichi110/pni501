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
        return [root]
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
            else:
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
