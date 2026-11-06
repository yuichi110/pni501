# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java AST security sink (CWE) and Spring MVC / Boot API endpoint extractor."""

from __future__ import annotations

import re
from typing import Final, Optional

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base.security import BaseSecurityChecker
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    ParsedUnit,
    SecuritySinkLocation,
)

_JAVA_SQL_METHODS: Final[frozenset[str]] = frozenset(
    {
        "executeQuery",
        "executeUpdate",
        "execute",
        "prepareStatement",
        "createNativeQuery",
        "createQuery",
        "query",
        "queryForObject",
        "queryForList",
    }
)
_SPRING_MAPPING_METHODS: Final[dict[str, str]] = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "DeleteMapping": "DELETE",
    "PatchMapping": "PATCH",
    "RequestMapping": "ANY",
}
_JAVA_AUTH_ANNOTATIONS: Final[tuple[str, ...]] = (
    "PreAuthorize",
    "PostAuthorize",
    "Secured",
    "RolesAllowed",
)
_JAVA_AUTH_PARAM_TOKENS: Final[tuple[str, ...]] = (
    "AuthenticationPrincipal",
    "Authentication",
    "Principal",
    "Jwt",
    "UserDetails",
)
_QUOTED_PATH_RE: Final[re.Pattern[str]] = re.compile(r'"([^"]*)"')
_PATH_ATTR_RE: Final[re.Pattern[str]] = re.compile(r'(?:value|path)\s*=\s*\{?\s*"([^"]*)"')
_REQ_METHOD_RE: Final[re.Pattern[str]] = re.compile(r"RequestMethod\.(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)")


def _first_java_arg(args_node: Optional[SgNode]) -> Optional[SgNode]:
    """Return the first named argument node inside a Java argument_list."""
    if args_node is None:
        return None
    for child in args_node.children():
        if child.is_named():
            return child
    return None


def _is_dynamic_java_sql(arg: Optional[SgNode]) -> bool:
    """Return True if a Java SQL argument uses string concatenation (+) or String.format."""
    if arg is None:
        return False
    if arg.kind() == "binary_expression" and '"' in arg.text():
        return True
    if arg.kind() == "method_invocation" and arg.text().startswith(("String.format", "formatted")):
        return True
    return False


def _check_java_invocation_sink(unit: ParsedUnit, inv: SgNode) -> Optional[SecuritySinkLocation]:
    """Inspect a Java method_invocation for SQLi, Runtime.exec, weak crypto, or CORS wildcard."""
    obj = inv.field("object")
    name_node = inv.field("name")
    args_node = inv.field("arguments")
    mname = name_node.text() if name_node is not None else ""
    obj_txt = obj.text().strip() if obj is not None else ""
    args_txt = args_node.text() if args_node is not None else ""
    lineno = inv.range().start.line + 1

    if mname in _JAVA_SQL_METHODS and _is_dynamic_java_sql(_first_java_arg(args_node)):
        return SecuritySinkLocation(
            category="sql_injection",
            cwe_id="CWE-89",
            severity="high",
            file=unit.rel_path,
            line=lineno,
            symbol=mname,
            detail=f"Concatenated SQL string passed to '{mname}(...)' — use PreparedStatement / named params",
        )
    if mname == "exec" and ("Runtime" in obj_txt or "getRuntime" in obj_txt):
        return SecuritySinkLocation(
            category="command_injection",
            cwe_id="CWE-78",
            severity="high",
            file=unit.rel_path,
            line=lineno,
            symbol="Runtime.exec",
            detail="OS command execution via Runtime.exec(...)",
        )
    if obj_txt == "MessageDigest" and mname == "getInstance":
        upper = args_txt.upper()
        if '"MD5"' in upper or '"SHA-1"' in upper or '"SHA1"' in upper:
            return SecuritySinkLocation(
                category="weak_cryptography",
                cwe_id="CWE-327",
                severity="medium",
                file=unit.rel_path,
                line=lineno,
                symbol="MessageDigest.getInstance",
                detail=f"Weak digest algorithm in MessageDigest.getInstance{args_txt} — prefer SHA-256+",
            )
    if obj_txt == "Cipher" and mname == "getInstance":
        upper = args_txt.upper()
        if '"DES' in upper or "/ECB/" in upper or '"AES"' in upper:
            return SecuritySinkLocation(
                category="weak_cryptography",
                cwe_id="CWE-327",
                severity="medium",
                file=unit.rel_path,
                line=lineno,
                symbol="Cipher.getInstance",
                detail=f"Insecure cipher transformation Cipher.getInstance{args_txt} — prefer AES/GCM/NoPadding",
            )
    if mname in {"allowedOrigins", "allowedOriginPatterns"} and '"*"' in args_txt:
        return SecuritySinkLocation(
            category="permissive_cors_or_debug",
            cwe_id="CWE-942",
            severity="medium",
            file=unit.rel_path,
            line=lineno,
            symbol=mname,
            detail=f"Wildcard CORS origin configured via '{mname}(\"*\")'",
        )
    return None


def _check_java_creation_and_annotations(unit: ParsedUnit) -> list[SecuritySinkLocation]:
    """Inspect Java object creations (ObjectInputStream, ProcessBuilder) and @CrossOrigin annotations."""
    sinks: list[SecuritySinkLocation] = []
    for creation in unit.root.find_all(kind="object_creation_expression"):
        type_node = creation.field("type")
        args_node = creation.field("arguments")
        tname = type_node.text().strip() if type_node is not None else ""
        args_txt = args_node.text() if args_node is not None else ""
        lineno = creation.range().start.line + 1
        if tname in {"ObjectInputStream", "XMLDecoder"}:
            sinks.append(
                SecuritySinkLocation(
                    category="unsafe_deserialization",
                    cwe_id="CWE-502",
                    severity="high",
                    file=unit.rel_path,
                    line=lineno,
                    symbol=tname,
                    detail=f"Untrusted Java deserialization sink 'new {tname}(...)'",
                )
            )
        elif tname == "ProcessBuilder" and ('"-c"' in args_txt or '"/c"' in args_txt):
            sinks.append(
                SecuritySinkLocation(
                    category="command_injection",
                    cwe_id="CWE-78",
                    severity="high",
                    file=unit.rel_path,
                    line=lineno,
                    symbol="ProcessBuilder",
                    detail="Shell invocation via ProcessBuilder(... '-c' ...)",
                )
            )

    for ann in (*unit.root.find_all(kind="marker_annotation"), *unit.root.find_all(kind="annotation")):
        txt = ann.text().strip()
        if txt == "@CrossOrigin" or (txt.startswith("@CrossOrigin") and '"*"' in txt):
            sinks.append(
                SecuritySinkLocation(
                    category="permissive_cors_or_debug",
                    cwe_id="CWE-942",
                    severity="medium",
                    file=unit.rel_path,
                    line=ann.range().start.line + 1,
                    symbol="@CrossOrigin",
                    detail="Permissive wildcard @CrossOrigin allows arbitrary origins",
                )
            )
    return sinks


def _extract_mapping_path(ann_text: str) -> str:
    """Extract the URL path string from a Spring @*Mapping annotation."""
    attr = _PATH_ATTR_RE.search(ann_text)
    if attr:
        return attr.group(1)
    if "=" not in ann_text:
        quoted = _QUOTED_PATH_RE.search(ann_text)
        if quoted:
            return quoted.group(1)
    return ""


def _extract_annotations_text(decl_node: SgNode) -> list[str]:
    """Return all annotation texts attached inside a Java modifiers node."""
    out: list[str] = []
    for child in decl_node.children():
        if child.kind() == "modifiers":
            for mod in child.children():
                if "annotation" in mod.kind():
                    out.append(mod.text().strip())
    return out


def _collect_auth_annotations(annotations: list[str]) -> set[str]:
    """Extract Spring Security annotation tokens from annotation strings."""
    found: set[str] = set()
    for ann in annotations:
        for auth_tok in _JAVA_AUTH_ANNOTATIONS:
            if f"@{auth_tok}" in ann:
                found.add(f"@{auth_tok}")
    return found


def _extract_method_endpoints(
    unit: ParsedUnit,
    cls_name: str,
    base_path: str,
    cls_auth: set[str],
    member: SgNode,
) -> list[ApiEndpointFact]:
    """Extract Spring route mappings declared on a single method_declaration."""
    mname_node = member.field("name")
    mname = mname_node.text() if mname_node is not None else "handler"
    params_node = member.field("parameters")
    params_txt = params_node.text() if params_node is not None else ""
    m_anns = _extract_annotations_text(member)
    auth_set = cls_auth | _collect_auth_annotations(m_anns)
    auth_set.update(ptok for ptok in _JAVA_AUTH_PARAM_TOKENS if ptok in params_txt)

    out: list[ApiEndpointFact] = []
    for ann in m_anns:
        for mapping_name, default_verb in _SPRING_MAPPING_METHODS.items():
            if not re.match(rf"^@{mapping_name}\b", ann):
                continue
            sub_path = _extract_mapping_path(ann)
            verb_match = _REQ_METHOD_RE.search(ann)
            verb = verb_match.group(1) if verb_match else default_verb
            out.append(
                ApiEndpointFact(
                    http_method=verb,
                    path=BaseSecurityChecker.join_route_paths(base_path, sub_path),
                    handler=f"{cls_name}.{mname}",
                    file=unit.rel_path,
                    line=member.range().start.line + 1,
                    has_auth_hint=bool(auth_set),
                    auth_mechanisms=sorted(auth_set),
                )
            )
    return out


class JavaSecurityChecker(BaseSecurityChecker):
    """Extract Java CWE dangerous sinks and Spring MVC / Boot API endpoints."""

    def find_dangerous_sinks(self, unit: ParsedUnit) -> list[SecuritySinkLocation]:
        """Inspect Java CSTs for SQLi, command execution, deserialization, weak crypto, and CORS."""
        findings: list[SecuritySinkLocation] = []
        for inv in unit.root.find_all(kind="method_invocation"):
            sink = _check_java_invocation_sink(unit, inv)
            if sink is not None:
                findings.append(sink)
        findings.extend(_check_java_creation_and_annotations(unit))
        return findings

    def find_api_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Extract Spring @RestController / @Controller endpoints and security annotations."""
        endpoints: list[ApiEndpointFact] = []
        for cls_node in unit.root.find_all(kind="class_declaration"):
            name_node = cls_node.field("name")
            cls_name = name_node.text() if name_node is not None else unit.file_path.stem
            cls_anns = _extract_annotations_text(cls_node)
            req_anns = [ann for ann in cls_anns if ann.startswith("@RequestMapping")]
            base_path = _extract_mapping_path(req_anns[0]) if req_anns else ""
            cls_auth = _collect_auth_annotations(cls_anns)
            body = cls_node.field("body")
            if body is None:
                continue
            for member in body.children():
                if member.kind() == "method_declaration":
                    endpoints.extend(_extract_method_endpoints(unit, cls_name, base_path, cls_auth, member))
        return endpoints
