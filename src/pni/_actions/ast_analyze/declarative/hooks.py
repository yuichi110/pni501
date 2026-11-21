# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Specialized CST audit hooks for SFC, legacy, IaC, schema, and markup languages."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze._cst import CstNode, parse_cst
from pni._actions.ast_analyze.base.operational import BaseOperationalChecker
from pni._actions.ast_analyze.declarative.profile import CustomHookResult
from pni._actions.ast_analyze.models import (
    MAX_BRANCH_COUNT,
    MAX_COGNITIVE_COMPLEXITY,
    MAX_FUNCTION_LINES,
    CodeLocation,
    ParsedUnit,
    SecuritySinkLocation,
)

_SCRIPT_BRANCH_KINDS: Final[frozenset[str]] = frozenset(
    {
        "if_statement",
        "for_statement",
        "for_in_statement",
        "while_statement",
        "do_statement",
        "switch_case",
        "catch_clause",
        "ternary_expression",
    }
)
_SCRIPT_CALLABLE_KINDS: Final[tuple[str, ...]] = (
    "function_declaration",
    "method_definition",
    "arrow_function",
    "function_expression",
)
_CURL_PIPE_SH_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh|dash|ash)\b",
    re.IGNORECASE,
)
_SECRET_KV_RE: Final[re.Pattern[str]] = re.compile(
    r"""(?i)\b([A-Za-z_][A-Za-z0-9_]*(?:password|passwd|secret|api_?key|token|private_?key)[A-Za-z0-9_]*)\s*(?:=|:)\s*['"]?([^\s'"#;,]+)['"]?"""
)
_COBOL_COPY_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\bCOPY\s+([A-Za-z0-9_-]+)")
_COBOL_GOTO_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\bGO\s+TO\b")
_COBOL_ALTER_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\bALTER\s+[A-Za-z0-9_-]+\s+TO\s+PROCEED")
_COBOL_EXEC_SQL_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\bEXEC\s+SQL\b")
_PERL_STRICT_RE: Final[re.Pattern[str]] = re.compile(
    r"(?m)^\s*use\s+(?:strict|v5\.(?:1[2-9]|[2-9]\d)|5\.0(?:1[2-9]|[2-9]\d)|Moo|Moose|Mojolicious)\b"
)
_PERL_WARNINGS_RE: Final[re.Pattern[str]] = re.compile(
    r"(?m)^\s*use\s+(?:warnings|v5\.(?:3[5-9]|[4-9]\d)|Moo|Moose|Mojolicious)\b"
)
_PERL_TWO_ARG_OPEN_RE: Final[re.Pattern[str]] = re.compile(r"\bopen\s*\(\s*(?:my\s+)?\$\w+\s*,\s*[\"'][^\"']*\$")
_R_LIB_RE: Final[re.Pattern[str]] = re.compile(r"""\b(?:library|require)\s*\(\s*['"]?([A-Za-z0-9._]+)['"]?""")
_R_ATTACH_RE: Final[re.Pattern[str]] = re.compile(r"\battach\s*\(")
_R_EVAL_PARSE_RE: Final[re.Pattern[str]] = re.compile(r"\beval\s*\(\s*parse\s*\(")
_R_SYSTEM_RE: Final[re.Pattern[str]] = re.compile(r"\b(?:system|system2|shell)\s*\(")
_GH_USES_UNPINNED_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@(?!([0-9a-f]{40})$)([^\s]+)$"
)
_PROTO_PASCAL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Za-z0-9]*$")
_PROTO_SNAKE_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]*$")
_SQL_DROP_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\b(DROP\s+(?:TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b")
_SQL_SELECT_STAR_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\bSELECT\s+\*\s+FROM\b")
_SQL_DYNAMIC_EXEC_RE: Final[re.Pattern[str]] = re.compile(r"(?i)\b(?:EXECUTE\s+IMMEDIATE|EXEC\s*\(|sp_executesql)\b")


def cobol_source_preprocessor(source: str) -> str:
    """Normalize COBOL fixed-format sequence columns while keeping exact line alignment."""
    lines = source.splitlines()
    out: list[str] = []
    for line in lines:
        if len(line) >= 7 and line[:6].isdigit() and line[6] in {" ", "*", "/", "-"}:
            body = line[6:72] if len(line) > 72 else line[6:]
            out.append("      " + body)
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if source.endswith("\n") else "")


def _resolve_script_callable_name(fn: CstNode, ckind: str) -> str | None:
    """Resolve callable symbol name inside an embedded SFC <script> block."""
    name_node = fn.field("name")
    fn_name = name_node.text() if name_node is not None else "<anonymous>"
    if ckind != "arrow_function":
        return fn_name
    parent = fn.parent()
    if parent is None or parent.kind() != "variable_declarator":
        return None
    p_name = parent.field("name")
    return p_name.text() if p_name is not None else fn_name


def _scan_embedded_script_lines(
    script_text: str,
    line_offset: int,
    rel_path: str,
) -> tuple[list[SecuritySinkLocation], list[CodeLocation]]:
    """Scan embedded SFC <script> text lines for dynamic eval, innerHTML, and hardcoded secrets."""
    sinks: list[SecuritySinkLocation] = []
    secrets: list[CodeLocation] = []
    for idx, line in enumerate(script_text.splitlines(), start=1):
        abs_line = line_offset + idx
        if re.search(r"\beval\s*\(|\bnew\s+Function\s*\(", line):
            sinks.append(
                SecuritySinkLocation(
                    category="code_execution",
                    cwe_id="CWE-94",
                    severity="high",
                    file=rel_path,
                    line=abs_line,
                    symbol="eval",
                    detail="Dynamic JavaScript/TypeScript code execution inside SFC <script>",
                )
            )
        if re.search(r"\.innerHTML\s*=|document\.write\s*\(", line):
            sinks.append(
                SecuritySinkLocation(
                    category="xss",
                    cwe_id="CWE-79",
                    severity="high",
                    file=rel_path,
                    line=abs_line,
                    symbol="innerHTML",
                    detail="Unsanitized DOM HTML sink inside SFC <script>",
                )
            )
        for m in _SECRET_KV_RE.finditer(line):
            if BaseOperationalChecker.is_likely_secret_literal(m.group(1), m.group(2)):
                secrets.append(
                    CodeLocation(
                        file=rel_path,
                        line=abs_line,
                        symbol=m.group(1),
                        detail="Hardcoded credential/secret literal in SFC <script>",
                    )
                )
    return sinks, secrets


def _inspect_embedded_script_block(
    script_el: CstNode,
    unit: ParsedUnit,
) -> tuple[int, list[str], list[CodeLocation], list[SecuritySinkLocation], list[CodeLocation]]:
    """Parse an embedded <script> element in Vue/Svelte with TS/TSX CST and inspect functions & sinks."""
    raw_node = script_el.find(kind="raw_text")
    if raw_node is None or not raw_node.text().strip():
        return 0, [], [], [], []
    script_text = raw_node.text()
    start_tag = script_el.find(kind="start_tag")
    tag_text = start_tag.text().lower() if start_tag is not None else ""
    grammar = "typescript" if ('lang="ts"' in tag_text or "lang='ts'" in tag_text) else "tsx"
    line_offset = raw_node.range().start.line
    sub_root = parse_cst(script_text, grammar)

    fn_count = 0
    pub_callables: list[str] = []
    complex_fns: list[CodeLocation] = []
    for ckind in _SCRIPT_CALLABLE_KINDS:
        for fn in sub_root.find_all(kind=ckind):
            fn_name = _resolve_script_callable_name(fn, ckind)
            if fn_name is None:
                continue
            fn_count += 1
            if fn_name != "<anonymous>" and not fn_name.startswith("_"):
                pub_callables.append(fn_name)
            fn_lines = fn.range().end.line - fn.range().start.line + 1
            branches = sum(len(fn.find_all(kind=bk)) for bk in _SCRIPT_BRANCH_KINDS)
            if fn_lines > MAX_FUNCTION_LINES or branches > MAX_BRANCH_COUNT or branches * 2 > MAX_COGNITIVE_COMPLEXITY:
                complex_fns.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_offset + fn.range().start.line + 1,
                        symbol=fn_name,
                        detail=f"length={fn_lines} lines, branches={branches}",
                    )
                )

    sinks, secrets = _scan_embedded_script_lines(script_text, line_offset, unit.rel_path)
    return fn_count, pub_callables, complex_fns, sinks, secrets


def vue_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit Vue SFC <template> directives (v-html XSS) and delegate <script> blocks to TS/JS CST."""
    fn_total = 0
    pub_callables: list[str] = []
    complex_fns: list[CodeLocation] = []
    sinks: list[SecuritySinkLocation] = []
    secrets: list[CodeLocation] = []

    for script_el in unit.root.find_all(kind="script_element"):
        cnt, pubs, cplx, s_sinks, s_secrets = _inspect_embedded_script_block(script_el, unit)
        fn_total += cnt
        pub_callables.extend(pubs)
        complex_fns.extend(cplx)
        sinks.extend(s_sinks)
        secrets.extend(s_secrets)

    for directive in unit.root.find_all(kind="directive_attribute"):
        d_name = directive.find(kind="directive_name")
        if d_name is not None and d_name.text().strip() == "v-html":
            sinks.append(
                SecuritySinkLocation(
                    category="xss",
                    cwe_id="CWE-79",
                    severity="high",
                    file=unit.rel_path,
                    line=directive.range().start.line + 1,
                    symbol="v-html",
                    detail="Vue v-html renders unescaped HTML; sanitize or bind text interpolation instead",
                )
            )

    return CustomHookResult(
        extra_functions=fn_total,
        extra_public_callables=tuple(sorted(set(pub_callables))),
        complex_functions=tuple(complex_fns),
        dangerous_sinks=tuple(sinks),
        hardcoded_secrets=tuple(secrets),
    )


def svelte_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit Svelte {@html} XSS tags and delegate <script> blocks to TS/JS CST."""
    fn_total = 0
    pub_callables: list[str] = []
    complex_fns: list[CodeLocation] = []
    sinks: list[SecuritySinkLocation] = []
    secrets: list[CodeLocation] = []

    for script_el in unit.root.find_all(kind="script_element"):
        cnt, pubs, cplx, s_sinks, s_secrets = _inspect_embedded_script_block(script_el, unit)
        fn_total += cnt
        pub_callables.extend(pubs)
        complex_fns.extend(cplx)
        sinks.extend(s_sinks)
        secrets.extend(s_secrets)

    for html_tag in unit.root.find_all(kind="html_tag"):
        sinks.append(
            SecuritySinkLocation(
                category="xss",
                cwe_id="CWE-79",
                severity="high",
                file=unit.rel_path,
                line=html_tag.range().start.line + 1,
                symbol="{@html}",
                detail="Svelte {@html} injects raw HTML without escaping; sanitize untrusted input",
            )
        )

    return CustomHookResult(
        extra_functions=fn_total,
        extra_public_callables=tuple(sorted(set(pub_callables))),
        complex_functions=tuple(complex_fns),
        dangerous_sinks=tuple(sinks),
        hardcoded_secrets=tuple(secrets),
    )


def cobol_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Extract COBOL copybook COPY edges, GO TO / ALTER control-flow debt, and EXEC SQL sinks."""
    idioms: list[CodeLocation] = []
    sinks: list[SecuritySinkLocation] = []
    imports: list[str] = []

    for line_no, line in enumerate(unit.source.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("*"):
            continue
        if _COBOL_GOTO_RE.search(line):
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol="GO TO",
                    detail="Unstructured COBOL GO TO transfer impedes modular migration (prefer structured PERFORM)",
                )
            )
        if _COBOL_ALTER_RE.search(line):
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol="ALTER",
                    detail="Self-modifying COBOL ALTER statement creates high-risk control-flow coupling",
                )
            )
        for m in _COBOL_COPY_RE.finditer(line):
            imports.append(m.group(1).lower())
        if _COBOL_EXEC_SQL_RE.search(line) and "PREPARE" in line.upper():
            sinks.append(
                SecuritySinkLocation(
                    category="sql_injection",
                    cwe_id="CWE-89",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="EXEC SQL PREPARE",
                    detail="Dynamic embedded SQL PREPARE in COBOL requires strict host-variable parameterization",
                )
            )

    return CustomHookResult(
        bug_risk_idioms=tuple(idioms),
        dangerous_sinks=tuple(sinks),
        import_targets=tuple(sorted(set(imports))),
    )


def perl_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Detect missing `use strict`/`use warnings` and legacy 2-arg `open()` in Perl modules/scripts."""
    idioms: list[CodeLocation] = []
    sinks: list[SecuritySinkLocation] = []

    if not _PERL_STRICT_RE.search(unit.source):
        idioms.append(
            CodeLocation(
                file=unit.rel_path,
                line=1,
                symbol="use strict",
                detail="Missing 'use strict;' (or modern Perl >= v5.12 pragma) permits implicit global variables",
            )
        )
    if not _PERL_WARNINGS_RE.search(unit.source):
        idioms.append(
            CodeLocation(
                file=unit.rel_path,
                line=1,
                symbol="use warnings",
                detail="Missing 'use warnings;' suppresses runtime diagnostics for uninitialized values",
            )
        )
    for line_no, line in enumerate(unit.source.splitlines(), start=1):
        if _PERL_TWO_ARG_OPEN_RE.search(line):
            sinks.append(
                SecuritySinkLocation(
                    category="command_injection",
                    cwe_id="CWE-78",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="open",
                    detail="Legacy 2-argument Perl open() with interpolated variable enables shell command injection",
                )
            )

    return CustomHookResult(bug_risk_idioms=tuple(idioms), dangerous_sinks=tuple(sinks))


def r_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Extract R package dependencies, `attach()` global pollution, and dynamic eval/system sinks."""
    imports: list[str] = []
    globals_found: list[CodeLocation] = []
    sinks: list[SecuritySinkLocation] = []

    for line_no, line in enumerate(unit.source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for m in _R_LIB_RE.finditer(line):
            imports.append(m.group(1))
        if _R_ATTACH_RE.search(line):
            globals_found.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol="attach",
                    detail="R attach() mutates the global search path and causes fragile name shadowing",
                )
            )
        if _R_EVAL_PARSE_RE.search(line):
            sinks.append(
                SecuritySinkLocation(
                    category="code_execution",
                    cwe_id="CWE-94",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="eval(parse)",
                    detail="Dynamic R eval(parse(...)) executes arbitrary code strings",
                )
            )
        if _R_SYSTEM_RE.search(line):
            sinks.append(
                SecuritySinkLocation(
                    category="command_injection",
                    cwe_id="CWE-78",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="system",
                    detail="OS shell execution via R system()/system2()/shell()",
                )
            )

    return CustomHookResult(
        global_state_usages=tuple(globals_found),
        dangerous_sinks=tuple(sinks),
        import_targets=tuple(sorted(set(imports))),
    )


def _audit_dockerfile_stages(unit: ParsedUnit) -> list[CodeLocation]:
    """Check FROM base image pinning and final-stage non-root USER directives."""
    idioms: list[CodeLocation] = []
    from_nodes = unit.root.find_all(kind="from_instruction")
    for from_node in from_nodes:
        img_spec = from_node.find(kind="image_spec")
        spec_text = img_spec.text().strip() if img_spec is not None else from_node.text().strip()
        tag_node = from_node.find(kind="image_tag")
        tag_text = tag_node.text().strip() if tag_node is not None else ""
        untagged = bool(
            spec_text
            and spec_text.lower() != "scratch"
            and ":" not in spec_text
            and "@" not in spec_text
            and "$" not in spec_text
        )
        if tag_text == ":latest" or untagged:
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=from_node.range().start.line + 1,
                    symbol=spec_text or "FROM",
                    detail="Unpinned or mutable ':latest' base image in FROM instruction (AVD-DS-0001)",
                )
            )
    if not from_nodes:
        return idioms
    last_stage_start = from_nodes[-1].range().start.line
    final_users = [
        u for u in unit.root.find_all(kind="user_instruction") if u.range().start.line >= last_stage_start
    ]
    if not final_users:
        idioms.append(
            CodeLocation(
                file=unit.rel_path,
                line=from_nodes[-1].range().start.line + 1,
                symbol="USER",
                detail="Final Dockerfile stage has no non-root USER instruction (AVD-DS-0002)",
            )
        )
        return idioms
    last_user = final_users[-1].text().split()
    user_val = last_user[1].strip().lower() if len(last_user) > 1 else ""
    if user_val in {"root", "0", "0:0", "root:root"}:
        idioms.append(
            CodeLocation(
                file=unit.rel_path,
                line=final_users[-1].range().start.line + 1,
                symbol=user_val,
                detail="Final Dockerfile stage runs as root user (AVD-DS-0002)",
            )
        )
    return idioms


def dockerfile_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit Dockerfile CST instructions for `:latest`, root final stage, remote `ADD`, pipe-to-shell, and secrets."""
    idioms = _audit_dockerfile_stages(unit)
    sinks: list[SecuritySinkLocation] = []
    secrets: list[CodeLocation] = []

    for add_node in unit.root.find_all(kind="add_instruction"):
        if "http://" in add_node.text().lower() or "https://" in add_node.text().lower():
            sinks.append(
                SecuritySinkLocation(
                    category="insecure_transport",
                    cwe_id="CWE-829",
                    severity="medium",
                    file=unit.rel_path,
                    line=add_node.range().start.line + 1,
                    symbol="ADD",
                    detail="Dockerfile ADD fetches remote URL without checksum verification (use curl + sha256sum)",
                )
            )
    for run_node in unit.root.find_all(kind="run_instruction"):
        if _CURL_PIPE_SH_RE.search(run_node.text()):
            sinks.append(
                SecuritySinkLocation(
                    category="command_injection",
                    cwe_id="CWE-829",
                    severity="high",
                    file=unit.rel_path,
                    line=run_node.range().start.line + 1,
                    symbol="RUN",
                    detail="Pipe-to-shell remote download (curl/wget | sh) inside Dockerfile RUN",
                )
            )
    for kind in ("env_instruction", "arg_instruction"):
        for node in unit.root.find_all(kind=kind):
            for m in _SECRET_KV_RE.finditer(node.text()):
                if BaseOperationalChecker.is_likely_secret_literal(m.group(1), m.group(2)):
                    secrets.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=node.range().start.line + 1,
                            symbol=m.group(1),
                            detail=f"Hardcoded secret baked into image layer via {kind.split('_')[0].upper()}",
                        )
                    )

    return CustomHookResult(
        bug_risk_idioms=tuple(idioms),
        dangerous_sinks=tuple(sinks),
        hardcoded_secrets=tuple(secrets),
    )


def hcl_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit HCL / Terraform CST blocks for 0.0.0.0/0 ingress, wildcard IAM permissions, and disabled encryption."""
    sinks: list[SecuritySinkLocation] = []
    idioms: list[CodeLocation] = []
    secrets: list[CodeLocation] = []

    for attr in unit.root.find_all(kind="attribute"):
        txt = attr.text()
        low = txt.lower()
        line_no = attr.range().start.line + 1
        if "0.0.0.0/0" in txt and any(k in low for k in ("cidr", "source_ranges", "allowed_ip")):
            sinks.append(
                SecuritySinkLocation(
                    category="permissive_cors_or_debug",
                    cwe_id="CWE-284",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="0.0.0.0/0",
                    detail="Overly permissive wildcard ingress CIDR 0.0.0.0/0 in IaC configuration",
                )
            )
        if re.search(r'(?i)\b(?:encrypted|storage_encrypted|enable_https_traffic_only)\s*=\s*false\b', txt):
            sinks.append(
                SecuritySinkLocation(
                    category="insecure_transport",
                    cwe_id="CWE-311",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="encrypted=false",
                    detail="Encryption explicitly disabled in Terraform/HCL resource",
                )
            )
        if re.search(r'(?i)\b(?:publicly_accessible|public_access)\s*=\s*true\b', txt):
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol="publicly_accessible",
                    detail="Resource configured as publicly accessible in Terraform/HCL",
                )
            )
        if re.search(r'(?i)\b(?:actions|action|resources|resource)\s*=\s*\[\s*"\*"\s*\]', txt):
            sinks.append(
                SecuritySinkLocation(
                    category="loose_comparison_or_auth",
                    cwe_id="CWE-269",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="IAM:*",
                    detail="Wildcard IAM action or resource ('*') violates least-privilege principle",
                )
            )
        for m in _SECRET_KV_RE.finditer(txt):
            if BaseOperationalChecker.is_likely_secret_literal(m.group(1), m.group(2)):
                secrets.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=m.group(1),
                        detail="Hardcoded credential literal in Terraform/HCL attribute",
                    )
                )

    return CustomHookResult(
        bug_risk_idioms=tuple(idioms),
        dangerous_sinks=tuple(sinks),
        hardcoded_secrets=tuple(secrets),
    )


def _audit_protobuf_message(msg: CstNode, rel_path: str) -> list[CodeLocation]:
    """Validate naming conventions and field tag uniqueness inside one Protobuf message."""
    idioms: list[CodeLocation] = []
    mname = msg.find(kind="message_name")
    if mname is not None and not _PROTO_PASCAL_RE.match(mname.text().strip()):
        idioms.append(
            CodeLocation(
                file=rel_path,
                line=mname.range().start.line + 1,
                symbol=mname.text().strip(),
                detail="Protobuf message name should follow PascalCase convention",
            )
        )
    seen_tags: set[str] = set()
    for fld in msg.find_all(kind="field"):
        parent_msg = fld.parent()
        if parent_msg is not None and parent_msg.parent() != msg:
            continue
        ident = fld.find(kind="identifier")
        if ident is not None and not _PROTO_SNAKE_RE.match(ident.text().strip()):
            idioms.append(
                CodeLocation(
                    file=rel_path,
                    line=ident.range().start.line + 1,
                    symbol=ident.text().strip(),
                    detail="Protobuf field name should follow lower_snake_case convention",
                )
            )
        tag_node = fld.find(kind="field_number")
        if tag_node is None:
            continue
        tag_txt = tag_node.text().strip()
        if tag_txt in seen_tags:
            idioms.append(
                CodeLocation(
                    file=rel_path,
                    line=tag_node.range().start.line + 1,
                    symbol=tag_txt,
                    detail=f"Duplicate Protobuf field tag number {tag_txt}",
                )
            )
        seen_tags.add(tag_txt)
    return idioms


def protobuf_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit Protobuf CST for package hygiene, PascalCase messages/services, snake_case fields, and duplicate tags."""
    idioms: list[CodeLocation] = []
    if not unit.root.find_all(kind="package"):
        idioms.append(
            CodeLocation(
                file=unit.rel_path,
                line=1,
                symbol="package",
                detail="Missing 'package' declaration risks global symbol collisions across Protobuf imports",
            )
        )
    for syn in unit.root.find_all(kind="syntax"):
        if "proto2" in syn.text():
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=syn.range().start.line + 1,
                    symbol="proto2",
                    detail="Legacy proto2 syntax detected; prefer proto3 or Protobuf Editions",
                )
            )
    for msg in unit.root.find_all(kind="message"):
        idioms.extend(_audit_protobuf_message(msg, unit.rel_path))
    return CustomHookResult(bug_risk_idioms=tuple(idioms))


def yaml_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit YAML (including GitHub Actions CI workflows) for write-all permissions, unpinned uses, and secrets."""
    sinks: list[SecuritySinkLocation] = []
    idioms: list[CodeLocation] = []
    secrets: list[CodeLocation] = []

    for pair in unit.root.find_all(kind="block_mapping_pair"):
        txt = pair.text().strip()
        line_no = pair.range().start.line + 1
        key_part, _, val_part = txt.partition(":")
        key = key_part.strip().strip("'\"").lower()
        val = val_part.strip().strip("'\"")
        if key == "permissions" and val.lower() == "write-all":
            sinks.append(
                SecuritySinkLocation(
                    category="loose_comparison_or_auth",
                    cwe_id="CWE-269",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="permissions: write-all",
                    detail="CI workflow grants overly broad 'write-all' token permissions",
                )
            )
        if key == "uses" and _GH_USES_UNPINNED_RE.match(val):
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol=val,
                    detail="GitHub Action reference is not pinned to a full 40-char commit SHA",
                )
            )
        if "\n" not in val and BaseOperationalChecker.is_likely_secret_literal(key, val):
            secrets.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol=key,
                    detail="Hardcoded credential/secret value in YAML configuration",
                )
            )

    return CustomHookResult(
        bug_risk_idioms=tuple(idioms),
        dangerous_sinks=tuple(sinks),
        hardcoded_secrets=tuple(secrets),
    )


def sql_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit SQL scripts/migrations for destructive DROP/TRUNCATE, SELECT *, and dynamic EXEC."""
    idioms: list[CodeLocation] = []
    sinks: list[SecuritySinkLocation] = []

    for line_no, line in enumerate(unit.source.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if _SQL_DROP_RE.search(line) and "IF EXISTS" not in line.upper():
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol="DROP/TRUNCATE",
                    detail="Destructive SQL DDL without IF EXISTS guard",
                )
            )
        if _SQL_SELECT_STAR_RE.search(line):
            idioms.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=line_no,
                    symbol="SELECT *",
                    detail="Wildcard SELECT * couples queries to schema column order",
                )
            )
        if _SQL_DYNAMIC_EXEC_RE.search(line):
            sinks.append(
                SecuritySinkLocation(
                    category="sql_injection",
                    cwe_id="CWE-89",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="EXECUTE",
                    detail="Dynamic SQL execution sink requires strict parameter binding",
                )
            )

    return CustomHookResult(bug_risk_idioms=tuple(idioms), dangerous_sinks=tuple(sinks))


def html_audit_hook(unit: ParsedUnit) -> CustomHookResult:
    """Audit HTML CST elements for unsafe target=_blank links, inline event handlers, and http:// scripts."""
    sinks: list[SecuritySinkLocation] = []
    idioms: list[CodeLocation] = []

    for start_tag in unit.root.find_all(kind="start_tag"):
        txt = start_tag.text()
        low = txt.lower()
        line_no = start_tag.range().start.line + 1
        if 'target="_blank"' in low or "target='_blank'" in low:
            if "noopener" not in low:
                idioms.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="target=_blank",
                        detail="Anchor with target='_blank' missing rel='noopener noreferrer' (reverse tabnabbing)",
                    )
                )
        if re.search(r"\bon(?:click|load|error|mouseover|focus)\s*=", low):
            sinks.append(
                SecuritySinkLocation(
                    category="xss",
                    cwe_id="CWE-79",
                    severity="medium",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="inline-handler",
                    detail="Inline DOM event handler hinders strict Content-Security-Policy (CSP)",
                )
            )
        if ("<script" in low or "<iframe" in low) and "src=\"http://" in low:
            sinks.append(
                SecuritySinkLocation(
                    category="insecure_transport",
                    cwe_id="CWE-319",
                    severity="high",
                    file=unit.rel_path,
                    line=line_no,
                    symbol="http://",
                    detail="Cleartext HTTP script/iframe resource enables active MITM tampering",
                )
            )

    return CustomHookResult(bug_risk_idioms=tuple(idioms), dangerous_sinks=tuple(sinks))
