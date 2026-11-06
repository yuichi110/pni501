# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for containerized Trivy security and supply-chain scanning."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

SecurityScanStatus = Literal["passed", "failed", "skipped", "error", "timeout"]
VulnSeverity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]


def _default_fail_severities() -> list[VulnSeverity]:
    """Return default severities that mark a security scan as failed."""
    return ["CRITICAL", "HIGH"]


class SecurityScanOptions(BaseModel):
    """Workflow step `with:` configuration options for `security_scan`."""

    container_engine: Literal["auto", "docker", "podman", "none"] = "auto"
    on_missing_runtime: Literal["skip", "fail"] = "skip"
    trivy_image: str = "ghcr.io/aquasecurity/trivy:0.69.3"
    scan_filesystem: bool = True
    scan_resolved_image: bool = True
    fail_on_severities: list[VulnSeverity] = Field(default_factory=_default_fail_severities)
    scan_timeout_sec: int = Field(default=240, ge=15, le=1200)
    build_timeout_sec: int = Field(default=300, ge=15, le=1800)


class VulnerabilitySummaryCounts(BaseModel):
    """Severity breakdown across deduplicated vulnerabilities."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class VulnerabilityItem(BaseModel):
    """Normalized CVE / advisory record extracted from Trivy JSON."""

    vuln_id: str
    pkg_name: str
    pkg_type: str
    installed_version: str
    fixed_version: str = ""
    severity: VulnSeverity
    title: str = ""
    target: str = ""
    cvss_score: Optional[float] = None
    is_unpinned_specifier: bool = False
    version_resolution_note: str = ""


class MisconfigItem(BaseModel):
    """Container / IaC misconfiguration finding extracted from Trivy JSON."""

    check_id: str
    severity: VulnSeverity
    title: str
    file_path: str
    start_line: Optional[int] = None
    message: str = ""
    resolution: str = ""


class SecretFindingItem(BaseModel):
    """Redacted secret leak finding extracted from Trivy secret scanner."""

    rule_id: str
    category: str
    severity: VulnSeverity
    title: str
    file_path: str
    start_line: Optional[int] = None
    redacted_match: str = ""


class SecurityFacts(BaseModel):
    """Canonical deterministic output persisted at `.pni/cache/<workflow_id>/security/security_facts.json`."""

    status: SecurityScanStatus
    scanner: str = "trivy"
    container_engine: str = "none"
    engine_available: bool = False
    skip_reason: str = ""
    trivy_image: str = ""
    scanned_filesystem: bool = False
    scanned_resolved_image: bool = False
    resolved_image_source: str = ""
    artifacts_dir: str = ""
    vuln_counts: VulnerabilitySummaryCounts = Field(default_factory=VulnerabilitySummaryCounts)
    app_vuln_counts: VulnerabilitySummaryCounts = Field(default_factory=VulnerabilitySummaryCounts)
    os_vuln_counts: VulnerabilitySummaryCounts = Field(default_factory=VulnerabilitySummaryCounts)
    vulnerabilities: list[VulnerabilityItem] = Field(default_factory=list)
    misconfigurations: list[MisconfigItem] = Field(default_factory=list)
    secrets: list[SecretFindingItem] = Field(default_factory=list)
    opt_out_counts: dict[str, int] = Field(default_factory=dict)
