# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for 12-Factor, Google SRE PRR, and OWASP ASVS operational signals."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Final

from pni._actions.ast_analyze.models import (
    CodeLocation,
    OperationalResult,
    ParsedUnit,
)

_SECRET_IDENT_SUBSTRINGS: Final[tuple[str, ...]] = (
    "password",
    "passwd",
    "api_key",
    "apikey",
    "secret_key",
    "access_token",
    "auth_token",
    "private_key",
    "client_secret",
)
_SECRET_IDENT_SUFFIXES: Final[tuple[str, ...]] = ("_secret", "_token", "_pwd")
_NON_SECRET_IDENT_HINTS: Final[tuple[str, ...]] = (
    "env",
    "header",
    "field",
    "path",
    "file",
    "url",
    "uri",
    "endpoint",
    "name",
    "type",
    "count",
    "limit",
    "max",
    "min",
    "prompt",
    "msg",
    "message",
    "error",
    "label",
    "pattern",
    "regex",
    "prefix",
    "suffix",
    "icon",
    "asset",
    "image",
    "img",
    "color",
    "style",
    "font",
    "glyph",
    "badge",
    "template",
    "slug",
    "theme",
    "logo",
)
_ASSET_OR_DOC_EXTENSIONS: Final[tuple[str, ...]] = (
    ".png",
    ".svg",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".ico",
    ".bmp",
    ".pdf",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".csv",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".css",
    ".html",
    ".md",
    ".txt",
)
_PLACEHOLDER_VALUES: Final[frozenset[str]] = frozenset(
    {
        "changeme",
        "placeholder",
        "dummy",
        "example",
        "your_api_key",
        "your-api-key",
        "none",
        "null",
        "undefined",
        "redacted",
        "secret",
        "password",
        "todo",
        "test",
    }
)
_ENV_KEY_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")
_NON_ALNUM_RE: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9]")


class BaseOperationalChecker(ABC):
    """Template-method base class extracting operational readiness and secret-hygiene AST facts."""

    def check(self, units: list[ParsedUnit]) -> OperationalResult:
        """Evaluate I/O timeouts, config centralization, structured logging, and hardcoded secrets.

        Args:
            units: Parsed compilation units in the target project.

        Returns:
            OperationalResult: Aggregated deterministic operational and security AST findings.
        """
        missing_timeouts: list[CodeLocation] = []
        scattered_env: list[CodeLocation] = []
        unstructured_logs: list[CodeLocation] = []
        secrets: list[CodeLocation] = []

        for unit in units:
            missing_timeouts.extend(self.find_missing_io_timeouts(unit))
            scattered_env.extend(self.find_scattered_env_access(unit))
            unstructured_logs.extend(self.find_unstructured_logging(unit))
            secrets.extend(self.find_hardcoded_secrets(unit))

        return OperationalResult(
            missing_io_timeouts=missing_timeouts,
            scattered_env_access=scattered_env,
            unstructured_logging=unstructured_logs,
            hardcoded_secrets=secrets,
        )

    @staticmethod
    def is_likely_secret_literal(identifier: str, literal_value: str) -> bool:
        """Return True if identifier and unquoted string literal strongly indicate a hardcoded secret."""
        ident_norm = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", identifier).lower().strip("_")
        is_secret_name = bool(ident_norm) and not any(hint in ident_norm for hint in _NON_SECRET_IDENT_HINTS) and (
            ident_norm == "secret"
            or any(sub in ident_norm for sub in _SECRET_IDENT_SUBSTRINGS)
            or ident_norm.endswith(_SECRET_IDENT_SUFFIXES)
        )
        if not is_secret_name:
            return False

        val = literal_value.strip()
        if len(val) < 8 or " " in val or "\n" in val or set(val) <= {"*", ".", "-", "_"}:
            return False
        lower_val = val.lower()
        if (
            lower_val in _PLACEHOLDER_VALUES
            or lower_val.startswith(("x-", "<", "${", "{{", "http://", "https://"))
            or lower_val.endswith(_ASSET_OR_DOC_EXTENSIONS)
        ):
            return False
        ident_alnum = _NON_ALNUM_RE.sub("", ident_norm)
        val_alnum = _NON_ALNUM_RE.sub("", lower_val)
        if val_alnum and ident_alnum and (val_alnum in ident_alnum or ident_alnum in val_alnum):
            return False
        return _ENV_KEY_NAME_RE.match(val) is None

    @abstractmethod
    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect external network/HTTP calls lacking explicit timeout configuration (SRE PRR)."""

    @abstractmethod
    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect direct environment variable reads outside dedicated config modules (12-Factor III)."""

    @abstractmethod
    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect raw stdout/stderr console prints outside CLI presentation layers (12-Factor XI)."""

    @abstractmethod
    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect hardcoded credentials/API keys assigned in source code (OWASP ASVS)."""
