# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Pydantic data models for PNI drawlib report scaffolding and compilation."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pydantic import BaseModel, Field

DEFAULT_REPORT_SRC_DIR: Final[str] = "reports_src"
DEFAULT_REPORT_OUTPUT_DIR: Final[str] = "reports"
DEFAULT_REPORT_FORMATS: Final[tuple[str, ...]] = ("pdf",)
SUPPORTED_REPORT_FORMATS: Final[frozenset[str]] = frozenset({"pdf", "html", "markdown", "images"})


class BrokenLinkRecord(BaseModel):
    """Single broken internal HTML link or missing asset discovered after compilation."""

    html_file: str = Field(description="Relative HTML file path inside the compiled HTML output directory.")
    tag: str = Field(description="HTML tag or attribute holding the broken reference.")
    target_url: str = Field(description="Unresolved target URL or asset path.")


class ReportProjectConfig(BaseModel):
    """Configuration parameters for scaffolding and building a drawlib report project."""

    target: str = Field(default="full_audit", description="Target prefix name creating '<src_dir>/<target>_src/'.")
    src_dir: str = Field(default=DEFAULT_REPORT_SRC_DIR, description="Base directory holding '<target>_src/' folders.")
    output_dir: str = Field(default=DEFAULT_REPORT_OUTPUT_DIR, description="Directory holding '<target>.pdf' outputs.")
    html_output_dir: str | None = Field(
        default=None,
        description="Optional custom directory for compiled HTML output (defaults to '<output_dir>/<target>_html').",
    )
    project_type: str = Field(default="doc", description="Drawlib project layout ('doc' or 'site').")
    formats: list[str] = Field(default_factory=lambda: ["pdf"], description="Output formats to build ('pdf', 'html').")
    lang: str = Field(default="en", description="Report language code (e.g., 'en', 'ja').")
    style: str = Field(default="google", description="Drawlib preset style theme ('google', 'default', 'monochrome').")


class ReportScaffoldResult(BaseModel):
    """Result metadata returned when scaffolding or refreshing a drawlib report project."""

    src_base_dir: Path
    src_dir: Path
    project_type: str
    target: str
    lang: str
    style: str
    preserved_existing: bool = False
    created_files: list[Path] = Field(default_factory=list)


class ReportBuildResult(BaseModel):
    """Result metadata returned when compiling a drawlib report project."""

    target: str
    src_dir: Path
    output_dir: Path
    formats: list[str] = Field(default_factory=list)
    pdf_file: Path | None = None
    html_dir: Path | None = None
    html_index: Path | None = None
    markdown_dir: Path | None = None
    images_dir: Path | None = None
    html_files_scanned: int = 0
    links_checked: int = 0
    broken_links: list[BrokenLinkRecord] = Field(default_factory=list)
    preflight_warnings: list[str] = Field(default_factory=list)
    generated_deliverables: list[Path] = Field(default_factory=list)
