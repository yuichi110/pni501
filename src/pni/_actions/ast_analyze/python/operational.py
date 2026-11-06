# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python operational readiness checker (SRE PRR timeouts, 12-Factor config/logs, OWASP secrets)."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base.operational import BaseOperationalChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_HTTP_TIMEOUT_CALLS: Final[frozenset[str]] = frozenset(
    {
        "requests.get",
        "requests.post",
        "requests.put",
        "requests.delete",
        "requests.patch",
        "requests.head",
        "requests.options",
        "requests.request",
        "httpx.get",
        "httpx.post",
        "httpx.put",
        "httpx.delete",
        "httpx.patch",
        "httpx.head",
        "httpx.options",
        "httpx.request",
        "urllib.request.urlopen",
        "urlopen",
    }
)
_CONFIG_MODULE_STEMS: Final[frozenset[str]] = frozenset(
    {"config", "settings", "env", "environment", "cli", "__main__", "constants", "conftest"}
)
_CLI_PRESENTATION_STEMS: Final[frozenset[str]] = frozenset(
    {"cli", "__main__", "console", "tui", "repl", "commands"}
)


def _unquote_py_string(raw: str) -> str:
    """Strip string prefixes and quotes from a Python string literal token."""
    trimmed = raw.lstrip("rRuUfFbB")
    for delim in ('"""', "'''", '"', "'"):
        if trimmed.startswith(delim) and trimmed.endswith(delim) and len(trimmed) >= 2 * len(delim):
            return trimmed[len(delim) : -len(delim)]
    return trimmed


def _has_module_role(rel_path: str, allowed_stems: frozenset[str]) -> bool:
    """Return True if file stem or any parent directory matches allowed architectural role names."""
    p = Path(rel_path)
    parts = {seg.lower().lstrip("_") for seg in (*p.parts[:-1], p.stem)}
    return bool(parts & {s.lstrip("_") for s in allowed_stems} or p.stem in allowed_stems)


def _extract_assign_lhs_name(left: SgNode) -> str:
    """Extract clean variable/attribute identifier from the left-hand side of a Python assignment."""
    if left.kind() == "identifier":
        return left.text()
    if left.kind() == "attribute":
        attr = left.field("attribute")
        return attr.text() if attr is not None else left.text()
    return left.text().split(":")[0].strip()


class PythonOperationalChecker(BaseOperationalChecker):
    """Inspect Python CSTs for missing HTTP timeouts, scattered os.environ, raw print(), and secrets."""

    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect requests/httpx/urlopen calls missing an explicit timeout argument."""
        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call"):
            fn = call.field("function")
            if fn is None:
                continue
            fn_text = fn.text().strip()
            if fn_text not in _HTTP_TIMEOUT_CALLS:
                continue
            args_node = call.field("arguments")
            compact_args = args_node.text().replace(" ", "") if args_node is not None else ""
            if "timeout=" not in compact_args:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=fn_text,
                        detail=f"External I/O call '{fn_text}(...)' lacks explicit 'timeout=' (SRE PRR / S113)",
                    )
                )
        return findings

    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect os.environ / os.getenv reads outside dedicated config, settings, or CLI modules."""
        if _has_module_role(unit.rel_path, _CONFIG_MODULE_STEMS):
            return []

        findings: list[CodeLocation] = []
        seen_lines: set[int] = set()
        for call in unit.root.find_all(kind="call"):
            fn = call.field("function")
            if fn is None:
                continue
            fn_text = fn.text().strip()
            lineno = call.range().start.line + 1
            if fn_text in {"os.getenv", "getenv", "os.environ.get", "environ.get"} and lineno not in seen_lines:
                seen_lines.add(lineno)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol=fn_text,
                        detail="Direct env lookup outside config/settings module — centralize config (12-Factor III)",
                    )
                )

        for sub in unit.root.find_all(kind="subscript"):
            val = sub.field("value")
            lineno = sub.range().start.line + 1
            if val is not None and val.text().strip() in {"os.environ", "environ"} and lineno not in seen_lines:
                seen_lines.add(lineno)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol="os.environ[...]",
                        detail="Direct os.environ[...] outside config/settings module (12-Factor III)",
                    )
                )
        return findings

    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect bare print() calls in non-CLI modules where structured logging should be used."""
        if _has_module_role(unit.rel_path, _CLI_PRESENTATION_STEMS):
            return []

        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call"):
            fn = call.field("function")
            if fn is not None and fn.kind() == "identifier" and fn.text() == "print":
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol="print",
                        detail="Unstructured 'print()' in non-CLI module — use structured logging (12-Factor XI)",
                    )
                )
        return findings

    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect hardcoded secret/token/password string literals in Python assignments."""
        findings: list[CodeLocation] = []
        for assign in unit.root.find_all(kind="assignment"):
            left = assign.field("left")
            right = assign.field("right")
            if left is None or right is None or right.kind() != "string":
                continue
            if right.find(kind="interpolation") is not None:
                continue
            var_name = _extract_assign_lhs_name(left)
            literal_val = _unquote_py_string(right.text())
            if self.is_likely_secret_literal(var_name, literal_val):
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=assign.range().start.line + 1,
                        symbol=var_name,
                        detail=f"Hardcoded secret literal assigned to '{var_name}' (OWASP ASVS / S105)",
                    )
                )
        return findings
