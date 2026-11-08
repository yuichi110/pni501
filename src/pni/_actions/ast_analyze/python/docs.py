# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python module, class, and function docstring presence, quality, and signature checker."""

from __future__ import annotations

import re
from typing import Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseDocChecker
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit, UnitDocStats
from pni._actions.ast_analyze.python._helpers import (
    VALID_PARAM_KINDS,
    extract_callable_param_names,
    extract_param_name,
    extract_python_docstring_text,
    function_symbol_name,
    is_overload_decorated,
)

_PLACEHOLDER_WORDS: Final[frozenset[str]] = frozenset({"todo", "tbd", "fixme", "wip", "..."})
_SPHINX_PARAM_RE = re.compile(r":param\s+(?:\w+\s+)?\*?\*?([A-Za-z_][A-Za-z0-9_]*)\s*:")
_GOOGLE_ARG_LINE_RE = re.compile(r"^\*{0,2}([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*:")
_GOOGLE_SECTION_STOP: Final[frozenset[str]] = frozenset(
    {
        "returns:",
        "return:",
        "yields:",
        "yield:",
        "raises:",
        "examples:",
        "example:",
        "notes:",
        "note:",
        "attributes:",
    }
)


def _is_empty_or_placeholder_doc(doc_text: str) -> bool:
    """Return True if a docstring body is blank or contains only a placeholder word."""
    cleaned = doc_text.strip().rstrip(".!").strip().lower()
    return not cleaned or cleaned in _PLACEHOLDER_WORDS


def _unquote_string_literal(raw_text: str) -> str:
    """Strip string prefixes and surrounding quotes from a Python string literal."""
    clean = raw_text.lstrip("rRuUfFbB")
    for delim in ('"""', "'''", '"', "'"):
        if clean.startswith(delim) and clean.endswith(delim) and len(clean) >= 2 * len(delim):
            return clean[len(delim) : -len(delim)]
    return clean


def _extract_string_arg_text(arg_node: SgNode) -> str | None:
    """Extract string text from a string or concatenated_string CST argument node."""
    if arg_node.kind() == "string":
        return _unquote_string_literal(arg_node.text())
    if arg_node.kind() == "concatenated_string":
        parts = [_unquote_string_literal(c.text()) for c in arg_node.named_children() if c.kind() == "string"]
        return "".join(parts) if parts else None
    return None


def _extract_annotated_doc_texts(type_node: SgNode | None) -> list[str]:
    """Extract PEP 727 `Doc("...")` string literals inside an `Annotated[...]` type annotation."""
    if type_node is None or "Annotated" not in type_node.text():
        return []
    docs: list[str] = []
    for call in type_node.find_all(kind="call"):
        fn = call.field("function")
        if fn is None:
            continue
        fn_text = fn.text().strip()
        if fn_text != "Doc" and not fn_text.endswith(".Doc"):
            continue
        args = call.field("arguments")
        arg_nodes = [c for c in (args.named_children() if args is not None else []) if c.kind() != "comment"]
        if not arg_nodes:
            continue
        first_arg = arg_nodes[0]
        if first_arg.kind() == "keyword_argument":
            val = first_arg.field("value")
            text = _extract_string_arg_text(val) if val is not None else None
        else:
            text = _extract_string_arg_text(first_arg)
        if text is not None:
            docs.append(text)
    return docs


def _inspect_callable_annotated_docs(fn_node: SgNode) -> tuple[set[str], list[str]]:
    """Collect parameter names documented via PEP 727 `Annotated[..., Doc()]` and all extracted Doc strings."""
    annotated_params: set[str] = set()
    all_texts: list[str] = []
    params_node = fn_node.field("parameters")
    if params_node is not None:
        for param in params_node.named_children():
            if param.kind() not in VALID_PARAM_KINDS:
                continue
            pname = extract_param_name(param)
            if pname in {"self", "cls", ""}:
                continue
            p_docs = _extract_annotated_doc_texts(param.field("type"))
            if p_docs:
                all_texts.extend(p_docs)
                if any(not _is_empty_or_placeholder_doc(t) for t in p_docs):
                    annotated_params.add(pname)

    all_texts.extend(_extract_annotated_doc_texts(fn_node.field("return_type")))
    return annotated_params, all_texts


def _parse_google_args_section(doc_text: str) -> list[str]:
    """Extract parameter names documented under Google-style 'Args:' / 'Keyword Args:' sections."""
    lines = doc_text.splitlines()
    in_args = False
    section_indent = 0
    entry_indent: int | None = None
    params: list[str] = []

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        lower = stripped.lower()

        if lower in {"args:", "arguments:", "keyword args:", "parameters:"}:
            in_args = True
            section_indent = indent
            entry_indent = None
            continue

        if not in_args:
            continue

        if indent <= section_indent or lower in _GOOGLE_SECTION_STOP:
            in_args = False
            continue

        if entry_indent is None:
            entry_indent = indent
        if indent == entry_indent:
            match = _GOOGLE_ARG_LINE_RE.match(stripped)
            if match:
                pname = match.group(1)
                if pname not in params:
                    params.append(pname)
    return params


def _extract_documented_params(doc_text: str) -> list[str]:
    """Extract documented parameter names from Google or Sphinx docstring conventions."""
    google_params = _parse_google_args_section(doc_text)
    if google_params:
        return google_params
    sphinx_matches = _SPHINX_PARAM_RE.findall(doc_text)
    return list(dict.fromkeys(sphinx_matches))


def _check_signature_mismatch(
    fn_node: SgNode,
    fn_name: str,
    doc_text: str,
    rel_path: str,
    annotated_params: set[str] | None = None,
) -> CodeLocation | None:
    """Compare documented parameter names against actual AST parameters when Args section exists."""
    doc_params = _extract_documented_params(doc_text)
    if not doc_params:
        return None

    actual_set = set(extract_callable_param_names(fn_node))
    doc_set = set(doc_params)
    combined_doc = doc_set | (annotated_params or set())
    missing_in_doc = sorted(actual_set - combined_doc)
    stale_in_doc = sorted(doc_set - actual_set)
    if not missing_in_doc and not stale_in_doc:
        return None

    parts: list[str] = []
    if missing_in_doc:
        parts.append(f"undocumented={missing_in_doc}")
    if stale_in_doc:
        parts.append(f"stale_in_docstring={stale_in_doc}")

    return CodeLocation(
        file=rel_path,
        line=fn_node.range().start.line + 1,
        symbol=fn_name,
        detail=f"Docstring Args mismatch ({', '.join(parts)})",
    )


def _evaluate_doc_target(
    container: SgNode | None,
    rel_path: str,
    line: int,
    symbol: str,
    missing_label: str,
    missing: list[CodeLocation],
    empty: list[CodeLocation],
) -> bool:
    """Check one doc candidate, appending missing or empty findings and returning True if documented."""
    doc_text = extract_python_docstring_text(container)
    if doc_text is None:
        missing.append(CodeLocation(file=rel_path, line=line, symbol=symbol, detail=missing_label))
        return False
    if _is_empty_or_placeholder_doc(doc_text):
        empty.append(
            CodeLocation(
                file=rel_path,
                line=line,
                symbol=symbol,
                detail="Empty or placeholder (TODO/TBD) docstring",
            )
        )
        return False
    return True


def _evaluate_callable_doc(
    fn_node: SgNode,
    fn_name: str,
    rel_path: str,
    missing: list[CodeLocation],
    empty: list[CodeLocation],
    mismatches: list[CodeLocation],
) -> tuple[bool, bool]:
    """Evaluate a public callable via leading docstring or PEP 727 Annotated[..., Doc()] metadata."""
    body = fn_node.field("body")
    lineno = fn_node.range().start.line + 1
    doc_text = extract_python_docstring_text(body)
    annotated_params, annotated_texts = _inspect_callable_annotated_docs(fn_node)

    if doc_text is not None:
        if _is_empty_or_placeholder_doc(doc_text):
            if annotated_texts and any(not _is_empty_or_placeholder_doc(t) for t in annotated_texts):
                return True, True
            empty.append(
                CodeLocation(
                    file=rel_path,
                    line=lineno,
                    symbol=fn_name,
                    detail="Empty or placeholder (TODO/TBD) docstring",
                )
            )
            return False, False
        mm = _check_signature_mismatch(fn_node, fn_name, doc_text, rel_path, annotated_params)
        if mm is not None:
            mismatches.append(mm)
        return True, bool(annotated_texts)

    if annotated_texts:
        if any(not _is_empty_or_placeholder_doc(t) for t in annotated_texts):
            return True, True
        empty.append(
            CodeLocation(
                file=rel_path,
                line=lineno,
                symbol=fn_name,
                detail="Empty or placeholder PEP 727 Annotated Doc() metadata",
            )
        )
        return False, False

    missing.append(
        CodeLocation(
            file=rel_path,
            line=lineno,
            symbol=fn_name,
            detail="Missing public function/method docstring",
        )
    )
    return False, False


def _is_private_or_protocol_stub_method(fn_node: SgNode) -> bool:
    """Return True if fn_node belongs to a private _Class or is an ellipsis (...) stub in a Protocol."""
    curr = fn_node.parent()
    while curr is not None:
        if curr.kind() == "class_definition":
            cname_node = curr.field("name")
            if cname_node is not None and cname_node.text().startswith("_"):
                return True
            superclasses = curr.field("superclasses")
            if superclasses is not None and "Protocol" in superclasses.text():
                body = fn_node.field("body")
                stmts = [c for c in (body.named_children() if body else []) if c.kind() != "comment"]
                if len(stmts) == 1 and stmts[0].text().strip() == "...":
                    return True
        curr = curr.parent()
    return False


def _should_skip_callable_doc(fn_node: SgNode, fn_name: str) -> bool:
    """Return True if a Python callable is private, nested, @overload, or a Protocol/private-class stub."""
    is_nested = fn_node.parent() is not None and fn_node.inside(kind="function_definition")
    return (
        fn_name.startswith("_")
        or is_nested
        or is_overload_decorated(fn_node)
        or _is_private_or_protocol_stub_method(fn_node)
    )


class PythonDocChecker(BaseDocChecker):
    """Check Python module/class/function docstrings, PEP 727 Doc(), placeholder docs, and Args consistency."""

    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Inspect module, public classes, and non-nested public callables in a Python unit."""
        candidates = 1
        documented = 0
        annotated_doc_fns = 0
        missing: list[CodeLocation] = []
        empty: list[CodeLocation] = []
        mismatches: list[CodeLocation] = []

        if _evaluate_doc_target(
            unit.root, unit.rel_path, 1, "<module>", "Missing module docstring", missing, empty
        ):
            documented += 1

        for cls_node in unit.root.find_all(kind="class_definition"):
            cname_node = cls_node.field("name")
            cname = cname_node.text() if cname_node is not None else "<class>"
            if cname.startswith("_"):
                continue
            candidates += 1
            if _evaluate_doc_target(
                cls_node.field("body"),
                unit.rel_path,
                cls_node.range().start.line + 1,
                cname,
                "Missing public class docstring",
                missing,
                empty,
            ):
                documented += 1

        for fn_node in unit.root.find_all(kind="function_definition"):
            fn_name = function_symbol_name(fn_node)
            if _should_skip_callable_doc(fn_node, fn_name):
                continue
            candidates += 1
            is_doc, used_annotated_doc = _evaluate_callable_doc(
                fn_node,
                fn_name,
                unit.rel_path,
                missing,
                empty,
                mismatches,
            )
            if is_doc:
                documented += 1
            if used_annotated_doc:
                annotated_doc_fns += 1

        return UnitDocStats(
            candidates=candidates,
            documented=documented,
            annotated_doc_functions=annotated_doc_fns,
            missing_docstrings=missing,
            empty_docstrings=empty,
            doc_signature_mismatches=mismatches,
        )
