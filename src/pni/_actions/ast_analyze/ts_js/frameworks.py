# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript framework best-practice and ES Module modernization checker."""

from __future__ import annotations

import re
from typing import ClassVar, Final

from pni._actions.ast_analyze.base import BaseFrameworkChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    FrameworkCheckResult,
    ParsedUnit,
)

_CJS_EXPORTS_RE: Final[re.Pattern[str]] = re.compile(r"\bmodule\.exports\s*=")
_CORS_WILDCARD_RE: Final[re.Pattern[str]] = re.compile(r"\bcors\s*\(\s*\)")
_REACT_INDEX_KEY_RE: Final[re.Pattern[str]] = re.compile(r"\bkey\s*=\s*\{\s*(?:idx|index|i)\s*\}")
_CLIENT_DIRECTIVE_RE: Final[re.Pattern[str]] = re.compile(r"""^\s*['"]use client['"]""")
_PROCESS_ENV_RE: Final[re.Pattern[str]] = re.compile(r"\bprocess\.env\.([A-Za-z_]\w*)")


class TsJsFrameworkChecker(BaseFrameworkChecker):
    """Detect Node/React/Express framework issues and CommonJS -> ES Module modernization hints."""

    framework_id: ClassVar[str] = "node-ecosystem"

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Apply to all TypeScript and JavaScript repositories."""
        _ = detected_frameworks
        return bool(units)

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Inspect a TS/JS unit for CommonJS `module.exports`, wildcard `cors()`, and React/Next.js issues."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []
        lines = unit.source.splitlines()
        is_use_client = any(_CLIENT_DIRECTIVE_RE.match(ln) for ln in lines[:10])

        for line_no, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()
            if stripped.startswith(("//", "*", "/*")):
                continue
            if _CJS_EXPORTS_RE.search(stripped):
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="module.exports",
                        detail="Legacy CommonJS `module.exports` — prefer standard ES Module `export` syntax",
                    )
                )
            if _CORS_WILDCARD_RE.search(stripped):
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="cors()",
                        detail=(
                            "Unrestricted `cors()` middleware allows all origins (`*`) — "
                            "configure explicit `origin` allowlist"
                        ),
                    )
                )
            if _REACT_INDEX_KEY_RE.search(stripped):
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="key={index}",
                        detail="React list item uses array index as `key` — use a stable entity identifier",
                    )
                )
            if is_use_client:
                for env_m in _PROCESS_ENV_RE.finditer(stripped):
                    env_name = env_m.group(1)
                    if env_name != "NODE_ENV" and not env_name.startswith("NEXT_PUBLIC_"):
                        issues.append(
                            CodeLocation(
                                file=unit.rel_path,
                                line=line_no,
                                symbol=f"process.env.{env_name}",
                                detail=(
                                    f"Server-only `process.env.{env_name}` referenced in `'use client'` module "
                                    "(undefined in browser bundle or risks secret exposure)"
                                ),
                            )
                        )

        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)
