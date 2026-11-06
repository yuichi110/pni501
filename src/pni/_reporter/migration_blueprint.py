# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic MigrationBlueprint builder converting MigrationPlanResult into 00..06 chapter specs."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pni._actions.migration_analyze.models import MigrationPlanResult
from pni._cache import default_migration_blueprint_rel_path, ensure_cache_parent
from pni._reporter.blueprint import BlueprintChapterSpec, ReportBlueprint

_MIGRATION_CHAPTER_TITLES: Final[dict[str, dict[str, str]]] = {
    "ja": {
        "00": "PNI マイグレーション実行計画書",
        "01": "1. 移行戦略サマリーと多軸ギャップマトリクス",
        "02": "2. ターゲットアーキテクチャ設計・改修Wave順序・データ契約",
        "03": "3. 仕様確認票（Decision Log：仕様かバグか）",
        "04": "4. 5段階フェーズゲート実行ロードマップ",
        "05": "5. 自動変換レシピと境界アダプタ（DB / Cache / Port）実装設計",
        "06": "6. PR分割WBS（チケット一覧）と検収テスト計画",
    },
    "en": {
        "00": "PNI Migration Execution Plan",
        "01": "1. Migration Strategy Summary & Multi-Axis Gap Matrix",
        "02": "2. Target Architecture, Refactoring Waves & Data Contracts",
        "03": "3. Stakeholder Decision Log (Spec vs. Bug)",
        "04": "4. 5-Phase Gated Execution Roadmap",
        "05": "5. Automated Codemods & Boundary Adapter Design",
        "06": "6. PR Work Breakdown Structure (WBS) & Verification Gates",
    },
}


def _pick_migration_titles(lang: str) -> dict[str, str]:
    """Select localized migration chapter title dictionary ('ja' or default 'en')."""
    return _MIGRATION_CHAPTER_TITLES["ja"] if lang.lower().startswith("ja") else _MIGRATION_CHAPTER_TITLES["en"]


def _build_mig_cover(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `00_cover.md` for the Migration Execution Plan PDF."""
    data = [
        f"- **Project**: `{plan.project_name}` (`{plan.target_root}`) | **Source Language**: `{plan.source_language}`",
        f"- **Workflow**: `{plan.workflow_id}` | **Run ID**: `{plan.workflow_run_id}`",
        f"- **Transformation Mode**: `{plan.transformation_mode}` | **Strategy**: `{plan.migration_strategy}`",
        f"- **API Compatibility**: `{plan.api_compatibility}` | **Bug Policy**: `{plan.bug_handling_policy}`",
        (
            f"- **Headline KPIs**: `{len(plan.target_axes)}` Migration Axes, "
            f"`{len(plan.pr_wbs)}` Phased PRs, `{len(plan.decision_log)}` Decision Log Items"
        ),
    ]
    return BlueprintChapterSpec(
        filename="00_cover.md",
        title=titles["00"],
        purpose=(
            "Dedicated cover page displaying project identity, confirmed migration strategy, transformation mode, "
            "and headline KPIs (Migration Axes, Total PRs, Decision Log items; followed by PDF Table of Contents)."
        ),
        required_diagrams=[
            (
                "Migration Plan Hero Banner (`Panel` + `KpiCards`: Transformation Mode/Strategy, "
                "Migration Axes Count, Total Phased PRs, Stakeholder Decisions)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _build_mig_strategy_chapter(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `01_migration_strategy_summary.md`."""
    data = [f"- **Executive Migration Summary**: {plan.executive_summary}"]
    for item in plan.confirmed_assumptions:
        data.append(f"- **Confirmed Assumption**: {item}")
    for ng in plan.non_goals:
        data.append(f"- **Explicit Non-Goal (Out of Scope)**: {ng}")
    for ax in plan.target_axes:
        data.append(
            f"- **Axis `[{ax.category}]` {ax.title} (`{ax.risk_level}`)**: "
            f"As-Is=`{ax.as_is}` -> To-Be=`{ax.to_be}` | Approach: {ax.migration_approach}"
        )
    return BlueprintChapterSpec(
        filename="01_migration_strategy_summary.md",
        title=titles["01"],
        purpose=(
            "Present confirmed assumptions, explicit non-goals, the multi-axis As-Is -> To-Be gap matrix "
            "(Language, Framework, Architecture, DB, Cache, Container), and effort/PR distribution across phases."
        ),
        required_diagrams=[
            "Multi-Axis As-Is vs. To-Be Gap Matrix (`Table`: Axis, As-Is, To-Be, Risk, Approach)",
            "PR Effort & Risk Distribution by Phase / Axis (`BarChart` + `KpiCards`)",
        ],
        sorted_data_markdown=data,
    )


def _build_mig_architecture_waves_chapter(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `02_architecture_waves_and_contracts.md`."""
    arch = plan.target_architecture
    data = [
        f"- **Target Architecture Pattern**: `{arch.pattern_name}` — {arch.summary}",
    ]
    for rule in arch.dependency_rules:
        data.append(f"- **Dependency Rule**: {rule}")
    for layer in arch.target_layers:
        data.append(
            f"- **Target Layer `{layer.layer_name}` (`{layer.package_or_dir}`)**: {layer.responsibility} "
            f"| allowed={layer.allowed_dependencies}, forbidden={layer.forbidden_imports}"
        )
    for mp in arch.component_mappings:
        data.append(
            f"- **Component Mapping**: `{mp.source_file}` (`{mp.source_symbol or '*'}`) -> "
            f"`[{mp.target_layer}]` `{mp.target_component}` ({mp.port_or_adapter_role}): {mp.refactoring_note}"
        )
    if plan.migration_facts is not None:
        for w in plan.migration_facts.refactoring_waves:
            data.append(f"- **{w.label}**: modules={w.modules} — {w.rationale}")
        for cut in plan.migration_facts.cycle_cuts:
            data.append(
                f"- **Cycle Cut**: `{cut.recommended_cut_from} -> {cut.recommended_cut_to}` — {cut.rationale}"
            )
        for ic in plan.migration_facts.implicit_contracts:
            ins = [f"{f.key}:{f.inferred_type}(default={f.default_value})" for f in ic.input_fields]
            outs = [f"{f.key}:{f.inferred_type}" for f in ic.output_fields]
            data.append(
                f"- **Implicit Contract `{ic.http_method} {ic.endpoint_or_file}`**: inputs={ins}, outputs={outs}"
            )
    return BlueprintChapterSpec(
        filename="02_architecture_waves_and_contracts.md",
        title=titles["02"],
        purpose=(
            "Visualize the To-Be layered / Port & Adapter architecture (`ClassDiagram`), topological Wave 1..4 "
            "refactoring order with cycle-cut edges (`Roadmap`), and implicit I/O contract -> typed DTO mappings."
        ),
        required_diagrams=[
            "To-Be Target Architecture & Port/Adapter Layer Diagram (`ClassDiagram`)",
            "Leaf-First Topological Wave 1..4 Order & Implicit Contract Mapping (`Roadmap` + `Table`)",
        ],
        sorted_data_markdown=data,
    )


def _build_mig_decision_log_chapter(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `03_spec_vs_bug_decision_log.md`."""
    data: list[str] = []
    for dec in plan.decision_log:
        ln = f":{dec.line}" if dec.line else ""
        data.append(
            f"- **`{dec.decision_id}` (`{dec.file_path}{ln}`)**: Current=`{dec.current_behavior}` | "
            f"Impact=`{dec.impact_if_changed}` | Recommended=`{dec.recommended_option}`"
        )
    if not data:
        data.append("- **Decision Log**: Zero ambiguous legacy behaviors detected; proceed under standard policy.")
    return BlueprintChapterSpec(
        filename="03_spec_vs_bug_decision_log.md",
        title=titles["03"],
        purpose=(
            "Isolate legacy quirks ('Spec vs. Bug' under Hyrum's Law) for Product Owner sign-off so Phase 0-2 "
            "infrastructure upgrades never silently alter billing, auth, or external response contracts."
        ),
        required_diagrams=[
            "Spec vs. Bug Stakeholder Decision Matrix (`Table`: ID, Location, Current Behavior, Impact, Recommended)",
            "Decision Handling Workflow Across Phase 0 Characterization -> Phase 3 Sign-Off (`CardList` / `Roadmap`)",
        ],
        sorted_data_markdown=data,
    )


def _build_mig_phase_gates_chapter(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `04_five_phase_gate_roadmap.md`."""
    data: list[str] = []
    for pg in sorted(plan.phase_gates, key=lambda p: p.phase_number):
        data.append(
            f"- **Phase {pg.phase_number} — {pg.title}**: Objective={pg.objective} | "
            f"Tasks={pg.key_tasks} | Exit Criteria={pg.exit_criteria} | Rollback={pg.rollback_or_coexistence_note}"
        )
    return BlueprintChapterSpec(
        filename="04_five_phase_gate_roadmap.md",
        title=titles["04"],
        purpose=(
            "Define the 5-Phase Gated Execution Pipeline (Phase 0 Characterization -> Phase 1 Cycle/Port Extraction -> "
            "Phase 2 Codemod & DB/Cache Adapters -> Phase 3 Typed DTO & Approved Fixes -> Phase 4 Cutover) with strict "
            "exit criteria and rollback/coexistence conditions."
        ),
        required_diagrams=[
            "5-Phase Gated Migration Execution Timeline (`Roadmap`: Phase 0..Phase 4)",
            "Phase Gate Exit Criteria & Rollback / Coexistence Matrix (`Table`)",
        ],
        sorted_data_markdown=data,
    )


def _build_mig_codemod_and_adapters_chapter(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `05_codemod_and_refactoring_design.md`."""
    data: list[str] = []
    if plan.migration_facts is not None:
        for blk in plan.migration_facts.manual_blockers:
            loc = f" (`{blk.file}:{blk.line}`)" if blk.file else ""
            data.append(f"- **Blocker `{blk.blocker_id}` (`{blk.severity}`){loc}**: {blk.description}")
        for cm in plan.migration_facts.mechanical_codemods:
            data.append(
                f"- **Codemod `{cm.tool}` — `{cm.recipe_id}`**: {cm.title} "
                f"(files={cm.applicable_files_count}) — {cm.rationale}"
            )
        for tp in plan.migration_facts.boundary_touchpoints:
            data.append(
                f"- **Boundary Touchpoint `[{tp.kind}]` `{tp.file}:{tp.line}` (`{tp.symbol}`)**: "
                f"{tp.current_coupling} -> {tp.recommended_port_hint}"
            )
    return BlueprintChapterSpec(
        filename="05_codemod_and_refactoring_design.md",
        title=titles["05"],
        purpose=(
            "Separate deterministic mechanical codemods (OpenRewrite / Rector / Ruff) from manual Port & Adapter "
            "extractions (Redis cache externalization, PostgreSQL/PDO persistence, HTTP client timeouts)."
        ),
        required_diagrams=[
            "Automated Codemod vs. Manual Refactoring Breakdown & Recipes (`BarChart` + `Table`)",
            "Boundary Touchpoints (State / DB / Outbound HTTP) -> Port & Adapter Design (`Table`)",
        ],
        sorted_data_markdown=data or ["- **Adapter Design**: Derive from `target_architecture.component_mappings`."],
    )


def _build_mig_pr_wbs_chapter(plan: MigrationPlanResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `06_pr_wbs_and_verification_gates.md`."""
    data: list[str] = []
    for pr in sorted(plan.pr_wbs, key=lambda item: (item.phase_number, item.wave, item.pr_id)):
        data.append(
            f"- **`{pr.pr_id}` (Phase {pr.phase_number}, Wave {pr.wave}, `{pr.estimated_size}`, "
            f"`{pr.automated_or_manual}`, deps={pr.depends_on_prs})**: **{pr.title}** | "
            f"files={pr.target_files} | verify=`{pr.verification_cmd}` — {pr.changes_summary}"
        )
    return BlueprintChapterSpec(
        filename="06_pr_wbs_and_verification_gates.md",
        title=titles["06"],
        purpose=(
            "Provide an issue-tracker-ready, topologically ordered PR Work Breakdown Structure (`PR-01`..`PR-NN`) "
            "with target files, size estimates, dependencies, and deterministic verification commands."
        ),
        required_diagrams=[
            "Topologically Ordered PR Work Breakdown Structure (`Table`: PR ID, Phase, Title, Files, Verify, Size)",
            "PR Dependency Chain & Verification Gate Summary (`BarChart` / `CardList`)",
        ],
        sorted_data_markdown=data,
    )


def build_migration_blueprint(
    plan: MigrationPlanResult,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
) -> ReportBlueprint:
    """Construct a deterministic 7-file (`00_cover` + `01`..`06`) ReportBlueprint from MigrationPlanResult."""
    titles = _pick_migration_titles(lang)
    chapters = [
        _build_mig_cover(plan, titles),
        _build_mig_strategy_chapter(plan, titles),
        _build_mig_architecture_waves_chapter(plan, titles),
        _build_mig_decision_log_chapter(plan, titles),
        _build_mig_phase_gates_chapter(plan, titles),
        _build_mig_codemod_and_adapters_chapter(plan, titles),
        _build_mig_pr_wbs_chapter(plan, titles),
    ]
    return ReportBlueprint(
        target=target,
        lang=lang,
        style=style,
        workflow_id=plan.workflow_id,
        workflow_run_id=plan.workflow_run_id,
        overall_score=100,
        grade="A",
        passed_rules_count=len(plan.phase_gates),
        total_rules_count=max(len(plan.pr_wbs), 1),
        chapters=chapters,
    )


def render_migration_blueprint_markdown(blueprint: ReportBlueprint, blueprint_rel_path: str = "") -> str:
    """Render the 7-chapter MigrationBlueprint into structured Markdown authoring instructions."""
    loc_note = f" (persisted at `{blueprint_rel_path}`)" if blueprint_rel_path else ""
    lines = [
        f"#### Deterministic 6-Chapter Migration Plan Blueprint (`00_cover.md` + `01`..`06`){loc_note}",
        (
            "All As-Is -> To-Be migration axes, Port & Adapter component mappings, topological Waves 1..4, "
            "implicit contracts, Decision Log items, 5-Phase Gates, codemods, and PR WBS tickets below are "
            "**validated and pre-sorted by PNI**. Render every chapter faithfully without inventing file paths."
        ),
    ]
    for ch in blueprint.chapters:
        lines.append(f"\n##### `{ch.filename}` — {ch.title}")
        lines.append(f"- **Chapter Goal**: {ch.purpose}")
        lines.append(f"- **Required Diagrams ({len(ch.required_diagrams)}+)**:")
        for idx, diag in enumerate(ch.required_diagrams, start=1):
            lines.append(f"  {idx}. {diag}")
        lines.append("- **Pre-Sorted Data to Render**:")
        lines.extend(f"  {row}" for row in ch.sorted_data_markdown)
    return "\n".join(lines)


def load_or_build_migration_blueprint(
    project_root: Path | None,
    plan_path: str,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
    workflow_id: str = "",
) -> tuple[ReportBlueprint | None, str]:
    """Load MigrationPlanResult from plan_path if present, build MigrationBlueprint, and cache JSON."""
    if project_root is None or not plan_path.strip():
        return None, ""
    root_resolved = project_root.resolve()
    plan_file = (root_resolved / plan_path.strip()).resolve()
    if not plan_file.is_relative_to(root_resolved) or not plan_file.is_file():
        return None, ""

    plan = MigrationPlanResult.model_validate_json(plan_file.read_text(encoding="utf-8"))
    blueprint = build_migration_blueprint(plan, target=target, lang=lang, style=style)
    cache_key = (workflow_id or plan.workflow_id or target).strip() or "migration"
    rel_bp = default_migration_blueprint_rel_path(cache_key)
    bp_file = (root_resolved / rel_bp).resolve()
    if bp_file.is_relative_to(root_resolved):
        ensure_cache_parent(project_root, bp_file)
        bp_file.write_text(blueprint.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return blueprint, rel_bp
