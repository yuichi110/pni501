# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for pni._reporter and 'pni report' CLI subcommands."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pni._actions import PrimitiveType, render_action_task_body
from pni._reporter import (
    DEFAULT_REPORT_OUTPUT_DIR,
    DEFAULT_REPORT_SRC_DIR,
    ReportProjectConfig,
    compile_report_project,
    normalize_report_target,
    render_drawlib_report_guide,
    scaffold_report_project,
)
from pni.cli import app

runner = CliRunner()

_SAMPLE_COVER_MD = """# PNI Sample Health Report

Executive overview of software engineering health.

```drawlib file=cover_radar.png caption="Category Radar"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.styles import Styles

setup(width=120, height=58, dpi=120)
chart = RadarChart(
    axis_line_style=Styles.Primary,
    categories=["Arch", "Quality", "Testing", "Docs", "Deps", "Maintain"],
    radius=18.0,
    min_value=0.0,
    max_value=100.0,
    levels=4,
    axis_text_style=Styles.Muted.patch(text_size=10.0),
    grid_style=Styles.MutedDashed,
)
chart.add_series("Score", [95, 92, 96, 94, 98, 95], style=Styles.PrimaryFlat)
chart.draw(xy=(24.0, 6.0))
save()
```
"""

_SAMPLE_METRICS_MD = """# 1. Module Quality Matrix

Heatmap breakdown across core modules.

```drawlib file=module_heatmap.png caption="Module Quality Heatmap"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=120, height=58, dpi=120)
hm = HeatmapChart(
    styles=[Styles.Neutral, Styles.PrimaryNeutral, Styles.PrimaryFlat],
    x_categories=["Types", "Docs", "Simplicity"],
    axis_line_style=Styles.Primary,
    axis_text_style=Styles.Muted.patch(text_size=10.0),
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    width=86.0,
    height=38.0,
    value_format="{:.0f}%",
)
hm.add_row("core.py", [100.0, 100.0, 95.0])
hm.add_row("cli.py", [100.0, 92.0, 90.0])
hm.draw(xy=(16.0, 12.0))
save()
```
"""


def test_report_project_config_and_target_normalization() -> None:
    """Test ReportProjectConfig defaults and normalize_report_target handling."""
    cfg = ReportProjectConfig()
    assert cfg.project_type == "doc"
    assert cfg.target == "full_audit"
    assert cfg.src_dir == DEFAULT_REPORT_SRC_DIR
    assert cfg.output_dir == DEFAULT_REPORT_OUTPUT_DIR
    assert cfg.formats == ["pdf"]
    assert cfg.lang == "en"
    assert cfg.style == "google"

    t1, b1 = normalize_report_target("python_clean", Path("reports_src"))
    assert t1 == "python_clean"
    assert b1 == Path("reports_src")

    t2, b2 = normalize_report_target("custom_src/my_target_src/", Path("reports_src"))
    assert t2 == "my_target"
    assert b2 == Path("custom_src")


def test_scaffold_non_destructive_chapter_preservation(tmp_path: Path) -> None:
    """Test scaffold_report_project preserves existing chapter Markdown files on both repeat and --force runs."""
    src_base = tmp_path / "reports_src"
    scaffold = scaffold_report_project("demo", src_base_dir=src_base, lang="ja", style="google")
    ja_dir = scaffold.src_dir / "ja"

    assert scaffold.src_dir == (src_base / "demo_src").resolve()
    assert scaffold.preserved_existing is False
    assert (scaffold.src_dir / "drawlib.toml").is_file()
    assert (scaffold.src_dir / "styles.py").is_file()
    assert (scaffold.src_dir / "utils.py").is_file()
    assert (scaffold.src_dir / "style.css").is_file()
    assert ja_dir.is_dir()
    assert not (ja_dir / "navbar.md").exists()
    assert not (ja_dir / "00_cover.md").exists()
    assert not (ja_dir / "01_overview.md").exists()

    # Author custom chapters inside <src_dir>/ja/
    (ja_dir / "00_cover.md").write_text("# Custom Cover v1\n", encoding="utf-8")
    (ja_dir / "03_findings_roadmap.md").write_text("# Custom Roadmap v1\n", encoding="utf-8")

    # Re-run without force -> idempotent no-op preserving chapters
    repeat = scaffold_report_project("demo", src_base_dir=src_base, lang="ja", style="google", force=False)
    assert repeat.preserved_existing is True
    assert repeat.created_files == []
    assert (ja_dir / "00_cover.md").read_text(encoding="utf-8") == "# Custom Cover v1\n"

    # Re-run WITH force=True -> refreshes scripts/templates while keeping custom chapters intact
    forced = scaffold_report_project("demo", src_base_dir=src_base, lang="ja", style="google", force=True)
    assert forced.preserved_existing is True
    assert (ja_dir / "00_cover.md").read_text(encoding="utf-8") == "# Custom Cover v1\n"
    assert (ja_dir / "03_findings_roadmap.md").read_text(encoding="utf-8") == "# Custom Roadmap v1\n"
    assert not (ja_dir / "01_overview.md").exists()
    assert not (ja_dir / "02_design.md").exists()


def test_compile_report_pdf_default_and_multi_format(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test PDF-only default compilation and optional HTML/Markdown/images compilation."""
    src_base = tmp_path / "reports_src"
    out_dir = tmp_path / "reports"
    scaffold = scaffold_report_project("demo", src_base_dir=src_base, lang="ja", style="google")
    ja_dir = scaffold.src_dir / "ja"

    # Empty chapters should raise ValueError
    with pytest.raises(ValueError, match="No chapter Markdown files found"):
        compile_report_project("demo", src_base_dir=src_base, output_dir=out_dir)

    # Unsupported format should raise ValueError
    (ja_dir / "00_cover.md").write_text(_SAMPLE_COVER_MD, encoding="utf-8")
    (ja_dir / "01_metrics.md").write_text(_SAMPLE_METRICS_MD, encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported report format"):
        compile_report_project("demo", src_base_dir=src_base, output_dir=out_dir, formats=("docx",))

    # Default formats=("pdf",) should normalize drawlib 0.3.5 'demo_ja.pdf' -> 'reports/demo.pdf'
    drawlib_tools = importlib.import_module("drawlib.tools")

    def _fake_build_pdf(src_dir_str: str, *, output_file: str, **_kwargs: object) -> str:
        assert Path(src_dir_str) == scaffold.src_dir
        out_p = Path(output_file)
        localized_pdf = out_p.with_name(f"{out_p.stem}_ja.pdf")
        localized_pdf.write_bytes(b"%PDF-1.4\n%mock\n")
        return str(localized_pdf)

    monkeypatch.setattr(drawlib_tools, "build_pdf", _fake_build_pdf)
    pdf_only = compile_report_project("demo", src_base_dir=src_base, output_dir=out_dir)
    assert pdf_only.formats == ["pdf"]
    assert pdf_only.pdf_file == (out_dir / "demo.pdf").resolve()
    assert pdf_only.pdf_file.is_file()
    assert not (out_dir / "demo_ja.pdf").exists()
    assert pdf_only.html_dir is None
    assert pdf_only.markdown_dir is None
    assert pdf_only.images_dir is None
    assert pdf_only.generated_deliverables == [pdf_only.pdf_file]

    # Opt-in HTML + Markdown + Images build
    built = compile_report_project(
        "demo",
        src_base_dir=src_base,
        output_dir=out_dir,
        formats=("html", "markdown", "images"),
        no_cache=True,
    )
    assert built.pdf_file is None
    assert built.html_index is not None and built.html_index.is_file()
    assert len(built.broken_links) == 0
    assert built.images_dir is not None
    assert (built.images_dir / "00_cover" / "cover_radar.png").is_file()
    assert (built.images_dir / "01_metrics" / "module_heatmap.png").is_file()
    assert built.markdown_dir is not None
    assert (built.markdown_dir / "ja" / "00_cover.md").is_file()
    assert len(built.generated_deliverables) >= 5


def test_compile_report_missing_src_and_broken_link_detection(tmp_path: Path) -> None:
    """Test compile_report_project error handling on missing src_dir and broken internal HTML links."""
    src_base = tmp_path / "reports_src"
    out_dir = tmp_path / "reports"
    with pytest.raises(FileNotFoundError, match="does not exist"):
        compile_report_project("missing", src_base_dir=src_base, output_dir=out_dir, formats=("html",))

    scaffold = scaffold_report_project("broken", src_base_dir=src_base, lang="en", style="default")
    bad_md = _SAMPLE_COVER_MD + "\n\nSee [Missing Asset](nonexistent_page.html) for details.\n"
    (scaffold.src_dir / "en" / "00_cover.md").write_text(bad_md, encoding="utf-8")

    with pytest.raises(ValueError, match="Broken internal links"):
        compile_report_project("broken", src_base_dir=src_base, output_dir=out_dir, formats=("html",), no_cache=True)

    non_strict = compile_report_project(
        "broken",
        src_base_dir=src_base,
        output_dir=out_dir,
        formats=("html",),
        no_cache=True,
        strict_links=False,
    )
    assert len(non_strict.broken_links) >= 1


def test_cli_report_init_and_build(tmp_path: Path) -> None:
    """Test 'pni report init' and 'pni report build' CLI subcommands."""
    src_base = tmp_path / "reports_src"
    out_dir = tmp_path / "reports"

    res_init = runner.invoke(
        app,
        [
            "report",
            "init",
            "cli_demo",
            "--src-dir",
            str(src_base),
            "--lang",
            "en",
            "--style",
            "google",
            "--keep-samples",
        ],
    )
    assert res_init.exit_code == 0
    assert "Drawlib report project" in res_init.stdout
    assert (src_base / "cli_demo_src" / "drawlib.toml").is_file()
    assert (src_base / "cli_demo_src" / "en" / "00_cover.md").is_file()

    # Re-running without --force succeeds idempotently and preserves chapters
    res_repeat = runner.invoke(app, ["report", "init", "cli_demo", "--src-dir", str(src_base)])
    assert res_repeat.exit_code == 0
    assert "preserved existing chapters" in res_repeat.stdout

    res_build = runner.invoke(
        app,
        [
            "report",
            "build",
            "cli_demo",
            "--src-dir",
            str(src_base),
            "--output-dir",
            str(out_dir),
            "-f",
            "html",
            "--no-cache",
        ],
    )
    assert res_build.exit_code == 0
    assert "Compiled Drawlib report" in res_build.stdout
    assert (out_dir / "cli_demo_html" / "index.html").is_file()

    res_build_fail = runner.invoke(
        app,
        ["report", "build", "nope", "--src-dir", str(src_base), "--output-dir", str(out_dir), "-f", "html"],
    )
    assert res_build_fail.exit_code == 1


def test_drawlib_guide_and_action_directive_rendering() -> None:
    """Test render_drawlib_report_guide and write_drawlib_report task body injection."""
    guide = render_drawlib_report_guide(
        target="lib_clean",
        src_base_dir="reports_src/python",
        output_dir="reports/python",
        score_path="reports/python/lib_clean_score.json",
        facts_path=".pni/cache/py_lib_clean/facts.json",
        target_root="examples/python/lib_clean",
        source_targets=["src"],
        doc_targets=["README.md"],
        lang="ja",
        style="google",
        workflow_id="py_lib_clean",
    )
    assert "lang=ja" in guide
    assert "reports_src/python/lib_clean_src/ja" in guide
    assert "HeatmapChart" in guide
    assert "HeatmapOverlay" in guide
    assert "pni report init lib_clean --src-dir reports_src/python --lang ja --style google" in guide
    assert "uv run drawlib -h" in guide
    assert "uv run drawlib rules show agent-instruction" in guide
    assert "uv run drawlib rules show api" in guide
    assert "uv run drawlib rules show lib-smartarts-overview" in guide
    assert "uv run drawlib rules show lib-charts-overview" in guide
    assert "uv run drawlib rules show lib-diagrams-overview" in guide
    assert "reports/python/lib_clean.pdf" in guide
    assert ".pni/cache/py_lib_clean/architecture.json" in guide
    assert "git diff" in guide

    body = render_action_task_body(
        PrimitiveType.WRITE_DRAWLIB_REPORT,
        {
            "workflow_id": "py_api_legacy_messy",
            "target": "api_legacy_messy",
            "src_dir": "reports_src/python",
            "output_dir": "reports/python",
            "score_path": "reports/python/api_legacy_messy_score.json",
            "facts_path": ".pni/cache/py_api_legacy_messy/facts.json",
            "target_root": "examples/python/api_legacy_messy",
            "source_targets": ["order_app"],
            "doc_targets": ["README.md"],
            "lang": "ja",
            "style": "google",
        },
        prompt="Focus on processor.py hotspots.",
    )
    assert "pni report build api_legacy_messy --src-dir reports_src/python --output-dir reports/python" in body
    assert "Focus on processor.py hotspots." in body


def test_drawlib_lazy_import_not_loaded_on_cli_startup() -> None:
    """Verify importing pni.cli and running non-report commands does not import drawlib."""
    saved_drawlib = {
        name: mod for name, mod in list(sys.modules.items()) if name == "drawlib" or name.startswith("drawlib.")
    }
    try:
        for name in saved_drawlib:
            sys.modules.pop(name, None)

        compiler_mod = importlib.import_module("pni._reporter.compiler")
        cli_mod = importlib.import_module("pni.cli")

        importlib.reload(compiler_mod)
        importlib.reload(cli_mod)

        assert "drawlib" not in sys.modules
        assert "drawlib.tools" not in sys.modules

        res_ver = runner.invoke(cli_mod.app, ["version"])
        assert res_ver.exit_code == 0
        res_rules = runner.invoke(cli_mod.app, ["rules", "list"])
        assert res_rules.exit_code == 0

        assert "drawlib" not in sys.modules
        assert "drawlib.tools" not in sys.modules
    finally:
        sys.modules.update(saved_drawlib)
