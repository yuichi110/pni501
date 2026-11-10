# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""TypeScript & JavaScript CWE dangerous sink detector and Express/Fastify/Hono/Next.js route extractor."""

from __future__ import annotations

import contextlib
import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseSecurityChecker
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    ParsedUnit,
    SecuritySinkLocation,
)
from pni._actions.ast_analyze.ts_js._helpers import iter_ts_js_callables

_EXEC_SINKS: Final[frozenset[str]] = frozenset(
    {"exec", "execSync", "child_process.exec", "child_process.execSync"}
)
_HTTP_METHODS: Final[dict[str, str]] = {
    "get": "GET",
    "post": "POST",
    "put": "PUT",
    "delete": "DELETE",
    "patch": "PATCH",
}
_NEXT_HTTP_EXPORTS: Final[frozenset[str]] = frozenset({"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"})
_SQL_TEMPLATE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?i)\b(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b.*?\$\{"
)
_REJECT_UNAUTH_RE: Final[re.Pattern[str]] = re.compile(r"\brejectUnauthorized\s*:\s*false\b")


def _extract_call_args(call_node: SgNode) -> list[SgNode]:
    """Return positional argument expression nodes inside a TS/JS `call_expression`."""
    args_node = call_node.field("arguments")
    if args_node is None:
        return []
    return [c for c in args_node.children() if c.kind() not in {"(", ")", ","}]


def _inspect_ts_js_sql_or_crypto_sink(
    fn_text: str,
    args: list[SgNode],
    rel_path: str,
    line_no: int,
) -> SecuritySinkLocation | None:
    """Check raw SQL query methods, `crypto.createHash`, and `Math.random` calls for CWE sinks."""
    if fn_text.endswith((".$queryRawUnsafe", ".$executeRawUnsafe")):
        return SecuritySinkLocation(
            category="sql_injection",
            cwe_id="CWE-89",
            severity="high",
            file=rel_path,
            line=line_no,
            symbol=fn_text,
            detail=f"Unsafe raw SQL execution `{fn_text}(...)`",
        )
    if fn_text.endswith((".query", ".execute", ".raw")) and args:
        q_text = args[0].text()
        if _SQL_TEMPLATE_RE.search(q_text) or (args[0].kind() == "binary_expression" and "SELECT" in q_text.upper()):
            return SecuritySinkLocation(
                category="sql_injection",
                cwe_id="CWE-89",
                severity="high",
                file=rel_path,
                line=line_no,
                symbol=fn_text,
                detail=f"Unparameterized SQL interpolation in `{fn_text}(...)`",
            )
    if fn_text in {"crypto.createHash", "createHash"} and args:
        alg = args[0].text().strip().strip("'\"").lower()
        if alg in {"md5", "sha1", "md4"}:
            return SecuritySinkLocation(
                category="weak_cryptography",
                cwe_id="CWE-327",
                severity="medium",
                file=rel_path,
                line=line_no,
                symbol=fn_text,
                detail=f"Weak cryptographic digest `{fn_text}('{alg}')`",
            )
    if fn_text == "Math.random":
        return SecuritySinkLocation(
            category="weak_cryptography",
            cwe_id="CWE-338",
            severity="low",
            file=rel_path,
            line=line_no,
            symbol="Math.random",
            detail="`Math.random()` is non-cryptographic — use `crypto.randomBytes`/`crypto.randomUUID`",
        )
    return None


def _inspect_ts_js_call_sink(call: SgNode, rel_path: str) -> SecuritySinkLocation | None:
    """Return a SecuritySinkLocation if a TS/JS call_expression matches a CWE sink."""
    fn_node = call.field("function")
    if fn_node is None:
        return None
    fn_text = fn_node.text().strip()
    line_no = call.range().start.line + 1
    args = _extract_call_args(call)

    if fn_text in {"eval", "window.eval", "globalThis.eval"}:
        return SecuritySinkLocation(
            category="code_execution",
            cwe_id="CWE-94",
            severity="high",
            file=rel_path,
            line=line_no,
            symbol=fn_text,
            detail=f"Dynamic code execution via `{fn_text}(...)`",
        )
    if fn_text in _EXEC_SINKS and args and (args[0].kind() != "string" or "${" in args[0].text()):
        return SecuritySinkLocation(
            category="command_injection",
            cwe_id="CWE-78",
            severity="high",
            file=rel_path,
            line=line_no,
            symbol=fn_text,
            detail=f"Shell command execution `{fn_text}(...)` with dynamic arg — prefer `execFile`/`spawn`",
        )
    if fn_text in {"document.write", "document.writeln"}:
        return SecuritySinkLocation(
            category="xss",
            cwe_id="CWE-79",
            severity="high",
            file=rel_path,
            line=line_no,
            symbol=fn_text,
            detail=f"DOM XSS sink `{fn_text}(...)`",
        )
    return _inspect_ts_js_sql_or_crypto_sink(fn_text, args, rel_path, line_no)


def _inspect_ts_js_dom_and_tls_sinks(unit: ParsedUnit) -> list[SecuritySinkLocation]:
    """Inspect `innerHTML`, `dangerouslySetInnerHTML`, `new Function`, and `rejectUnauthorized: false`."""
    sinks: list[SecuritySinkLocation] = []
    for new_expr in unit.root.find_all(kind="new_expression"):
        ctor = new_expr.field("constructor")
        if ctor is not None and ctor.text().strip() == "Function":
            sinks.append(
                SecuritySinkLocation(
                    category="code_execution",
                    cwe_id="CWE-94",
                    severity="high",
                    file=unit.rel_path,
                    line=new_expr.range().start.line + 1,
                    symbol="new Function",
                    detail="Dynamic code compilation via `new Function(...)`",
                )
            )

    for assign in unit.root.find_all(kind="assignment_expression"):
        left = assign.field("left")
        if left is not None and left.text().strip().endswith((".innerHTML", ".outerHTML")):
            sinks.append(
                SecuritySinkLocation(
                    category="xss",
                    cwe_id="CWE-79",
                    severity="high",
                    file=unit.rel_path,
                    line=assign.range().start.line + 1,
                    symbol=left.text().strip(),
                    detail=f"Unescaped HTML assignment to `{left.text().strip()}`",
                )
            )

    with contextlib.suppress(RuntimeError):
        for jsx_attr in unit.root.find_all(kind="jsx_attribute"):
            if jsx_attr.text().lstrip().startswith("dangerouslySetInnerHTML"):
                sinks.append(
                    SecuritySinkLocation(
                        category="xss",
                        cwe_id="CWE-79",
                        severity="medium",
                        file=unit.rel_path,
                        line=jsx_attr.range().start.line + 1,
                        symbol="dangerouslySetInnerHTML",
                        detail="React `dangerouslySetInnerHTML` bypasses automatic XSS escaping",
                    )
                )

    for pair in unit.root.find_all(kind="pair"):
        if _REJECT_UNAUTH_RE.search(pair.text()):
            sinks.append(
                SecuritySinkLocation(
                    category="insecure_transport",
                    cwe_id="CWE-295",
                    severity="high",
                    file=unit.rel_path,
                    line=pair.range().start.line + 1,
                    symbol="rejectUnauthorized",
                    detail="`rejectUnauthorized: false` disables TLS certificate verification",
                )
            )
    return sinks


class TsJsSecurityChecker(BaseSecurityChecker):
    """Extract TS/JS CWE sinks (`eval`, `exec`, `dangerouslySetInnerHTML`, `innerHTML`, SQLi, TLS) and routes."""

    def find_dangerous_sinks(self, unit: ParsedUnit) -> list[SecuritySinkLocation]:
        """Inspect a TypeScript or JavaScript unit for CWE-classified dangerous sinks."""
        sinks: list[SecuritySinkLocation] = []
        for call in unit.root.find_all(kind="call_expression"):
            call_sink = _inspect_ts_js_call_sink(call, unit.rel_path)
            if call_sink is not None:
                sinks.append(call_sink)
        sinks.extend(_inspect_ts_js_dom_and_tls_sinks(unit))
        return sinks

    def find_api_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract HTTP routes from Express/Fastify/Hono/Koa and Next.js App Router `route.ts`/`route.js`."""
        endpoints: list[ApiEndpointFact] = []

        for call in unit.root.find_all(kind="call_expression"):
            fn_node = call.field("function")
            if fn_node is None or fn_node.kind() != "member_expression":
                continue
            prop = fn_node.field("property")
            if prop is None:
                continue
            http_method = _HTTP_METHODS.get(prop.text().strip())
            if http_method is None:
                continue
            args = _extract_call_args(call)
            if len(args) < 2 or args[0].kind() != "string":
                continue
            route_path = args[0].text().strip().strip("'\"")
            if not route_path.startswith("/"):
                continue
            handler_txt = args[-1].text().strip().splitlines()[0][:60]
            all_args_low = " ".join(a.text() for a in args[1:]).lower()
            has_auth = any(tok in all_args_low for tok in ("auth", "jwt", "guard", "session", "permission", "role"))
            endpoints.append(
                ApiEndpointFact(
                    http_method=http_method,
                    path=route_path,
                    handler=handler_txt,
                    file=unit.rel_path,
                    line=call.range().start.line + 1,
                    has_auth_hint=has_auth,
                    auth_mechanisms=["middleware"] if has_auth else [],
                )
            )

        if unit.file_path.stem == "route":
            for _qual, short, is_exp, fn_node, _anchor in iter_ts_js_callables(unit):
                if is_exp and short in _NEXT_HTTP_EXPORTS:
                    endpoints.append(
                        ApiEndpointFact(
                            http_method=short,
                            path=f"/{unit.rel_path}",
                            handler=short,
                            file=unit.rel_path,
                            line=fn_node.range().start.line + 1,
                            has_auth_hint="auth" in fn_node.text().lower(),
                            auth_mechanisms=["session"] if "auth" in fn_node.text().lower() else [],
                        )
                    )

        return endpoints
