# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Containerized Trivy security, supply-chain CVE, IaC misconfig, and secret scanning."""

from __future__ import annotations

from pni._actions.security_scan.models import (
    MisconfigItem,
    SecretFindingItem,
    SecurityFacts,
    SecurityScanOptions,
    SecurityScanStatus,
    VulnerabilityItem,
    VulnerabilitySummaryCounts,
    VulnSeverity,
)
from pni._actions.security_scan.parsers import (
    UNPINNED_RESOLUTION_NOTE,
    ParsedTrivyBundle,
    is_os_package_type,
    is_symbolic_or_unpinned_version,
    normalize_severity,
    parse_trivy_reports,
    redact_secret_match,
)
from pni._actions.security_scan.runner import run_security_scan

__all__ = [
    "UNPINNED_RESOLUTION_NOTE",
    "MisconfigItem",
    "ParsedTrivyBundle",
    "SecretFindingItem",
    "SecurityFacts",
    "SecurityScanOptions",
    "SecurityScanStatus",
    "VulnSeverity",
    "VulnerabilityItem",
    "VulnerabilitySummaryCounts",
    "is_os_package_type",
    "is_symbolic_or_unpinned_version",
    "normalize_severity",
    "parse_trivy_reports",
    "redact_secret_match",
    "run_security_scan",
]
