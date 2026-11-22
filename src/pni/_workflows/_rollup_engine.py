# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Multi-Language / Monorepo Multi-Audit Rollup collector, hybrid weighted scorer, and synthesizer."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, Optional

from pydantic import BaseModel, Field

from pni._actions import (
    ActionItem,
    AstFacts,
    CategoryRationales,
    CategoryScores,
    ComponentScoreSummary,
    Finding,
    ProjectFacts,
    RollupSynthesisInput,
    ScoreResult,
    consolidate_findings_by_location,
    record_audit_history_from_score,
    run_project_inspect,
)
from pni._actions.ast_analyze.companion import scan_companion_languages
from pni._cache import ensure_cache_parent
from pni._reporter import DEFAULT_REPORT_OUTPUT_DIR
from pni._reporter.sarif import (
    build_score_summary,
    default_sarif_rel_path,
    default_summary_rel_path,
    write_sarif_report,
    write_score_summary,
)
from pni._workflows.aggregator import PRIORITY_RANK, SEVERITY_RANK, score_to_grade
from pni._workflows.base_model import (
    ActionRunRecord,
    RollupComponentSpec,
    WorkflowDefinition,
    WorkflowPrerequisiteError,
    WorkflowRunRecord,
)
from pni._workflows.planner import default_plan_rel_path
from pni._workflows.provenance import build_rollup_execution_dag_summary

_WEAKEST_LINK_MARGIN: Final[int] = 15
_CATEGORY_KEYS: Final[tuple[str, ...]] = (
    "architecture",
    "code_quality",
    "typing",
    "testing",
    "dependencies",
    "security",
    "documentation",
)


class RollupComponentData(BaseModel):
    """Loaded sub-audit score and normalized weight for one rollup component."""

    spec: RollupComponentSpec
    score_file: str
    score: ScoreResult
    normalized_weight: float = 1.0


class RollupFacts(BaseModel):
    """Aggregated deterministic facts combining N sub-audits, root governance, and companion DSLs."""

    workflow_id: str
    components: list[ComponentScoreSummary] = Field(default_factory=list)
    weighted_category_scores: CategoryScores
    weighted_overall_score: int = Field(ge=0, le=100)
    root_project_facts: Optional[ProjectFacts] = None
    companion_ast_facts: dict[str, AstFacts] = Field(default_factory=dict)
    merged_findings: list[Finding] = Field(default_factory=list)
    merged_action_plan: list[ActionItem] = Field(default_factory=list)
    merged_strengths: list[str] = Field(default_factory=list)
    weakest_link_notes: list[str] = Field(default_factory=list)


def _locate_component_score_file(project_root: Path, spec: RollupComponentSpec) -> Optional[Path]:
    """Resolve `reports/<workflow_or_id>_score.json` for a RollupComponentSpec."""
    wf_id = (spec.workflow_id or spec.id).strip()
    candidates = [
        project_root / DEFAULT_REPORT_OUTPUT_DIR / f"{wf_id}_score.json",
        project_root / DEFAULT_REPORT_OUTPUT_DIR / f"{spec.id}_score.json",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def inspect_rollup_prerequisites(
    workflow_def: WorkflowDefinition,
    project_root: Path,
) -> Optional[str]:
    """Ensure every component declared in `includes` already has a completed score JSON."""
    if not workflow_def.includes:
        return None
    missing = [
        f"{spec.id} (expected reports/{spec.workflow_id or spec.id}_score.json)"
        for spec in workflow_def.includes
        if _locate_component_score_file(project_root, spec) is None
    ]
    if missing:
        return (
            f"Rollup workflow '{workflow_def.id}' is missing completed sub-audit score(s): "
            f"{', '.join(missing)}. Run the component sub-audits first."
        )
    return None


def _compute_normalized_weights(loaded: list[tuple[RollupComponentSpec, Path, ScoreResult]]) -> list[float]:
    """Compute normalized component weights using explicit overrides or log1p(LOC) smoothing."""
    raw_weights: list[float] = []
    for spec, _, sr in loaded:
        if spec.weight is not None and spec.weight > 0:
            raw_weights.append(float(spec.weight))
        else:
            raw_loc = sr.metrics_snapshot.get("total_loc")
            loc = int(raw_loc) if isinstance(raw_loc, (int, float)) and raw_loc > 0 else 100
            raw_weights.append(max(1.0, math.log1p(loc)))
    total = sum(raw_weights) or 1.0
    return [round(w / total, 4) for w in raw_weights]


def _normalize_component_path(raw_path: Optional[str], comp_root: str) -> Optional[str]:
    """Prefix component-relative file path with comp_root when not already repo-root relative."""
    if not raw_path or not raw_path.strip():
        return raw_path
    clean = raw_path.strip().replace("\\", "/")
    root_norm = comp_root.strip().strip("/")
    if not root_norm or root_norm == "." or clean.startswith(f"{root_norm}/") or clean == root_norm:
        return clean
    return f"{root_norm}/{clean}"


def _aggregate_hybrid_scores(
    items: list[RollupComponentData],
) -> tuple[CategoryScores, int, list[str]]:
    """Compute weighted 7-axis scores plus weakest-link guardrail for security and testing."""
    cat_vals: dict[str, int] = {}
    notes: list[str] = []

    for cat in _CATEGORY_KEYS:
        weighted = sum(getattr(it.score.category_scores, cat) * it.normalized_weight for it in items)
        score_val = max(0, min(100, round(weighted)))
        if cat in {"security", "testing"}:
            primaries = [it for it in items if it.spec.primary]
            if primaries:
                min_comp = min(primaries, key=lambda x: getattr(x.score.category_scores, cat))
                min_score = getattr(min_comp.score.category_scores, cat)
                cap = min_score + _WEAKEST_LINK_MARGIN
                if score_val > cap:
                    notes.append(
                        f"Weakest-link guardrail capped `{cat}` from {score_val} to {cap} "
                        f"(primary component `{min_comp.spec.id}` scored {min_score})."
                    )
                    score_val = cap
        cat_vals[cat] = max(0, min(100, score_val))

    scores = CategoryScores(**cat_vals)
    overall = round(sum(cat_vals.values()) / len(_CATEGORY_KEYS))
    return scores, max(0, min(100, overall)), notes


def execute_rollup_collect(
    run: WorkflowRunRecord,
    project_root: Path,
) -> RollupFacts:
    """Collect component ScoreResults, root governance, companion DSLs, and compute hybrid rollup."""
    loaded: list[tuple[RollupComponentSpec, Path, ScoreResult]] = []
    for spec in run.includes:
        sf = _locate_component_score_file(project_root, spec)
        if sf is None:
            msg = f"Missing sub-audit score JSON for rollup component '{spec.id}'."
            raise WorkflowPrerequisiteError(msg)
        sr = ScoreResult.model_validate_json(sf.read_text(encoding="utf-8"))
        loaded.append((spec, sf, sr))

    weights = _compute_normalized_weights(loaded)
    comp_data = [
        RollupComponentData(
            spec=spec,
            score_file=sf.resolve().relative_to(project_root.resolve()).as_posix(),
            score=sr,
            normalized_weight=w,
        )
        for (spec, sf, sr), w in zip(loaded, weights, strict=True)
    ]

    cat_scores, overall, guard_notes = _aggregate_hybrid_scores(comp_data)
    root_pf = run_project_inspect(project_root, source_dirs=["."], test_dirs=[], doc_files=run.targets.docs)
    companions = scan_companion_languages(project_root, exclude_globs=run.targets.exclude)

    comp_summaries: list[ComponentScoreSummary] = []
    merged_findings: list[Finding] = []
    merged_actions: list[ActionItem] = []
    merged_strengths: list[str] = []

    for item in comp_data:
        sr = item.score
        raw_loc = sr.metrics_snapshot.get("total_loc")
        total_loc = int(raw_loc) if isinstance(raw_loc, (int, float)) else 0
        raw_cov = sr.metrics_snapshot.get("measured_line_coverage_pct")
        line_cov = float(raw_cov) if isinstance(raw_cov, (int, float)) else None
        crit_hi = sum(1 for f in sr.findings if f.severity in {"critical", "high"})
        comp_summaries.append(
            ComponentScoreSummary(
                component_id=item.spec.id,
                language=sr.language,
                root=item.spec.root,
                weight=item.normalized_weight,
                primary=item.spec.primary,
                total_loc=total_loc,
                overall_score=sr.overall_score,
                grade=sr.grade,
                category_scores=sr.category_scores,
                measured_line_coverage_pct=line_cov,
                findings_count=len(sr.findings),
                critical_or_high_count=crit_hi,
                score_file=item.score_file,
                summary=sr.summary,
            )
        )
        for f in sr.findings:
            merged_findings.append(
                f.model_copy(
                    update={
                        "component": f.component or item.spec.id,
                        "file_path": _normalize_component_path(f.file_path, item.spec.root),
                    }
                )
            )
        for act in sr.action_plan:
            norm_files = [
                p for p in (_normalize_component_path(tf, item.spec.root) for tf in act.target_files) if p
            ]
            merged_actions.append(
                act.model_copy(update={"component": act.component or item.spec.id, "target_files": norm_files})
            )
        for st in sr.strengths[:4]:
            merged_strengths.append(f"[{item.spec.id}] {st}")

    merged_findings.sort(
        key=lambda f: (SEVERITY_RANK.get(f.severity, 99), f.component or "", f.file_path or "~", f.line or 0)
    )
    merged_actions.sort(key=lambda a: (PRIORITY_RANK.get(a.priority, 99), a.component or "", a.title))

    return RollupFacts(
        workflow_id=run.workflow_id,
        components=comp_summaries,
        weighted_category_scores=cat_scores,
        weighted_overall_score=overall,
        root_project_facts=root_pf,
        companion_ast_facts=companions,
        merged_findings=merged_findings,
        merged_action_plan=merged_actions,
        merged_strengths=merged_strengths[:15],
        weakest_link_notes=guard_notes,
    )


def render_rollup_facts_markdown(rf: RollupFacts) -> str:
    """Render deterministic RollupFacts into concise Markdown for `synthesize_rollup`."""
    cs = rf.weighted_category_scores
    lines = [
        "\n### Deterministic Multi-Component Rollup Summary",
        (
            f"- **Rolled-Up Overall Score**: `{rf.weighted_overall_score}/100` "
            f"(Grade `{score_to_grade(rf.weighted_overall_score)}`)"
        ),
        (
            f"- **Rolled-Up 7-Axis Scores**: arch=`{cs.architecture}`, code=`{cs.code_quality}`, "
            f"typing=`{cs.typing}`, test=`{cs.testing}`, deps=`{cs.dependencies}`, "
            f"sec=`{cs.security}`, docs=`{cs.documentation}`"
        ),
        "\n| Component | Language | Root | Weight | LOC | Score | Grade | Crit/High |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | :---: | ---: |",
    ]
    for c in rf.components:
        lines.append(
            f"| `{c.component_id}` | `{c.language}` | `{c.root}` | `{c.weight:.2f}` | "
            f"`{c.total_loc}` | `{c.overall_score}` | `{c.grade}` | `{c.critical_or_high_count}` |"
        )
    if rf.weakest_link_notes:
        lines.append("\n- **Weakest-Link Guardrails Applied**:")
        lines.extend(f"  - {note}" for note in rf.weakest_link_notes)
    if rf.companion_ast_facts:
        comp_summary = ", ".join(f"`{k}` ({v.total_files} files)" for k, v in sorted(rf.companion_ast_facts.items()))
        lines.append(f"- **Repo Companion DSLs**: {comp_summary}")
    lines.append(f"- **Merged Component Findings**: `{len(rf.merged_findings)}` total")
    for f in rf.merged_findings[:12]:
        loc = f" (`{f.file_path}:{f.line}`)" if f.file_path else ""
        lines.append(f"  - `[{f.severity.upper()}]` `[{f.component}]` `{f.rule_id}`{loc}: {f.description}")
    return "\n".join(lines)


def validate_and_persist_rollup(
    run: WorkflowRunRecord,
    action: ActionRunRecord,
    rollup_facts: RollupFacts,
    raw_input: str,
    project_root: Path,
    *,
    all_actions: list[ActionRunRecord] | None = None,
) -> str:
    """Validate RollupSynthesisInput, assemble unified ScoreResult, and emit Score + Summary + SARIF."""
    synth = RollupSynthesisInput.model_validate_json(raw_input)
    all_findings = [*rollup_facts.merged_findings, *synth.boundary_findings]
    all_findings.sort(
        key=lambda f: (SEVERITY_RANK.get(f.severity, 99), f.component or "", f.file_path or "~", f.line or 0)
    )
    all_actions_plan = synth.unified_action_plan or rollup_facts.merged_action_plan
    all_strengths = list(dict.fromkeys([*rollup_facts.merged_strengths, *synth.strengths]))[:15]
    langs = sorted({c.language for c in rollup_facts.components})
    total_loc = sum(c.total_loc for c in rollup_facts.components)

    default_score = f"{DEFAULT_REPORT_OUTPUT_DIR}/{run.workflow_id}_score.json"
    score_rel = str(action.params.get("score_path") or run.outputs.score or default_score)
    summary_rel = default_summary_rel_path(score_rel)
    sarif_rel = default_sarif_rel_path(score_rel)
    rollup_facts_rel = f".pni/cache/{run.workflow_id}/rollup_facts.json"
    artifact_manifest = {
        "score_json": score_rel,
        "summary_json": summary_rel,
        "findings_sarif": sarif_rel,
        "plan_json": default_plan_rel_path(run.workflow_id),
        "rollup_facts_json": rollup_facts_rel,
    }
    exec_dag = build_rollup_execution_dag_summary(
        run,
        all_actions or [action],
        rollup_facts,
        project_root,
        artifact_manifest=artifact_manifest,
    )

    unified = ScoreResult(
        schema_version="2.0",
        project_name=project_root.name,
        workflow_id=run.workflow_id,
        workflow_run_id=run.run_id,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        language="+".join(langs) if langs else "multi",
        target_root=".",
        overall_score=rollup_facts.weighted_overall_score,
        grade=score_to_grade(rollup_facts.weighted_overall_score),
        category_scores=rollup_facts.weighted_category_scores,
        baseline_scores=rollup_facts.weighted_category_scores,
        category_rationales=CategoryRationales(
            architecture=synth.cross_component_architecture or "Rolled up across components.",
        ),
        metrics_snapshot={
            "total_loc": total_loc,
            "components_count": len(rollup_facts.components),
            "languages": langs,
            "companion_languages": sorted(rollup_facts.companion_ast_facts.keys()),
        },
        strengths=all_strengths,
        findings=all_findings,
        consolidated_findings=consolidate_findings_by_location(all_findings),
        action_plan=all_actions_plan,
        execution_dag=exec_dag,
        components=rollup_facts.components,
        report_hints=synth.report_hints,
        summary=synth.summary,
    )

    score_file = project_root / score_rel
    score_file.parent.mkdir(parents=True, exist_ok=True)
    canonical = unified.model_dump_json(indent=2)
    score_file.write_text(canonical + "\n", encoding="utf-8")

    summary_obj = build_score_summary(unified, score_file=score_rel, sarif_file=sarif_rel)
    write_score_summary(summary_obj, project_root / summary_rel)
    write_sarif_report(unified, project_root / sarif_rel)
    record_audit_history_from_score(project_root, run.workflow_id, unified)

    facts_file = project_root / rollup_facts_rel
    ensure_cache_parent(project_root, facts_file)
    facts_file.write_text(rollup_facts.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return canonical
