# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic Mermaid generator helpers and 2-layer (static + Playwright mermaid.parse) validator."""

from __future__ import annotations

import contextlib
import re
from pathlib import Path
from typing import Final, Literal, Optional

from pydantic import BaseModel, Field

SUPPORTED_MERMAID_HEADERS: Final[tuple[str, ...]] = (
    "flowchart",
    "graph",
    "sequencediagram",
    "statediagram",
    "statediagram-v2",
    "classdiagram",
    "erdiagram",
    "xychart-beta",
)
_RESERVED_NODE_IDS: Final[frozenset[str]] = frozenset(
    {"end", "subgraph", "style", "class", "classdef", "click", "graph", "flowchart", "linkstyle"}
)
_EDGE_SPLIT_RE: Final[re.Pattern[str]] = re.compile(r"\s*(?:-->|==>|-.->|---|===|--\|[^|]*\|-->|--\|[^|]*\|)\s*")
_NODE_BRACKET_RE: Final[re.Pattern[str]] = re.compile(r"\b([A-Za-z_][A-Za-z0-9_-]*)\s*\[([^\]\"]*)\]")
_RAW_HTML_TAG_RE: Final[re.Pattern[str]] = re.compile(r"<(?!/?br\s*/?>)[a-zA-Z][^>]*>", re.IGNORECASE)
_FENCED_MERMAID_RE: Final[re.Pattern[str]] = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


class MermaidValidationIssue(BaseModel):
    """Single syntax or structural issue found in a Mermaid diagram block."""

    line: int = Field(ge=1)
    code: str
    message: str


class MermaidValidationResult(BaseModel):
    """Outcome of validating a Mermaid diagram via static rules and/or Playwright mermaid.parse()."""

    valid: bool
    engine: Literal["static", "playwright_mermaid"] = "static"
    diagram_type: str = ""
    issues: list[MermaidValidationIssue] = Field(default_factory=list)


def sanitize_mermaid_id(raw: str) -> str:
    """Convert any identifier into a valid, non-reserved Mermaid node ID."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", raw.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"n_{cleaned}" if cleaned else "n_node"
    if cleaned.lower() in _RESERVED_NODE_IDS:
        cleaned = f"node_{cleaned}"
    return cleaned


def escape_mermaid_label(raw: str) -> str:
    """Escape a human-readable label for safe inclusion inside Mermaid double-quoted labels."""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace('"', "'")
    text = _RAW_HTML_TAG_RE.sub("", text)
    text = text.replace("\n", "<br/>")
    return text.strip()


def extract_mermaid_blocks(text: str) -> list[str]:
    """Extract fenced ```mermaid ... ``` blocks from Markdown, or return [text] if raw Mermaid."""
    blocks = [m.group(1).strip() for m in _FENCED_MERMAID_RE.finditer(text)]
    if blocks:
        return blocks
    stripped = text.strip()
    return [stripped] if stripped else []


def _check_flowchart_line(lineno: int, stripped: str, issues: list[MermaidValidationIssue]) -> None:
    """Validate flowchart/graph node IDs, label quoting, and unsafe raw HTML on one line."""
    if _RAW_HTML_TAG_RE.search(stripped):
        issues.append(
            MermaidValidationIssue(
                line=lineno,
                code="MM-HTML",
                message="Disallowed HTML tag in Mermaid diagram (only <br/> is allowed inside quoted labels).",
            )
        )

    for match in _NODE_BRACKET_RE.finditer(stripped):
        node_id, label_body = match.group(1), match.group(2)
        if node_id.lower() in _RESERVED_NODE_IDS:
            issues.append(
                MermaidValidationIssue(
                    line=lineno,
                    code="MM-RESERVED-ID",
                    message=f"Reserved Mermaid keyword '{node_id}' cannot be used as a node ID.",
                )
            )
        if any(ch in label_body for ch in ("(", ")", "{", "}", "[", "]", ":", ";")):
            issues.append(
                MermaidValidationIssue(
                    line=lineno,
                    code="MM-UNQUOTED-SPECIAL",
                    message=(
                        f"Node '{node_id}' contains special characters inside unquoted [...] label; "
                        f'quote it as {node_id}["..."].'
                    ),
                )
            )

    parts = _EDGE_SPLIT_RE.split(stripped)
    if len(parts) > 1:
        for seg in parts:
            tok = seg.strip().split(maxsplit=1)[0] if seg.strip() else ""
            bare_id = re.split(r"[\[\(\{\|]", tok, maxsplit=1)[0].strip()
            if bare_id.lower() == "end":
                issues.append(
                    MermaidValidationIssue(
                        line=lineno,
                        code="MM-RESERVED-ID",
                        message="Reserved keyword 'end' used as an edge endpoint; rename node ID (e.g., node_end).",
                    )
                )


def _check_body_line(
    lineno: int,
    stripped: str,
    diagram_type: str,
    subgraph_depth: int,
    issues: list[MermaidValidationIssue],
) -> int:
    """Validate one non-header Mermaid body line and return updated subgraph_depth."""
    if stripped.count('"') % 2 != 0:
        issues.append(
            MermaidValidationIssue(
                line=lineno,
                code="MM-UNBALANCED-QUOTE",
                message="Unbalanced double quotes on Mermaid line.",
            )
        )
    low = stripped.lower()
    if low.startswith("subgraph ") or low == "subgraph":
        return subgraph_depth + 1
    if low == "end":
        if subgraph_depth <= 0 and diagram_type in {"flowchart", "graph"}:
            issues.append(
                MermaidValidationIssue(
                    line=lineno,
                    code="MM-UNMATCHED-END",
                    message="Found 'end' without a matching 'subgraph'.",
                )
            )
            return subgraph_depth
        return max(0, subgraph_depth - 1)
    if diagram_type in {"flowchart", "graph"} and not low.startswith(("classdef ", "class ", "style ", "click ")):
        _check_flowchart_line(lineno, stripped, issues)
    return subgraph_depth


def _check_header_and_blocks(lines: list[str]) -> tuple[str, list[MermaidValidationIssue]]:
    """Validate Mermaid diagram header, subgraph/end balance, and double-quote balance."""
    issues: list[MermaidValidationIssue] = []
    diagram_type = ""
    subgraph_depth = 0

    for lineno, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        if not diagram_type:
            first_tok = stripped.split(maxsplit=1)[0].lower()
            if first_tok not in SUPPORTED_MERMAID_HEADERS:
                issues.append(
                    MermaidValidationIssue(
                        line=lineno,
                        code="MM-HEADER",
                        message=(
                            f"Unsupported or missing Mermaid diagram header '{first_tok}'. "
                            f"Expected one of: {', '.join(SUPPORTED_MERMAID_HEADERS)}."
                        ),
                    )
                )
                return first_tok, issues
            diagram_type = first_tok
            continue
        subgraph_depth = _check_body_line(lineno, stripped, diagram_type, subgraph_depth, issues)

    if not diagram_type:
        issues.append(MermaidValidationIssue(line=1, code="MM-EMPTY", message="Mermaid diagram content is empty."))
    elif subgraph_depth > 0:
        issues.append(
            MermaidValidationIssue(
                line=len(lines),
                code="MM-UNCLOSED-SUBGRAPH",
                message=f"{subgraph_depth} unclosed 'subgraph' block(s) missing matching 'end'.",
            )
        )
    return diagram_type, issues


def validate_mermaid_static(code: str) -> MermaidValidationResult:
    """Run Layer-1 (<1 ms) pure-Python Mermaid syntax and structural guardrail checks."""
    lines = code.splitlines()
    diagram_type, issues = _check_header_and_blocks(lines)
    return MermaidValidationResult(
        valid=len(issues) == 0,
        engine="static",
        diagram_type=diagram_type,
        issues=issues,
    )


def _find_local_mermaid_js(explicit_path: Optional[Path] = None) -> Optional[Path]:
    """Locate a local mermaid.min.js bundle if provided or cached under ~/.cache/pni or .pni/cache."""
    candidates: list[Path] = []
    if explicit_path is not None:
        candidates.append(explicit_path)
    candidates.extend(
        [
            Path.home() / ".cache" / "pni" / "mermaid.min.js",
            Path(".pni/cache/mermaid.min.js"),
        ]
    )
    for cand in candidates:
        if cand.is_file() and cand.stat().st_size > 0:
            return cand
    return None


def validate_mermaid_with_browser(
    code: str,
    *,
    mermaid_js_path: Optional[Path] = None,
) -> MermaidValidationResult:
    """Run Layer-2 official mermaid.parse() validation inside Playwright Chromium when available."""
    static_res = validate_mermaid_static(code)
    if not static_res.valid:
        return static_res

    js_path = _find_local_mermaid_js(mermaid_js_path)
    if js_path is None:
        return static_res

    with contextlib.suppress(Exception):
        from playwright.sync_api import sync_playwright  # noqa: PLC0415

        js_src = js_path.read_text(encoding="utf-8", errors="ignore")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_content("<!doctype html><html><body></body></html>")
                page.add_script_tag(content=js_src)
                err_msg = page.evaluate(
                    """async (src) => {
                        try {
                            mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });
                            await mermaid.parse(src);
                            return null;
                        } catch (e) {
                            return String(e && e.message ? e.message : e);
                        }
                    }""",
                    code,
                )
            finally:
                browser.close()
        if err_msg:
            return MermaidValidationResult(
                valid=False,
                engine="playwright_mermaid",
                diagram_type=static_res.diagram_type,
                issues=[MermaidValidationIssue(line=1, code="MM-PARSE-ERROR", message=str(err_msg)[:300])],
            )
        return MermaidValidationResult(
            valid=True,
            engine="playwright_mermaid",
            diagram_type=static_res.diagram_type,
            issues=[],
        )

    return static_res


def _validate_single_mermaid_block(
    block: str,
    *,
    use_browser: bool = False,
    mermaid_js_path: Optional[Path] = None,
) -> MermaidValidationResult:
    """Validate one extracted Mermaid diagram block."""
    if use_browser:
        return validate_mermaid_with_browser(block, mermaid_js_path=mermaid_js_path)
    return validate_mermaid_static(block)


def validate_mermaid(
    code: str,
    *,
    use_browser: bool = False,
    mermaid_js_path: Optional[Path] = None,
) -> MermaidValidationResult:
    """Validate raw Mermaid or fenced ```mermaid blocks inside Markdown."""
    blocks = extract_mermaid_blocks(code)
    if not blocks:
        return validate_mermaid_static("")
    if len(blocks) == 1:
        return _validate_single_mermaid_block(blocks[0], use_browser=use_browser, mermaid_js_path=mermaid_js_path)

    all_issues: list[MermaidValidationIssue] = []
    engine: Literal["static", "playwright_mermaid"] = "static"
    first_type = ""
    for idx, blk in enumerate(blocks, start=1):
        res = _validate_single_mermaid_block(blk, use_browser=use_browser, mermaid_js_path=mermaid_js_path)
        if not first_type and res.diagram_type:
            first_type = res.diagram_type
        if res.engine == "playwright_mermaid":
            engine = "playwright_mermaid"
        for iss in res.issues:
            all_issues.append(
                MermaidValidationIssue(
                    line=iss.line,
                    code=iss.code,
                    message=f"[diagram #{idx}] {iss.message}",
                )
            )
    return MermaidValidationResult(
        valid=len(all_issues) == 0,
        engine=engine,
        diagram_type=first_type,
        issues=all_issues,
    )
