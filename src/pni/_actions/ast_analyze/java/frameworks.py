# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java framework best-practice and ecosystem modernization AST checkers (Spring Boot, Java APIs)."""

from __future__ import annotations

from typing import ClassVar, Final

from pni._actions.ast_analyze.base import BaseFrameworkChecker
from pni._actions.ast_analyze.java._helpers import callable_symbol_name, get_modifiers_node
from pni._actions.ast_analyze.models import (
    CodeLocation,
    FrameworkCheckResult,
    ParsedUnit,
)

_LEGACY_JAVA_TYPES: Final[dict[str, str]] = {
    "Date": "Legacy java.util.Date usage; prefer java.time (Instant / LocalDate / ZonedDateTime)",
    "Calendar": "Legacy java.util.Calendar usage; prefer java.time APIs",
    "SimpleDateFormat": "Mutable non-thread-safe SimpleDateFormat; prefer java.time.format.DateTimeFormatter",
    "Vector": "Legacy synchronized Vector; prefer ArrayList or CopyOnWriteArrayList",
    "Hashtable": "Legacy Hashtable; prefer ConcurrentHashMap or HashMap",
    "Stack": "Legacy java.util.Stack; prefer Deque / ArrayDeque",
}


class SpringBootFrameworkChecker(BaseFrameworkChecker):
    """Check Spring Boot DI hygiene (@Autowired field injection) and controller annotations."""

    framework_id: ClassVar[str] = "spring-boot"

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Run when spring-boot is in manifest or org.springframework is imported."""
        if self.framework_id in detected_frameworks:
            return True
        return any("org.springframework" in u.source for u in units)

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Inspect a Java compilation unit for Spring field injection and @RequestMapping methods."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []

        for fnode in unit.root.find_all(kind="field_declaration"):
            mods = get_modifiers_node(fnode)
            if mods is not None and ("@Autowired" in mods.text() or "@Inject" in mods.text()):
                declarators = fnode.find_all(kind="variable_declarator")
                names = [n.text() for d in declarators if (n := d.field("name")) is not None]
                fname = ", ".join(names) or "field"
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=fnode.range().start.line + 1,
                        symbol=fname,
                        detail="Field injection (@Autowired/@Inject) hinders testability; use constructor injection",
                    )
                )

        for mnode in unit.root.find_all(kind="method_declaration"):
            mods = get_modifiers_node(mnode)
            if mods is not None and "@RequestMapping" in mods.text():
                mname = callable_symbol_name(mnode)
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=mnode.range().start.line + 1,
                        symbol=mname,
                        detail="Method-level @RequestMapping; prefer @GetMapping/@PostMapping/@PutMapping",
                    )
                )

        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)


class JavaModernSyntaxChecker(BaseFrameworkChecker):
    """Detect legacy JDK APIs (Date/Calendar/SimpleDateFormat/Vector/Hashtable) replaceable by modern Java."""

    framework_id: ClassVar[str] = "java-core"

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Always run on non-empty Java units."""
        _ = detected_frameworks
        return bool(units)

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Scan object creation expressions and type identifiers for legacy JDK classes."""
        hints: list[CodeLocation] = []
        seen_lines: set[tuple[int, str]] = set()
        for tid in unit.root.find_all(kind="type_identifier"):
            tname = tid.text()
            msg = _LEGACY_JAVA_TYPES.get(tname)
            if msg is None:
                continue
            lineno = tid.range().start.line + 1
            if (lineno, tname) in seen_lines:
                continue
            seen_lines.add((lineno, tname))
            hints.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=lineno,
                    symbol=tname,
                    detail=msg,
                )
            )
        return FrameworkCheckResult(modernization_hints=hints)
