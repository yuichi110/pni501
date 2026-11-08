# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic ReportBlueprint builder converting sorted ScoreResult data into 00..06 chapter specs."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pydantic import BaseModel, Field

from pni._actions.base_model import (
    ArchitectureRecord,
    MetricScalar,
    ScoreResult,
    consolidate_findings_by_location,
)
from pni._actions.runtime_check.parsers import extract_verbatim_error_excerpt
from pni._cache import default_blueprint_rel_path, ensure_cache_parent

_CHAPTER_TITLES: Final[dict[str, dict[str, str]]] = {
    "ja": {
        "00": "PNI ソフトウェア健全性診断レポート",
        "01": "1. エグゼクティブサマリー",
        "02": "2. アーキテクチャとソースコード構成",
        "03": "3. 推奨する変更対応",
        "04": "4. 検査指標・ルール適合マトリクスと指摘一覧",
        "05": "5. 詳細分析：コード品質・テスト・動的検証",
        "06": "6. 詳細分析：セキュリティ・脆弱性・API境界",
    },
    "en": {
        "00": "PNI Software Health Diagnostic Report",
        "01": "1. Executive Summary",
        "02": "2. Architecture & Source Code Structure",
        "03": "3. Recommended Remediation Roadmap",
        "04": "4. Audit Standards, Rule Compliance & Findings",
        "05": "5. Deep Dive: Code Quality, Testing & Runtime",
        "06": "6. Deep Dive: Security, Supply Chain & API Surface",
    },
}


class BlueprintChapterSpec(BaseModel):
    """Specification and pre-sorted data payload for a single numbered Drawlib Markdown chapter."""

    filename: str
    title: str
    purpose: str
    required_diagrams: list[str] = Field(default_factory=list)
    sorted_data_markdown: list[str] = Field(default_factory=list)


class ReportBlueprint(BaseModel):
    """Deterministically ordered 7-file (`00_cover` + `01`..`06`) visual report blueprint."""

    target: str
    lang: str = "en"
    style: str = "google"
    workflow_id: str = ""
    workflow_run_id: str = ""
    overall_score: int = 0
    grade: str = "B"
    passed_rules_count: int = 0
    total_rules_count: int = 0
    chapters: list[BlueprintChapterSpec] = Field(default_factory=list)

    @property
    def expected_filenames(self) -> list[str]:
        """Return ordered list of chapter Markdown filenames required in <target>_src/."""
        return [ch.filename for ch in self.chapters]


def _pick_titles(lang: str) -> dict[str, str]:
    """Select localized chapter title dictionary ('ja' or default 'en')."""
    return _CHAPTER_TITLES["ja"] if lang.lower().startswith("ja") else _CHAPTER_TITLES["en"]


def _build_cover_chapter(
    score: ScoreResult,
    titles: dict[str, str],
    passed_rules: int,
    total_rules: int,
) -> BlueprintChapterSpec:
    """Build `00_cover.md` (Dedicated Cover Page immediately preceding auto-generated ToC)."""
    data = [
        f"- **Project**: `{score.project_name}` (`{score.target_root}`) | **Language**: `{score.language}`",
        f"- **Workflow**: `{score.workflow_id}` | **Run ID**: `{score.workflow_run_id}`",
        f"- **Evaluated At**: `{score.evaluated_at or 'latest'}`",
        f"- **Overall Score & Grade**: **{score.overall_score}/100 (Grade {score.grade})**",
        f"- **Rule Pass Rate**: `{passed_rules}/{total_rules}` rules passed",
    ]
    return BlueprintChapterSpec(
        filename="00_cover.md",
        title=titles["00"],
        purpose=(
            "Dedicated cover page displaying project identity, evaluation metadata, and Overall Score/Grade "
            "hero badge (Drawlib automatically inserts the Table of Contents right after `00_cover.md`)."
        ),
        required_diagrams=[
            (
                "Cover Hero Scorecard Banner (`Panel` + `KpiCards`: Overall Score/Grade, "
                "Target Language, Rule Pass Rate, Total Findings)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _format_runtime_and_security_summary_kpis(score: ScoreResult) -> list[str]:
    """Format concise runtime and security headline lines for Chapter 1 Executive Summary."""
    lines: list[str] = []
    if score.runtime_facts is not None:
        rf = score.runtime_facts
        cov_str = (
            f"{rf.coverage.line_coverage_pct}%"
            if rf.coverage.measured and rf.coverage.line_coverage_pct is not None
            else "N/A"
        )
        lines.append(
            f"- **Container Runtime Verification**: status=`{rf.status}`, "
            f"build=`{rf.harness_build.status}`, "
            f"tests=`{rf.test_execution.passed_tests}/{rf.test_execution.total_tests}` (`{rf.test_execution.status}`), "
            f"line_cov=`{cov_str}`, smoke=`{rf.smoke_check.status}` (`{rf.smoke_check.archetype}`)"
        )
    if score.security_facts is not None:
        sf = score.security_facts
        ac = sf.app_vuln_counts
        lines.append(
            f"- **Security & Supply-Chain Headline**: status=`{sf.status}`, "
            f"app_cves=`{ac.total}` (CRITICAL=`{ac.critical}`, HIGH=`{ac.high}`), "
            f"misconfigs=`{len(sf.misconfigurations)}`, secrets=`{len(sf.secrets)}`"
        )
    if score.pentest_facts is not None:
        pf = score.pentest_facts
        ps = pf.probe_summary
        lines.append(
            f"- **Dynamic Web Penetration Test (`web_pentest`)**: status=`{pf.status}`, "
            f"probes=`{ps.passed_probes}/{ps.total_probes}` passed, "
            f"findings=`{len(pf.findings)}` (`{pf.pentests_dir or '.pni/pentests'}`)"
        )
    return lines


def _build_executive_summary_chapter(
    score: ScoreResult,
    titles: dict[str, str],
    passed_rules: int,
    total_rules: int,
) -> BlueprintChapterSpec:
    """Build `01_executive_summary.md` (1. Executive Summary: 7-Axis Radar + Key KPIs & Top Risks)."""
    cats = score.category_scores
    sev_counts: dict[str, int] = {}
    for f in score.findings:
        sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1
    weakest = score.audit_dimensions[:3]
    weak_str = ", ".join(f"{d.audit_id}={d.score}({d.grade})" for d in weakest) if weakest else "None"

    data = [
        f"- **Executive Synthesis**: {score.summary}",
        (
            f"- **Overall Health**: **{score.overall_score}/100 (Grade {score.grade})**, "
            f"`{passed_rules}/{total_rules}` rules passed"
        ),
        (
            f"- **7-Axis Radar Series**: `[architecture={cats.architecture}, "
            f"code_quality={cats.code_quality}, typing={cats.typing}, "
            f"testing={cats.testing}, dependencies={cats.dependencies}, "
            f"security={cats.security}, documentation={cats.documentation}]`"
        ),
        f"- **Findings Count by Severity**: `{sev_counts or {'violations': 0}}`",
        f"- **Lowest-Scoring Audit Steps (Sorted Ascending)**: {weak_str}",
        *_format_runtime_and_security_summary_kpis(score),
    ]
    for s in score.strengths[:4]:
        data.append(f"- **Strength**: {s}")
    for top_f in score.findings[:3]:
        data.append(f"- **Top Risk (`[{top_f.severity.upper()}]` `{top_f.rule_id}`)**: {top_f.description}")

    return BlueprintChapterSpec(
        filename="01_executive_summary.md",
        title=titles["01"],
        purpose=(
            "Deliver the 1-page executive conclusion: 7-dimension balance radar, headline health KPIs "
            "(rule compliance, test/coverage, CVE/security status), key strengths, and top risks."
        ),
        required_diagrams=[
            (
                "7-Dimension Engineering Health Radar (`RadarChart`: Architecture, Code Quality, Typing, "
                "Testing, Dependencies, Security, Documentation)"
            ),
            (
                "Executive Health KPIs + Strengths vs Top Risks (`KpiCards` + `CardList`)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _format_structure_lines(arch: ArchitectureRecord | None, score: ScoreResult) -> list[str]:
    """Format SystemProfile, StructureMap layers, and AST module_inventory source tree details."""
    lines: list[str] = []
    if arch and arch.system_profile:
        sp = arch.system_profile
        lines.append(
            f"- **System Profile**: runtime=`{sp.runtime_types}`, stack={sp.tech_stack}, "
            f"integrations={sp.external_integrations or ['None']} — {sp.system_purpose}"
        )
    if arch and arch.structure_map:
        sm = arch.structure_map
        lines.append(f"- **Architecture Pattern**: {sm.architecture_pattern}")
        for layer in sm.layers:
            lines.append(
                f"  - **Layer `{layer.name}`**: paths={layer.paths}, "
                f"allowed_deps={layer.allowed_dependencies} — {layer.responsibility}"
            )
        if sm.boundary_assessment:
            lines.append(f"- **Boundary Assessment**: {sm.boundary_assessment}")
    elif score.architecture_overview.pattern:
        lines.append(f"- **Architecture Pattern**: {score.architecture_overview.pattern}")

    if score.module_inventory:
        lines.append(f"- **Source Code Module Inventory (`TreeNode` / `Table`, {len(score.module_inventory)} files)**:")
        for mod in score.module_inventory[:20]:
            lines.append(
                f"  - `{mod.file}` (`{mod.loc}` LOC): types={mod.public_types[:4]}, "
                f"callables={mod.public_callables[:5]}"
            )
    elif score.architecture_overview.modules:
        lines.append("- **Mapped Modules**:")
        for m in score.architecture_overview.modules[:15]:
            lines.append(f"  - `{m.path}`: {m.role} (depends_on={m.depends_on})")
    return lines


def _format_flow_and_hotspot_lines(arch: ArchitectureRecord | None, score: ScoreResult) -> list[str]:
    """Format pre-sorted module hotspots and ExecutionFlowMap runtime flows."""
    lines: list[str] = []
    if score.module_hotspots:
        lines.append("- **Pre-Sorted Module Hotspots (`HeatmapOverlay` exact `value`s, descending risk)**:")
        for hs in score.module_hotspots[:8]:
            lines.append(
                f"  - `{hs.file_path}` ({hs.loc} LOC): **risk_score=`{hs.risk_score:.2f}`**, "
                f"findings={hs.finding_counts or '0'}, rules={hs.top_rules}"
            )
    if arch and arch.execution_flow_map:
        fm = arch.execution_flow_map
        lines.append(f"- **Entry Points**: {fm.entry_points}")
        for flow in fm.execution_flows:
            lines.append(f"  - **Flow `{flow.name}`** (trigger: {flow.trigger}): {' -> '.join(flow.steps)}")
        if fm.state_and_storage:
            lines.append(f"- **State & Storage**: {fm.state_and_storage}")
        if fm.error_and_concurrency_model:
            lines.append(f"- **Error & Concurrency Model**: {fm.error_and_concurrency_model}")
    return lines


def _build_architecture_chapter(score: ScoreResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `02_architecture_and_structure.md` (2. Architecture & Source Code Structure)."""
    data = [
        *_format_structure_lines(score.architecture_record, score),
        *_format_flow_and_hotspot_lines(score.architecture_record, score),
    ]
    if not data:
        data = [f"- **Modules**: {[m.path for m in score.architecture_overview.modules]}"]
    return BlueprintChapterSpec(
        filename="02_architecture_and_structure.md",
        title=titles["02"],
        purpose=(
            "Visualize the discovered architecture and physical source layout: directory/module tree with "
            "LOC & responsibilities, layer dependency graph with thermal risk overlay, and runtime execution flows."
        ),
        required_diagrams=[
            (
                "Source Directory & Module Structure Tree (`TreeNode` + Module Responsibility/LOC `Table` "
                "grounded in `module_inventory`)"
            ),
            (
                "Layer & Component Dependency Diagram + Thermal Risk Overlay (`ClassDiagram` + `HeatmapOverlay` "
                "using exact `module_hotspots.risk_score` values) and Execution Flow `Roadmap`"
            ),
        ],
        sorted_data_markdown=data,
    )


def _build_remediation_roadmap_chapter(score: ScoreResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `03_remediation_roadmap.md` (3. Recommended Remediation Roadmap: P0 -> P1 -> P2)."""
    data: list[str] = []
    if score.action_plan:
        data.append(f"- **Remediation Action Plan (Pre-Sorted `P0 -> P1 -> P2`, total={len(score.action_plan)})**:")
        for idx, item in enumerate(score.action_plan, start=1):
            rules_lbl = f", related_rules={item.related_rules}" if item.related_rules else ""
            data.append(
                f"  {idx}. `[{item.priority}]` **{item.title}** (`{item.category}`, "
                f"targets={item.target_files}{rules_lbl}): {item.action} (Impact: {item.expected_impact})"
            )
    else:
        data.append(
            "- **Remediation Action Plan**: `0` urgent P0/P1 defects; present continuous-improvement maintenance "
            "milestones (dependency pinning automation, coverage guardrails, periodic CVE scanning)."
        )

    return BlueprintChapterSpec(
        filename="03_remediation_roadmap.md",
        title=titles["03"],
        purpose=(
            "Present concrete, prioritized engineering actions (`P0` urgent -> `P1` high-value -> `P2` polish) "
            "with exact target files, expected impact, and traceability to rule IDs / CVEs."
        ),
        required_diagrams=[
            "Phased Remediation Timeline `P0 -> P1 -> P2` (`Roadmap`)",
            (
                "Action Plan Traceability Matrix (`Table`: Priority, Action Title, `target_files`, "
                "`expected_impact`, and `related_rules`)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _build_standards_and_findings_chapter(score: ScoreResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `04_standards_and_findings.md` (4. Audit Standards, Rule Compliance & Findings)."""
    data: list[str] = []
    if score.audit_dimensions:
        data.append("- **Audit Step Scores (Pre-Sorted Weakest -> Strongest for `BarChart`)**:")
        for dim in score.audit_dimensions:
            data.append(
                f"  - `{dim.audit_id}`: **{dim.score}/100 ({dim.grade})** "
                f"[pass={dim.pass_count}, warn={dim.warn_count}, fail={dim.fail_count}] — {dim.summary}"
            )
    if score.rule_compliance:
        data.append("- **Rule Compliance Matrix (Pre-Sorted `FAIL -> WARN -> PASS` for `Table`)**:")
        for rc in score.rule_compliance:
            data.append(
                f"  - `[{rc.status.upper()}]` | `{rc.rule_id}` | `{rc.source_action}` | {rc.evidence}"
            )

    consolidated = score.consolidated_findings or consolidate_findings_by_location(score.findings)
    if consolidated:
        data.append(
            "- **Consolidated Location Findings Index (Pre-Sorted `CRITICAL -> HIGH -> MEDIUM -> LOW -> INFO`, "
            f"consolidated_locations={len(consolidated)} from raw_findings={len(score.findings)} — "
            "render 1 row per location in `Table` without duplicating `file:line`)**:"
        )
        for idx, cf in enumerate(consolidated, start=1):
            loc = f"{cf.file_path}:{cf.line}" if cf.file_path and cf.line else (cf.file_path or "-")
            rules_lbl = ", ".join(cf.rule_ids)
            data.append(
                f"  {idx}. `[{cf.severity.upper()}]` `{loc}` | rules=`[{rules_lbl}]` — "
                f"Evidence: `{cf.combined_evidence}` -> Fix: {cf.merged_recommendation}"
            )
    else:
        data.append("- **Findings Index**: `0` rule violations across all evaluated standards.")

    if score.opt_outs:
        data.append(
            f"- **Configured Scope & Accepted Design Waivers (`pni.toml`, total={len(score.opt_outs)})**:"
        )
        for idx, wv in enumerate(score.opt_outs, start=1):
            scope_lbl = ", ".join(wv.scope) if wv.scope else "repo-wide"
            data.append(
                f"  {idx}. `{wv.id}` | scope=`[{scope_lbl}]` | matched=`{wv.matched_count}` — "
                f"Reason: {wv.reason}"
            )

    return BlueprintChapterSpec(
        filename="04_standards_and_findings.md",
        title=titles["04"],
        purpose=(
            "Bridge high-level recommendations to detailed chapters by presenting every audit step score, "
            "the full `FAIL -> WARN -> PASS` rule compliance matrix, the consolidated `CRITICAL -> INFO` "
            "findings index (grouped by `file:line` to eliminate duplicate rows), and any configured "
            "`pni.toml` design waivers (`[[opt_out]]`)."
        ),
        required_diagrams=[
            (
                "Executed Audit Step Score Comparison (`BarChart`, weakest-first) + "
                "Rule Compliance Matrix (`Table`, `FAIL -> WARN -> PASS`)"
            ),
            (
                "Consolidated Location Findings Evidence Table (`Table` preserving exact `CRITICAL -> INFO` "
                "order with multi-rule tags per `file:line`)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _fmt_metric_group(title: str, m: dict[str, MetricScalar], keys: tuple[str, ...]) -> str:
    """Format a subset of metrics_snapshot keys into a compact bullet line."""
    pairs = [f"`{k}={m[k]}`" for k in keys if k in m]
    return f"- **{title}**: {', '.join(pairs)}" if pairs else ""


def _format_runtime_verbatim_evidence(score: ScoreResult) -> list[str]:
    """Format verbatim compiler/build/test/smoke failure excerpts from RuntimeFacts for Chapter 5."""
    rf = score.runtime_facts
    if rf is None:
        return []
    lines: list[str] = []
    if rf.project_dockerfile_build is not None and rf.project_dockerfile_build.status == "failed":
        excerpt = extract_verbatim_error_excerpt(rf.project_dockerfile_build.error_tail, max_lines=4)
        if excerpt:
            lines.append(
                f"- **Project Dockerfile Verbatim Failure Excerpt (`{rf.project_dockerfile_build.dockerfile_used}`)**:"
            )
            lines.extend(f"  - `{ln}`" for ln in excerpt)
    if rf.harness_build.status == "failed" and rf.harness_build.error_tail:
        excerpt = extract_verbatim_error_excerpt(rf.harness_build.error_tail, max_lines=5)
        if excerpt:
            lines.append("- **Harness Build / Compiler Verbatim Failure Excerpt (`harness_build`)**:")
            lines.extend(f"  - `{ln}`" for ln in excerpt)
    if rf.test_execution.failures:
        total_fail = len(rf.test_execution.failures)
        lines.append(f"- **Failed / Error Unit Test Cases (`test_execution`, total={total_fail})**:")
        for fc in rf.test_execution.failures[:8]:
            lines.append(f"  - `[{fc.kind.upper()}]` `{fc.classname}.{fc.name}`: `{fc.message[:200]}`")
    if rf.smoke_check.status in {"failed", "error", "timeout"} and rf.smoke_check.log_tail:
        excerpt = extract_verbatim_error_excerpt(rf.smoke_check.log_tail, max_lines=4)
        if excerpt:
            lines.append(f"- **Startup Smoke Check Verbatim Failure Excerpt (`{rf.smoke_check.failure_kind}`)**:")
            lines.extend(f"  - `{ln}`" for ln in excerpt)
    return lines


def _build_code_and_runtime_chapter(score: ScoreResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `05_code_and_runtime_analysis.md` (5. Deep Dive: Code Quality, Testing & Runtime)."""
    m = score.metrics_snapshot
    groups = [
        _fmt_metric_group(
            "Codebase & Static Quality Coverage",
            m,
            (
                "total_files",
                "total_loc",
                "total_functions",
                "import_hygiene_coverage_pct",
                "type_safety_coverage_pct",
                "docstring_coverage_pct",
                "module_test_coverage_pct",
            ),
        ),
        _fmt_metric_group(
            "SIG Maintainability & Coupling",
            m,
            (
                "complex_functions_count",
                "excessive_parameters_count",
                "global_state_usages_count",
                "circular_dependencies_count",
                "bug_risk_idioms_count",
                "undeclared_dependencies_count",
                "language_version_mismatches_count",
            ),
        ),
        _fmt_metric_group(
            "Operational Readiness (12-Factor / PRR)",
            m,
            (
                "missing_io_timeouts_count",
                "scattered_env_access_count",
                "unstructured_logging_count",
            ),
        ),
        _fmt_metric_group(
            "Container Runtime & Measured Coverage",
            m,
            (
                "runtime_status",
                "harness_build_status",
                "tests_passed",
                "tests_failed",
                "measured_line_coverage_pct",
                "measured_branch_coverage_pct",
                "smoke_check_status",
            ),
        ),
    ]
    data = [g for g in groups if g] or ["- **Metrics**: Load `metrics_snapshot` from `score.json`."]
    if score.language_version_mismatches:
        data.append(
            f"- **AST Declared Language-Version API / Syntax Mismatches "
            f"(total={len(score.language_version_mismatches)})**:"
        )
        for loc in score.language_version_mismatches[:10]:
            data.append(f"  - `{loc.file}:{loc.line}` (`{loc.symbol}`): {loc.detail}")
    data.extend(_format_runtime_verbatim_evidence(score))
    if score.runtime_facts and score.runtime_facts.coverage.lowest_covered_modules:
        data.append("- **Lowest-Covered Modules (Measured Line & Branch Coverage, Ascending)**:")
        for item in score.runtime_facts.coverage.lowest_covered_modules[:8]:
            br = f", branch=`{item.branch_coverage_pct}%`" if item.branch_coverage_pct is not None else ""
            data.append(
                f"  - `{item.file_path}`: line=`{item.line_coverage_pct}%`{br} "
                f"(`{item.covered_lines}/{item.total_statements}` stmts, missing={item.missing_lines_preview[:8]})"
            )
    return BlueprintChapterSpec(
        filename="05_code_and_runtime_analysis.md",
        title=titles["05"],
        purpose=(
            "Deep-dive quantitative analysis of AST code quality, SIG maintainability, typing, "
            "12-Factor operational readiness, containerized build/unit tests (citing verbatim compiler/runtime "
            "error excerpts when stages fail), measured coverage, and smoke checks."
        ),
        required_diagrams=[
            "Module × Quality Dimension Fitness Matrix (`HeatmapChart`)",
            (
                "Container Runtime Verification & Lowest-Covered Modules Breakdown (`BarChart` / `Table`, "
                "or Static AST Test Health when container runtime was skipped)"
            ),
        ],
        sorted_data_markdown=data,
    )


def _format_trivy_security_lines(score: ScoreResult) -> list[str]:
    """Format Trivy CVE, misconfiguration, and redacted secret lines for Chapter 6."""
    sf = score.security_facts
    if sf is None:
        return [
            "- **Container Vulnerability Scan (`security_scan`)**: Not executed in static quick-check mode "
            "(evaluate supply-chain lockfile/pinning hygiene from `metrics_snapshot` + AST security facts below)."
        ]
    ac = sf.app_vuln_counts
    cc = sf.core_app_vuln_counts
    dc = sf.dev_app_vuln_counts
    oc = sf.os_vuln_counts
    hc = sf.harness_os_vuln_counts
    lines = [
        (
            f"- **Trivy Security Scan (`status={sf.status}`)**: engine=`{sf.container_engine}`, "
            f"fs=`{sf.scanned_filesystem}`, resolved_image=`{sf.scanned_resolved_image}` "
            f"(`{sf.resolved_image_source or 'none'}`)"
        ),
        (
            f"- **Application Dependency CVEs (Total=`{ac.total}`)**: "
            f"Core Runtime=`{cc.total}` (CRITICAL=`{cc.critical}`, HIGH=`{cc.high}`, "
            f"MEDIUM=`{cc.medium}`, LOW=`{cc.low}`) | "
            f"Dev/Optional Lockfile=`{dc.total}` (CRITICAL=`{dc.critical}`, HIGH=`{dc.high}`, "
            f"MEDIUM=`{dc.medium}`, LOW=`{dc.low}`)"
        ),
        (
            f"- **Container OS Base-Image CVEs**: Project Dockerfile OS=`{oc.total}` "
            f"(CRITICAL=`{oc.critical}`, HIGH=`{oc.high}`, MEDIUM=`{oc.medium}`, LOW=`{oc.low}`)"
            + (
                f" | Test Harness Base-OS (`{sf.resolved_image_source}`, non-shipped)=`{hc.total}` "
                f"(CRITICAL=`{hc.critical}`, HIGH=`{hc.high}`)"
                if hc.total > 0
                else ""
            )
        ),
    ]
    app_items = sf.app_vulnerabilities or [
        v for v in sf.vulnerabilities if v.scope in {"runtime_core", "dev_or_optional"}
    ]
    for v in app_items[:15]:
        fix_lbl = f" -> fix=`{v.fixed_version}`" if v.fixed_version else " (no upstream fix)"
        unpinned_lbl = (
            f" | [UNPINNED SPECIFIER RANGE MATCH — {v.version_resolution_note}]"
            if v.is_unpinned_specifier
            else ""
        )
        lines.append(
            f"  - **App CVE** `[{v.severity}]` `[{v.scope}]` `{v.vuln_id}` | "
            f"`{v.pkg_name}@{v.installed_version}` (`{v.pkg_type}`){fix_lbl}{unpinned_lbl} | {v.title[:90]}"
        )
    for v in sf.os_vulnerabilities[:10]:
        fix_lbl = f" -> fix=`{v.fixed_version}`" if v.fixed_version else " (no upstream fix)"
        lines.append(
            f"  - **OS CVE** `[{v.severity}]` `{v.vuln_id}` | `{v.pkg_name}@{v.installed_version}` "
            f"(`{v.pkg_type}`){fix_lbl} | {v.title[:90]}"
        )
    for mc in sf.misconfigurations[:10]:
        ln = f":{mc.start_line}" if mc.start_line else ""
        lines.append(f"  - **Misconfig** `[{mc.severity}]` `{mc.check_id}` (`{mc.file_path}{ln}`): {mc.title}")
    for sec in sf.secrets[:10]:
        ln = f":{sec.start_line}" if sec.start_line else ""
        lines.append(
            f"  - **Secret (Redacted)** `[{sec.severity}]` `{sec.rule_id}` (`{sec.file_path}{ln}`): "
            f"`{sec.redacted_match}`"
        )
    return lines


def _build_security_and_supply_chain_chapter(score: ScoreResult, titles: dict[str, str]) -> BlueprintChapterSpec:
    """Build `06_security_and_supply_chain.md` (6. Deep Dive: Security, Supply Chain & API Surface)."""
    m = score.metrics_snapshot
    supply_line = _fmt_metric_group(
        "Supply-Chain & Governance Baseline",
        m,
        (
            "has_lockfile",
            "dependencies_count",
            "unpinned_dependencies_count",
            "has_security_policy",
            "has_dependency_automation",
            "committed_secret_files_count",
            "hardcoded_secrets_count",
            "ast_dangerous_sinks_count",
            "api_endpoints_count",
        ),
    )
    data: list[str] = [supply_line] if supply_line else []
    data.extend(_format_trivy_security_lines(score))

    if score.dangerous_sinks:
        data.append(f"- **AST Dangerous Code Sinks (CWE SAST, total={len(score.dangerous_sinks)})**:")
        for sink in score.dangerous_sinks[:15]:
            data.append(
                f"  - `[{sink.severity.upper()}]` `{sink.cwe_id}` (`{sink.category}`) at "
                f"`{sink.file}:{sink.line}`: {sink.detail}"
            )
    else:
        data.append("- **AST Dangerous Code Sinks (CWE SAST)**: `0` dangerous sinks detected in production source.")

    if score.api_endpoints:
        unauth = sum(1 for ep in score.api_endpoints if not ep.has_auth_hint)
        data.append(
            f"- **Extracted API Attack Surface (`api_endpoints`, total={len(score.api_endpoints)}, "
            f"without_auth_hint={unauth})**:"
        )
        for ep in score.api_endpoints[:20]:
            auth_lbl = f"auth={ep.auth_mechanisms}" if ep.has_auth_hint else "auth_hint=NONE"
            data.append(
                f"  - `{ep.http_method} {ep.path}` -> `{ep.handler}` (`{ep.file}:{ep.line}`, {auth_lbl})"
            )
    else:
        data.append("- **Extracted API Attack Surface (`api_endpoints`)**: `0` HTTP routes (library / CLI profile).")

    if score.pentest_facts is not None:
        pf = score.pentest_facts
        ps = pf.probe_summary
        data.append(
            f"- **Dynamic Web Penetration Testing (`web_pentest`, status=`{pf.status}`)**: "
            f"suite=`{pf.pentests_dir or '.pni/pentests'}`, probes=`{ps.passed_probes}/{ps.total_probes}` passed "
            f"(failed=`{ps.failed_probes}`, skipped=`{ps.skipped_probes}`, skip_reason=`{pf.skip_reason or 'none'}`)"
        )
        for finding in pf.findings[:15]:
            data.append(
                f"  - **DAST** `[{finding.severity.upper()}]` `{finding.cwe_id}` on `{finding.endpoint}` "
                f"(`{finding.test_file}`): {finding.title} — `{finding.evidence}`"
            )

    return BlueprintChapterSpec(
        filename="06_security_and_supply_chain.md",
        title=titles["06"],
        purpose=(
            "Deep-dive analysis of dependency & OS container CVEs (with fixed versions), Dockerfile hardening, "
            "secret hygiene, CWE-tagged dangerous AST sinks, and HTTP API authorization boundaries."
        ),
        required_diagrams=[
            (
                "Supply-Chain & Container Vulnerability Breakdown (`BarChart` / `Table` comparing App vs OS CVEs, "
                "installed -> `fixed_version`, IaC misconfigs, and secret scan status)"
            ),
            (
                "AST Dangerous Code Sinks (CWE) & API Endpoint Attack Surface Map (`Table` / `CardList` "
                "listing CWE sinks and HTTP routes with auth-boundary status)"
            ),
        ],
        sorted_data_markdown=data,
    )


def build_report_blueprint(
    score: ScoreResult,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
) -> ReportBlueprint:
    """Construct a deterministic 7-file (`00_cover` + `01`..`06`) ReportBlueprint from ScoreResult."""
    titles = _pick_titles(lang)
    total_rules = len(score.rule_compliance)
    passed_rules = sum(1 for r in score.rule_compliance if r.status == "pass")
    chapters = [
        _build_cover_chapter(score, titles, passed_rules, total_rules),
        _build_executive_summary_chapter(score, titles, passed_rules, total_rules),
        _build_architecture_chapter(score, titles),
        _build_remediation_roadmap_chapter(score, titles),
        _build_standards_and_findings_chapter(score, titles),
        _build_code_and_runtime_chapter(score, titles),
        _build_security_and_supply_chain_chapter(score, titles),
    ]
    return ReportBlueprint(
        target=target,
        lang=lang,
        style=style,
        workflow_id=score.workflow_id,
        workflow_run_id=score.workflow_run_id,
        overall_score=score.overall_score,
        grade=score.grade,
        passed_rules_count=passed_rules,
        total_rules_count=total_rules,
        chapters=chapters,
    )


def render_blueprint_markdown(blueprint: ReportBlueprint, blueprint_rel_path: str = "") -> str:
    """Render the chapter-by-chapter pre-sorted ReportBlueprint into Markdown instructions."""
    loc_note = f" (persisted at `{blueprint_rel_path}`)" if blueprint_rel_path else ""
    lines = [
        f"#### Deterministic 6-Chapter Report Blueprint (`00_cover.md` + `01`..`06`){loc_note}",
        (
            "All 7-axis scores, compliance checks, hotspots, findings, runtime metrics, security CVEs, "
            "dangerous sinks, API endpoints, and roadmap items below have ALREADY been "
            "**programmatically aggregated, deduplicated, and sorted by PNI**. "
            "Do NOT re-order rows, drop audit dimensions, or invent metrics."
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


def _resolve_safe_workspace_path(root: Path, rel_or_abs: str) -> Path | None:
    """Resolve rel_or_abs safely inside root, returning None if outside workspace boundary."""
    root_resolved = root.resolve()
    candidate = (root_resolved / rel_or_abs).resolve()
    if candidate != root_resolved and not candidate.is_relative_to(root_resolved):
        return None
    return candidate


def load_or_build_blueprint(
    project_root: Path | None,
    score_path: str,
    *,
    target: str,
    lang: str = "en",
    style: str = "google",
    workflow_id: str = "",
) -> tuple[ReportBlueprint | None, str]:
    """Load ScoreResult from score_path if present, build ReportBlueprint, and persist JSON cache."""
    if project_root is None:
        return None, ""
    score_file = _resolve_safe_workspace_path(project_root, score_path)
    if score_file is None or not score_file.is_file():
        return None, ""

    score = ScoreResult.model_validate_json(score_file.read_text(encoding="utf-8"))
    blueprint = build_report_blueprint(score, target=target, lang=lang, style=style)
    cache_key = (workflow_id or score.workflow_id or target).strip() or "full_audit"
    rel_bp = default_blueprint_rel_path(cache_key)
    bp_file = _resolve_safe_workspace_path(project_root, rel_bp)
    if bp_file is not None:
        ensure_cache_parent(project_root, bp_file)
        bp_file.write_text(blueprint.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return blueprint, rel_bp
