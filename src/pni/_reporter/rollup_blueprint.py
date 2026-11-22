# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unified Drawlib ReportBlueprint builder for multi-language Rollup ScoreResults."""

from __future__ import annotations

from typing import Final

from pni._actions.base_model import ScoreResult
from pni._reporter.blueprint import (
    BlueprintChapterSpec,
    ReportBlueprint,
    format_artifact_manifest_lines,
    format_execution_dag_and_scope_lines,
    format_finding_source_and_triage_lines,
)

_ROLLUP_TITLES: Final[dict[str, dict[str, str]]] = {
    "ja": {
        "00": "PNI マルチ言語・モノレポ統合健全性診断レポート",
        "01": "1. エグゼクティブサマリー・コンポーネント比較",
        "02": "2. 横断アーキテクチャと境界整合性",
        "03": "3. 統合改善ロードマップ（全言語横断）",
        "04": "4. 統合監査パイプライン（DAG）・共通ガバナンス・セキュリティ総括",
        "05": "5. コンポーネント別詳細分析",
    },
    "en": {
        "00": "PNI Polyglot & Monorepo Unified Health Diagnostic Report",
        "01": "1. Executive Summary & Component Comparison",
        "02": "2. Cross-Component Architecture & Contract Alignment",
        "03": "3. Unified Cross-Language Remediation Roadmap",
        "04": "4. Rollup Pipeline (DAG), Governance & Companion Security",
        "05": "5. Per-Component Deep Dives",
    },
}


def build_rollup_report_blueprint(
    score: ScoreResult,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
) -> ReportBlueprint:
    """Build a unified 6-file Drawlib ReportBlueprint covering repo rollup + per-component deep dives."""
    titles = _ROLLUP_TITLES["ja"] if lang.lower().startswith("ja") else _ROLLUP_TITLES["en"]
    comp_lines = [
        f"- `{c.component_id}` (`{c.language}`, `{c.root}`, weight=`{c.weight:.2f}`): "
        f"**{c.overall_score}/100 ({c.grade})** | LOC=`{c.total_loc}` | crit/high=`{c.critical_or_high_count}`"
        for c in score.components
    ]
    scope_lines = [f"- **Approved Audit Scope**: {score.approved_plan_summary}"] if score.approved_plan_summary else []

    chapters = [
        BlueprintChapterSpec(
            filename="00_cover.md",
            title=titles["00"],
            purpose="Unified cover page with PNI501 emblem, overall rollup score, and audited languages.",
            required_diagrams=["Cover Hero Banner (`Panel` + `KpiCards` + `draw_pni_logo()`)"],
            sorted_data_markdown=[
                f"- **Project**: `{score.project_name}` | **Languages**: `{score.language}`",
                f"- **Overall Rollup Score**: **{score.overall_score}/100 (Grade {score.grade})**",
                f"- **Components Audited**: `{len(score.components)}`",
            ],
        ),
        BlueprintChapterSpec(
            filename="01_executive_summary.md",
            title=titles["01"],
            purpose="Unified 7-axis Radar, Component Comparison BarChart/Table, and Approved Audit Scope.",
            required_diagrams=[
                "7-Axis Unified RadarChart (`drawlib.charts.RadarChart`)",
                "Component Score Comparison BarChart (`drawlib.charts.BarChart`)",
            ],
            sorted_data_markdown=[
                f"- **Summary**: {score.summary}",
                *scope_lines,
                *comp_lines,
            ],
        ),
        BlueprintChapterSpec(
            filename="02_cross_component_architecture.md",
            title=titles["02"],
            purpose="End-to-end polyglot topology diagram and cross-component API/schema alignment.",
            required_diagrams=["Cross-Component Topology Diagram (`drawlib.diagrams.architecture` / `graph`)"],
            sorted_data_markdown=[
                f"- **Cross-Component Assessment**: {score.category_rationales.architecture}",
            ],
        ),
        BlueprintChapterSpec(
            filename="03_remediation_roadmap.md",
            title=titles["03"],
            purpose="Deduplicated P0/P1/P2 remediation roadmap spanning all components.",
            required_diagrams=["Priority Roadmap (`drawlib.smartarts.Roadmap` or `Table`)"],
            sorted_data_markdown=[
                f"- `[{a.priority}]` `[{a.component or 'repo'}]` **{a.title}**: {a.action}"
                for a in score.action_plan[:15]
            ],
        ),
        BlueprintChapterSpec(
            filename="04_governance_and_companions.md",
            title=titles["04"],
            purpose=(
                "Visualize the executed Multi-Component Rollup DAG (component sub-audits + companion DSL scan -> "
                "log1p(LOC) weighted synthesis & weakest-link guardrails), repo-wide CI/CD & security findings, "
                "finding source split, and Machine-Readable Artifact Reference Table (never dump raw JSON)."
            ),
            required_diagrams=[
                (
                    "Executed Multi-Component Rollup Pipeline DAG (`drawlib.graph.get_layout()` or "
                    "`drawlib.diagrams.flow`: parallel component sub-audits + companion DSL scan -> "
                    "hybrid weighted synthesis -> unified report)"
                ),
                "Findings by Severity & Component Chart (`drawlib.charts.BarChart`) + Artifact Reference Table",
            ],
            sorted_data_markdown=[
                *format_execution_dag_and_scope_lines(score.execution_dag),
                *format_finding_source_and_triage_lines(score.findings, score.triaged_adjustments),
                *[
                    f"- `[{f.severity.upper()}]` `[{f.component or 'repo'}]` `{f.rule_id}` (`{f.file_path or '-'}`): "
                    f"{f.description}"
                    for f in score.findings[:20]
                ],
                *format_artifact_manifest_lines(
                    score.execution_dag,
                    fallback_manifest={
                        "score_json": f"reports/{score.workflow_id or target}_score.json",
                        "summary_json": f"reports/{score.workflow_id or target}_summary.json",
                        "findings_sarif": f"reports/{score.workflow_id or target}_findings.sarif",
                        "rollup_facts_json": f".pni/cache/{score.workflow_id or target}/rollup_facts.json",
                    },
                ),
            ],
        ),
        BlueprintChapterSpec(
            filename="05_component_deep_dives.md",
            title=titles["05"],
            purpose="Dedicated subsection per component summarizing 7-axis scores, coverage, and top findings.",
            required_diagrams=["Per-Component Scorecard Table (`drawlib.smartarts.Table`)"],
            sorted_data_markdown=[
                f"### Component `{c.component_id}` (`{c.language}` — `{c.root}`)\n"
                f"- Score: **{c.overall_score}/100 ({c.grade})** | LOC: `{c.total_loc}` | "
                f"Coverage: `{c.measured_line_coverage_pct if c.measured_line_coverage_pct is not None else 'N/A'}%`\n"
                f"- Summary: {c.summary} (Full JSON: `{c.score_file}`)"
                for c in score.components
            ],
        ),
    ]
    return ReportBlueprint(
        target=target,
        lang=lang,
        style=style,
        workflow_id=score.workflow_id,
        workflow_run_id=score.workflow_run_id,
        overall_score=score.overall_score,
        grade=score.grade,
        chapters=chapters,
    )
