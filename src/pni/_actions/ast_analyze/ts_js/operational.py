# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript operational readiness checker: fetch/axios timeouts, process.env, console.log, secrets."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze.base import BaseOperationalChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_AXIOS_CALLS: Final[frozenset[str]] = frozenset(
    {
        "axios",
        "axios.get",
        "axios.post",
        "axios.put",
        "axios.delete",
        "axios.patch",
        "axios.request",
        "axios.create",
    }
)
_CONFIG_FILE_HINTS: Final[tuple[str, ...]] = (
    "config",
    "env",
    "setting",
    "constant",
    "cli",
    "bin/",
    "main.",
    "index.",
    "next.config",
    "vite.config",
)
_CLI_FILE_HINTS: Final[tuple[str, ...]] = ("cli", "bin/", "scripts/", "seed", "migrate")
_CONSOLE_CALLS: Final[frozenset[str]] = frozenset({"console.log", "console.debug", "console.info"})
_PROCESS_ENV_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:process\.env|import\.meta\.env)\b")


class TsJsOperationalChecker(BaseOperationalChecker):
    """Evaluate TS/JS HTTP timeouts (`fetch`/`axios`), `process.env` centralization, `console.log`, and secrets."""

    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `fetch(...)` or `axios.*(...)` calls lacking `signal` or `timeout` configuration."""
        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            args = call.field("arguments")
            if fn is None or args is None:
                continue
            fn_text = fn.text().strip()
            args_text = args.text()
            if fn_text == "fetch":
                if "signal" not in args_text and "AbortSignal" not in args_text and "timeout" not in args_text:
                    findings.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=call.range().start.line + 1,
                            symbol="fetch",
                            detail=(
                                "`fetch(...)` called without `signal: AbortSignal.timeout(...)` — "
                                "network I/O can hang indefinitely"
                            ),
                        )
                    )
            elif fn_text in _AXIOS_CALLS and "timeout" not in args_text and "signal" not in args_text:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=fn_text,
                        detail=f"`{fn_text}(...)` called without an explicit `timeout` or `signal` option",
                    )
                )
        return findings

    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `process.env` / `import.meta.env` reads outside dedicated config or entrypoint files."""
        rel_low = unit.rel_path.lower()
        if any(hint in rel_low for hint in _CONFIG_FILE_HINTS):
            return []

        findings: list[CodeLocation] = []
        for line_no, raw_line in enumerate(unit.source.splitlines(), start=1):
            stripped = raw_line.strip()
            if stripped.startswith(("//", "*", "/*")):
                continue
            if _PROCESS_ENV_RE.search(stripped):
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="process.env",
                        detail="Direct `process.env` / `import.meta.env` read in domain module — centralize config",
                    )
                )
        return findings

    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `console.log` / `console.debug` in non-CLI modules."""
        rel_low = unit.rel_path.lower()
        if any(hint in rel_low for hint in _CLI_FILE_HINTS):
            return []

        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            if fn is None:
                continue
            fn_text = fn.text().strip()
            if fn_text in _CONSOLE_CALLS:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=fn_text,
                        detail=f"Unstructured `{fn_text}(...)` output — use a structured logger (`pino`, `winston`)",
                    )
                )
        return findings

    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect hardcoded secret string literals in variable declarators and object properties."""
        findings: list[CodeLocation] = []
        seen_lines: set[int] = set()

        for decl in unit.root.find_all(kind="variable_declarator"):
            name_node = decl.field("name")
            val_node = decl.field("value")
            if name_node is None or val_node is None or val_node.kind() != "string":
                continue
            ident = name_node.text().strip()
            raw_val = val_node.text().strip().strip("'\"")
            line_no = decl.range().start.line + 1
            if line_no not in seen_lines and self.is_likely_secret_literal(ident, raw_val):
                seen_lines.add(line_no)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=ident,
                        detail=f"Hardcoded secret literal assigned to '{ident}'",
                    )
                )

        for pair in unit.root.find_all(kind="pair"):
            key_node = pair.field("key")
            val_node = pair.field("value")
            if key_node is None or val_node is None or val_node.kind() != "string":
                continue
            ident = key_node.text().strip().strip("'\"")
            raw_val = val_node.text().strip().strip("'\"")
            line_no = pair.range().start.line + 1
            if line_no not in seen_lines and self.is_likely_secret_literal(ident, raw_val):
                seen_lines.add(line_no)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=ident,
                        detail=f"Hardcoded secret literal in object property '{ident}'",
                    )
                )

        return findings
