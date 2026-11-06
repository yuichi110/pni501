# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Laravel and WordPress framework-specific architecture, security, and modernization checkers."""

from __future__ import annotations

import re
from typing import ClassVar, Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseFrameworkChecker
from pni._actions.ast_analyze.models import CodeLocation, FrameworkCheckResult, ParsedUnit
from pni._actions.ast_analyze.php._helpers import (
    USER_INPUT_SUPERGLOBALS,
    enclosing_callable_symbol,
    extract_node_name,
    iter_php_callables,
    iter_php_types,
)

_WP_NONCE_FUNCS: Final[tuple[str, ...]] = ("wp_verify_nonce", "check_admin_referer", "check_ajax_referer")
_WP_SANITIZE_FUNCS: Final[tuple[str, ...]] = (
    "sanitize_text_field",
    "sanitize_email",
    "sanitize_key",
    "sanitize_file_name",
    "sanitize_textarea_field",
    "esc_url_raw",
    "absint",
    "intval",
    "wp_kses",
)
_INLINE_SCRIPT_TAG_RE: Final[re.Pattern[str]] = re.compile(r"(?i)<script\b[^>]*\bsrc\s*=")


class LaravelFrameworkChecker(BaseFrameworkChecker):
    """Inspect Laravel projects for Eloquent `$guarded = []`, `env()` misuse, and fat controllers."""

    framework_id: ClassVar[str] = "laravel"

    def _inspect_controller_type(
        self,
        unit: ParsedUnit,
        type_name: str,
        tnode: SgNode,
        issues: list[CodeLocation],
    ) -> None:
        """Flag `DB::table(...)` and `$request->all()` mass assignment inside Laravel controllers."""
        for scall in tnode.find_all(kind="scoped_call_expression"):
            if scall.text().startswith(("DB::table", "\\DB::table")):
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=scall.range().start.line + 1,
                        symbol=enclosing_callable_symbol(scall) or type_name,
                        detail="Controller queries 'DB::table(...)' directly — extract to Service or Repository",
                    )
                )
        for mcall in tnode.find_all(kind="member_call_expression"):
            mtxt = re.sub(r"\s+", "", mcall.text())
            if "->create($request->all())" in mtxt or "->update($request->all())" in mtxt:
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=mcall.range().start.line + 1,
                        symbol=enclosing_callable_symbol(mcall) or type_name,
                        detail="Passing '$request->all()' to Eloquent create/update — use validated FormRequest data",
                    )
                )

    def _inspect_eloquent_and_accessors(
        self,
        unit: ParsedUnit,
        type_name: str,
        tnode: SgNode,
        issues: list[CodeLocation],
        hints: list[CodeLocation],
    ) -> None:
        """Inspect a class for `$guarded = []` and legacy `get*Attribute` accessors."""
        for prop in tnode.find_all(kind="property_declaration"):
            ptxt = re.sub(r"\s+", "", prop.text())
            if "$guarded=[]" in ptxt or "$guarded=array()" in ptxt:
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=prop.range().start.line + 1,
                        symbol=f"{type_name}::$guarded",
                        detail=(
                            "Unrestricted Eloquent '$guarded = []' enables Mass Assignment — "
                            "define explicit '$fillable'"
                        ),
                    )
                )
        for mnode in tnode.find_all(kind="method_declaration"):
            mname = extract_node_name(mnode)
            if mname.startswith("get") and mname.endswith("Attribute") and len(mname) > 12:
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=mnode.range().start.line + 1,
                        symbol=f"{type_name}::{mname}",
                        detail=(
                            "Legacy Laravel 8 accessor 'get*Attribute' — "
                            "consider Illuminate\\Database\\Eloquent\\Casts\\Attribute"
                        ),
                    )
                )

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Inspect a single PHP unit for Laravel security and architectural anti-patterns."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []

        for type_name, tnode in iter_php_types(unit.root):
            base_clause = tnode.find(kind="base_clause")
            base_txt = base_clause.text() if base_clause is not None else ""
            self._inspect_eloquent_and_accessors(unit, type_name, tnode, issues, hints)
            if "Controller" in type_name or "Controller" in base_txt:
                self._inspect_controller_type(unit, type_name, tnode, issues)

        if not unit.rel_path.lower().startswith("config/"):
            for fcall in unit.root.find_all(kind="function_call_expression"):
                children = fcall.children()
                if children and children[0].text().strip() == "env":
                    issues.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=fcall.range().start.line + 1,
                            symbol=enclosing_callable_symbol(fcall) or "env",
                            detail=(
                                "Direct 'env()' call outside config/*.php returns null when "
                                "'php artisan config:cache' is active — use 'config()'"
                            ),
                        )
                    )

        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)


class WordPressFrameworkChecker(BaseFrameworkChecker):
    """Inspect WordPress plugins/themes for ABSPATH guard, Nonce/Capability checks, and sanitization."""

    framework_id: ClassVar[str] = "wordpress"

    def _check_abspath_guard(self, unit: ParsedUnit, issues: list[CodeLocation]) -> None:
        """Flag WordPress plugin/theme PHP files missing top-of-file ABSPATH direct-access guard."""
        fname_low = unit.file_path.name.lower()
        if fname_low in {"wp-config.php", "wp-config-sample.php"} or "WP_UNINSTALL_PLUGIN" in unit.source:
            return
        head_text = "\n".join(unit.source.splitlines()[:35])
        if "ABSPATH" not in head_text:
            issues.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=1,
                    symbol=unit.file_path.name,
                    detail="Missing 'if (!defined(\\'ABSPATH\\')) { exit; }' direct-access guard at top of file",
                )
            )

    def _check_post_handlers(self, unit: ParsedUnit, issues: list[CodeLocation]) -> None:
        """Flag WordPress callables reading `$_POST`/`$_FILES` without Nonce or `current_user_can`."""
        for symbol, cnode in iter_php_callables(unit.root):
            body_txt = cnode.text()
            if "$_POST" not in body_txt and "$_FILES" not in body_txt:
                continue
            line = cnode.range().start.line + 1
            if not any(nf in body_txt for nf in _WP_NONCE_FUNCS):
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=symbol,
                        detail=(
                            "WordPress handler reads '$_POST'/'$_FILES' without 'wp_verify_nonce()' "
                            "or 'check_admin_referer()' (CSRF risk)"
                        ),
                    )
                )
            if "current_user_can" not in body_txt:
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line,
                        symbol=symbol,
                        detail="WordPress handler processes POST mutation without 'current_user_can(...)' check",
                    )
                )

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Inspect a WordPress PHP file for plugin security and WPCS violations."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []

        self._check_abspath_guard(unit, issues)
        self._check_post_handlers(unit, issues)

        for assign in unit.root.find_all(kind="assignment_expression"):
            children = assign.children()
            if len(children) < 3:
                continue
            rhs_txt = children[-1].text()
            if any(sg in rhs_txt for sg in USER_INPUT_SUPERGLOBALS) and not any(
                sf in rhs_txt for sf in _WP_SANITIZE_FUNCS
            ):
                lhs_txt = children[0].text().strip()
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=assign.range().start.line + 1,
                        symbol=enclosing_callable_symbol(assign) or lhs_txt,
                        detail=(
                            f"Unsanitized superglobal assigned to '{lhs_txt}' — "
                            "wrap with 'wp_unslash()' + 'sanitize_text_field()'/'absint()'"
                        ),
                    )
                )

        for idx, raw_line in enumerate(unit.source.splitlines(), start=1):
            if _INLINE_SCRIPT_TAG_RE.search(raw_line) and "wp_enqueue_script" not in unit.source:
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=idx,
                        symbol="wp_enqueue_script",
                        detail="Hardcoded '<script src=...>' tag — register assets via 'wp_enqueue_script()'",
                    )
                )

        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)
