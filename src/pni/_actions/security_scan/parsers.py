# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic parsers and normalizers for Trivy JSON vulnerability, misconfig, and secret reports."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Optional

from pni._actions.security_scan.models import (
    MisconfigItem,
    SecretFindingItem,
    VulnerabilityItem,
    VulnerabilitySummaryCounts,
    VulnSeverity,
)
from pni._config import OptOutEntry, match_opt_out, matches_opt_out_scope

MAX_STORED_VULNERABILITIES: Final[int] = 40
MAX_STORED_MISCONFIGS: Final[int] = 25
MAX_STORED_SECRETS: Final[int] = 25

_SEVERITY_ORDER: Final[dict[str, int]] = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "UNKNOWN": 4,
}

_OS_PKG_TYPES: Final[frozenset[str]] = frozenset(
    {
        "alpine",
        "alma",
        "amazon",
        "azurelinux",
        "cbl-mariner",
        "centos",
        "chainguard",
        "debian",
        "fedora",
        "opensuse",
        "opensuse-leap",
        "opensuse-tumbleweed",
        "oracle",
        "photon",
        "redhat",
        "rocky",
        "sles",
        "suse",
        "ubuntu",
        "wolfi",
    }
)


@dataclass(frozen=True)
class ParsedTrivyBundle:
    """Aggregated normalized records and counts across Trivy filesystem and image JSON outputs."""

    vuln_counts: VulnerabilitySummaryCounts
    app_vuln_counts: VulnerabilitySummaryCounts
    os_vuln_counts: VulnerabilitySummaryCounts
    vulnerabilities: list[VulnerabilityItem]
    misconfigurations: list[MisconfigItem]
    secrets: list[SecretFindingItem]
    opt_out_counts: dict[str, int] = field(default_factory=dict)


def normalize_severity(raw: object) -> VulnSeverity:
    """Normalize arbitrary severity string into canonical VulnSeverity literal."""
    up = str(raw or "UNKNOWN").strip().upper()
    if up == "CRITICAL":
        return "CRITICAL"
    if up == "HIGH":
        return "HIGH"
    if up == "MEDIUM":
        return "MEDIUM"
    if up == "LOW":
        return "LOW"
    return "UNKNOWN"


def is_os_package_type(pkg_type: str, result_class: str = "") -> bool:
    """Return True if a Trivy result belongs to an OS base-image package manager."""
    if result_class.strip().lower() == "os-pkgs":
        return True
    return pkg_type.strip().lower() in _OS_PKG_TYPES


def _extract_cvss_score(raw_cvss: object) -> Optional[float]:
    """Extract the highest CVSS v3/v2 score from a Trivy CVSS vendor map."""
    if not isinstance(raw_cvss, dict):
        return None
    scores: list[float] = []
    for entry in raw_cvss.values():
        if not isinstance(entry, dict):
            continue
        for key in ("V3Score", "V2Score"):
            val = entry.get(key)
            if isinstance(val, (int, float)):
                scores.append(float(val))
    return round(max(scores), 1) if scores else None


def redact_secret_match(raw_match: object) -> str:
    """Ensure any matched secret snippet is safely masked and bounded in length."""
    text = str(raw_match or "").strip()
    if not text:
        return "***REDACTED***"
    if "***" in text:
        return text[:100]
    if "=" in text:
        lhs = text.split("=", maxsplit=1)[0].strip()
        return f"{lhs}=***REDACTED***"[:100]
    if ":" in text:
        lhs = text.split(":", maxsplit=1)[0].strip()
        return f"{lhs}: ***REDACTED***"[:100]
    return "***REDACTED***"


def _summarize_counts(items: list[VulnerabilityItem]) -> VulnerabilitySummaryCounts:
    """Compute severity breakdown across a list of deduplicated vulnerabilities."""
    crit = sum(1 for v in items if v.severity == "CRITICAL")
    high = sum(1 for v in items if v.severity == "HIGH")
    med = sum(1 for v in items if v.severity == "MEDIUM")
    low = sum(1 for v in items if v.severity == "LOW")
    return VulnerabilitySummaryCounts(
        critical=crit,
        high=high,
        medium=med,
        low=low,
        total=len(items),
    )


UNPINNED_RESOLUTION_NOTE: Final[str] = (
    "Unpinned symbolic version in manifest; static SCA evaluates full historical CVE range until locked"
)
_SYMBOLIC_EXACT_VERSIONS: Final[frozenset[str]] = frozenset(
    {"latest", "release", "main", "master", "head", "trunk", "*", "x"}
)
_RANGE_OPERATOR_PREFIXES: Final[tuple[str, ...]] = ("^", "~", ">=", "<=", ">", "<", "!=", "[", "(")


def is_symbolic_or_unpinned_version(version: str) -> bool:
    """Return True if an installed_version string is a symbolic tag, wildcard, snapshot, or open range."""
    clean = version.strip()
    if not clean:
        return True
    low = clean.lower()
    if low in _SYMBOLIC_EXACT_VERSIONS:
        return True
    if low.startswith("dev-") or low.endswith(("-dev", "-snapshot")):
        return True
    if "*" in low or low.endswith(".x"):
        return True
    return clean.startswith(_RANGE_OPERATOR_PREFIXES)


def _as_list(val: object) -> list[object]:
    """Return val as a list if it is a list, otherwise an empty list."""
    return val if isinstance(val, list) else []


def _parse_result_vulns(
    res: dict[str, object],
    vuln_map: dict[tuple[str, str, str], tuple[VulnerabilityItem, bool]],
) -> None:
    """Extract and deduplicate VulnerabilityItem records from one Trivy Result entry."""
    target = str(res.get("Target") or "")
    pkg_type = str(res.get("Type") or res.get("Class") or "unknown")
    res_class = str(res.get("Class") or "")
    is_os = is_os_package_type(pkg_type, res_class)

    for raw_v in _as_list(res.get("Vulnerabilities")):
        if not isinstance(raw_v, dict):
            continue
        vuln_id = str(raw_v.get("VulnerabilityID") or "").strip()
        pkg_name = str(raw_v.get("PkgName") or "").strip()
        installed = str(raw_v.get("InstalledVersion") or "").strip()
        if not vuln_id or not pkg_name:
            continue
        unpinned = is_symbolic_or_unpinned_version(installed)
        item = VulnerabilityItem(
            vuln_id=vuln_id,
            pkg_name=pkg_name,
            pkg_type=pkg_type,
            installed_version=installed,
            fixed_version=str(raw_v.get("FixedVersion") or "").strip(),
            severity=normalize_severity(raw_v.get("Severity")),
            title=str(raw_v.get("Title") or raw_v.get("Description") or "").strip()[:180],
            target=target,
            cvss_score=_extract_cvss_score(raw_v.get("CVSS")),
            is_unpinned_specifier=unpinned,
            version_resolution_note=UNPINNED_RESOLUTION_NOTE if unpinned else "",
        )
        key = (vuln_id, pkg_name, installed)
        existing = vuln_map.get(key)
        if existing is None or (not existing[0].fixed_version and item.fixed_version):
            vuln_map[key] = (item, is_os)


def _parse_result_misconfigs(
    res: dict[str, object],
    misconfig_map: dict[tuple[str, str, Optional[int]], MisconfigItem],
) -> None:
    """Extract failed MisconfigItem records from one Trivy Result entry."""
    target = str(res.get("Target") or "")
    for raw_m in _as_list(res.get("Misconfigurations")):
        if not isinstance(raw_m, dict):
            continue
        status = str(raw_m.get("Status") or "FAIL").upper()
        if status == "PASS":
            continue
        check_id = str(raw_m.get("ID") or raw_m.get("AVDID") or "MISCONFIG").strip()
        cause = raw_m.get("CauseMetadata")
        start_line = cause.get("StartLine") if isinstance(cause, dict) else None
        line_num = int(start_line) if isinstance(start_line, int) and start_line > 0 else None
        key = (check_id, target, line_num)
        if key not in misconfig_map:
            misconfig_map[key] = MisconfigItem(
                check_id=check_id,
                severity=normalize_severity(raw_m.get("Severity")),
                title=str(raw_m.get("Title") or check_id).strip()[:160],
                file_path=target,
                start_line=line_num,
                message=str(raw_m.get("Message") or "").strip()[:200],
                resolution=str(raw_m.get("Resolution") or "").strip()[:200],
            )


def _parse_result_secrets(
    res: dict[str, object],
    secret_map: dict[tuple[str, str, Optional[int]], SecretFindingItem],
) -> None:
    """Extract redacted SecretFindingItem records from one Trivy Result entry."""
    target = str(res.get("Target") or "")
    for raw_s in _as_list(res.get("Secrets")):
        if not isinstance(raw_s, dict):
            continue
        rule_id = str(raw_s.get("RuleID") or "secret").strip()
        start_line = raw_s.get("StartLine")
        line_num = int(start_line) if isinstance(start_line, int) and start_line > 0 else None
        key = (rule_id, target, line_num)
        if key not in secret_map:
            secret_map[key] = SecretFindingItem(
                rule_id=rule_id,
                category=str(raw_s.get("Category") or "general").strip(),
                severity=normalize_severity(raw_s.get("Severity")),
                title=str(raw_s.get("Title") or rule_id).strip()[:160],
                file_path=target,
                start_line=line_num,
                redacted_match=redact_secret_match(raw_s.get("Match")),
            )


def _load_trivy_results(json_path: Optional[Path]) -> list[dict[str, object]]:
    """Load the `Results` list from a Trivy JSON report file if present and valid."""
    if json_path is None or not json_path.is_file():
        return []
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict):
        return []
    results = payload.get("Results")
    return [r for r in results if isinstance(r, dict)] if isinstance(results, list) else []


def _is_skipped_target_path(
    target_path: str,
    skip_files: Sequence[str],
    skip_dirs: Sequence[str],
) -> bool:
    """Return True if a Trivy target path matches skip_files or skip_dirs."""
    if not target_path:
        return False
    norm = target_path.strip().lstrip("/")
    if norm.startswith("target/"):
        norm = norm[len("target/") :]
    if skip_files and matches_opt_out_scope(norm, skip_files):
        return True
    dir_globs = [f"{d.strip().strip('/')}/**" for d in skip_dirs if d.strip().strip("/")]
    return bool(dir_globs and matches_opt_out_scope(norm, dir_globs))


def _filter_trivy_maps(
    vuln_map: dict[tuple[str, str, str], tuple[VulnerabilityItem, bool]],
    misconfig_map: dict[tuple[str, str, Optional[int]], MisconfigItem],
    secret_map: dict[tuple[str, str, Optional[int]], SecretFindingItem],
    *,
    opt_outs: Sequence[OptOutEntry],
    skip_files: Sequence[str],
    skip_dirs: Sequence[str],
) -> tuple[
    list[tuple[VulnerabilityItem, bool]],
    list[MisconfigItem],
    list[SecretFindingItem],
    dict[str, int],
]:
    """Filter parsed Trivy items against skip_files/skip_dirs and [[opt_out]] waivers."""
    opt_out_counts: dict[str, int] = {}
    all_pairs: list[tuple[VulnerabilityItem, bool]] = []
    for item, is_os in vuln_map.values():
        if _is_skipped_target_path(item.target, skip_files, skip_dirs):
            continue
        matched = match_opt_out(
            opt_outs,
            (item.vuln_id, f"vuln/{item.pkg_name}", "common/dependencies"),
            item.target,
        )
        if matched is not None:
            opt_out_counts[matched.id] = opt_out_counts.get(matched.id, 0) + 1
        else:
            all_pairs.append((item, is_os))

    filtered_misconfigs: list[MisconfigItem] = []
    for m_item in misconfig_map.values():
        if _is_skipped_target_path(m_item.file_path, skip_files, skip_dirs):
            continue
        matched = match_opt_out(
            opt_outs,
            (m_item.check_id, f"AVD-{m_item.check_id}", "common/container_security"),
            m_item.file_path,
        )
        if matched is not None:
            opt_out_counts[matched.id] = opt_out_counts.get(matched.id, 0) + 1
        else:
            filtered_misconfigs.append(m_item)

    filtered_secrets: list[SecretFindingItem] = []
    for s_item in secret_map.values():
        if _is_skipped_target_path(s_item.file_path, skip_files, skip_dirs):
            continue
        matched = match_opt_out(
            opt_outs,
            (s_item.rule_id, f"secret/{s_item.rule_id}", "common/secrets"),
            s_item.file_path,
        )
        if matched is not None:
            opt_out_counts[matched.id] = opt_out_counts.get(matched.id, 0) + 1
        else:
            filtered_secrets.append(s_item)

    return all_pairs, filtered_misconfigs, filtered_secrets, opt_out_counts


def parse_trivy_reports(
    fs_json_path: Optional[Path] = None,
    image_json_path: Optional[Path] = None,
    *,
    opt_outs: Sequence[OptOutEntry] = (),
    skip_files: Sequence[str] = (),
    skip_dirs: Sequence[str] = (),
) -> ParsedTrivyBundle:
    """Parse, deduplicate, classify, and cap Trivy filesystem and resolved-image JSON reports."""
    vuln_map: dict[tuple[str, str, str], tuple[VulnerabilityItem, bool]] = {}
    misconfig_map: dict[tuple[str, str, Optional[int]], MisconfigItem] = {}
    secret_map: dict[tuple[str, str, Optional[int]], SecretFindingItem] = {}

    for report_path in (fs_json_path, image_json_path):
        for res in _load_trivy_results(report_path):
            _parse_result_vulns(res, vuln_map)
            _parse_result_misconfigs(res, misconfig_map)
            _parse_result_secrets(res, secret_map)

    all_pairs, filtered_misconfigs, filtered_secrets, opt_out_counts = _filter_trivy_maps(
        vuln_map,
        misconfig_map,
        secret_map,
        opt_outs=opt_outs,
        skip_files=skip_files,
        skip_dirs=skip_dirs,
    )

    all_vulns = [pair[0] for pair in all_pairs]
    app_vulns = [pair[0] for pair in all_pairs if not pair[1]]
    os_vulns = [pair[0] for pair in all_pairs if pair[1]]

    sorted_pairs = sorted(
        all_pairs,
        key=lambda p: (
            _SEVERITY_ORDER.get(p[0].severity, 9),
            1 if p[1] else 0,
            -(p[0].cvss_score or 0.0),
            p[0].pkg_name,
            p[0].vuln_id,
        ),
    )
    capped_vulns = [p[0] for p in sorted_pairs[:MAX_STORED_VULNERABILITIES]]

    sorted_misconfigs = sorted(
        filtered_misconfigs,
        key=lambda m: (_SEVERITY_ORDER.get(m.severity, 9), m.file_path, m.check_id),
    )[:MAX_STORED_MISCONFIGS]

    sorted_secrets = sorted(
        filtered_secrets,
        key=lambda s: (_SEVERITY_ORDER.get(s.severity, 9), s.file_path, s.start_line or 0),
    )[:MAX_STORED_SECRETS]

    return ParsedTrivyBundle(
        vuln_counts=_summarize_counts(all_vulns),
        app_vuln_counts=_summarize_counts(app_vulns),
        os_vuln_counts=_summarize_counts(os_vulns),
        vulnerabilities=capped_vulns,
        misconfigurations=sorted_misconfigs,
        secrets=sorted_secrets,
        opt_out_counts=opt_out_counts,
    )
