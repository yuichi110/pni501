# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Implicit dynamic I/O schema and environment/configuration contract extractor."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze.models import ApiEndpointFact, AstFacts
from pni._actions.migration_analyze.models import (
    ContractFieldSpec,
    EnvVarContract,
    ImplicitEndpointContract,
)

_SENSITIVE_KEY_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:SECRET|PASSWORD|PASSWD|TOKEN|API_KEY|PRIVATE_KEY|CREDENTIAL)",
    re.IGNORECASE,
)

_JAVA_MAP_IN_RE: Final[re.Pattern[str]] = re.compile(
    r"\b\w+\.getOrDefault\(\s*\"([^\"]+)\"\s*,\s*(\"[^\"]*\"|\d+[Ll]?|true|false)\s*\)"
    r"|\b(?:payload|request|body|params|input)\.get\(\s*\"([^\"]+)\"\s*\)"
    r"|\b\w+\.getParameter\(\s*\"([^\"]+)\"\s*\)"
)
_JAVA_MAP_OUT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:summary|result|response|out|resp)\.put\(\s*\"([^\"]+)\"\s*,"
)
_JAVA_ENV_RE: Final[re.Pattern[str]] = re.compile(r"\bSystem\.getenv\(\s*\"([^\"]+)\"\s*\)")
_JAVA_PROP_RE: Final[re.Pattern[str]] = re.compile(r"@Value\(\s*\"\$\{([^:}]+)(?::([^}]*))?\}\"\s*\)")

_PHP_SUPER_IN_RE: Final[re.Pattern[str]] = re.compile(
    r"\$_(?:GET|POST|REQUEST|COOKIE)\s*\[\s*['\"]([^'\"]+)['\"]\s*\](?:\s*\?\?\s*(['\"][^'\"]*['\"]|\d+))?"
)
_PHP_LARAVEL_IN_RE: Final[re.Pattern[str]] = re.compile(
    r"\$request\s*->\s*(?:input|query|post|get)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*(['\"][^'\"]*['\"]|\d+))?\s*\)"
)
_PHP_ENV_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:getenv|env)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*(['\"][^'\"]*['\"]|\d+))?\s*\)"
)
_PHP_DEFINE_RE: Final[re.Pattern[str]] = re.compile(
    r"\bdefine\(\s*['\"]([A-Z0-9_]+)['\"]\s*,\s*(['\"][^'\"]*['\"]|\d+)\s*\)"
)

_PY_DICT_IN_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:payload|data|body|params|args|form)\.get\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*(['\"][^'\"]*['\"]|\d+))?\s*\)"
)
_PY_ENV_RE: Final[re.Pattern[str]] = re.compile(
    r"\bos\.(?:getenv|environ\.get)\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*(['\"][^'\"]*['\"]|\d+))?\s*\)"
)
_GO_IN_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:r\.URL\.Query\(\)\.Get|c\.Query|c\.Param|c\.PostForm|r\.FormValue)\(\s*\"([^\"]+)\"\s*\)"
    r"|\b(?:c\.DefaultQuery|c\.DefaultPostForm)\(\s*\"([^\"]+)\"\s*,\s*(\"[^\"]*\"|\d+)\s*\)"
)
_GO_ENV_RE: Final[re.Pattern[str]] = re.compile(r"\bos\.(?:Getenv|LookupEnv)\(\s*\"([^\"]+)\"\s*\)")
_NODE_IN_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:req|request|ctx)\.(?:body|query|params)\.([A-Za-z_]\w*)"
    r"(?:\s*(?:\?\?|\|\|)\s*(['\"][^'\"]*['\"]|\d+))?"
)
_NODE_ENV_RE: Final[re.Pattern[str]] = re.compile(
    r"\bprocess\.env\.([A-Z0-9_]+)\b(?:\s*(?:\?\?|\|\|)\s*(['\"][^'\"]*['\"]|\d+))?"
)


def _sanitize_default(name: str, raw_val: str | None) -> str | None:
    """Strip quotes and redact secret defaults when the key name indicates credentials."""
    if raw_val is None:
        return None
    cleaned = raw_val.strip().strip("'\"")
    if _SENSITIVE_KEY_RE.search(name):
        return "<REDACTED>"
    return cleaned


def _infer_field_type(line_text: str, default_val: str | None) -> str:
    """Infer primitive contract type ('integer', 'boolean', 'string') from cast/parse context."""
    if any(tok in line_text for tok in ("parseLong", "parseInt", "Atoi", "int(", "(int)", "Cents", "_id")):
        return "integer"
    if any(tok in line_text for tok in ("parseBoolean", "ParseBool", "bool(")):
        return "boolean"
    if default_val is not None and default_val.rstrip("Ll").isdigit():
        return "integer"
    return "string"


def _extract_java_fields(rel_path: str, source: str) -> tuple[list[ContractFieldSpec], list[ContractFieldSpec]]:
    """Extract dynamic Map/Servlet input and output keys from a Java source file."""
    inputs: list[ContractFieldSpec] = []
    outputs: list[ContractFieldSpec] = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        for match in _JAVA_MAP_IN_RE.finditer(line):
            key = match.group(1) or match.group(3) or match.group(4) or ""
            raw_def = match.group(2)
            if key:
                clean_def = _sanitize_default(key, raw_def)
                inputs.append(
                    ContractFieldSpec(
                        key=key,
                        direction="input",
                        inferred_type=_infer_field_type(line, clean_def),
                        default_value=clean_def,
                        file=rel_path,
                        line=line_no,
                    )
                )
        for match in _JAVA_MAP_OUT_RE.finditer(line):
            out_key = match.group(1)
            outputs.append(
                ContractFieldSpec(
                    key=out_key,
                    direction="output",
                    inferred_type=_infer_field_type(line, None),
                    file=rel_path,
                    line=line_no,
                )
            )
    return inputs, outputs


def _patterns_for_dynamic_fields(language: str) -> tuple[re.Pattern[str], ...]:
    """Return input extraction regex patterns for non-Java languages."""
    if language == "php":
        return (_PHP_SUPER_IN_RE, _PHP_LARAVEL_IN_RE)
    if language == "go":
        return (_GO_IN_RE,)
    if language in ("typescript", "javascript"):
        return (_NODE_IN_RE,)
    return (_PY_DICT_IN_RE,)


def _extract_php_or_py_fields(
    rel_path: str,
    source: str,
    language: str,
) -> tuple[list[ContractFieldSpec], list[ContractFieldSpec]]:
    """Extract superglobal/request/dict input keys from PHP, Go, TS/JS, or Python files."""
    inputs: list[ContractFieldSpec] = []
    patterns = _patterns_for_dynamic_fields(language)
    for line_no, line in enumerate(source.splitlines(), start=1):
        for pat in patterns:
            for match in pat.finditer(line):
                if language == "go":
                    key = match.group(1) or match.group(2) or ""
                    raw_def = match.group(3)
                else:
                    key = match.group(1)
                    raw_def = match.group(2) if match.lastindex and match.lastindex >= 2 else None
                if not key:
                    continue
                clean_def = _sanitize_default(key, raw_def)
                inputs.append(
                    ContractFieldSpec(
                        key=key,
                        direction="input",
                        inferred_type=_infer_field_type(line, clean_def),
                        default_value=clean_def,
                        file=rel_path,
                        line=line_no,
                    )
                )
    return inputs, []


def _dedup_fields(fields: list[ContractFieldSpec]) -> list[ContractFieldSpec]:
    """Deduplicate ContractFieldSpec entries by (direction, key), preferring entries with default_value."""
    by_key: dict[tuple[str, str], ContractFieldSpec] = {}
    for item in fields:
        k = (item.direction, item.key)
        existing = by_key.get(k)
        if existing is None or (existing.default_value is None and item.default_value is not None):
            by_key[k] = item
    return sorted(by_key.values(), key=lambda f: (f.file, f.line, f.key))


def _build_endpoint_contracts(
    per_file_in: dict[str, list[ContractFieldSpec]],
    per_file_out: dict[str, list[ContractFieldSpec]],
    endpoints: list[ApiEndpointFact],
) -> list[ImplicitEndpointContract]:
    """Correlate file-level dynamic inputs/outputs with extracted API routes or standalone PHP scripts."""
    ep_by_file: dict[str, ApiEndpointFact] = {}
    for ep in endpoints:
        ep_by_file.setdefault(ep.file, ep)

    all_global_outputs = [fld for flds in per_file_out.values() for fld in flds]
    contracts: list[ImplicitEndpointContract] = []

    candidate_files = sorted(set(per_file_in) | set(per_file_out) | set(ep_by_file))
    for rel_path in candidate_files:
        in_fields = per_file_in.get(rel_path, [])
        out_fields = list(per_file_out.get(rel_path, []))
        ep = ep_by_file.get(rel_path)
        if ep is not None and not out_fields and all_global_outputs:
            out_fields = list(all_global_outputs)
        if not in_fields and not out_fields and ep is None:
            continue
        if ep is None and not in_fields:
            continue
        contracts.append(
            ImplicitEndpointContract(
                endpoint_or_file=ep.path if ep is not None else rel_path,
                http_method=ep.http_method if ep is not None else "POST/GET",
                handler=ep.handler if ep is not None else rel_path,
                input_fields=_dedup_fields(in_fields),
                output_fields=_dedup_fields(out_fields),
            )
        )
    return contracts


def _extract_java_line_env(rel_path: str, lines: list[str], idx: int, line: str) -> list[EnvVarContract]:
    """Extract Java System.getenv and @Value / getProperty contracts from a single line."""
    found: list[EnvVarContract] = []
    for m in _JAVA_ENV_RE.finditer(line):
        name = m.group(1)
        fallback: str | None = None
        nearby = "\n".join(lines[idx : min(len(lines), idx + 4)])
        fb_match = re.search(r'=\s*"([^"]+)"', nearby)
        if fb_match is not None:
            fallback = _sanitize_default(name, fb_match.group(1))
        found.append(EnvVarContract(name=name, default_value=fallback, file=rel_path, line=idx, kind="env"))
    for m in _JAVA_PROP_RE.finditer(line):
        name = m.group(1)
        found.append(
            EnvVarContract(
                name=name,
                default_value=_sanitize_default(name, m.group(2)),
                file=rel_path,
                line=idx,
                kind="config_property",
            )
        )
    return found


def _extract_php_line_env(rel_path: str, idx: int, line: str) -> list[EnvVarContract]:
    """Extract PHP getenv/$_ENV and define() constant contracts from a single line."""
    found: list[EnvVarContract] = []
    for m in _PHP_ENV_RE.finditer(line):
        name = m.group(1)
        found.append(
            EnvVarContract(
                name=name,
                default_value=_sanitize_default(name, m.group(2)),
                file=rel_path,
                line=idx,
                kind="env",
            )
        )
    for m in _PHP_DEFINE_RE.finditer(line):
        name = m.group(1)
        found.append(
            EnvVarContract(
                name=name,
                default_value=_sanitize_default(name, m.group(2)),
                file=rel_path,
                line=idx,
                kind="constant",
            )
        )
    return found


def _extract_file_env_contracts(rel_path: str, source: str, lang: str) -> list[EnvVarContract]:
    """Extract environment variable and config constant contracts from a single file."""
    found: list[EnvVarContract] = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        if lang == "java":
            found.extend(_extract_java_line_env(rel_path, lines, idx, line))
        elif lang == "php":
            found.extend(_extract_php_line_env(rel_path, idx, line))
        elif lang == "go":
            found.extend(
                EnvVarContract(name=m.group(1), default_value=None, file=rel_path, line=idx, kind="env")
                for m in _GO_ENV_RE.finditer(line)
            )
        else:
            env_re = _NODE_ENV_RE if lang in ("typescript", "javascript") else _PY_ENV_RE
            found.extend(
                EnvVarContract(
                    name=m.group(1),
                    default_value=_sanitize_default(m.group(1), m.group(2)),
                    file=rel_path,
                    line=idx,
                    kind="env",
                )
                for m in env_re.finditer(line)
            )
    return found


def extract_implicit_and_env_contracts(
    source_files: dict[str, str],
    language: str,
    ast_facts: AstFacts | None = None,
) -> tuple[list[ImplicitEndpointContract], list[EnvVarContract]]:
    """Extract implicit dynamic endpoint I/O schemas and environment variable contracts.

    Args:
        source_files: Workspace-relative file path to source content mapping.
        language: Primary language ('java', 'php', 'python').
        ast_facts: Optional AST facts providing extracted API route endpoints.

    Returns:
        tuple[list[ImplicitEndpointContract], list[EnvVarContract]]: Implicit I/O and env contracts.
    """
    lang = language.lower()
    per_file_in: dict[str, list[ContractFieldSpec]] = {}
    per_file_out: dict[str, list[ContractFieldSpec]] = {}
    env_items: list[EnvVarContract] = []

    for rel_path in sorted(source_files):
        src = source_files[rel_path]
        if lang == "java":
            ins, outs = _extract_java_fields(rel_path, src)
        else:
            ins, outs = _extract_php_or_py_fields(rel_path, src, lang)
        if ins:
            per_file_in[rel_path] = ins
        if outs:
            per_file_out[rel_path] = outs
        env_items.extend(_extract_file_env_contracts(rel_path, src, lang))

    endpoints = ast_facts.api_endpoints if ast_facts is not None else []
    implicit = _build_endpoint_contracts(per_file_in, per_file_out, endpoints)
    env_dedup = {(e.name, e.file, e.line): e for e in env_items}
    sorted_env = sorted(env_dedup.values(), key=lambda e: (e.file, e.line, e.name))
    return implicit, sorted_env
