# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP 12-Factor, SRE I/O timeout, structured logging, and hardcoded credential AST checker."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze.base import BaseOperationalChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit
from pni._actions.ast_analyze.php._helpers import (
    enclosing_callable_symbol,
    strip_php_quotes,
)

_DEBUG_PRINT_FUNCS: Final[frozenset[str]] = frozenset(
    {"var_dump", "print_r", "var_export", "dd", "dump", "debug_zval_dump"}
)
_CONFIG_FILE_HINTS: Final[tuple[str, ...]] = ("config/", "config.php", "settings.php", "wp-config")
_DEFINE_CALL_RE: Final[re.Pattern[str]] = re.compile(
    r"\bdefine\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)"
)
_ARRAY_KV_SECRET_RE: Final[re.Pattern[str]] = re.compile(
    r"['\"]([A-Za-z0-9_.-]+)['\"]\s*=>\s*['\"]([^'\"]+)['\"]"
)


def _is_config_module(rel_path: str) -> bool:
    """Return True if rel_path represents a dedicated configuration file."""
    low = rel_path.lower()
    return any(hint in low for hint in _CONFIG_FILE_HINTS)


class PhpOperationalChecker(BaseOperationalChecker):
    """Detect missing HTTP/cURL timeouts, scattered env reads, debug dumps, and hardcoded PHP secrets."""

    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `curl_init`, remote `file_get_contents`, Guzzle `Client`, or `Http::*` without timeouts."""
        findings: list[CodeLocation] = []
        src = unit.source

        for fcall in unit.root.find_all(kind="function_call_expression"):
            children = fcall.children()
            callee = children[0].text().strip().lstrip("\\") if children else ""
            line = fcall.range().start.line + 1
            sym = enclosing_callable_symbol(fcall) or callee

            if callee == "curl_init":
                # Check enclosing scope or file for CURLOPT_TIMEOUT / CURLOPT_CONNECTTIMEOUT
                if "CURLOPT_TIMEOUT" not in src and "CURLOPT_TIMEOUT_MS" not in src:
                    findings.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line,
                            symbol=sym,
                            detail="cURL handle initialized without CURLOPT_TIMEOUT — risks indefinite hang",
                        )
                    )
            elif callee == "file_get_contents":
                args_txt = fcall.text()
                if ("http://" in args_txt or "https://" in args_txt) and "stream_context_create" not in src:
                    findings.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line,
                            symbol=sym,
                            detail="Remote HTTP 'file_get_contents(...)' without stream_context timeout",
                        )
                    )

        for obj in unit.root.find_all(kind="object_creation_expression"):
            txt = obj.text()
            if re.search(r"\bnew\s+(?:\\?GuzzleHttp\\)?Client\s*\(", txt) and "timeout" not in txt.lower():
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=obj.range().start.line + 1,
                        symbol=enclosing_callable_symbol(obj) or "GuzzleHttp\\Client",
                        detail="Guzzle Client instantiated without explicit 'timeout' / 'connect_timeout'",
                    )
                )

        for scall in unit.root.find_all(kind="scoped_call_expression"):
            stxt = scall.text()
            if re.match(r"^\\?(?:Illuminate\\Support\\Facades\\)?Http::(?:get|post|put|delete|patch)\b", stxt):
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=scall.range().start.line + 1,
                        symbol=enclosing_callable_symbol(scall) or "Http",
                        detail="Direct 'Http::*' call without preceding 'Http::timeout(N)->...'",
                    )
                )

        return findings

    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Flag `getenv(...)`, `$_ENV[...]`, and `env(...)` outside dedicated config files."""
        if _is_config_module(unit.rel_path):
            return []

        findings: list[CodeLocation] = []
        seen_lines: set[int] = set()

        for fcall in unit.root.find_all(kind="function_call_expression"):
            children = fcall.children()
            callee = children[0].text().strip().lstrip("\\") if children else ""
            if callee in {"getenv", "env"}:
                line = fcall.range().start.line + 1
                seen_lines.add(line)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=enclosing_callable_symbol(fcall) or callee,
                        detail=f"Direct '{callee}()' call outside config module — centralize in typed config",
                    )
                )

        for vnode in unit.root.find_all(kind="variable_name"):
            if vnode.text().strip() == "$_ENV":
                line = vnode.range().start.line + 1
                if line in seen_lines:
                    continue
                seen_lines.add(line)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=enclosing_callable_symbol(vnode) or "$_ENV",
                        detail="Direct '$_ENV' access outside config module",
                    )
                )
        return findings

    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `var_dump`, `print_r`, `dd`, and raw `error_log` calls in production code."""
        findings: list[CodeLocation] = []
        for fcall in unit.root.find_all(kind="function_call_expression"):
            children = fcall.children()
            callee = children[0].text().strip().lstrip("\\").lower() if children else ""
            if callee in _DEBUG_PRINT_FUNCS or callee == "error_log":
                line = fcall.range().start.line + 1
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=enclosing_callable_symbol(fcall) or callee,
                        detail=f"Unstructured debug/log function '{callee}()' — use PSR-3 LoggerInterface",
                    )
                )
        return findings

    def _record_secret(
        self,
        unit: ParsedUnit,
        line: int,
        name: str,
        value: str,
        detail: str,
        seen: set[tuple[int, str]],
        findings: list[CodeLocation],
    ) -> None:
        """Append a secret finding if `is_likely_secret_literal` matches and `(line, name)` is new."""
        if self.is_likely_secret_literal(name, value) and (line, name) not in seen:
            seen.add((line, name))
            findings.append(CodeLocation(file=unit.rel_path, line=line, symbol=name, detail=detail))

    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect hardcoded credentials in PHP variables, class constants, `define()`, and arrays."""
        findings: list[CodeLocation] = []
        seen: set[tuple[int, str]] = set()

        for assign in unit.root.find_all(kind="assignment_expression"):
            children = assign.children()
            if len(children) >= 3 and children[-1].kind() in {"string", "encapsed_string"}:
                lhs = children[0].text().strip().lstrip("$")
                val = strip_php_quotes(children[-1].text())
                self._record_secret(
                    unit,
                    assign.range().start.line + 1,
                    lhs,
                    val,
                    f"Hardcoded secret literal assigned to '${lhs}'",
                    seen,
                    findings,
                )

        for cdecl in unit.root.find_all(kind="const_element"):
            children = cdecl.children()
            if len(children) >= 3 and children[-1].kind() in {"string", "encapsed_string"}:
                cname = children[0].text().strip()
                val = strip_php_quotes(children[-1].text())
                self._record_secret(
                    unit,
                    cdecl.range().start.line + 1,
                    cname,
                    val,
                    f"Hardcoded secret literal in constant '{cname}'",
                    seen,
                    findings,
                )

        for idx, raw_line in enumerate(unit.source.splitlines(), start=1):
            for def_m in _DEFINE_CALL_RE.finditer(raw_line):
                kname, kval = def_m.group(1), def_m.group(2)
                self._record_secret(
                    unit,
                    idx,
                    kname,
                    kval,
                    f"Hardcoded credential in define('{kname}', ...)",
                    seen,
                    findings,
                )
            for kv_m in _ARRAY_KV_SECRET_RE.finditer(raw_line):
                kname, kval = kv_m.group(1), kv_m.group(2)
                self._record_secret(
                    unit,
                    idx,
                    kname,
                    kval,
                    f"Hardcoded credential in array key '{kname}'",
                    seen,
                    findings,
                )

        return findings
