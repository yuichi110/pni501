# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic boundary touchpoint extractor for state/cache, database, and outbound HTTP/RPC."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze.models import AstFacts
from pni._actions.migration_analyze.models import BoundaryTouchpoint, TouchpointKind

_PatternRule = tuple[TouchpointKind, re.Pattern[str], str, str]

_JAVA_TOUCHPOINT_RULES: Final[tuple[_PatternRule, ...]] = (
    (
        "in_memory_state",
        re.compile(r"\bstatic\s+(?:final\s+)?(?:Map|HashMap|ConcurrentHashMap|List|Set)\b[^{;=]*?\b([A-Za-z_]\w*)"),
        "Process-local static mutable collection ({symbol})",
        "Externalize into Cache/State Port (e.g. Redis / Caffeine Adapter with explicit TTL)",
    ),
    (
        "persistence_db",
        re.compile(r"@Transactional\b"),
        "@Transactional persistence boundary without dedicated Repository Port",
        "Extract Repository Port interface and move transaction/JPA/JDBC logic to Outbound Persistence Adapter",
    ),
    (
        "persistence_db",
        re.compile(r"\b(JdbcTemplate|EntityManager|DriverManager\.getConnection|JpaRepository)\b"),
        "Direct database/ORM access ({symbol})",
        "Isolate behind domain Repository Port and Infrastructure Persistence Adapter",
    ),
    (
        "external_http_rpc",
        re.compile(r"\b(HttpClient\.newHttpClient|RestTemplate|WebClient|HttpURLConnection)\b"),
        "Direct outbound HTTP client invocation ({symbol})",
        "Abstract behind Outbound Gateway Port with explicit connect/read timeout Adapter",
    ),
)

_PHP_TOUCHPOINT_RULES: Final[tuple[_PatternRule, ...]] = (
    (
        "in_memory_state",
        re.compile(r"(\$_SESSION\s*\[\s*['\"][^'\"]+['\"]\s*\])"),
        "Direct PHP superglobal session state access ({symbol})",
        "Migrate to framework Session/Cache store (e.g. Redis-backed session/cache driver)",
    ),
    (
        "in_memory_state",
        re.compile(r"\bglobal\s+(\$[A-Za-z_]\w*)"),
        "Mutable PHP `global` state variable ({symbol})",
        "Eliminate global state via stateless Service DI or external Cache/Repository",
    ),
    (
        "in_memory_state",
        re.compile(r"\bunserialize\s*\(\s*(\$_COOKIE\s*\[\s*['\"][^'\"]+['\"]\s*\])"),
        "Client cookie PHP object/array deserialization state ({symbol})",
        "Replace insecure cookie state with server-side Redis/DB cart state or signed JSON DTO",
    ),
    (
        "persistence_db",
        re.compile(r"\b(mysqli_connect|mysqli_query|PDO|\$wpdb\s*->\s*\w+)\b"),
        "Direct procedural/raw database call ({symbol})",
        "Extract Repository / Eloquent / parameterized PDO Query Adapter",
    ),
    (
        "external_http_rpc",
        re.compile(r"\b(curl_init|curl_exec|GuzzleHttp\\Client)\b"),
        "Outbound HTTP partner/API call ({symbol})",
        "Wrap in Outbound HTTP Gateway Service/Port with TLS verification & timeout enforcement",
    ),
)

_PYTHON_TOUCHPOINT_RULES: Final[tuple[_PatternRule, ...]] = (
    (
        "persistence_db",
        re.compile(r"\b(sqlite3\.connect|psycopg\.connect|psycopg2\.connect|create_engine|SessionLocal)\b"),
        "Direct database engine/session call ({symbol})",
        "Isolate behind Repository / Unit-of-Work Port and SQLAlchemy/DB Adapter",
    ),
    (
        "external_http_rpc",
        re.compile(r"\b(requests\.(?:get|post|put|delete|request)|httpx\.(?:get|post|Client|AsyncClient)|urlopen)\b"),
        "Outbound HTTP call ({symbol})",
        "Isolate behind Outbound Client Port with explicit timeout & retry configuration",
    ),
)

_GO_TOUCHPOINT_RULES: Final[tuple[_PatternRule, ...]] = (
    (
        "persistence_db",
        re.compile(r"\b(sql\.Open|gorm\.Open|pgx\.Connect|sqlx\.Connect)\b"),
        "Direct database/ORM connection call ({symbol})",
        "Isolate behind Go interface Repository Port and infrastructure DB Adapter",
    ),
    (
        "external_http_rpc",
        re.compile(r"\b(http\.(?:Get|Post|PostForm|DefaultClient\.Do)|grpc\.Dial|grpc\.NewClient)\b"),
        "Direct outbound HTTP/gRPC call ({symbol})",
        "Abstract behind Outbound Client Port with context.Context deadline and explicit http.Client timeout",
    ),
)

_NODE_TOUCHPOINT_RULES: Final[tuple[_PatternRule, ...]] = (
    (
        "persistence_db",
        re.compile(r"\b(new\s+PrismaClient|mongoose\.connect|createConnection|new\s+Pool|knex)\b"),
        "Direct database/ORM client call ({symbol})",
        "Isolate behind Repository interface Port and Persistence Adapter",
    ),
    (
        "external_http_rpc",
        re.compile(r"\b(axios\.(?:get|post|put|delete|request)|fetch|got)\s*\("),
        "Direct outbound HTTP call ({symbol})",
        "Isolate behind Outbound Gateway Port with AbortSignal.timeout and typed response validation",
    ),
)

_JAVA_BEAN_CLASS_RE: Final[re.Pattern[str]] = re.compile(r"@(?:RestController|Controller|Service|Component)\b")
_JAVA_MUTABLE_FIELD_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:private|protected|public)\s+(?!static\b)(?!final\b)"
    r"(?:String|int|long|boolean|double|Map|List|Set|Object)\s+([A-Za-z_]\w*)\s*(?:=|;)"
)


def _rules_for_language(language: str) -> tuple[_PatternRule, ...]:
    """Return regex touchpoint rules matching the source language."""
    lang = language.lower()
    if lang == "java":
        return _JAVA_TOUCHPOINT_RULES
    if lang == "php":
        return _PHP_TOUCHPOINT_RULES
    if lang == "go":
        return _GO_TOUCHPOINT_RULES
    if lang in ("typescript", "javascript"):
        return _NODE_TOUCHPOINT_RULES
    return _PYTHON_TOUCHPOINT_RULES


def _scan_file_rules(rel_path: str, source: str, rules: tuple[_PatternRule, ...]) -> list[BoundaryTouchpoint]:
    """Scan a single source file's lines against language touchpoint regex rules."""
    found: list[BoundaryTouchpoint] = []
    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(("//", "#", "/*", "*")):
            continue
        for kind, pattern, coupling_tpl, port_hint in rules:
            match = pattern.search(raw_line)
            if match is None:
                continue
            sym = match.group(1) if match.lastindex else match.group(0)
            found.append(
                BoundaryTouchpoint(
                    kind=kind,
                    file=rel_path,
                    line=line_no,
                    symbol=sym.strip(),
                    current_coupling=coupling_tpl.format(symbol=sym.strip()),
                    recommended_port_hint=port_hint,
                )
            )
    return found


def _scan_java_singleton_mutable_fields(rel_path: str, source: str) -> list[BoundaryTouchpoint]:
    """Detect non-final mutable scalar/collection fields on Spring singleton beans."""
    if _JAVA_BEAN_CLASS_RE.search(source) is None:
        return []
    found: list[BoundaryTouchpoint] = []
    lines = source.splitlines()
    for idx, raw_line in enumerate(lines, start=1):
        prev_line = lines[idx - 2].strip() if idx >= 2 else ""
        if prev_line.startswith(("@Autowired", "@Inject", "@Value", "@Resource")):
            continue
        match = _JAVA_MUTABLE_FIELD_RE.match(raw_line)
        if match is not None:
            field_name = match.group(1)
            found.append(
                BoundaryTouchpoint(
                    kind="in_memory_state",
                    file=rel_path,
                    line=idx,
                    symbol=field_name,
                    current_coupling=f"Mutable instance field `{field_name}` on singleton Spring bean",
                    recommended_port_hint=(
                        "Convert bean to stateless; pass request-scoped context or externalize state to Redis/DB"
                    ),
                )
            )
    return found


def _append_ast_global_state(
    touchpoints: list[BoundaryTouchpoint],
    ast_facts: AstFacts | None,
) -> None:
    """Backfill in-memory state touchpoints from AstFacts.global_state_usages without duplicates."""
    if ast_facts is None:
        return
    existing = {(tp.file, tp.line, tp.kind) for tp in touchpoints}
    for loc in ast_facts.global_state_usages:
        key = (loc.file, loc.line, "in_memory_state")
        if key in existing:
            continue
        existing.add(key)
        touchpoints.append(
            BoundaryTouchpoint(
                kind="in_memory_state",
                file=loc.file,
                line=loc.line,
                symbol=loc.symbol,
                current_coupling=loc.detail,
                recommended_port_hint="Externalize shared mutable state into Cache/State Port or stateless DI",
            )
        )


def extract_boundary_touchpoints(
    source_files: dict[str, str],
    language: str,
    ast_facts: AstFacts | None = None,
) -> list[BoundaryTouchpoint]:
    """Extract deterministic in-memory state, database, and outbound HTTP touchpoints.

    Args:
        source_files: Mapping of workspace-relative file paths to UTF-8 file contents.
        language: Primary language ('java', 'php', 'python').
        ast_facts: Optional pre-computed AST facts for global state correlation.

    Returns:
        list[BoundaryTouchpoint]: Deterministically sorted boundary touchpoints.
    """
    rules = _rules_for_language(language)
    collected: list[BoundaryTouchpoint] = []
    is_java = language.lower() == "java"

    for rel_path in sorted(source_files):
        content = source_files[rel_path]
        collected.extend(_scan_file_rules(rel_path, content, rules))
        if is_java:
            collected.extend(_scan_java_singleton_mutable_fields(rel_path, content))

    _append_ast_global_state(collected, ast_facts)

    dedup: dict[tuple[str, str, int, str], BoundaryTouchpoint] = {}
    for tp in collected:
        dedup.setdefault((tp.kind, tp.file, tp.line, tp.symbol), tp)

    kind_order = {"in_memory_state": 0, "persistence_db": 1, "external_http_rpc": 2}
    return sorted(
        dedup.values(),
        key=lambda t: (kind_order.get(t.kind, 9), t.file, t.line, t.symbol),
    )
