# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Structured AI authoring and incremental update guide for Drawlib ('doc') reports."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pni._cache import default_architecture_rel_path
from pni._reporter.base_model import (
    DEFAULT_REPORT_FORMATS,
    DEFAULT_REPORT_OUTPUT_DIR,
    DEFAULT_REPORT_SRC_DIR,
)
from pni._reporter.blueprint import load_or_build_blueprint, render_blueprint_markdown
from pni._reporter.migration_blueprint import (
    load_or_build_migration_blueprint,
    render_migration_blueprint_markdown,
)
from pni._reporter.progress_blueprint import (
    load_or_build_progress_blueprint,
    render_progress_blueprint_markdown,
)

_FALLBACK_CHAPTER_SPECS = (
    (
        "`00_cover.md`",
        "Dedicated Cover Page (`Panel` + `KpiCards` + PNI501 logo badge via `draw_pni_logo()` / "
        "`_assets/logo.png` displaying project identity, Overall Score/Grade, "
        "and Rule Pass Rate; followed automatically by Drawlib's generated Table of Contents).",
    ),
    (
        "`01_executive_summary.md`",
        "1. Executive Summary: 7-Axis Health `RadarChart` (`architecture`, `code_quality`, `typing`, "
        "`testing`, `dependencies`, `security`, `documentation`) + Key Health `KpiCards` & Strengths/Top Risks.",
    ),
    (
        "`02_architecture_and_structure.md`",
        "2. Architecture & Source Code Structure: Source Directory/Module `TreeNode` + `Table` (`module_inventory`) "
        "and Layer/Module `ClassDiagram` + `HeatmapOverlay` (`module_hotspots`) + Execution Flow `Roadmap`.",
    ),
    (
        "`03_remediation_roadmap.md`",
        "3. Recommended Remediation Roadmap: Phased `P0 -> P1 -> P2` `Roadmap` + Action Plan `Table` "
        "(`target_files`, `expected_impact`, `related_rules`).",
    ),
    (
        "`04_standards_and_findings.md`",
        "4. Audit Standards, Rule Compliance & Findings: Audit Step Scores (`BarChart`, weakest-first), "
        "Rule Compliance Matrix (`Table`, `FAIL -> WARN -> PASS`), and Findings Index (`Table`, `CRITICAL -> INFO`).",
    ),
    (
        "`05_code_and_runtime_analysis.md`",
        "5. Deep Dive — Code Quality, Testing & Runtime: Module × Quality Dimension `HeatmapChart` + "
        "Container Build, Unit Test, Measured Coverage & Smoke Breakdown (`BarChart` / `Table`).",
    ),
    (
        "`06_security_and_supply_chain.md`",
        "6. Deep Dive — Security, Supply Chain & API Surface: App vs OS CVE Breakdown & Upgrade `Table` "
        "(`fixed_version`), IaC Misconfigs, Redacted Secrets, AST `dangerous_sinks` (CWE), and `api_endpoints`.",
    ),
)

_FALLBACK_MIGRATION_CHAPTER_SPECS = (
    (
        "`00_cover.md`",
        "Dedicated Cover Page (`Panel` + `KpiCards` + PNI501 logo badge via `draw_pni_logo()` / "
        "`_assets/logo.png`: Transformation Mode, Strategy, Migration Axes, "
        "Total PRs, Stakeholder Decisions; followed automatically by Drawlib's Table of Contents).",
    ),
    (
        "`01_migration_strategy_summary.md`",
        "1. Migration Strategy Summary & Multi-Axis Gap Matrix: Confirmed Assumptions/Non-Goals, "
        "`target_axes` As-Is vs To-Be `Table`, and PR Effort/Risk Distribution `BarChart`.",
    ),
    (
        "`02_architecture_waves_and_contracts.md`",
        "2. Target Architecture, Refactoring Waves & Data Contracts: To-Be Layer & Port/Adapter `ClassDiagram`, "
        "Wave 1..4 `Roadmap` (with cycle cuts), and Implicit I/O Contract -> Typed DTO `Table`.",
    ),
    (
        "`03_spec_vs_bug_decision_log.md`",
        "3. Stakeholder Decision Log (Spec vs. Bug): Hyrum's Law legacy quirk sign-off `Table` + "
        "Phase 0 Characterization -> Phase 3 Sign-Off handling `CardList` / `Roadmap`.",
    ),
    (
        "`04_five_phase_gate_roadmap.md`",
        "4. 5-Phase Gated Execution Roadmap: Phase 0..Phase 4 `Roadmap` + Exit Criteria & Rollback `Table`.",
    ),
    (
        "`05_codemod_and_refactoring_design.md`",
        "5. Automated Codemods & Boundary Adapter Design: Codemod vs Manual `BarChart` + Recipes `Table` "
        "and State/DB/HTTP `boundary_touchpoints` -> Port & Adapter `Table`.",
    ),
    (
        "`06_pr_wbs_and_verification_gates.md`",
        "6. PR Work Breakdown Structure (WBS) & Verification Gates: Topologically ordered `PR-01`..`PR-NN` `Table` "
        "and Verification Gate Summary `BarChart` / `CardList`.",
    ),
)

_FALLBACK_PROGRESS_CHAPTER_SPECS = (
    (
        "`00_cover.md`",
        "Dedicated Cover Page (`Panel` + `KpiCards` + PNI501 logo badge via `draw_pni_logo()` / "
        "`_assets/logo.png`: Delivery Status, Overall Health Score, "
        "Schedule Adherence, Git & Merge Hygiene; followed automatically by Drawlib's Table of Contents).",
    ),
    (
        "`01_schedule_and_milestones.md`",
        "1. Milestone Schedule vs. Verified Progress: Planned vs. Verified `GanttChart` + "
        "Declared vs. Verified Completion `Table`.",
    ),
    (
        "`02_git_methodology_and_conflicts.md`",
        "2. Git Methodology Compliance, Branch Topology & Conflicts: Branch `ahead/behind` `BarChart`, "
        "`git merge-tree` Conflict `Table`, and Cross-Branch Overlap Hotspots.",
    ),
    (
        "`03_code_and_test_trajectories.md`",
        "3. Commit, LOC & Test Historical Trajectories: Source LOC vs. Test LOC `LineChart`, "
        "Weekly Commit/Churn `BarChart`, and Linked Audit Score Summary.",
    ),
    (
        "`04_risks_and_next_actions.md`",
        "4. Delivery Bottlenecks & Next-Sprint Actions (P0-P2): Recovery `Roadmap` + Action `Table`.",
    ),
)


def _render_chapter_spec_block(
    project_root: Path | None,
    score_path: str,
    target: str,
    lang: str,
    style: str,
    workflow_id: str = "",
    *,
    report_kind: str = "audit",
    plan_path: str = "",
    progress_path: str = "",
) -> list[str]:
    """Render either the live pre-sorted Blueprint or the canonical chapter fallback layout."""
    if report_kind == "migration":
        mig_bp, mig_rel = load_or_build_migration_blueprint(
            project_root,
            plan_path or score_path,
            target=target,
            lang=lang,
            style=style,
            workflow_id=workflow_id,
        )
        if mig_bp is not None:
            return [render_migration_blueprint_markdown(mig_bp, mig_rel)]
        lines = ["     - **Canonical 6-Chapter Migration Plan Structure (`00_cover.md` + `01`..`06`)**:"]
        for fname, desc in _FALLBACK_MIGRATION_CHAPTER_SPECS:
            lines.append(f"       - {fname}: {desc}")
        return lines

    if report_kind == "progress":
        prog_bp, prog_rel = load_or_build_progress_blueprint(
            project_root,
            progress_path or score_path,
            target=target,
            lang=lang,
            style=style,
            workflow_id=workflow_id,
        )
        if prog_bp is not None:
            return [render_progress_blueprint_markdown(prog_bp, prog_rel)]
        lines = ["     - **Canonical 4-Chapter Project Progress Structure (`00_cover.md` + `01`..`04`)**:"]
        for fname, desc in _FALLBACK_PROGRESS_CHAPTER_SPECS:
            lines.append(f"       - {fname}: {desc}")
        return lines

    blueprint, bp_rel = load_or_build_blueprint(
        project_root,
        score_path,
        target=target,
        lang=lang,
        style=style,
        workflow_id=workflow_id,
    )
    if blueprint is not None:
        return [render_blueprint_markdown(blueprint, bp_rel)]
    lines = ["     - **Canonical 6-Chapter Structure (`00_cover.md` + `01`..`06`)**:"]
    for fname, desc in _FALLBACK_CHAPTER_SPECS:
        lines.append(f"       - {fname}: {desc}")
    return lines


def render_drawlib_report_guide(
    *,
    target: str,
    src_base_dir: str = DEFAULT_REPORT_SRC_DIR,
    output_dir: str = DEFAULT_REPORT_OUTPUT_DIR,
    html_output_dir: str | None = None,
    formats: Sequence[str] = DEFAULT_REPORT_FORMATS,
    score_path: str,
    facts_path: str,
    target_root: str,
    source_targets: list[str],
    doc_targets: list[str],
    lang: str = "en",
    style: str = "google",
    architecture_path: str = "",
    workflow_id: str = "",
    project_root: Path | None = None,
    report_kind: str = "audit",
    plan_path: str = "",
    progress_path: str = "",
) -> str:
    """Render deterministic instructions and pre-sorted Blueprint for authoring a Drawlib report."""
    clean_target = target.strip().removesuffix("_src") or "full_audit"
    src_dir = f"{src_base_dir.rstrip('/')}/{clean_target}_src"
    primary_lang = (lang.split(",", maxsplit=1)[0].strip() if lang.strip() else "en") or "en"
    chapter_dir = f"{src_dir}/{primary_lang}"
    clean_out = output_dir.rstrip("/")
    clean_html_out = html_output_dir.strip().rstrip("/") if html_output_dir and html_output_dir.strip() else None
    cache_key = workflow_id.strip() or clean_target
    arch_ref = architecture_path or default_architecture_rel_path(cache_key)
    fmt_list = [f.strip().lower() for f in formats if f.strip()] or ["pdf"]
    fmt_flags = " ".join(f"-f {f}" for f in fmt_list) if fmt_list != ["pdf"] else ""
    html_dir_flag = f" --html-output-dir {clean_html_out}" if clean_html_out else ""
    build_cmd = (
        f"pni report build {clean_target} --src-dir {src_base_dir} --output-dir {clean_out}"
        + html_dir_flag
        + (f" {fmt_flags}" if fmt_flags else "")
    )

    expected_outputs: list[str] = []
    if "pdf" in fmt_list:
        expected_outputs.append(f"`{clean_out}/{clean_target}.pdf`")
    if "html" in fmt_list:
        html_dest = clean_html_out if clean_html_out else f"{clean_out}/{clean_target}_html"
        expected_outputs.append(f"`{html_dest}/index.html`")

    is_mig = report_kind == "migration"
    is_prog = report_kind == "progress"
    chapter_block = _render_chapter_spec_block(
        project_root,
        score_path,
        clean_target,
        primary_lang,
        style,
        workflow_id,
        report_kind=report_kind,
        plan_path=plan_path,
        progress_path=progress_path,
    )
    if is_prog:
        sample_ch = "02_git_methodology_and_conflicts.md"
        primary_prog = progress_path or score_path
        read_step_desc = (
            f"   - Load `{primary_prog}` (`ProgressResult` containing `delivery_status`, `dimension_scores`,\n"
            "     `task_assessments`, `branch_assessments`, `next_actions`, and deterministic `progress_facts`),\n"
            f"     and `{facts_path}`."
        )
        report_label = "Project Progress"
        file_count_note = "5 Markdown files (`00_cover.md` + `01_*.md` .. `04_*.md`)"
        end_ch_num = "04"
    elif is_mig:
        sample_ch = "02_architecture_waves_and_contracts.md"
        primary_mig = plan_path or score_path
        read_step_desc = (
            f"   - Load `{primary_mig}` (`MigrationPlanResult` containing `target_axes`, `target_architecture`,\n"
            "     `decision_log`, `phase_gates`, `pr_wbs`, and deterministic `migration_facts`),\n"
            f"     `{arch_ref}`, and `{facts_path}`."
        )
        report_label = "Migration Plan"
        file_count_note = "7 Markdown files (`00_cover.md` + `01_*.md` .. `06_*.md`)"
        end_ch_num = "06"
    else:
        sample_ch = "02_architecture_and_structure.md"
        read_step_desc = (
            f"   - Load `{score_path}` (`ScoreResult` containing 7-axis `category_scores`, pre-sorted\n"
            "     `audit_dimensions`, `rule_compliance`, `module_hotspots`, `architecture_record`,\n"
            "     `runtime_facts`, `security_facts`, `module_inventory`, `dangerous_sinks`, `api_endpoints`,\n"
            "     `findings`, `action_plan`, `metrics_snapshot`),\n"
            f"     `{arch_ref}`, and `{facts_path}`."
        )
        report_label = "Visual"
        file_count_note = "7 Markdown files (`00_cover.md` + `01_*.md` .. `06_*.md`)"
        end_ch_num = "06"

    lines = [
        (
            f"### 3-Phase Blueprint-Driven {report_label} Report Synthesis "
            f"(`target={clean_target}`, `lang={lang}`, `style={style}`)"
        ),
        "",
        "1. **READ Structured Artifacts**:",
        read_step_desc,
        "2. **READ Target Code & Documentation**:",
        f"   - Inspect `{target_root}` (`source={source_targets}`, `docs={doc_targets}`) so class/module nodes,",
        "     API endpoints, and execution flow diagrams match actual code symbols.",
        f"3. **WRITE or INCREMENTALLY UPDATE drawlib Report (`00_cover.md` + Chapters `01`..`{end_ch_num}`)**:",
        "   - **Step 3a — Consult Drawlib CLI & Built-In API Rules On-Demand (Never Guess APIs)**:",
        "     - Before writing ```` ```drawlib ```` code blocks, inspect Drawlib's CLI usage, coordinate system,",
        "       and exact Python component signatures (never guess argument names or fall back to raw",
        "       `rectangle()`/`line()` primitives when a high-level component exists):",
        "       ```bash",
        "       uv run drawlib -h                                # Or `drawlib -h`: CLI overview & options",
        "       uv run drawlib rules list                        # List all guideline & `lib-*` API rule topics",
        "       uv run drawlib rules show agent-instruction      # 3-stage multimodal review loop & component map",
        "       uv run drawlib rules show overview               # Bottom-left (0, 0) coordinate space & lifecycle",
        "       uv run drawlib rules show project-doc            # Single-doc cover/ToC, 720pt typography & PDF rules",
        "       uv run drawlib rules show api                    # Complete module/class signature cheat sheet",
        "       uv run drawlib rules show lib-smartarts-overview # Panel, KpiCards, Roadmap, Table, TreeNode, CardList",
        "       uv run drawlib rules show lib-charts-overview    # RadarChart, BarChart, HeatmapChart, LineChart",
        "       uv run drawlib rules show lib-diagrams-overview  # ClassDiagram, HeatmapOverlay, architecture/flow",
        "       uv run drawlib rules show lib-icons-overview     # phosphor, FontAwesome & cloud icon helpers",
        "       ```",
        f"   - **Step 3b — Ensure `{src_dir}/` Scaffolding Exists (Preserve Manifest & Theme Assets)**:",
        "     ```bash",
        f"     pni report init {clean_target} --src-dir {src_base_dir} --lang {lang} --style {style}",
        "     ```",
        (
            "     - Preserve `drawlib.toml`, `styles.py`, `utils.py`, `style.css`, and `template.html` "
            f"inside `{src_dir}/`."
        ),
        f"     - **Blueprint Chapter Sync Policy**: Author or overwrite the exact {file_count_note}",
        f"       defined in the Blueprint below inside `{chapter_dir}/`, and delete any stale",
        f"       numbered `*.md` files in `{chapter_dir}/` from older templates.",
        (
            f"   - **Step 3c — Author `00_cover.md` + Chapters `01`..`{end_ch_num}` in `{chapter_dir}/`** "
            f"(all prose & labels in `{primary_lang}`):"
        ),
        *chapter_block,
       "   - **Step 3d — Drawlib `doc` Authoring Rules (Mandatory)**:",
        (
            f"     - **Never create `navbar.md`** inside `{src_dir}/` or `{chapter_dir}/` "
            "(preserves single-page `doc` + PDF ToC after `00_cover.md`)."
        ),
        f"     - **Zero `file:///` or absolute paths** (`/usr/...`, `/home/...`) inside `{chapter_dir}/*.md`.",
        (
            f"     - **`00_cover.md` is dedicated to the Cover Page and MUST display the PNI501 Logo**: "
            "Place the bundled PNI501 triangle emblem (`_assets/logo.png` on light backgrounds or "
            "`_assets/logo_dark.png` on dark `Styles.Primary` headers) inside the Cover Hero diagram via "
            "`from drawlib.utils import draw_pni_logo; draw_pni_logo((135, 48), width=9.0, dark=True)` "
            "(or `from drawlib.images import image; image((135, 48), width=9.0, image='_assets/logo.png')`). "
            f"Chapters `01_*.md`..`{end_ch_num}_*.md`"
        ),
        "       MUST each start with `# N. Title`, lead prose, and **2+ diagrams** (first diagram at lines 5–15).",
        "       Every ```` ```drawlib ```` fence MUST set `file=<name>.png` and `caption=\"...\"`.",
        "     - **Exact `drawlib` (`v0.3.9+`) Import & Style Cheat Sheet (Prevent Hallucinations)**:",
        "       - Chart imports use submodules (`from drawlib.charts.bar import BarChart`,",
        "         `from drawlib.charts.radar import RadarChart`, `from drawlib.charts.heatmap import HeatmapChart`).",
        "       - Neutral warning/danger fills come from `Styles.*` (`Styles.WarningNeutral.shape_fill_color`,",
        "         `Styles.DangerNeutral.shape_fill_color`, `Styles.SuccessNeutral.shape_fill_color` —",
        "         do NOT invent non-existent `Colors.AmberNeutral` attributes).",
        "       - `ClassDiagram` and `ClassNode`: Always pass `node_style=Styles.Neutral` / `style=Styles.Neutral`",
        "         (dark text on light surface); NEVER pass `Styles.White` (whose `text_color` is white, making",
        "         attributes/methods invisible).",
        "       - Companion / external portal links: Use full `https://...` URLs rather than `../../` relative",
        "         links so standalone report link verification succeeds (or pass `--link-check-root <dir>`).",
        "     - **Multi-Language (`en` / `ja`) Image Parity**: When multiple languages are configured in",
        "       `drawlib.toml`, every language directory MUST contain the exact same chapter filenames",
        "       and identical `file=<name>.png` diagram counts.",
        "     - **Landscape aspect ratios & typography**: Prefer `setup(width=146, height=64, dpi=150)`,",
        "       `text_size >= 9.5`, and `50%+` neutral fills (`Styles.Neutral`, `Styles.PrimaryNeutral`).",
        "     - **Coordinate Anchors (Origin `(0, 0)` is Bottom-Left)**:",
        "       - `shapes`, `text`, `icons`: **Center `(cx, cy)`**",
        "       - `RadarChart`, `BarChart`, `HeatmapChart`, `HeatmapOverlay`, `ClassDiagram`,",
        "         `KpiCards`, `CardList`, `Roadmap`, `Panel`: **Bottom-Left `(x0, y0)`**",
        "       - `Table`, `TreeNode`: **Top-Left `(x0, y0)`**",
        "     - **Visual Clarity & Anti-Collision Guardrails (Enforced by Preflight Check)**:",
        "       - **Multi-series `BarChart` / `LineChart`**: Whenever `.add_series(...)` is called 2+ times,",
        "         you MUST explicitly call `chart.draw_legend(xy=(x, y), orientation='horizontal')`.",
        "       - **`ClassDiagram` + `HeatmapOverlay`**: Set `height >= 80` and `show_contour_lines=False`",
        "         on `HeatmapOverlay` to prevent contour curves from colliding with class box labels.",
        "       - **`Table` `rule_id` column widths**: Allocate `>= 38` width units for `rule_id` columns",
        "         (or insert explicit `'\\n'` after `'/'` such as `'common/\\ndocumentation'`) so path",
        "         prefixes never wrap mid-word without a slash.",
        "   - **Step 3e — Multimodal Grid Verification (`drawlib show -g`) & Report Build**:",
        "     - Export diagrams with the coordinate grid overlaid and visually inspect `.drawlib/scratch/*.png`",
        "       with your image-viewing tool to fix text clipping, arrow/label collisions, or anchor mistakes",
        "       before finalizing the PDF compilation:",
        "     ```bash",
        f"     uv run drawlib show {chapter_dir}/{sample_ch} <diagram>.png \\",
        f"       -s {src_dir}/styles.py -u {src_dir}/utils.py -g -o .drawlib/scratch/grid_check.png",
        f"     {build_cmd}",
        "     ```",
        "   - **Step 3f — Push `ReportCompletionInput` (workspace-relative paths)**:",
        f"     - Verify zero target source edits (`git diff -- {target_root}` must be empty).",
        f"     - Include {', '.join(expected_outputs) or f'`{clean_out}/{clean_target}.pdf`'} in `generated_files`.",
    ]
    return "\n".join(lines)
