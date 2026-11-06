# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PHP CWE dangerous-sink SAST extractor and 4-mode HTTP/REST/WordPress/Raw-PHP attack-surface analyzer."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseSecurityChecker
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    ParsedUnit,
    SecuritySinkLocation,
    SinkSeverity,
)
from pni._actions.ast_analyze.php._helpers import (
    INCLUDE_EXPR_KINDS,
    USER_INPUT_SUPERGLOBALS,
    enclosing_callable_symbol,
    extract_node_name,
    extract_php_namespace,
    iter_php_types,
    strip_php_quotes,
)

_CMD_EXEC_FUNCS: Final[frozenset[str]] = frozenset(
    {"exec", "shell_exec", "system", "passthru", "popen", "proc_open", "pcntl_exec"}
)
_WEAK_HASH_FUNCS: Final[frozenset[str]] = frozenset({"md5", "sha1"})
_WEAK_RNG_FUNCS: Final[frozenset[str]] = frozenset({"rand", "mt_rand", "uniqid"})
_FILE_SINK_FUNCS: Final[frozenset[str]] = frozenset(
    {"file_get_contents", "file_put_contents", "readfile", "fopen", "unlink", "move_uploaded_file"}
)
_XSS_ESCAPERS: Final[tuple[str, ...]] = (
    "htmlspecialchars",
    "htmlentities",
    "esc_html",
    "esc_attr",
    "esc_url",
    "esc_js",
    "esc_textarea",
    "wp_kses",
    "intval",
    "absint",
    "(int)",
    "urlencode",
    "json_encode",
)
_XSS_SOURCES: Final[tuple[str, ...]] = (
    "$_GET",
    "$_POST",
    "$_REQUEST",
    "$_COOKIE",
    "PHP_SELF",
    "REQUEST_URI",
    "QUERY_STRING",
)
_AUTH_TOKEN_VAR_RE: Final[re.Pattern[str]] = re.compile(
    r"(?i)\$(?:[A-Za-z0-9_]*?(?:password|passwd|pwd|pw_hash|hash|token|hmac|signature|secret|api_key|otp|nonce)[A-Za-z0-9_]*)"
)
_SQL_MEMBER_METHODS: Final[frozenset[str]] = frozenset(
    {
        "query",
        "exec",
        "get_results",
        "get_row",
        "get_var",
        "get_col",
        "whereRaw",
        "selectRaw",
        "orderByRaw",
        "havingRaw",
    }
)
_BLADE_RAW_ECHO_RE: Final[re.Pattern[str]] = re.compile(r"\{!!\s*(.+?)\s*!!\}")
_LARAVEL_ROUTE_CALL_RE: Final[re.Pattern[str]] = re.compile(
    r"Route::(?:(?P<pre>[^\n;]*?)->)?(?P<verb>get|post|put|patch|delete|any)\s*\(\s*"
    r"['\"](?P<path>[^'\"]+)['\"]\s*,\s*(?P<handler>[^;\n]+?)\)(?P<post>[^\n;]*)"
)
_LARAVEL_MIDDLEWARE_RE: Final[re.Pattern[str]] = re.compile(
    r"middleware\s*\(\s*(?:\[([^\]]+)\]|['\"]([^'\"]+)['\"])"
)
_SYMFONY_ATTR_ROUTE_RE: Final[re.Pattern[str]] = re.compile(
    r"#\[\s*(?:Symfony\\Component\\Routing\\Attribute\\)?Route\s*\(\s*(?:path\s*:\s*)?"
    r"['\"](?P<path>[^'\"]+)['\"](?P<rest>[^\]]*)\]"
)
_WP_REST_ROUTE_RE: Final[re.Pattern[str]] = re.compile(
    r"register_rest_route\s*\(\s*['\"](?P<ns>[^'\"]+)['\"]\s*,\s*['\"](?P<route>[^'\"]+)['\"]\s*,\s*(?P<args>[\s\S]*?)\)\s*;"
)
_WP_AJAX_HOOK_RE: Final[re.Pattern[str]] = re.compile(
    r"add_action\s*\(\s*['\"]wp_ajax_(?P<nopriv>nopriv_)?(?P<act>[A-Za-z0-9_-]+)['\"]\s*,\s*(?P<cb>[^)\n]+)\)"
)


def _extract_call_args_text(call_node: SgNode) -> list[str]:
    """Return top-level argument text strings inside `arguments` of a PHP call expression."""
    args_node = call_node.find(kind="arguments")
    if args_node is None:
        return []
    return [c.text().strip() for c in args_node.children() if c.kind() not in {"(", ")", ","}]


def _has_dynamic_sql_expr(expr_txt: str) -> bool:
    """Return True if an SQL argument interpolates `$` variables or concatenates via `.` without `->prepare(`."""
    if "->prepare(" in expr_txt:
        return False
    stripped = expr_txt.strip()
    if stripped.startswith("'") and stripped.endswith("'") and "." not in stripped:
        return False
    return "$" in stripped or "." in stripped


def _is_dynamic_code_eval_call(callee: str, args: list[str]) -> bool:
    """Return True if a PHP function call evaluates dynamic PHP code (`CWE-94`)."""
    if callee in {"eval", "create_function"}:
        return True
    if callee == "preg_replace" and args:
        return bool(re.search(r"/[imsxuADSUXJu]*e[imsxuADSUXJu]*['\"]$", args[0]))
    if callee == "assert" and args and "$" in args[0]:
        return any(tok in args[0] for tok in ("'", '"', "."))
    return False


class PhpSecurityChecker(BaseSecurityChecker):
    """Extract PHP CWE dangerous sinks (SQLi, XSS, LFI, RCE, Deserialization, Type Juggling) and HTTP/WP endpoints."""

    def find_dangerous_sinks(self, unit: ParsedUnit) -> list[SecuritySinkLocation]:
        """Scan a parsed PHP unit for 10 categories of CWE-classified dangerous code sinks."""
        sinks: list[SecuritySinkLocation] = []
        self._scan_function_calls(unit, sinks)
        self._scan_member_and_scoped_calls(unit, sinks)
        self._scan_xss_and_shell_backticks(unit, sinks)
        self._scan_dynamic_includes(unit, sinks)
        self._scan_loose_auth_comparisons_and_headers(unit, sinks)
        return sinks

    def _classify_injection_or_deser_call(
        self,
        unit: ParsedUnit,
        callee: str,
        args: list[str],
        full_txt: str,
        line: int,
        sym: str | None,
    ) -> SecuritySinkLocation | None:
        """Check a PHP function call for SQLi, Command Injection, Code Exec, Path Traversal, or Deserialization."""
        result: SecuritySinkLocation | None = None
        if callee in {"mysqli_query", "mysql_query", "pg_query"}:
            sql_arg = args[1] if callee == "mysqli_query" and len(args) >= 2 else (args[0] if args else "")
            if callee == "mysql_query" or _has_dynamic_sql_expr(sql_arg):
                result = SecuritySinkLocation(
                    category="sql_injection",
                    cwe_id="CWE-89",
                    severity="high",
                    file=unit.rel_path,
                    line=line,
                    symbol=sym,
                    detail=f"Unparameterized SQL execution via '{callee}({sql_arg[:50]})'",
                )
        elif callee in _CMD_EXEC_FUNCS:
            result = SecuritySinkLocation(
                category="command_injection",
                cwe_id="CWE-78",
                severity="high",
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail=f"OS shell command execution via '{callee}(...)'",
            )
        elif _is_dynamic_code_eval_call(callee, args):
            result = SecuritySinkLocation(
                category="code_execution",
                cwe_id="CWE-94",
                severity="high",
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail=f"Dynamic PHP code evaluation via '{callee}(...)'",
            )
        elif callee in _FILE_SINK_FUNCS and any(sg in full_txt for sg in USER_INPUT_SUPERGLOBALS):
            result = SecuritySinkLocation(
                category="file_inclusion_or_traversal",
                cwe_id="CWE-22",
                severity="high",
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail=f"Unvalidated superglobal passed directly to filesystem sink '{callee}(...)'",
            )
        elif callee == "unserialize":
            has_safe_opts = len(args) >= 2 and "allowed_classes" in args[1] and "false" in args[1].lower()
            if not has_safe_opts:
                result = SecuritySinkLocation(
                    category="unsafe_deserialization",
                    cwe_id="CWE-502",
                    severity="high",
                    file=unit.rel_path,
                    line=line,
                    symbol=sym,
                    detail="Unsafe 'unserialize(...)' without ['allowed_classes' => false] enables Object Injection",
                )
        return result

    def _classify_crypto_tls_or_scope_call(
        self,
        unit: ParsedUnit,
        fcall: SgNode,
        callee: str,
        args: list[str],
        full_txt: str,
        line: int,
        sym: str | None,
    ) -> SecuritySinkLocation | None:
        """Check a PHP function call for weak crypto/PRNG, disabled TLS, variable pollution, or debug exposure."""
        result: SecuritySinkLocation | None = None
        if callee in _WEAK_HASH_FUNCS:
            sev: SinkSeverity = "high" if _AUTH_TOKEN_VAR_RE.search(full_txt) else "medium"
            result = SecuritySinkLocation(
                category="weak_cryptography",
                cwe_id="CWE-327",
                severity=sev,
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail=f"Broken digest '{callee}(...)' — use 'password_hash()' for passwords or SHA-256/HMAC",
            )
        elif callee in _WEAK_RNG_FUNCS:
            parent_node = fcall.parent()
            ctx_txt = parent_node.text() if parent_node is not None else full_txt
            if _AUTH_TOKEN_VAR_RE.search(ctx_txt):
                result = SecuritySinkLocation(
                    category="weak_cryptography",
                    cwe_id="CWE-338",
                    severity="high",
                    file=unit.rel_path,
                    line=line,
                    symbol=sym,
                    detail=f"Predictable PRNG '{callee}()' in security context — use 'random_bytes()'/'random_int()'",
                )
        elif callee == "curl_setopt" and len(args) >= 3:
            opt, val = args[1], args[2].lower()
            if opt in {"CURLOPT_SSL_VERIFYPEER", "CURLOPT_SSL_VERIFYHOST"} and val in {"false", "0"}:
                result = SecuritySinkLocation(
                    category="insecure_transport",
                    cwe_id="CWE-295",
                    severity="high",
                    file=unit.rel_path,
                    line=line,
                    symbol=sym,
                    detail=f"TLS certificate verification disabled via '{opt} => {args[2]}'",
                )
        elif callee == "extract" and (
            any(sg in full_txt for sg in USER_INPUT_SUPERGLOBALS) or "EXTR_SKIP" not in full_txt
        ):
            result = SecuritySinkLocation(
                category="loose_comparison_or_auth",
                cwe_id="CWE-621",
                severity="high",
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail="Variable table pollution via 'extract(...)' allows overwriting local security state",
            )
        elif callee == "parse_str" and len(args) == 1:
            result = SecuritySinkLocation(
                category="loose_comparison_or_auth",
                cwe_id="CWE-621",
                severity="high",
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail="Single-argument 'parse_str(...)' extracts query parameters into local scope",
            )
        else:
            result = self._classify_debug_exposure_call(unit, callee, args, line, sym)
        return result

    @staticmethod
    def _classify_debug_exposure_call(
        unit: ParsedUnit,
        callee: str,
        args: list[str],
        line: int,
        sym: str | None,
    ) -> SecuritySinkLocation | None:
        """Check `phpinfo()` and `ini_set('display_errors', '1')` debug exposure sinks (`CWE-489`)."""
        if callee == "phpinfo":
            return SecuritySinkLocation(
                category="permissive_cors_or_debug",
                cwe_id="CWE-489",
                severity="medium",
                file=unit.rel_path,
                line=line,
                symbol=sym,
                detail="'phpinfo()' exposes runtime environment variables, extensions, and paths",
            )
        if callee == "ini_set" and len(args) >= 2 and "display_errors" in args[0].lower():
            if strip_php_quotes(args[1]).lower() in {"1", "on", "true"}:
                return SecuritySinkLocation(
                    category="permissive_cors_or_debug",
                    cwe_id="CWE-489",
                    severity="medium",
                    file=unit.rel_path,
                    line=line,
                    symbol=sym,
                    detail="'ini_set(\"display_errors\", ...)' leaks stack traces and paths to clients",
                )
        return None

    def _scan_function_calls(self, unit: ParsedUnit, sinks: list[SecuritySinkLocation]) -> None:
        """Inspect PHP `function_call_expression` nodes for SQLi, RCE, LFI, deserialization, and crypto sinks."""
        for fcall in unit.root.find_all(kind="function_call_expression"):
            children = fcall.children()
            callee = children[0].text().strip().lstrip("\\").lower() if children else ""
            if not callee:
                continue
            line = fcall.range().start.line + 1
            sym = enclosing_callable_symbol(fcall)
            args = _extract_call_args_text(fcall)
            full_txt = fcall.text()
            sink = self._classify_injection_or_deser_call(unit, callee, args, full_txt, line, sym)
            if sink is None:
                sink = self._classify_crypto_tls_or_scope_call(unit, fcall, callee, args, full_txt, line, sym)
            if sink is not None:
                sinks.append(sink)

    def _scan_member_and_scoped_calls(self, unit: ParsedUnit, sinks: list[SecuritySinkLocation]) -> None:
        """Inspect `$pdo->query(...)`, `$wpdb->get_results(...)`, `DB::raw(...)`, and `Http::withoutVerifying()`."""
        for mcall in unit.root.find_all(kind="member_call_expression"):
            children = mcall.children()
            mname_node = next((c for c in children if c.kind() == "name"), None)
            mname = mname_node.text().strip() if mname_node is not None else ""
            line = mcall.range().start.line + 1
            sym = enclosing_callable_symbol(mcall)
            args = _extract_call_args_text(mcall)

            if mname in _SQL_MEMBER_METHODS and args and _has_dynamic_sql_expr(args[0]):
                recv = children[0].text().strip() if children else ""
                sinks.append(
                    SecuritySinkLocation(
                        category="sql_injection",
                        cwe_id="CWE-89",
                        severity="high",
                        file=unit.rel_path,
                        line=line,
                        symbol=sym,
                        detail=f"Unparameterized SQL in '{recv}->{mname}({args[0][:45]})' — use prepared placeholders",
                    )
                )
            elif mname == "withoutVerifying":
                sinks.append(
                    SecuritySinkLocation(
                        category="insecure_transport",
                        cwe_id="CWE-295",
                        severity="high",
                        file=unit.rel_path,
                        line=line,
                        symbol=sym,
                        detail="TLS verification disabled via '->withoutVerifying()'",
                    )
                )

        for scall in unit.root.find_all(kind="scoped_call_expression"):
            stxt = scall.text().lstrip("\\")
            line = scall.range().start.line + 1
            sym = enclosing_callable_symbol(scall)
            args = _extract_call_args_text(scall)
            if stxt.startswith(("DB::raw(", "DB::select(", "DB::statement(", "DB::delete(", "DB::update(")):
                if args and len(args) == 1 and _has_dynamic_sql_expr(args[0]):
                    sinks.append(
                        SecuritySinkLocation(
                            category="sql_injection",
                            cwe_id="CWE-89",
                            severity="high",
                            file=unit.rel_path,
                            line=line,
                            symbol=sym,
                            detail=f"Interpolated/concatenated SQL in '{stxt[:50]}' without bindings",
                        )
                    )
            elif "Http::withoutVerifying" in stxt:
                sinks.append(
                    SecuritySinkLocation(
                        category="insecure_transport",
                        cwe_id="CWE-295",
                        severity="high",
                        file=unit.rel_path,
                        line=line,
                        symbol=sym,
                        detail="TLS verification disabled via 'Http::withoutVerifying()'",
                    )
                )

    def _scan_xss_and_shell_backticks(self, unit: ParsedUnit, sinks: list[SecuritySinkLocation]) -> None:
        """Detect unescaped `echo`/`print`/`<?=` XSS (`CWE-79`), Blade `{!! !!}`, and backtick RCE (`CWE-78`)."""
        for out_kind in ("echo_statement", "print_intrinsic"):
            for enode in unit.root.find_all(kind=out_kind):
                etxt = enode.text()
                if any(src in etxt for src in _XSS_SOURCES) and not any(esc in etxt for esc in _XSS_ESCAPERS):
                    sinks.append(
                        SecuritySinkLocation(
                            category="xss",
                            cwe_id="CWE-79",
                            severity="high",
                            file=unit.rel_path,
                            line=enode.range().start.line + 1,
                            symbol=enclosing_callable_symbol(enode),
                            detail=f"Unescaped request input rendered directly via '{etxt.strip()[:55]}'",
                        )
                    )

        for idx, raw_line in enumerate(unit.source.splitlines(), start=1):
            for blade_m in _BLADE_RAW_ECHO_RE.finditer(raw_line):
                expr = blade_m.group(1).strip()
                sinks.append(
                    SecuritySinkLocation(
                        category="xss",
                        cwe_id="CWE-79",
                        severity="high",
                        file=unit.rel_path,
                        line=idx,
                        symbol="blade_raw_echo",
                        detail=f"Unescaped Blade '{{!! {expr[:40]} !!}}' raw HTML output",
                    )
                )

        for btick in unit.root.find_all(kind="shell_command_expression"):
            sinks.append(
                SecuritySinkLocation(
                    category="command_injection",
                    cwe_id="CWE-78",
                    severity="high",
                    file=unit.rel_path,
                    line=btick.range().start.line + 1,
                    symbol=enclosing_callable_symbol(btick),
                    detail=f"Backtick shell command execution {btick.text().strip()[:45]}",
                )
            )

    def _scan_dynamic_includes(self, unit: ParsedUnit, sinks: list[SecuritySinkLocation]) -> None:
        """Detect dynamic variable/superglobal `include`/`require` (`CWE-98` LFI/RFI)."""
        for inc_kind in INCLUDE_EXPR_KINDS:
            for inc_node in unit.root.find_all(kind=inc_kind):
                txt = inc_node.text().strip()
                if "$" in txt:
                    sinks.append(
                        SecuritySinkLocation(
                            category="file_inclusion_or_traversal",
                            cwe_id="CWE-98",
                            severity="high",
                            file=unit.rel_path,
                            line=inc_node.range().start.line + 1,
                            symbol=enclosing_callable_symbol(inc_node),
                            detail=f"Dynamic PHP file inclusion '{txt[:55]}' risks Local/Remote File Inclusion",
                        )
                    )

    def _scan_loose_auth_comparisons_and_headers(
        self,
        unit: ParsedUnit,
        sinks: list[SecuritySinkLocation],
    ) -> None:
        """Detect PHP `==`/`!=` type-juggling on auth/hash variables (`CWE-697`), TLS off, and wildcard CORS."""
        for bin_node in unit.root.find_all(kind="binary_expression"):
            children = bin_node.children()
            if len(children) != 3:
                continue
            op = children[1].text().strip()
            if op not in {"==", "!=", "<>"}:
                continue
            full_cmp = bin_node.text()
            if re.search(r"\bnull\b", full_cmp, flags=re.IGNORECASE):
                continue
            if _AUTH_TOKEN_VAR_RE.search(full_cmp):
                cmp_snip = full_cmp.strip()[:45]
                sinks.append(
                    SecuritySinkLocation(
                        category="loose_comparison_or_auth",
                        cwe_id="CWE-697",
                        severity="high",
                        file=unit.rel_path,
                        line=bin_node.range().start.line + 1,
                        symbol=enclosing_callable_symbol(bin_node),
                        detail=(
                            f"Loose '{op}' comparison on credential/hash '{cmp_snip}' "
                            "enables PHP type-juggling bypass — use 'hash_equals()' or '==='"
                        ),
                    )
                )

        for idx, raw_line in enumerate(unit.source.splitlines(), start=1):
            compact = re.sub(r"\s+", "", raw_line.lower())
            if "'verify'=>false" in compact or '"verify"=>false' in compact:
                sinks.append(
                    SecuritySinkLocation(
                        category="insecure_transport",
                        cwe_id="CWE-295",
                        severity="high",
                        file=unit.rel_path,
                        line=idx,
                        symbol=None,
                        detail="HTTP client option 'verify => false' disables TLS certificate validation",
                    )
                )
            if "access-control-allow-origin:*" in compact:
                sinks.append(
                    SecuritySinkLocation(
                        category="permissive_cors_or_debug",
                        cwe_id="CWE-942",
                        severity="medium",
                        file=unit.rel_path,
                        line=idx,
                        symbol=None,
                        detail="Wildcard CORS header 'Access-Control-Allow-Origin: *'",
                    )
                )

    def find_api_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract API & HTTP attack surface across Laravel, Symfony Attributes, WordPress, and Raw PHP scripts."""
        endpoints: list[ApiEndpointFact] = []
        endpoints.extend(self._extract_laravel_routes(unit))
        endpoints.extend(self._extract_symfony_attribute_routes(unit))
        endpoints.extend(self._extract_wordpress_endpoints(unit))
        if not endpoints:
            endpoints.extend(self._extract_raw_php_entry_endpoint(unit))
        return endpoints

    def _extract_laravel_routes(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract `Route::get/post/put/patch/delete/any` endpoints and `middleware(...)` hints."""
        found: list[ApiEndpointFact] = []
        prefix_match = re.search(
            r"Route::[^\n]*prefix\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*(?:->[^\n]*)?group\s*\(",
            unit.source,
        )
        if "routes/api.php" in unit.rel_path and prefix_match:
            file_prefix = f"/api/{prefix_match.group(1).strip('/')}"
        elif unit.rel_path.endswith("routes/api.php"):
            file_prefix = "/api"
        else:
            file_prefix = prefix_match.group(1) if prefix_match else ""

        brace_depth = 0
        auth_group_depths: list[int] = []
        for idx, raw_line in enumerate(unit.source.splitlines(), start=1):
            if re.search(
                r"Route::(?:[^\n]*middleware\s*\([^)]*(?:auth|sanctum|can:)[^\n]*->group\s*\("
                r"|group\s*\([^\n]*middleware[^\n]*(?:auth|sanctum|can:))",
                raw_line,
            ):
                auth_group_depths.append(brace_depth + raw_line.count("{") - raw_line.count("}"))

            m = _LARAVEL_ROUTE_CALL_RE.search(raw_line)
            if m:
                verb = m.group("verb").upper()
                raw_path = m.group("path")
                full_path = self.join_route_paths(file_prefix, raw_path)
                handler_raw = m.group("handler").strip()
                chain_ctx = f"{m.group('pre') or ''} {m.group('post') or ''}"
                mw_tokens = self._parse_laravel_middleware_tokens(chain_ctx)
                auth_mechs = [
                    tok
                    for tok in mw_tokens
                    if any(
                        k in tok.lower()
                        for k in ("auth", "sanctum", "can:", "verified", "role", "permission", "admin")
                    )
                ]
                if not auth_mechs and auth_group_depths:
                    auth_mechs = ["group_middleware:auth"]

                found.append(
                    ApiEndpointFact(
                        http_method=verb,
                        path=full_path,
                        handler=handler_raw[:60],
                        file=unit.rel_path,
                        line=idx,
                        has_auth_hint=bool(auth_mechs),
                        auth_mechanisms=auth_mechs,
                    )
                )

            brace_depth += raw_line.count("{") - raw_line.count("}")
            auth_group_depths = [d for d in auth_group_depths if brace_depth >= d > 0]
        return found

    @staticmethod
    def _parse_laravel_middleware_tokens(chain_ctx: str) -> list[str]:
        """Extract `middleware:<name>` tokens from an inline Laravel `Route` chain."""
        mw_tokens: list[str] = []
        for mw_m in _LARAVEL_MIDDLEWARE_RE.finditer(chain_ctx):
            raw_mw = mw_m.group(1) or mw_m.group(2) or ""
            for tok in raw_mw.split(","):
                cleaned = strip_php_quotes(tok).strip()
                if cleaned:
                    mw_tokens.append(f"middleware:{cleaned}")
        return mw_tokens

    @staticmethod
    def _collect_route_attributes(node: SgNode) -> tuple[list[re.Match[str]], bool]:
        """Return (`#[Route(...)]` regex matches, has_auth_attribute) on a PHP class or method node."""
        matches: list[re.Match[str]] = []
        has_auth = False
        for child in node.children():
            if child.kind() == "attribute_list":
                atxt = child.text()
                matches.extend(_SYMFONY_ATTR_ROUTE_RE.finditer(atxt))
                if "IsGranted" in atxt or "Security" in atxt:
                    has_auth = True
        return matches, has_auth

    def _extract_symfony_attribute_routes(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract PHP 8 `#[Route('/path', methods: [...])]` and `#[IsGranted(...)]` controller routes."""
        found: list[ApiEndpointFact] = []
        for type_name, tnode in iter_php_types(unit.root):
            cls_routes, cls_has_auth = self._collect_route_attributes(tnode)
            cls_prefix = cls_routes[0].group("path") if cls_routes else ""

            for mnode in tnode.find_all(kind="method_declaration"):
                mname = extract_node_name(mnode)
                route_matches, m_has_auth = self._collect_route_attributes(mnode)
                m_auth = ["attribute:IsGranted"] if (cls_has_auth or m_has_auth) else []

                for rm in route_matches:
                    rest = rm.group("rest") or ""
                    methods_m = re.search(r"methods\s*:\s*\[([^\]]+)\]", rest)
                    raw_verbs = methods_m.group(1).split(",") if methods_m else []
                    methods = [strip_php_quotes(tok).upper() for tok in raw_verbs if strip_php_quotes(tok)] or ["ANY"]
                    full_path = self.join_route_paths(cls_prefix, rm.group("path"))
                    for verb in methods:
                        found.append(
                            ApiEndpointFact(
                                http_method=verb,
                                path=full_path,
                                handler=f"{type_name}::{mname}",
                                file=unit.rel_path,
                                line=mnode.range().start.line + 1,
                                has_auth_hint=bool(m_auth),
                                auth_mechanisms=m_auth,
                            )
                        )
        return found

    @staticmethod
    def _normalize_wp_rest_verb(args_txt: str) -> str:
        """Extract and normalize WordPress `register_rest_route` HTTP method."""
        method_m = re.search(r"['\"]methods['\"]\s*=>\s*([^,\n\]]+)", args_txt)
        raw_method = strip_php_quotes(method_m.group(1).strip()) if method_m else "GET"
        verb = raw_method.upper() if raw_method.isalpha() else "ANY"
        for marker, mapped in (
            ("CREATABLE", "POST"),
            ("EDITABLE", "ANY"),
            ("ALLMETHODS", "ANY"),
            ("DELETABLE", "DELETE"),
            ("READABLE", "GET"),
        ):
            if marker in raw_method:
                verb = mapped
                break
        return verb

    def _extract_wordpress_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract WordPress `register_rest_route(...)` and `add_action('wp_ajax_*', ...)` attack surface."""
        found: list[ApiEndpointFact] = []
        src = unit.source

        for rm in _WP_REST_ROUTE_RE.finditer(src):
            line = src.count("\n", 0, rm.start()) + 1
            ns = rm.group("ns").strip("/")
            route = rm.group("route").strip("/")
            args_txt = rm.group("args")
            path = f"/wp-json/{ns}/{route}" if route else f"/wp-json/{ns}"
            verb = self._normalize_wp_rest_verb(args_txt)
            cb_m = re.search(r"['\"]callback['\"]\s*=>\s*([^,\n\]]+)", args_txt)
            handler = strip_php_quotes(cb_m.group(1).strip())[:55] if cb_m else "rest_callback"
            perm_m = re.search(r"['\"]permission_callback['\"]\s*=>\s*([^,\n\]]+)", args_txt)
            perm_val = strip_php_quotes(perm_m.group(1).strip()) if perm_m else ""
            is_public_open = (not perm_val) or ("__return_true" in perm_val)
            auth_mechs = [] if is_public_open else [f"permission_callback:{perm_val[:35]}"]

            found.append(
                ApiEndpointFact(
                    http_method=verb,
                    path=path,
                    handler=handler,
                    file=unit.rel_path,
                    line=line,
                    has_auth_hint=not is_public_open,
                    auth_mechanisms=auth_mechs,
                )
            )

        nopriv_actions: set[str] = set()
        ajax_entries: list[tuple[bool, str, str, int]] = []
        for am in _WP_AJAX_HOOK_RE.finditer(src):
            is_nopriv = bool(am.group("nopriv"))
            act = am.group("act")
            cb = strip_php_quotes(am.group("cb").strip())[:55]
            line = src.count("\n", 0, am.start()) + 1
            if is_nopriv:
                nopriv_actions.add(act)
            ajax_entries.append((is_nopriv, act, cb, line))

        for is_nopriv, act, cb, line in ajax_entries:
            if not is_nopriv and act in nopriv_actions:
                continue
            mechs = [] if is_nopriv else (
                ["wp_ajax_session", "current_user_can"] if "current_user_can" in src else ["wp_ajax_session"]
            )
            found.append(
                ApiEndpointFact(
                    http_method="POST",
                    path=f"/wp-admin/admin-ajax.php?action={act}",
                    handler=cb,
                    file=unit.rel_path,
                    line=line,
                    has_auth_hint=not is_nopriv,
                    auth_mechanisms=mechs,
                )
            )
        return found

    @staticmethod
    def _extract_raw_php_entry_endpoint(unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Treat standalone procedural `.php` web scripts reading `$_GET`/`$_POST`/`$_REQUEST` as HTTP endpoints."""
        if extract_php_namespace(unit.root) or iter_php_types(unit.root):
            return []
        rel_low = unit.rel_path.lower()
        if any(seg in rel_low for seg in ("includes/", "inc/", "config/", "lib/", "vendor/")):
            return []

        has_get = "$_GET" in unit.source
        has_post = "$_POST" in unit.source or "$_FILES" in unit.source or "php://input" in unit.source
        has_req = "$_REQUEST" in unit.source
        if not (has_get or has_post or has_req):
            return []

        if has_req or (has_get and has_post):
            verb = "ANY"
        elif has_post:
            verb = "POST"
        else:
            verb = "GET"

        web_path = unit.rel_path.removeprefix("public/")
        norm_path = web_path if web_path.startswith("/") else f"/{web_path}"
        head_lines = "\n".join(unit.source.splitlines()[:35])
        has_session_guard = bool(
            re.search(r"\$_SESSION\s*\[['\"](?:user|admin|auth|logged_in|uid|role)", head_lines, flags=re.IGNORECASE)
        )
        mechs = ["session_guard"] if has_session_guard else []
        return [
            ApiEndpointFact(
                http_method=verb,
                path=norm_path,
                handler=unit.file_path.name,
                file=unit.rel_path,
                line=1,
                has_auth_hint=has_session_guard,
                auth_mechanisms=mechs,
            )
        ]
