# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go CWE dangerous sink detector and Gin/Echo/Fiber/Chi/net-http route extractor."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseSecurityChecker
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    ParsedUnit,
    SecuritySinkLocation,
)

_SQL_QUERY_METHODS: Final[frozenset[str]] = frozenset(
    {"Query", "QueryContext", "QueryRow", "QueryRowContext", "Exec", "ExecContext", "Raw"}
)
_WEAK_CRYPTO_CALLS: Final[frozenset[str]] = frozenset(
    {"md5.New", "md5.Sum", "sha1.New", "sha1.Sum", "des.NewCipher", "rc4.NewCipher"}
)
_HTTP_ROUTE_METHODS: Final[dict[str, str]] = {
    "GET": "GET",
    "POST": "POST",
    "PUT": "PUT",
    "DELETE": "DELETE",
    "PATCH": "PATCH",
    "Get": "GET",
    "Post": "POST",
    "Put": "PUT",
    "Delete": "DELETE",
    "Patch": "PATCH",
    "HandleFunc": "ANY",
}
_INSECURE_TLS_RE: Final[re.Pattern[str]] = re.compile(r"\bInsecureSkipVerify\s*:\s*true\b")


def _extract_call_args(call_node: SgNode) -> list[SgNode]:
    """Return positional argument expression nodes inside a Go `call_expression`."""
    args_node = call_node.field("arguments")
    if args_node is None:
        return []
    return [
        c
        for c in args_node.children()
        if c.kind() not in {"(", ")", ","}
    ]


def _inspect_go_call_sinks(call: SgNode, rel_path: str) -> list[SecuritySinkLocation]:
    """Inspect a single Go call_expression for CWE command injection, SQLi, XSS, and weak crypto."""
    fn_node = call.field("function")
    if fn_node is None:
        return []
    fn_text = fn_node.text().strip()
    line_no = call.range().start.line + 1
    args = _extract_call_args(call)
    sinks: list[SecuritySinkLocation] = []

    if fn_text in {"exec.Command", "exec.CommandContext"}:
        cmd_idx = 1 if fn_text == "exec.CommandContext" else 0
        if len(args) > cmd_idx:
            cmd_arg = args[cmd_idx]
            is_literal = cmd_arg.kind() in {"interpreted_string_literal", "raw_string_literal"}
            all_text = " ".join(a.text() for a in args[cmd_idx:])
            if not is_literal or '"-c"' in all_text:
                sinks.append(
                    SecuritySinkLocation(
                        category="command_injection",
                        cwe_id="CWE-78",
                        severity="high",
                        file=rel_path,
                        line=line_no,
                        symbol=fn_text,
                        detail=f"`{fn_text}(...)` invoked with dynamic command or shell `-c`",
                    )
                )

    method_name = fn_text.rsplit(".", 1)[-1] if "." in fn_text else ""
    if method_name in _SQL_QUERY_METHODS and args:
        q_idx = 1 if method_name.endswith("Context") and len(args) > 1 else 0
        q_arg = args[q_idx]
        q_text = q_arg.text().strip()
        if q_arg.kind() == "binary_expression" or "fmt.Sprintf(" in q_text:
            sinks.append(
                SecuritySinkLocation(
                    category="sql_injection",
                    cwe_id="CWE-89",
                    severity="high",
                    file=rel_path,
                    line=line_no,
                    symbol=fn_text,
                    detail=f"Dynamic SQL query string concatenation/formatting in `{fn_text}(...)`",
                )
            )

    if fn_text in {"template.HTML", "template.JS", "template.URL"} and args:
        if args[0].kind() not in {"interpreted_string_literal", "raw_string_literal"}:
            sinks.append(
                SecuritySinkLocation(
                    category="xss",
                    cwe_id="CWE-79",
                    severity="medium",
                    file=rel_path,
                    line=line_no,
                    symbol=fn_text,
                    detail=f"Unescaped `{fn_text}(...)` type conversion with non-literal content",
                )
            )

    if fn_text in _WEAK_CRYPTO_CALLS:
        sinks.append(
            SecuritySinkLocation(
                category="weak_cryptography",
                cwe_id="CWE-327",
                severity="medium",
                file=rel_path,
                line=line_no,
                symbol=fn_text,
                detail=f"Broken or weak cryptographic primitive `{fn_text}(...)`",
            )
        )
    return sinks


class GoSecurityChecker(BaseSecurityChecker):
    """Extract Go CWE security sinks (SQLi, command injection, XSS, weak crypto, TLS) and HTTP routes."""

    def find_dangerous_sinks(self, unit: ParsedUnit) -> list[SecuritySinkLocation]:
        """Inspect a Go compilation unit for CWE-classified dangerous sinks."""
        sinks: list[SecuritySinkLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            sinks.extend(_inspect_go_call_sinks(call, unit.rel_path))

        for comp in unit.root.find_all(kind="composite_literal"):
            if _INSECURE_TLS_RE.search(comp.text()):
                sinks.append(
                    SecuritySinkLocation(
                        category="insecure_transport",
                        cwe_id="CWE-295",
                        severity="high",
                        file=unit.rel_path,
                        line=comp.range().start.line + 1,
                        symbol="tls.Config",
                        detail="`InsecureSkipVerify: true` disables TLS certificate verification",
                    )
                )

        return sinks

    def find_api_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract HTTP route registrations from Gin, Echo, Fiber, Chi, Gorilla Mux, and `net/http`."""
        endpoints: list[ApiEndpointFact] = []
        for call in unit.root.find_all(kind="call_expression"):
            fn_node = call.field("function")
            if fn_node is None or fn_node.kind() != "selector_expression":
                continue
            field_node = fn_node.field("field")
            if field_node is None:
                continue
            mname = field_node.text().strip()
            http_method = _HTTP_ROUTE_METHODS.get(mname)
            if http_method is None:
                continue
            args = _extract_call_args(call)
            if len(args) < 2:
                continue
            path_arg = args[0]
            if path_arg.kind() not in {"interpreted_string_literal", "raw_string_literal"}:
                continue
            route_path = path_arg.text().strip().strip('"`')
            if not route_path.startswith("/"):
                continue
            handler_text = args[-1].text().strip().splitlines()[0][:60]
            all_args_text = " ".join(a.text() for a in args[1:]).lower()
            has_auth = any(tok in all_args_text for tok in ("auth", "jwt", "token", "admin", "session", "rbac"))
            endpoints.append(
                ApiEndpointFact(
                    http_method=http_method,
                    path=route_path,
                    handler=handler_text,
                    file=unit.rel_path,
                    line=call.range().start.line + 1,
                    has_auth_hint=has_auth,
                    auth_mechanisms=["middleware"] if has_auth else [],
                )
            )
        return endpoints
