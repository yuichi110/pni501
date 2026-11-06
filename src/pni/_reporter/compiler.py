# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Drawlib project scaffolding and non-destructive report compiler via drawlib.tools."""

from __future__ import annotations

import importlib
import re
import shutil
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import Final, Protocol, cast

from pni._reporter.base_model import (
    DEFAULT_REPORT_FORMATS,
    DEFAULT_REPORT_OUTPUT_DIR,
    DEFAULT_REPORT_SRC_DIR,
    SUPPORTED_REPORT_FORMATS,
    BrokenLinkRecord,
    ReportBuildResult,
    ReportScaffoldResult,
)

_STARTER_SAMPLE_CHAPTERS = (
    "00_cover.md",
    "01_overview.md",
    "02_design.md",
)
_SAFE_LANG_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
_DRAWLIB_FENCE_RE: Final[re.Pattern[str]] = re.compile(r"```drawlib([^\n]*)\n(.*?)```", re.DOTALL)
_FENCE_FILE_ATTR_RE: Final[re.Pattern[str]] = re.compile(r"file=([^\s\"']+)")


def lint_drawlib_chapters(chapters: Sequence[Path]) -> list[str]:
    """Scan chapter Markdown drawlib blocks for missing multi-series legends and contour-line collisions."""
    warnings: list[str] = []
    for md_path in chapters:
        if not md_path.is_file():
            continue
        content = md_path.read_text(encoding="utf-8")
        for match in _DRAWLIB_FENCE_RE.finditer(content):
            header, code = match.group(1), match.group(2)
            file_match = _FENCE_FILE_ATTR_RE.search(header)
            fig_name = file_match.group(1) if file_match is not None else "inline"

            is_multi_chart = ("BarChart(" in code or "LineChart(" in code) and code.count(".add_series(") >= 2
            if is_multi_chart and ".draw_legend(" not in code:
                warnings.append(
                    f"{md_path.name} ({fig_name}): multi-series BarChart/LineChart (>=2 add_series) "
                    "is missing chart.draw_legend(...)"
                )

            if "ClassDiagram(" in code and "HeatmapOverlay(" in code and "show_contour_lines=True" in code:
                warnings.append(
                    f"{md_path.name} ({fig_name}): ClassDiagram + HeatmapOverlay uses show_contour_lines=True; "
                    "set show_contour_lines=False to avoid contour label collisions"
                )
    return warnings


class _DrawlibToolsProtocol(Protocol):
    """Typed protocol for lazily imported drawlib.tools functions (drawlib >= 0.3.5)."""

    def init_project(
        self,
        project_type: str,
        *,
        destination: Path,
        target: str,
        force: bool,
        lang: str,
        style: str,
    ) -> list[Path]: ...

    def build_html(
        self,
        input_dir: str,
        /,
        *,
        output_dir: str,
        styles_path: str | None,
        utils_path: str | None,
        no_cache: bool,
    ) -> object: ...

    def build_markdown(
        self,
        input_dir: str,
        /,
        *,
        output_dir: str,
        styles_path: str | None,
        utils_path: str | None,
        no_cache: bool,
    ) -> object: ...

    def build_image(
        self,
        input_path: str,
        /,
        *,
        output_path: str,
        styles_path: str | None,
        utils_path: str | None,
        no_cache: bool,
    ) -> object: ...

    def build_pdf(
        self,
        input_path: str,
        /,
        *,
        output_file: str,
        page_break: bool,
        generate_index: bool,
        styles_path: str | None,
        utils_path: str | None,
        no_cache: bool,
    ) -> object: ...

    def scan_broken_links(self, html_dir: str, /) -> tuple[int, int, list[tuple[str, str, str]]]: ...


def _get_drawlib_tools() -> _DrawlibToolsProtocol:
    """Lazily import drawlib.tools only when report commands are executed."""
    return cast(_DrawlibToolsProtocol, importlib.import_module("drawlib.tools"))


def normalize_report_target(target_or_path: str, default_src_base: Path) -> tuple[str, Path]:
    """Normalize a target name or path (e.g., 'python_clean' or 'reports_src/python_clean_src').

    Args:
        target_or_path: Target name or relative path to '<target>_src'.
        default_src_base: Default base directory holding '*_src' folders.

    Returns:
        tuple[str, Path]: Clean target name (without '_src') and resolved src_base_dir.
    """
    cleaned = target_or_path.strip().rstrip("/")
    if "/" in cleaned or "\\" in cleaned:
        p = Path(cleaned)
        target_name = p.name.removesuffix("_src")
        return target_name or "report", p.parent
    return cleaned.removesuffix("_src") or "report", default_src_base


def _validate_locale_code(src_dir: Path, raw_lang: str) -> str:
    """Validate that a locale code is safe and resolves strictly within src_dir."""
    code = raw_lang.strip()
    if not _SAFE_LANG_RE.match(code):
        msg = f"Invalid locale code '{raw_lang}' in '{src_dir / 'drawlib.toml'}'."
        raise ValueError(msg)
    resolved_root = src_dir.resolve()
    resolved_sub = (resolved_root / code).resolve()
    if resolved_sub == resolved_root or not resolved_sub.is_relative_to(resolved_root):
        msg = f"Locale directory '{raw_lang}' escapes report source root '{src_dir}'."
        raise ValueError(msg)
    return code


def _parse_lang_spec(src_dir: Path, lang_spec: str) -> list[str]:
    """Parse a comma-separated locale string (e.g. 'en' or 'en,ja') into validated codes."""
    codes = [_validate_locale_code(src_dir, part) for part in lang_spec.split(",") if part.strip()]
    return codes or [_validate_locale_code(src_dir, "en")]


def _read_drawlib_i18n_config(src_dir: Path, *, fallback_lang: str = "en") -> tuple[str, list[str]]:
    """Read [i18n] default_lang and langs from <src_dir>/drawlib.toml."""
    manifest_path = src_dir / "drawlib.toml"
    if not manifest_path.is_file():
        codes = _parse_lang_spec(src_dir, fallback_lang)
        return codes[0], codes

    parsed = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    i18n = parsed.get("i18n")
    if not isinstance(i18n, dict):
        codes = _parse_lang_spec(src_dir, fallback_lang)
        return codes[0], codes

    raw_langs = i18n.get("langs")
    langs = (
        [_validate_locale_code(src_dir, str(item)) for item in raw_langs if str(item).strip()]
        if isinstance(raw_langs, list)
        else []
    )
    if not langs:
        langs = _parse_lang_spec(src_dir, fallback_lang)

    raw_default = i18n.get("default_lang")
    default_lang = _validate_locale_code(src_dir, str(raw_default)) if isinstance(raw_default, str) else langs[0]
    if default_lang not in langs:
        langs = [default_lang, *langs]
    return default_lang, langs


def _find_locale_chapters(locale_dir: Path) -> list[Path]:
    """Return sorted chapter Markdown files inside a single <src_dir>/<lang>/ directory."""
    if not locale_dir.is_dir():
        return []
    return [
        md_file
        for md_file in sorted(locale_dir.glob("*.md"))
        if md_file.name not in {"README.md", "navbar.md"} and not md_file.name.startswith("_")
    ]


def _find_chapter_markdown_files(src_dir: Path, *, fallback_lang: str = "en") -> list[Path]:
    """Return sorted chapter Markdown files across configured <src_dir>/<lang>/ directories."""
    if not src_dir.is_dir():
        return []
    _, langs = _read_drawlib_i18n_config(src_dir, fallback_lang=fallback_lang)
    chapters: list[Path] = []
    for lc in langs:
        chapters.extend(_find_locale_chapters(src_dir / lc))
    return chapters


def _snapshot_existing_chapters(src_dir: Path, *, fallback_lang: str) -> dict[tuple[str, str], str]:
    """Snapshot existing localized chapter Markdown files keyed by (lang, filename)."""
    if not src_dir.is_dir():
        return {}
    _, langs = _read_drawlib_i18n_config(src_dir, fallback_lang=fallback_lang)
    snapshot: dict[tuple[str, str], str] = {}
    for lc in langs:
        for md_path in _find_locale_chapters(src_dir / lc):
            snapshot[(lc, md_path.name)] = md_path.read_text(encoding="utf-8")
    return snapshot


def _normalize_formats(formats: Sequence[str]) -> list[str]:
    """Validate and deduplicate requested report output formats."""
    normalized: list[str] = []
    for raw in formats:
        for part in raw.split(","):
            fmt = part.strip().lower()
            if not fmt:
                continue
            if fmt not in SUPPORTED_REPORT_FORMATS:
                allowed = ", ".join(sorted(SUPPORTED_REPORT_FORMATS))
                msg = f"Unsupported report format '{fmt}'. Supported formats: {allowed}"
                raise ValueError(msg)
            if fmt not in normalized:
                normalized.append(fmt)
    return normalized or list(DEFAULT_REPORT_FORMATS)


def _unlink_missing_starter_samples(
    src_dir: Path,
    langs: Sequence[str],
    keep_keys: set[tuple[str, str]],
) -> None:
    """Remove starter sample Markdown files in each locale unless present in keep_keys."""
    for lc in langs:
        loc_dir = src_dir / lc
        for sample_name in _STARTER_SAMPLE_CHAPTERS:
            if (lc, sample_name) not in keep_keys:
                sample_path = loc_dir / sample_name
                if sample_path.exists():
                    sample_path.unlink()


def _restore_or_clean_chapters(
    src_dir: Path,
    langs: Sequence[str],
    existing_chapters: dict[tuple[str, str], str],
    *,
    clean_sample_chapters: bool,
) -> None:
    """Restore pre-existing localized chapter files or clean starter samples on fresh init."""
    if existing_chapters:
        _unlink_missing_starter_samples(src_dir, langs, set(existing_chapters))
        for (lc, name), content in existing_chapters.items():
            loc_dir = src_dir / lc
            loc_dir.mkdir(parents=True, exist_ok=True)
            (loc_dir / name).write_text(content, encoding="utf-8")
        return

    if clean_sample_chapters:
        _unlink_missing_starter_samples(src_dir, langs, set())


_PRINT_TABLE_CSS_MARKER: Final[str] = "Wide-table print optimization for PNI audit matrices"
_PRINT_TABLE_CSS_BLOCK: Final[str] = """
@media print {
    /* Wide-table print optimization for PNI audit matrices */
    th, th code {
        white-space: nowrap;
    }
    td {
        font-size: 9pt;
        line-height: 1.45;
        vertical-align: top;
    }
    td code {
        overflow-wrap: anywhere;
        word-break: break-word;
    }
}
"""


def _ensure_print_table_css(src_dir: Path, created_files: Sequence[Path]) -> None:
    """Append wide-table @media print CSS rules to scaffolded style.css files if not already present."""
    candidates: list[Path] = [
        src_dir / "_assets" / "style.css",
        src_dir / "style.css",
        *(p for p in created_files if p.name == "style.css"),
    ]
    seen: set[Path] = set()
    for css_path in candidates:
        resolved = css_path.resolve()
        if resolved in seen or not css_path.is_file():
            continue
        seen.add(resolved)
        existing = css_path.read_text(encoding="utf-8")
        if _PRINT_TABLE_CSS_MARKER not in existing:
            css_path.write_text(existing.rstrip() + "\n" + _PRINT_TABLE_CSS_BLOCK, encoding="utf-8")


def scaffold_report_project(
    target: str = "full_audit",
    *,
    src_base_dir: Path = Path(DEFAULT_REPORT_SRC_DIR),
    project_type: str = "doc",
    lang: str = "en",
    style: str = "google",
    clean_sample_chapters: bool = True,
    force: bool = False,
) -> ReportScaffoldResult:
    """Scaffold or refresh <src_base_dir>/<target>_src/ without deleting existing chapter documents.

    Args:
        target: Target prefix name creating '<src_base_dir>/<target>_src/'.
        src_base_dir: Base directory for report source projects (default 'reports_src').
        project_type: Drawlib project type ('doc' recommended for linear A4 PDF reports).
        lang: Localized typography and stylesheet language ('en', 'ja', or 'en,ja').
        style: Drawlib preset theme ('google', 'default', 'monochrome').
        clean_sample_chapters: Remove starter sample chapters on initial creation.
        force: Refresh theme/template/scripts even if initialized (always preserves existing '*.md' chapters).

    Returns:
        ReportScaffoldResult: Paths, preservation status, and scaffolded files metadata.
    """
    clean_target, eff_base = normalize_report_target(target, src_base_dir)
    resolved_base = eff_base.resolve()
    src_dir = resolved_base / f"{clean_target}_src"

    existing_chapters = _snapshot_existing_chapters(src_dir, fallback_lang=lang)
    if src_dir.is_dir() and not force:
        _ensure_print_table_css(src_dir, ())
        return ReportScaffoldResult(
            src_base_dir=resolved_base,
            src_dir=src_dir,
            project_type=project_type,
            target=clean_target,
            lang=lang,
            style=style,
            preserved_existing=True,
            created_files=[],
        )

    resolved_base.mkdir(parents=True, exist_ok=True)
    drawlib_tools = _get_drawlib_tools()
    raw_created = drawlib_tools.init_project(
        project_type,
        destination=resolved_base,
        target=clean_target,
        force=force,
        lang=lang,
        style=style,
    )

    _, target_langs = _read_drawlib_i18n_config(src_dir, fallback_lang=lang)
    _restore_or_clean_chapters(
        src_dir,
        target_langs,
        existing_chapters,
        clean_sample_chapters=clean_sample_chapters,
    )
    _ensure_print_table_css(src_dir, raw_created)
    kept_files = [p for p in raw_created if p.exists()]
    return ReportScaffoldResult(
        src_base_dir=resolved_base,
        src_dir=src_dir,
        project_type=project_type,
        target=clean_target,
        lang=lang,
        style=style,
        preserved_existing=bool(existing_chapters),
        created_files=kept_files,
    )


def _normalize_compiled_pdf(
    out_dir: Path,
    clean_target: str,
    default_lang: str,
    langs: Sequence[str],
    pdf_candidate: Path,
    raw_ret: object,
) -> Path:
    """Normalize drawlib >= 0.3.5 '<target>_<default_lang>.pdf' output to '<target>.pdf'."""
    if isinstance(raw_ret, (str, Path)) and str(raw_ret).strip():
        emitted = Path(raw_ret).resolve()
    else:
        emitted = (out_dir / f"{clean_target}_{default_lang}.pdf").resolve()

    resolved_target = pdf_candidate.resolve()
    if emitted.is_file() and emitted != resolved_target:
        if len(langs) <= 1:
            emitted.replace(resolved_target)
        else:
            shutil.copy2(emitted, resolved_target)
    return pdf_candidate


def _collect_deliverables(
    pdf_file: Path | None,
    html_index: Path | None,
    markdown_dir: Path | None,
    images_dir: Path | None,
) -> list[Path]:
    """Collect non-empty compiled output artifacts in deterministic order."""
    deliverables: list[Path] = []
    if pdf_file is not None and pdf_file.is_file():
        deliverables.append(pdf_file)
    if html_index is not None and html_index.is_file():
        deliverables.append(html_index)
    if markdown_dir is not None and markdown_dir.is_dir():
        deliverables.extend(
            sorted(
                p
                for p in markdown_dir.rglob("*.md")
                if p.is_file() and p.resolve().parent != markdown_dir.resolve()
            )
        )
    if images_dir is not None and images_dir.is_dir():
        deliverables.extend(sorted(p for p in images_dir.rglob("*.png") if p.is_file()))
    return deliverables


def _verify_links(html_dir: Path, *, strict: bool) -> tuple[int, int, list[BrokenLinkRecord]]:
    """Scan generated HTML files for broken links and raise ValueError when strict is enabled."""
    drawlib_tools = _get_drawlib_tools()
    files_scanned, links_checked, raw_broken = drawlib_tools.scan_broken_links(str(html_dir))
    records = [
        BrokenLinkRecord(html_file=rel_html, tag=tag, target_url=url)
        for rel_html, tag, url in raw_broken
    ]
    if strict and records:
        details = ", ".join(f"{r.html_file} -> {r.target_url} ({r.tag})" for r in records[:5])
        msg = f"Broken internal links or assets detected in '{html_dir}': {details}"
        raise ValueError(msg)
    return files_scanned, links_checked, records


def _run_optional_non_pdf_builds(
    drawlib_tools: _DrawlibToolsProtocol,
    src_dir: Path,
    out_dir: Path,
    clean_target: str,
    active_formats: list[str],
    styles_arg: str | None,
    utils_arg: str | None,
    *,
    no_cache: bool,
    html_output_dir: Path | None = None,
) -> tuple[Path | None, Path | None, Path | None, Path | None]:
    """Execute optional HTML, Markdown, and standalone PNG builds if requested."""
    html_dir: Path | None = None
    html_index: Path | None = None
    markdown_dir: Path | None = None
    images_dir: Path | None = None

    if "html" in active_formats:
        html_dir = html_output_dir.resolve() if html_output_dir is not None else (out_dir / f"{clean_target}_html")
        html_dir.mkdir(parents=True, exist_ok=True)
        drawlib_tools.build_html(
            str(src_dir),
            output_dir=str(html_dir),
            styles_path=styles_arg,
            utils_path=utils_arg,
            no_cache=no_cache,
        )
        html_index = html_dir / "index.html"

    if "markdown" in active_formats:
        markdown_dir = out_dir / f"{clean_target}_markdown"
        drawlib_tools.build_markdown(
            str(src_dir),
            output_dir=str(markdown_dir),
            styles_path=styles_arg,
            utils_path=utils_arg,
            no_cache=no_cache,
        )

    if "images" in active_formats:
        images_dir = out_dir / f"{clean_target}_images"
        drawlib_tools.build_image(
            str(src_dir),
            output_path=str(images_dir),
            styles_path=styles_arg,
            utils_path=utils_arg,
            no_cache=no_cache,
        )

    return html_dir, html_index, markdown_dir, images_dir


def compile_report_project(
    target: str = "full_audit",
    *,
    src_base_dir: Path = Path(DEFAULT_REPORT_SRC_DIR),
    output_dir: Path = Path(DEFAULT_REPORT_OUTPUT_DIR),
    html_output_dir: Path | None = None,
    formats: Sequence[str] = DEFAULT_REPORT_FORMATS,
    generate_toc: bool = True,
    page_break: bool = True,
    no_cache: bool = False,
    strict_links: bool = True,
    strict_preflight: bool = False,
) -> ReportBuildResult:
    """Compile <src_base_dir>/<target>_src/ into <output_dir>/<target>.pdf (and optional extra formats).

    Args:
        target: Project target prefix or path (e.g. 'python_clean' -> 'reports_src/python_clean_src').
        src_base_dir: Base directory containing '<target>_src/' (default 'reports_src').
        output_dir: Destination directory for compiled deliverables (default 'reports').
        html_output_dir: Optional custom destination directory for compiled HTML output.
        formats: Output formats to build (defaults to ('pdf',); supports 'pdf', 'html', 'markdown', 'images').
        generate_toc: Inject automatic Table of Contents after 00_cover.md in PDF output.
        page_break: Insert page breaks between chapters in PDF output.
        no_cache: Bypass drawlib SQLite image build cache.
        strict_links: Raise ValueError if HTML output is built and scan_broken_links finds broken links.
        strict_preflight: Raise ValueError if lint_drawlib_chapters finds preflight visual warnings.

    Returns:
        ReportBuildResult: Paths of compiled deliverables and link scan statistics.

    Raises:
        FileNotFoundError: If '<src_base_dir>/<target>_src/' does not exist.
        ValueError: If drawlib.toml or chapters are missing, format is invalid, or link/preflight checks fail.
    """
    clean_target, eff_src_base = normalize_report_target(target, src_base_dir)
    active_formats = _normalize_formats(formats)
    resolved_src_base = eff_src_base.resolve()
    src_dir = resolved_src_base / f"{clean_target}_src"
    if not src_dir.is_dir() and (resolved_src_base / "drawlib.toml").is_file():
        src_dir = resolved_src_base
    if not src_dir.is_dir():
        msg = f"Report source directory '{src_dir}' does not exist. Run 'pni report init {clean_target}' first."
        raise FileNotFoundError(msg)
    if not (src_dir / "drawlib.toml").is_file():
        msg = f"Missing 'drawlib.toml' in '{src_dir}'. Run 'pni report init {clean_target} --force' first."
        raise ValueError(msg)

    default_lang, langs = _read_drawlib_i18n_config(src_dir)
    chapters = _find_chapter_markdown_files(src_dir, fallback_lang=default_lang)
    if not chapters:
        msg = (
            f"No chapter Markdown files found in '{src_dir}/{default_lang}/' "
            "(create 00_cover.md, 01_*.md, ...)."
        )
        raise ValueError(msg)

    preflight_warnings = lint_drawlib_chapters(chapters)
    if strict_preflight and preflight_warnings:
        joined = "; ".join(preflight_warnings)
        msg = f"Drawlib preflight visual check failed ({len(preflight_warnings)} warning(s)): {joined}"
        raise ValueError(msg)

    out_dir = output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    styles_file = src_dir / "styles.py"
    utils_file = src_dir / "utils.py"
    styles_arg = str(styles_file) if styles_file.is_file() else None
    utils_arg = str(utils_file) if utils_file.is_file() else None
    drawlib_tools = _get_drawlib_tools()

    pdf_file: Path | None = None
    if "pdf" in active_formats:
        pdf_candidate = out_dir / f"{clean_target}.pdf"
        raw_pdf = drawlib_tools.build_pdf(
            str(src_dir),
            output_file=str(pdf_candidate),
            page_break=page_break,
            generate_index=generate_toc,
            styles_path=styles_arg,
            utils_path=utils_arg,
            no_cache=no_cache,
        )
        pdf_file = _normalize_compiled_pdf(out_dir, clean_target, default_lang, langs, pdf_candidate, raw_pdf)

    html_dir, html_index, markdown_dir, images_dir = _run_optional_non_pdf_builds(
        drawlib_tools,
        src_dir,
        out_dir,
        clean_target,
        active_formats,
        styles_arg,
        utils_arg,
        no_cache=no_cache,
        html_output_dir=html_output_dir,
    )

    scanned, checked, broken = (0, 0, [])
    if html_dir is not None:
        scanned, checked, broken = _verify_links(html_dir, strict=strict_links)

    deliverables = _collect_deliverables(pdf_file, html_index, markdown_dir, images_dir)
    return ReportBuildResult(
        target=clean_target,
        src_dir=src_dir,
        output_dir=out_dir,
        formats=active_formats,
        pdf_file=pdf_file,
        html_dir=html_dir,
        html_index=html_index,
        markdown_dir=markdown_dir,
        images_dir=images_dir,
        html_files_scanned=scanned,
        links_checked=checked,
        broken_links=broken,
        preflight_warnings=preflight_warnings,
        generated_deliverables=deliverables,
    )
