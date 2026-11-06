# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic ProgressBlueprint builder converting ProgressResult into 00..04 chapter specs."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pni._actions.base_model import HealthGrade
from pni._actions.progress_analyze.models import ProgressResult
from pni._cache import default_progress_blueprint_rel_path, ensure_cache_parent
from pni._reporter.blueprint import BlueprintChapterSpec, ReportBlueprint

_PROGRESS_CHAPTER_TITLES: Final[dict[str, dict[str, str]]] = {
    "ja": {
        "00": "PNI プロジェクト進行・Git統合健全性レポート",
        "01": "1. マイルストーン計画 vs 実績診断",
        "02": "2. Gitメソドロジー適合・ブランチ派生・コンフリクト診断",
        "03": "3. コミット・行数（LOC）・テスト履歴の遷移分析",
        "04": "4. 進行ボトルネックと次スプリント優先アクション（P0〜P2）",
    },
    "en": {
        "00": "PNI Project Progress & Git Integration Health Report",
        "01": "1. Milestone Schedule vs. Verified Progress",
        "02": "2. Git Methodology Compliance, Branch Topology & Conflicts",
        "03": "3. Commit, LOC & Test Historical Trajectories",
        "04": "4. Delivery Bottlenecks & Next-Sprint Actions (P0-P2)",
    },
}


def _score_to_health_grade(score: int) -> HealthGrade:
    """Map `overall_health_score` (`0..100`) to a canonical `HealthGrade`."""
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def _pick_progress_titles(lang: str) -> dict[str, str]:
    """Select localized progress chapter title dictionary ('ja' or default 'en')."""
    return _PROGRESS_CHAPTER_TITLES["ja"] if lang.lower().startswith("ja") else _PROGRESS_CHAPTER_TITLES["en"]


def _build_prog_cover(res: ProgressResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `00_cover.md` for the Project Progress & Git Report PDF."""
    ds = res.dimension_scores
    data = [
        f"- **Project**: `{res.project_name}` (`{res.target_root}`) | **As-Of Date**: `{res.as_of_date}`",
        f"- **Workflow**: `{res.workflow_id}` | **Run ID**: `{res.workflow_run_id}`",
        (
            f"- **Delivery Status**: `{res.delivery_status.upper()}` | "
            f"**Overall Health Score**: `{res.overall_health_score}/100`"
        ),
        (
            f"- **4-Axis Dimension Scores**: Schedule=`{ds.schedule_adherence}`, "
            f"Git/Merge=`{ds.git_and_merge_hygiene}`, Momentum/Churn=`{ds.momentum_and_churn}`, "
            f"Test/Quality=`{ds.test_and_quality_trajectory}`"
        ),
    ]
    if res.audit_status_note:
        data.append(f"- **Audit Summary Link**: {res.audit_status_note}")
    return BlueprintChapterSpec(
        filename="00_cover.md",
        title=titles["00"],
        purpose=(
            "Dedicated cover page displaying project identity, delivery status (`on_track` / `at_risk` / "
            "`delayed` / `blocked`), overall progress health score, and 4-axis KPI cards (followed by PDF ToC)."
        ),
        required_diagrams=[
            (
                "Progress Health Hero Banner (`Panel` + `KpiCards`: Delivery Status, Overall Health Score, "
                "Schedule Adherence, Git & Merge Hygiene)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _build_prog_schedule_chapter(res: ProgressResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `01_schedule_and_milestones.md`."""
    data = [f"- **Executive Summary**: {res.executive_summary}"]
    if res.progress_facts is not None:
        for ms in res.progress_facts.plan.milestones:
            data.append(f"- **Milestone `{ms.id}` ({ms.name})**: Due=`{ms.due_date}`")
    for ta in res.task_assessments:
        data.append(
            f"- **Task `{ta.task_id}` ({ta.name})**: Verdict=`{ta.status_verdict}` | "
            f"Declared=`{ta.declared_progress}%` vs Verified=`{ta.verified_progress}%` | "
            f"Evidence: {ta.evidence_summary}"
        )
    return BlueprintChapterSpec(
        filename="01_schedule_and_milestones.md",
        title=titles["01"],
        purpose=(
            "Compare planned milestones and task windows against verified repository progress, highlighting "
            "gaps between declared vs. verified completion (`GanttChart` + `Table`)."
        ),
        required_diagrams=[
            "Planned vs. Verified Task Progress Schedule (`GanttChart` with `as_of_date` marker)",
            "Declared vs. Verified Task Completion & Evidence Matrix (`Table` / `BarChart`)",
        ],
        sorted_data_markdown=data,
    )


def _build_prog_git_conflicts_chapter(res: ProgressResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `02_git_methodology_and_conflicts.md`."""
    data: list[str] = []
    if res.progress_facts is not None:
        pf = res.progress_facts
        pol = pf.plan.git_policy
        data.append(
            f"- **Git Policy**: methodology=`{pol.methodology}`, trunk=`{pol.trunk_branch}`, "
            f"merge_strategy=`{pol.merge_strategy}`, conventional_commit_ratio=`{pf.conventional_commit_ratio}`"
        )
        wt = pf.working_tree_conflicts
        if wt.unmerged_index_files or wt.committed_conflict_markers or wt.in_progress_operations:
            data.append(
                f"- **Working-Tree Conflicts**: unmerged={wt.unmerged_index_files}, "
                f"ops={wt.in_progress_operations}, markers={wt.committed_conflict_markers}"
            )
        for br in pf.branches[:20]:
            data.append(
                f"- **Branch `{br.branch_name}`**: merged=`{br.is_merged}`, ahead=`{br.ahead_commits}`, "
                f"behind=`{br.behind_commits}`, age=`{br.age_days}d`, conflict=`{br.has_conflict}` "
                f"({br.conflicting_files})"
            )
        for ov in pf.overlapping_file_hotspots[:10]:
            data.append(f"- **Cross-Branch Overlap Hotspot `{ov.file_path}`**: branches={ov.branches}")
        for viol in pf.policy_violations[:15]:
            data.append(f"- **Policy Violation `[{viol.severity.upper()}]` `{viol.code}`**: {viol.detail}")
    for ba in res.branch_assessments:
        data.append(
            f"- **Branch Assessment `{ba.branch_name}` (`{ba.integration_risk}`)**: {ba.merge_recommendation}"
        )
    if not data:
        data.append("- **Git Governance**: Clean trunk and zero active branch conflicts.")
    return BlueprintChapterSpec(
        filename="02_git_methodology_and_conflicts.md",
        title=titles["02"],
        purpose=(
            "Visualize branch divergence (`ahead/behind`), `git merge-tree` dry-run merge conflicts against "
            "trunk, cross-branch overlapping files, and Git methodology compliance."
        ),
        required_diagrams=[
            "Branch Divergence (`ahead` / `behind`) & Merge Conflict Matrix (`BarChart` + `Table`)",
            "Git Policy Compliance & Cross-Branch Conflict Hotspots (`CardList` / `Table`)",
        ],
        sorted_data_markdown=data,
    )


def _build_prog_trajectories_chapter(res: ProgressResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `03_code_and_test_trajectories.md`."""
    data: list[str] = []
    if res.progress_facts is not None:
        pf = res.progress_facts
        for pt in pf.trajectory:
            data.append(
                f"- **`{pt.period_label}` (`{pt.commit_sha or '-'}`)**: commits=`{pt.commits_count}`, "
                f"+{pt.lines_added}/-{pt.lines_deleted}, source_loc=`{pt.source_loc}`, "
                f"test_loc=`{pt.test_loc}` (ratio=`{pt.test_to_code_ratio}`), "
                f"static_test_cases=`{pt.static_test_cases}`"
            )
        for ch in pf.churn_hotspots[:10]:
            data.append(
                f"- **Rework Churn Hotspot `{ch.file_path}`**: commits=`{ch.commits_count}`, "
                f"+{ch.lines_added}/-{ch.lines_deleted}, rework_ratio=`{ch.rework_ratio}`"
            )
        if pf.audit_summary is not None and pf.audit_summary.latest_score is not None:
            au = pf.audit_summary
            data.append(
                f"- **Linked Audit Summary (`{au.base_workflow_id}`)**: "
                f"latest=`{au.latest_score}/100 ({au.latest_grade})`, "
                f"delta=`{au.score_delta}`, critical=`{au.critical_findings}`, high=`{au.high_findings}`, "
                f"history_snapshots=`{len(au.history_points)}`"
            )
    if not data:
        data.append("- **Historical Trajectory**: Minimal commit history available in the configured window.")
    return BlueprintChapterSpec(
        filename="03_code_and_test_trajectories.md",
        title=titles["03"],
        purpose=(
            "Analyze historical commit velocity, Source LOC vs. Test LOC growth curves, static/dynamic test "
            "trends, rework churn hotspots, and linked `audit` score history summary."
        ),
        required_diagrams=[
            "Source LOC vs. Test LOC & Test Case Growth Trajectory (`LineChart` with `draw_legend`)",
            "Weekly Commit Velocity, Churn Hotspots & Linked Audit Health Summary (`BarChart` + `Table`)",
        ],
        sorted_data_markdown=data,
    )


def _build_prog_actions_chapter(res: ProgressResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `04_risks_and_next_actions.md`."""
    data = [f"- **Bottleneck / Risk**: {risk}" for risk in res.bottlenecks_and_risks]
    for act in res.next_actions:
        data.append(
            f"- **`[{act.priority}]` `{act.category}` — {act.title}**: {act.description} "
            f"(branches={act.target_branches}, files={act.target_files}, impact={act.expected_impact})"
        )
    if not data:
        data.append("- **Next Actions**: Maintain current sprint cadence and branch integration hygiene.")
    return BlueprintChapterSpec(
        filename="04_risks_and_next_actions.md",
        title=titles["04"],
        purpose=(
            "Present prioritized P0-P2 operational actions for conflict resolution, stale branch cleanup, "
            "test-gap recovery, and realistic milestone adjustments."
        ),
        required_diagrams=[
            "Prioritized P0 -> P1 -> P2 Delivery Recovery & Git Hygiene Roadmap (`Roadmap`)",
            "Actionable Next-Sprint Execution Table (`Table`: Priority, Category, Targets, Impact)",
        ],
        sorted_data_markdown=data,
    )


def build_progress_blueprint(
    result: ProgressResult,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
) -> ReportBlueprint:
    """Construct a deterministic 5-file (`00_cover` + `01`..`04`) ReportBlueprint from ProgressResult."""
    titles = _pick_progress_titles(lang)
    chapters = [
        _build_prog_cover(result, titles),
        _build_prog_schedule_chapter(result, titles),
        _build_prog_git_conflicts_chapter(result, titles),
        _build_prog_trajectories_chapter(result, titles),
        _build_prog_actions_chapter(result, titles),
    ]
    done_tasks = sum(1 for t in result.task_assessments if t.status_verdict == "completed")
    return ReportBlueprint(
        target=target,
        lang=lang,
        style=style,
        workflow_id=result.workflow_id,
        workflow_run_id=result.workflow_run_id,
        overall_score=result.overall_health_score,
        grade=_score_to_health_grade(result.overall_health_score),
        passed_rules_count=done_tasks,
        total_rules_count=max(len(result.task_assessments), 1),
        chapters=chapters,
    )


def render_progress_blueprint_markdown(blueprint: ReportBlueprint, blueprint_rel_path: str = "") -> str:
    """Render the 5-file ProgressBlueprint into structured Markdown authoring instructions."""
    loc_note = f" (persisted at `{blueprint_rel_path}`)" if blueprint_rel_path else ""
    lines = [
        f"#### Deterministic 4-Chapter Project Progress Blueprint (`00_cover.md` + `01`..`04`){loc_note}",
        (
            "All milestone dates, task completion comparisons, `git merge-tree` branch conflict facts, "
            "LOC/test trajectories, and prioritized P0-P2 actions below are **validated by PNI**. "
            "Render these exact 5 Markdown files (`00_cover.md` + `01`..`04`) faithfully."
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


def load_or_build_progress_blueprint(
    project_root: Path | None,
    progress_path: str,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
    workflow_id: str = "",
) -> tuple[ReportBlueprint | None, str]:
    """Load ProgressResult from `progress_path` if present, build ProgressBlueprint, and cache JSON."""
    if project_root is None or not progress_path.strip():
        return None, ""
    root_resolved = project_root.resolve()
    prog_file = (root_resolved / progress_path.strip()).resolve()
    if not prog_file.is_relative_to(root_resolved) or not prog_file.is_file():
        return None, ""

    result = ProgressResult.model_validate_json(prog_file.read_text(encoding="utf-8"))
    blueprint = build_progress_blueprint(result, target=target, lang=lang, style=style)
    cache_key = (workflow_id or result.workflow_id or target).strip() or "project_progress"
    rel_bp = default_progress_blueprint_rel_path(cache_key)
    bp_file = (root_resolved / rel_bp).resolve()
    if bp_file.is_relative_to(root_resolved):
        ensure_cache_parent(project_root, bp_file)
        bp_file.write_text(blueprint.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return blueprint, rel_bp
