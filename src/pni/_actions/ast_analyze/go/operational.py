# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go operational readiness checker: HTTP timeouts, scattered env reads, console prints, and secrets."""

from __future__ import annotations

from typing import Final

from pni._actions.ast_analyze.base import BaseOperationalChecker
from pni._actions.ast_analyze.go._helpers import extract_package_name
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_DEFAULT_HTTP_CALLS: Final[frozenset[str]] = frozenset(
    {
        "http.Get",
        "http.Post",
        "http.PostForm",
        "http.Head",
        "http.DefaultClient.Do",
        "http.DefaultClient.Get",
        "http.DefaultClient.Post",
    }
)
_CONFIG_PATH_TOKENS: Final[tuple[str, ...]] = ("config", "env", "setting", "option", "cmd/", "main.go")
_CLI_PATH_TOKENS: Final[tuple[str, ...]] = ("cmd/", "cli", "main.go")
_CONSOLE_PRINT_CALLS: Final[frozenset[str]] = frozenset(
    {"fmt.Print", "fmt.Println", "fmt.Printf", "print", "println"}
)


class GoOperationalChecker(BaseOperationalChecker):
    """Evaluate Go I/O timeouts, `os.Getenv` centralization, `fmt.Print*` logging, and hardcoded secrets."""

    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `http.Get`/`http.Post` (using `http.DefaultClient`) and `http.Client{}` without `Timeout`."""
        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            if fn is None:
                continue
            fn_text = fn.text().strip()
            if fn_text in _DEFAULT_HTTP_CALLS:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=fn_text,
                        detail=(
                            f"`{fn_text}(...)` uses `http.DefaultClient` with no timeout — "
                            "use `&http.Client{Timeout: ...}`"
                        ),
                    )
                )

        for comp in unit.root.find_all(kind="composite_literal"):
            type_node = comp.field("type")
            if type_node is None or type_node.text().strip() != "http.Client":
                continue
            body_node = comp.field("body")
            body_text = body_node.text() if body_node is not None else ""
            if "Timeout" not in body_text:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=comp.range().start.line + 1,
                        symbol="http.Client",
                        detail="`http.Client{...}` initialized without an explicit `Timeout` field",
                    )
                )
        return findings

    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `os.Getenv` / `os.LookupEnv` outside config or cmd/main packages."""
        rel_low = unit.rel_path.lower()
        pkg_name = extract_package_name(unit).lower()
        if pkg_name in {"main", "config", "env"} or any(tok in rel_low for tok in _CONFIG_PATH_TOKENS):
            return []

        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            if fn is None:
                continue
            fn_text = fn.text().strip()
            if fn_text in {"os.Getenv", "os.LookupEnv"}:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=fn_text,
                        detail=f"Direct `{fn_text}(...)` in domain package '{pkg_name}' — centralize env config",
                    )
                )
        return findings

    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect `fmt.Print*` / `println` in non-CLI packages."""
        rel_low = unit.rel_path.lower()
        pkg_name = extract_package_name(unit).lower()
        if pkg_name == "main" or any(tok in rel_low for tok in _CLI_PATH_TOKENS):
            return []

        findings: list[CodeLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            if fn is None:
                continue
            fn_text = fn.text().strip()
            if fn_text in _CONSOLE_PRINT_CALLS:
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=fn_text,
                        detail=(
                            f"Unstructured console output `{fn_text}(...)` — "
                            "use structured logging (`log/slog`, `zap`, `zerolog`)"
                        ),
                    )
                )
        return findings

    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect hardcoded secret string literals in Go var/const declarations, `:=`, and struct fields."""
        findings: list[CodeLocation] = []
        seen_lines: set[int] = set()

        for kind_name in ("var_spec", "const_spec"):
            for spec in unit.root.find_all(kind=kind_name):
                name_node = spec.field("name")
                val_node = spec.field("value")
                if name_node is None or val_node is None:
                    continue
                ident = name_node.text().strip()
                for str_node in val_node.find_all(kind="interpreted_string_literal"):
                    raw_val = str_node.text().strip().strip('"')
                    line_no = spec.range().start.line + 1
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

        for short_decl in unit.root.find_all(kind="short_var_declaration"):
            left = short_decl.field("left")
            right = short_decl.field("right")
            if left is None or right is None:
                continue
            ident = left.text().strip()
            for str_node in right.find_all(kind="interpreted_string_literal"):
                raw_val = str_node.text().strip().strip('"')
                line_no = short_decl.range().start.line + 1
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

        return findings
