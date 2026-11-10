# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Go HTTP/gRPC framework and Go 1.18+ modernization AST checker."""

from __future__ import annotations

from typing import ClassVar

from pni._actions.ast_analyze.base import BaseFrameworkChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    FrameworkCheckResult,
    ParsedUnit,
)


class GoModernizationChecker(BaseFrameworkChecker):
    """Detect Go ecosystem modernization hints (`interface{}` -> `any`, `ioutil` deprecation, `http.ListenAndServe`)."""

    framework_id: ClassVar[str] = "go-stdlib"

    def applies_to(self, detected_frameworks: set[str], units: list[ParsedUnit]) -> bool:
        """Always apply Go standard library and modernization checks when Go units exist."""
        _ = detected_frameworks
        return bool(units)

    def inspect_unit(self, unit: ParsedUnit) -> FrameworkCheckResult:
        """Inspect a Go compilation unit for deprecated `io/ioutil`, legacy `interface{}`, and `http.ListenAndServe`."""
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []

        for spec in unit.root.find_all(kind="import_spec"):
            path_node = spec.field("path")
            if path_node is not None and path_node.text().strip().strip('"`') == "io/ioutil":
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=spec.range().start.line + 1,
                        symbol="io/ioutil",
                        detail="`io/ioutil` is deprecated since Go 1.16 — use `io` and `os` functions directly",
                    )
                )

        for iface in unit.root.find_all(kind="interface_type"):
            if iface.text().strip().replace(" ", "") == "interface{}":
                hints.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=iface.range().start.line + 1,
                        symbol="interface{}",
                        detail="Legacy `interface{}` — consider modernizing to `any` or `[T any]` (Go 1.18+)",
                    )
                )
                break

        for call in unit.root.find_all(kind="call_expression"):
            fn = call.field("function")
            if fn is not None and fn.text().strip() == "http.ListenAndServe":
                issues.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=call.range().start.line + 1,
                        symbol="http.ListenAndServe",
                        detail=(
                            "`http.ListenAndServe(...)` lacks ReadHeaderTimeout/IdleTimeout — "
                            "use `&http.Server{ReadHeaderTimeout: ...}`"
                        ),
                    )
                )

        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)
