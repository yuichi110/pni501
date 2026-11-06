# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java operational readiness checker (SRE PRR timeouts, 12-Factor config/logs, OWASP secrets)."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.base.operational import BaseOperationalChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_JAVA_CONFIG_CLASS_SUFFIXES: Final[tuple[str, ...]] = (
    "Config",
    "Configuration",
    "Properties",
    "Settings",
    "Application",
    "Main",
    "Cli",
)
_JAVA_CLI_CLASS_SUFFIXES: Final[tuple[str, ...]] = ("Main", "Cli", "Command")


class JavaOperationalChecker(BaseOperationalChecker):
    """Inspect Java CSTs for unconfigured HTTP timeouts, System.getenv, System.out, and secrets."""

    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect HttpClient.newHttpClient() and URL.openConnection/openStream without timeouts."""
        findings: list[CodeLocation] = []
        for inv in unit.root.find_all(kind="method_invocation"):
            obj = inv.field("object")
            name_node = inv.field("name")
            mname = name_node.text() if name_node is not None else ""
            obj_txt = obj.text().strip() if obj is not None else ""
            lineno = inv.range().start.line + 1

            if obj_txt == "HttpClient" and mname == "newHttpClient":
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol="HttpClient.newHttpClient",
                        detail="Default HttpClient.newHttpClient() has no connectTimeout — use newBuilder() (SRE PRR)",
                    )
                )
            elif mname in {"openConnection", "openStream"} and "Timeout" not in unit.source:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol=mname,
                        detail=f"URL.{mname}() used without connect/read timeout configuration (SRE PRR)",
                    )
                )
        return findings

    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect System.getenv / System.getProperty in non-config Java classes."""
        stem = unit.file_path.stem
        if stem.endswith(_JAVA_CONFIG_CLASS_SUFFIXES) or "/config/" in f"/{unit.rel_path.lower()}":
            return []

        findings: list[CodeLocation] = []
        for inv in unit.root.find_all(kind="method_invocation"):
            obj = inv.field("object")
            name_node = inv.field("name")
            mname = name_node.text() if name_node is not None else ""
            if obj is not None and obj.text().strip() == "System" and mname in {"getenv", "getProperty"}:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=inv.range().start.line + 1,
                        symbol=f"System.{mname}",
                        detail=(
                            f"Direct System.{mname}() in '{stem}' — centralize via "
                            "@ConfigurationProperties or typed config (12-Factor III)"
                        ),
                    )
                )
        return findings

    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect System.out/err prints and Throwable.printStackTrace() in non-CLI Java classes."""
        stem = unit.file_path.stem
        if stem.endswith(_JAVA_CLI_CLASS_SUFFIXES):
            return []

        findings: list[CodeLocation] = []
        for inv in unit.root.find_all(kind="method_invocation"):
            obj = inv.field("object")
            name_node = inv.field("name")
            mname = name_node.text() if name_node is not None else ""
            obj_txt = obj.text().strip() if obj is not None else ""
            lineno = inv.range().start.line + 1

            if obj_txt in {"System.out", "System.err"}:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol=obj_txt,
                        detail=f"Unstructured {obj_txt} output — route through SLF4J logger (12-Factor XI)",
                    )
                )
            elif mname == "printStackTrace":
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol="printStackTrace",
                        detail="Raw printStackTrace() writes unstructured stderr — log exception via SLF4J",
                    )
                )
        return findings

    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect hardcoded secret/password/API-key string literals in Java variable declarators."""
        findings: list[CodeLocation] = []
        for decl in unit.root.find_all(kind="variable_declarator"):
            name_node = decl.field("name")
            val_node = decl.field("value")
            if name_node is None or val_node is None or val_node.kind() != "string_literal":
                continue
            var_name = name_node.text().strip()
            raw_lit = val_node.text().strip()
            unquoted = raw_lit.strip('"')
            if self.is_likely_secret_literal(var_name, unquoted):
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=decl.range().start.line + 1,
                        symbol=var_name,
                        detail=f"Hardcoded secret literal assigned to '{var_name}' (OWASP ASVS)",
                    )
                )
        return findings
