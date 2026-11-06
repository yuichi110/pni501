# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for CWE-classified dangerous code sinks and API attack-surface endpoints."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    ParsedUnit,
    SecurityAstResult,
    SecuritySinkLocation,
)


class BaseSecurityChecker(ABC):
    """Template-method base class extracting dangerous AST sinks and API route specifications."""

    def check(self, units: list[ParsedUnit]) -> SecurityAstResult:
        """Collect CWE-tagged dangerous sinks and API endpoints across production source units.

        Args:
            units: Parsed production source compilation units.

        Returns:
            SecurityAstResult: Deterministic dangerous sink locations and API route inventory.
        """
        sinks: list[SecuritySinkLocation] = []
        endpoints: list[ApiEndpointFact] = []
        for unit in units:
            sinks.extend(self.find_dangerous_sinks(unit))
            endpoints.extend(self.find_api_endpoints(unit))
        sinks.sort(key=lambda s: (0 if s.severity == "high" else 1, s.file, s.line, s.cwe_id))
        endpoints.sort(key=lambda e: (e.path, e.http_method, e.file, e.line))
        return SecurityAstResult(dangerous_sinks=sinks, api_endpoints=endpoints)

    @staticmethod
    def join_route_paths(prefix: str, subpath: str) -> str:
        """Normalize and concatenate a router/controller prefix with an endpoint path."""
        clean_prefix = prefix.strip().rstrip("/")
        clean_sub = subpath.strip()
        if not clean_prefix and not clean_sub:
            return "/"
        if not clean_prefix:
            return clean_sub if clean_sub.startswith("/") else f"/{clean_sub}"
        norm_prefix = clean_prefix if clean_prefix.startswith("/") else f"/{clean_prefix}"
        if not clean_sub or clean_sub == "/":
            return norm_prefix
        norm_sub = clean_sub if clean_sub.startswith("/") else f"/{clean_sub}"
        return f"{norm_prefix}{norm_sub}"

    @abstractmethod
    def find_dangerous_sinks(self, unit: ParsedUnit) -> list[SecuritySinkLocation]:
        """Extract CWE-classified SQLi, command execution, deserialization, crypto, or TLS sinks."""

    @abstractmethod
    def find_api_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract HTTP route specifications and authorization hints from framework definitions."""
