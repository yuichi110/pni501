# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""GoDoc comment coverage checker for exported Go types, functions, and methods."""

from __future__ import annotations

import re

from pni._actions.ast_analyze.base import BaseDocChecker
from pni._actions.ast_analyze.go._helpers import (
    extract_package_name,
    extract_preceding_godoc,
    extract_receiver_type_name,
    is_exported_go_name,
    iter_go_callables,
    iter_go_type_specs,
)
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    UnitDocStats,
)


def _clean_godoc_body(raw_comment: str) -> str:
    """Strip `//` and `/* ... */` markers from a GoDoc comment block."""
    cleaned_lines: list[str] = []
    for line in raw_comment.splitlines():
        s = line.strip()
        if s.startswith("//"):
            cleaned_lines.append(s.removeprefix("//").strip())
        else:
            s = re.sub(r"^/\*+|\*+/$", "", s).strip()
            s = s.lstrip("*").strip()
            if s:
                cleaned_lines.append(s)
    return " ".join(part for part in cleaned_lines if part).strip()


def _record_godoc_status(
    raw_doc: str | None,
    rel_path: str,
    line_no: int,
    symbol: str,
    kind_label: str,
    missing: list[CodeLocation],
    empty: list[CodeLocation],
) -> bool:
    """Append missing/empty GoDoc CodeLocation if needed and return True when documented."""
    if raw_doc is None:
        missing.append(
            CodeLocation(
                file=rel_path,
                line=line_no,
                symbol=symbol,
                detail=f"Exported Go {kind_label} '{symbol}' is missing a GoDoc comment",
            )
        )
        return False
    if not _clean_godoc_body(raw_doc):
        empty.append(
            CodeLocation(
                file=rel_path,
                line=line_no,
                symbol=symbol,
                detail=f"Exported Go {kind_label} '{symbol}' has an empty GoDoc comment",
            )
        )
        return False
    return True


class GoDocChecker(BaseDocChecker):
    """Evaluate GoDoc comment presence on exported types, functions, and methods."""

    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Check exported Go declarations in unit for preceding GoDoc comments."""
        pkg_name = extract_package_name(unit)
        candidates = 0
        documented = 0
        annotated_doc_fns = 0
        missing: list[CodeLocation] = []
        empty: list[CodeLocation] = []

        for tname, tkind, spec_node, decl_node in iter_go_type_specs(unit):
            if not is_exported_go_name(tname):
                continue
            candidates += 1
            raw_doc = extract_preceding_godoc(spec_node, decl_node)
            line_no = spec_node.range().start.line + 1
            if _record_godoc_status(raw_doc, unit.rel_path, line_no, tname, tkind, missing, empty):
                documented += 1

        for qual, short, node in iter_go_callables(unit):
            if (pkg_name == "main" and short == "main") or not is_exported_go_name(short):
                continue
            if node.kind() == "method_declaration":
                recv = extract_receiver_type_name(node)
                if recv and not is_exported_go_name(recv):
                    continue
            candidates += 1
            raw_doc = extract_preceding_godoc(node)
            line_no = node.range().start.line + 1
            if _record_godoc_status(raw_doc, unit.rel_path, line_no, qual, "callable", missing, empty):
                documented += 1
                annotated_doc_fns += 1

        return UnitDocStats(
            candidates=candidates,
            documented=documented,
            annotated_doc_functions=annotated_doc_fns,
            missing_docstrings=missing,
            empty_docstrings=empty,
            doc_signature_mismatches=[],
        )
