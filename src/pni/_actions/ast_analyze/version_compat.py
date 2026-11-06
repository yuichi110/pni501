# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic AST compatibility checks between source APIs/syntax and declared language versions."""

from __future__ import annotations

import re
from typing import Final, Optional

from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit

_JAVA_LEGACY_1X_RE: Final[re.Pattern[str]] = re.compile(r"(?:^|[^\d])1\.(\d+)\b")
_JAVA_MAJOR_RE: Final[re.Pattern[str]] = re.compile(r"\b(\d{1,2})\b")
_MIN_VERSION_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"(?<![<!])(?:>=|\^|~=|~|=|\b)(\d+)(?:\.(\d+|\*))?")

_JAVA_9_CALL_SNIPPETS: Final[tuple[tuple[str, str], ...]] = (
    ("List.of(", "List.of"),
    ("Map.of(", "Map.of"),
    ("Set.of(", "Set.of"),
)
_JAVA_11_CALL_SNIPPETS: Final[tuple[tuple[str, str], ...]] = (
    (".isBlank()", "String.isBlank"),
    (".strip()", "String.strip"),
    (".lines()", "String.lines"),
    ("Files.readString(", "Files.readString"),
    ("Files.writeString(", "Files.writeString"),
)


def parse_java_target_major(constraint: Optional[str]) -> Optional[int]:
    """Parse a Maven/Gradle Java target version string ('1.8', '8', '17', '21') into major integer."""
    if not constraint or not constraint.strip():
        return None
    clean = constraint.strip()
    legacy_match = _JAVA_LEGACY_1X_RE.search(clean)
    if legacy_match is not None:
        return int(legacy_match.group(1))
    major_match = _JAVA_MAJOR_RE.search(clean)
    if major_match is not None:
        val = int(major_match.group(1))
        if 5 <= val <= 30:
            return val
    return None


def parse_min_language_version(constraint: Optional[str]) -> Optional[tuple[int, int]]:
    """Extract the lowest declared (major, minor) target version from Composer/PEP 621 version specs."""
    if not constraint or not constraint.strip():
        return None
    candidates: list[tuple[int, int]] = []
    for part in re.split(r"[,|]|\s+", constraint.strip()):
        tok = part.strip()
        if not tok or tok.startswith(("<", "!")):
            continue
        match = _MIN_VERSION_TOKEN_RE.search(tok)
        if match is None:
            continue
        major = int(match.group(1))
        raw_minor = match.group(2)
        minor = int(raw_minor) if raw_minor and raw_minor.isdigit() else 0
        candidates.append((major, minor))
    return min(candidates) if candidates else None


def _check_java_imports_and_records(unit: ParsedUnit, target_major: int, raw_constraint: str) -> list[CodeLocation]:
    """Check Java import declarations and record syntax against target_major."""
    mismatches: list[CodeLocation] = []
    seen_imports: set[str] = set()
    import_rules = (
        (11, "java.net.http.", "java.net.http", "Java 11+ 'java.net.http' API"),
        (21, "java.lang.foreign.", "foreign", "Java 21+ 'java.lang.foreign' API"),
    )
    for imp in unit.root.find_all(kind="import_declaration"):
        imp_text = imp.text().removeprefix("import").strip().removesuffix(";").strip()
        lineno = imp.range().start.line + 1
        for min_ver, prefix, key, label in import_rules:
            if target_major < min_ver and imp_text.startswith(prefix) and key not in seen_imports:
                seen_imports.add(key)
                mismatches.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=lineno,
                        symbol=imp_text,
                        detail=f"{label} imported while declared target is Java {raw_constraint}",
                    )
                )

    if target_major < 16:
        for rnode in unit.root.find_all(kind="record_declaration"):
            name_node = rnode.field("name")
            sym = name_node.text() if name_node is not None else "record"
            mismatches.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=rnode.range().start.line + 1,
                    symbol=sym,
                    detail=f"Java 16+ 'record' declaration used while declared target is Java {raw_constraint}",
                )
            )
    return mismatches


def _check_java_unit(unit: ParsedUnit, target_major: int, raw_constraint: str) -> list[CodeLocation]:
    """Inspect a Java CST unit for standard library imports or syntax newer than target_major."""
    mismatches = _check_java_imports_and_records(unit, target_major, raw_constraint)
    active_snippets: list[tuple[int, str, str]] = []
    if target_major < 9:
        active_snippets.extend((9, snip, sym) for snip, sym in _JAVA_9_CALL_SNIPPETS)
    if target_major < 11:
        active_snippets.extend((11, snip, sym) for snip, sym in _JAVA_11_CALL_SNIPPETS)
    if not active_snippets:
        return mismatches

    for idx, line_str in enumerate(unit.source.splitlines(), start=1):
        for min_ver, snippet, sym in active_snippets:
            if snippet in line_str:
                mismatches.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=idx,
                        symbol=sym,
                        detail=f"Java {min_ver}+ '{sym}' API used while declared target is Java {raw_constraint}",
                    )
                )
    return mismatches


def _check_php_unit(unit: ParsedUnit, min_ver: tuple[int, int], raw_constraint: str) -> list[CodeLocation]:
    """Inspect a PHP CST unit for PHP 8.0+ / 8.1+ syntax incompatible with declared minimum PHP version."""
    mismatches: list[CodeLocation] = []
    if min_ver < (8, 0):
        for kind, label in (
            ("match_expression", "PHP 8.0+ 'match' expression"),
            ("attribute_list", "PHP 8.0+ '#[Attribute]' syntax"),
            ("nullsafe_member_access_expression", "PHP 8.0+ nullsafe '?->' operator"),
            ("nullsafe_member_call_expression", "PHP 8.0+ nullsafe '?->' operator"),
        ):
            for node in unit.root.find_all(kind=kind):
                mismatches.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=node.range().start.line + 1,
                        symbol=kind,
                        detail=f"{label} used while declared PHP constraint is '{raw_constraint}'",
                    )
                )
    if min_ver < (8, 1):
        for kind, label in (
            ("enum_declaration", "PHP 8.1+ 'enum' declaration"),
            ("readonly_modifier", "PHP 8.1+ 'readonly' property/class modifier"),
        ):
            for node in unit.root.find_all(kind=kind):
                mismatches.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=node.range().start.line + 1,
                        symbol=kind,
                        detail=f"{label} used while declared PHP constraint is '{raw_constraint}'",
                    )
                )
    return mismatches


def _check_python_unit(unit: ParsedUnit, min_ver: tuple[int, int], raw_constraint: str) -> list[CodeLocation]:
    """Inspect a Python CST unit for syntax/stdlib modules newer than declared requires-python."""
    mismatches: list[CodeLocation] = []
    if min_ver < (3, 10):
        for node in unit.root.find_all(kind="match_statement"):
            mismatches.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=node.range().start.line + 1,
                    symbol="match",
                    detail=f"Python 3.10+ 'match/case' syntax used while requires-python is '{raw_constraint}'",
                )
            )
    if min_ver < (3, 11):
        for stmt in [*unit.root.find_all(kind="import_statement"), *unit.root.find_all(kind="import_from_statement")]:
            txt = stmt.text()
            if re.search(r"\btomllib\b", txt):
                mismatches.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=stmt.range().start.line + 1,
                        symbol="tomllib",
                        detail=f"Python 3.11+ stdlib 'tomllib' imported while requires-python is '{raw_constraint}'",
                    )
                )
    if min_ver < (3, 12):
        for node in unit.root.find_all(kind="type_alias_statement"):
            mismatches.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=node.range().start.line + 1,
                    symbol="type",
                    detail=f"Python 3.12+ 'type' alias syntax used while requires-python is '{raw_constraint}'",
                )
            )
    return mismatches


def check_language_version_compatibility(
    language: str,
    declared_version: Optional[str],
    units: list[ParsedUnit],
) -> list[CodeLocation]:
    """Detect source code syntax and stdlib APIs newer than the manifest's declared language version."""
    if not declared_version or not units:
        return []
    lang_low = language.strip().lower()
    raw = declared_version.strip()

    if lang_low == "java":
        java_major = parse_java_target_major(raw)
        return [loc for u in units for loc in _check_java_unit(u, java_major, raw)] if java_major is not None else []

    min_ver = parse_min_language_version(raw)
    if min_ver is None:
        return []
    checker = _check_php_unit if lang_low == "php" else (_check_python_unit if lang_low == "python" else None)
    return [loc for u in units for loc in checker(u, min_ver, raw)] if checker is not None else []

