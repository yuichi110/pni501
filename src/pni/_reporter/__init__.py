# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Drawlib visual report scaffolding, compilation, and AI authoring guide domain."""

from __future__ import annotations

from pni._reporter.base_model import (
    DEFAULT_REPORT_FORMATS,
    DEFAULT_REPORT_OUTPUT_DIR,
    DEFAULT_REPORT_SRC_DIR,
    SUPPORTED_REPORT_FORMATS,
    BrokenLinkRecord,
    ReportBuildResult,
    ReportProjectConfig,
    ReportScaffoldResult,
)
from pni._reporter.blueprint import (
    BlueprintChapterSpec,
    ReportBlueprint,
    build_report_blueprint,
    load_or_build_blueprint,
    render_blueprint_markdown,
)
from pni._reporter.compiler import (
    compile_report_project,
    lint_drawlib_chapters,
    normalize_report_target,
    scaffold_report_project,
)
from pni._reporter.drawlib_guide import render_drawlib_report_guide
from pni._reporter.migration_blueprint import (
    build_migration_blueprint,
    load_or_build_migration_blueprint,
    render_migration_blueprint_markdown,
)
from pni._reporter.progress_blueprint import (
    build_progress_blueprint,
    load_or_build_progress_blueprint,
    render_progress_blueprint_markdown,
)

__all__ = [
    "DEFAULT_REPORT_FORMATS",
    "DEFAULT_REPORT_OUTPUT_DIR",
    "DEFAULT_REPORT_SRC_DIR",
    "SUPPORTED_REPORT_FORMATS",
    "BlueprintChapterSpec",
    "BrokenLinkRecord",
    "ReportBlueprint",
    "ReportBuildResult",
    "ReportProjectConfig",
    "ReportScaffoldResult",
    "build_migration_blueprint",
    "build_progress_blueprint",
    "build_report_blueprint",
    "compile_report_project",
    "lint_drawlib_chapters",
    "load_or_build_blueprint",
    "load_or_build_migration_blueprint",
    "load_or_build_progress_blueprint",
    "normalize_report_target",
    "render_blueprint_markdown",
    "render_drawlib_report_guide",
    "render_migration_blueprint_markdown",
    "render_progress_blueprint_markdown",
    "scaffold_report_project",
]
