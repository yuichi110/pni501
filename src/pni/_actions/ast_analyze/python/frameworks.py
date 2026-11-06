# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python framework best-practice checkers (FastAPI, Pydantic) and Modern Stack signals."""

from __future__ import annotations

from typing import ClassVar, Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseFrameworkChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    FrameworkCheckResult,
    ParsedUnit,
)
from pni._actions.ast_analyze.python._helpers import function_symbol_name

_SYNC_BLOCKING_CALLS: Final[tuple[str, ...]] = (
    "time.sleep",
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.delete",
    "requests.patch",
    "requests.request",
    "urllib.request.urlopen",
)
_FASTAPI_HTTP_METHODS: Final[frozenset[str]] = frozenset(
    {"get", "post", "put", "delete", "patch", "options", "head"}
)
_LEGACY_TYPING_ALIASES: Final[frozenset[str]] = frozenset(
    {"List", "Dict", "Tuple", "Set", "FrozenSet", "Type"}
)


def _is_async_function(fn_node: SgNode) -> bool:
    """Return True if a Python function_definition is declared with 'async def'."""
    return fn_node.text().lstrip().startswith("async ")


def _check_async_blocking_calls(fn_node: SgNode, rel_path: str) -> list[CodeLocation]:
    """Detect synchronous blocking calls inside an async def coroutine."""
    issues: list[CodeLocation] = []
    fn_name = function_symbol_name(fn_node)
    for call in fn_node.find_all(kind="call"):
        callee = call.field("function")
        if callee is None:
            continue
        ctext = callee.text().strip()
        if ctext in _SYNC_BLOCKING_CALLS:
            issues.append(
                CodeLocation(
                    file=rel_path,
                    line=call.range().start.line + 1,
                    symbol=fn_name,
                    detail=(
                        f"Synchronous blocking call '{ctext}()' inside 'async def' blocks the event loop "
                        "(use asyncio.sleep / httpx.AsyncClient)"
                    ),
                )
            )
    return issues


def _is_fastapi_route_decorator(dec_text: str) -> bool:
    """Return True if decorator text looks like @app.get(...) or @router.post(...)."""
    body = dec_text.lstrip("@").split("(", maxsplit=1)[0].strip()
    parts = body.split(".")
    return len(parts) == 2 and parts[1] in _FASTAPI_HTTP_METHODS


class FastApiFrameworkChecker(BaseFrameworkChecker):
    """Inspect FastAPI endpoints for event-loop blocking I/O and missing response schemas."""

    framework_id: ClassVar[str] = "fastapi"

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Check async blocking calls, missing response_model/return types, and deprecated on_event."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []

        for fn_node in unit.root.find_all(kind="function_definition"):
            if _is_async_function(fn_node):
                issues.extend(_check_async_blocking_calls(fn_node, unit.rel_path))

            parent = fn_node.parent()
            if parent is None or parent.kind() != "decorated_definition":
                continue
            fn_name = function_symbol_name(fn_node)
            lineno = fn_node.range().start.line + 1
            for child in parent.named_children():
                if child.kind() != "decorator":
                    continue
                dtext = child.text().strip()
                if ".on_event(" in dtext:
                    hints.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=child.range().start.line + 1,
                            symbol=fn_name,
                            detail="Deprecated FastAPI '@app.on_event' — migrate to 'lifespan' context manager",
                        )
                    )
                if (
                    _is_fastapi_route_decorator(dtext)
                    and "response_model" not in dtext
                    and fn_node.field("return_type") is None
                ):
                    issues.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=lineno,
                            symbol=fn_name,
                            detail="FastAPI route lacks both 'response_model=' and return type annotation",
                        )
                    )

        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)


class PydanticFrameworkChecker(BaseFrameworkChecker):
    """Detect legacy Pydantic v1 idioms (.dict(), .parse_obj(), inner class Config, @validator)."""

    framework_id: ClassVar[str] = "pydantic"

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Scan for deprecated Pydantic v1 class Config and @validator patterns."""
        hints: list[CodeLocation] = []
        for cls_node in unit.root.find_all(kind="class_definition"):
            cname_node = cls_node.field("name")
            if cname_node is not None and cname_node.text() == "Config" and cls_node.inside(kind="class_definition"):
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=cls_node.range().start.line + 1,
                        symbol="class Config",
                        detail="Legacy Pydantic v1 'class Config' — migrate to 'model_config = ConfigDict(...)'",
                    )
                )
        for dec in unit.root.find_all(kind="decorator"):
            dhead = dec.text().lstrip("@").split("(", maxsplit=1)[0].strip()
            if dhead in {"validator", "root_validator"}:
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=dec.range().start.line + 1,
                        symbol=f"@{dhead}",
                        detail=f"Legacy Pydantic v1 '@{dhead}' — migrate to '@field_validator' / '@model_validator'",
                    )
                )
        return FrameworkCheckResult(modernization_hints=hints)


class FlaskModernizationChecker(BaseFrameworkChecker):
    """Emit factual REST/JSON vs template signals when Flask is detected."""

    framework_id: ClassVar[str] = "flask"

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Apply when flask is declared in manifest or imported in source units."""
        if self.framework_id in detected_frameworks:
            return True
        return any("from flask" in u.source or "import flask" in u.source for u in units)

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Detect Flask route files without HTML template rendering."""
        hints: list[CodeLocation] = []
        has_flask_route = "jsonify" in unit.source or (
            ("from flask" in unit.source or "import flask" in unit.source) and ".route(" in unit.source
        )
        if has_flask_route and "render_template" not in unit.source:
            hints.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=1,
                    symbol="Flask API",
                    detail=(
                        "Flask API endpoint without HTML template rendering — "
                        "consider FastAPI + Pydantic v2 for typed validation & automatic OpenAPI"
                    ),
                )
            )
        return FrameworkCheckResult(modernization_hints=hints)


class PythonModernSyntaxChecker(BaseFrameworkChecker):
    """Always-on Python modern syntax checker (PEP 585 builtin generics, os.path -> pathlib)."""

    framework_id: ClassVar[str] = "python-core"

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Always apply to Python source units."""
        _ = detected_frameworks
        return bool(units)

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Flag deprecated typing.List/Dict/Tuple/Set imports and os.path calls."""
        hints: list[CodeLocation] = []
        for stmt in unit.root.find_all(kind="import_from_statement"):
            mod_node = stmt.field("module_name")
            if mod_node is None or mod_node.text().strip() != "typing":
                continue
            legacy = [
                n.text().split(" as ")[0].strip()
                for n in stmt.field_children("name")
                if n.text().split(" as ")[0].strip() in _LEGACY_TYPING_ALIASES
            ]
            if legacy:
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=stmt.range().start.line + 1,
                        symbol=f"from typing import {', '.join(legacy)}",
                        detail="Legacy typing generics (UP006) — prefer PEP 585 builtin generics (list, dict, tuple)",
                    )
                )

        for call in unit.root.find_all(kind="call"):
            fn = call.field("function")
            if fn is not None and fn.text().strip().startswith("os.path."):
                callee = fn.text().strip()
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol=callee,
                        detail=f"Legacy '{callee}' usage (PTH) — prefer 'pathlib.Path' methods",
                    )
                )
        return FrameworkCheckResult(modernization_hints=hints)
