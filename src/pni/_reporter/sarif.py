# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""SARIF 2.1.0 and lightweight ScoreSummary exporters for CI, IDEs, and multi-repo portals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pni._actions.base_model import (
    ConsolidatedFinding,
    ScoreResult,
    ScoreSummary,
    consolidate_findings_by_location,
)

SARIF_SCHEMA_URI: Final[str] = "https://json.schemastore.org/sarif-2.1.0.json"
_SARIF_LEVEL_BY_SEV: Final[dict[str, str]] = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "note",
}


def default_summary_rel_path(score_rel_path: str) -> str:
    """Derive `<target>_summary.json` path adjacent to `<target>_score.json`."""
    if score_rel_path.endswith("_score.json"):
        return score_rel_path.removesuffix("_score.json") + "_summary.json"
    return score_rel_path.removesuffix(".json") + "_summary.json"


def default_sarif_rel_path(score_rel_path: str) -> str:
    """Derive `<target>_findings.sarif` path adjacent to `<target>_score.json`."""
    if score_rel_path.endswith("_score.json"):
        return score_rel_path.removesuffix("_score.json") + "_findings.sarif"
    return score_rel_path.removesuffix(".json") + "_findings.sarif"


def _build_sarif_rules(items: list[ConsolidatedFinding]) -> list[dict[str, object]]:
    """Build deduplicated SARIF 2.1.0 tool.driver.rules entries from consolidated findings."""
    seen: dict[str, dict[str, object]] = {}
    for item in items:
        primary_rule = item.rule_ids[0] if item.rule_ids else "pni/general"
        if primary_rule in seen:
            continue
        seen[primary_rule] = {
            "id": primary_rule,
            "name": primary_rule.replace("/", "_").replace("-", "_"),
            "shortDescription": {"text": item.primary_description[:160]},
            "defaultConfiguration": {"level": _SARIF_LEVEL_BY_SEV.get(item.severity, "warning")},
        }
    return [seen[k] for k in sorted(seen)]


def _build_sarif_result(item: ConsolidatedFinding) -> dict[str, object]:
    """Convert one ConsolidatedFinding into a SARIF 2.1.0 result object."""
    rule_id = item.rule_ids[0] if item.rule_ids else "pni/general"
    msg = item.primary_description
    if item.merged_recommendation:
        msg = f"{msg} — Recommendation: {item.merged_recommendation}"
    res: dict[str, object] = {
        "ruleId": rule_id,
        "level": _SARIF_LEVEL_BY_SEV.get(item.severity, "warning"),
        "message": {"text": msg},
        "properties": {
            "severity": item.severity,
            "rule_ids": item.rule_ids,
            "categories": item.categories,
        },
    }
    if item.file_path:
        region: dict[str, object] = {"startLine": max(1, item.line or 1)}
        res["locations"] = [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": item.file_path.replace("\\", "/")},
                    "region": region,
                }
            }
        ]
    return res


def build_sarif_log(score: ScoreResult, *, tool_version: str = "2.0.0") -> dict[str, object]:
    """Build a canonical SARIF 2.1.0 dictionary from ScoreResult findings."""
    consolidated = score.consolidated_findings or consolidate_findings_by_location(score.findings)
    return {
        "$schema": SARIF_SCHEMA_URI,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "PNI501",
                        "version": tool_version,
                        "informationUri": "https://github.com/yuichi110/pni501",
                        "rules": _build_sarif_rules(consolidated),
                    }
                },
                "results": [_build_sarif_result(item) for item in consolidated],
                "properties": {
                    "project_name": score.project_name,
                    "workflow_id": score.workflow_id,
                    "workflow_run_id": score.workflow_run_id,
                    "language": score.language,
                    "overall_score": score.overall_score,
                    "grade": score.grade,
                },
            }
        ],
    }


def write_sarif_report(score: ScoreResult, dest_path: Path) -> Path:
    """Write SARIF 2.1.0 JSON report to dest_path."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_sarif_log(score)
    dest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest_path


def build_score_summary(
    score: ScoreResult,
    *,
    score_file: str = "",
    sarif_file: str = "",
) -> ScoreSummary:
    """Construct a lightweight ScoreSummary artifact (~2 KB) for dashboards and multi-repo catalogs."""
    sev_counts: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in score.findings:
        sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1
    passed_rules = sum(1 for r in score.rule_compliance if r.status == "pass")
    applicable_rules = sum(1 for r in score.rule_compliance if r.status != "not_applicable")
    raw_loc = score.metrics_snapshot.get("total_loc")
    total_loc = int(raw_loc) if isinstance(raw_loc, (int, float)) else 0
    raw_cov = score.metrics_snapshot.get("measured_line_coverage_pct")
    line_cov = float(raw_cov) if isinstance(raw_cov, (int, float)) else None

    return ScoreSummary(
        schema_version=score.schema_version,
        project_name=score.project_name,
        workflow_id=score.workflow_id,
        workflow_run_id=score.workflow_run_id,
        evaluated_at=score.evaluated_at,
        language=score.language,
        target_root=score.target_root,
        overall_score=score.overall_score,
        grade=score.grade,
        category_scores=score.category_scores,
        baseline_scores=score.baseline_scores,
        total_loc=total_loc,
        measured_line_coverage_pct=line_cov,
        passed_rules=passed_rules,
        applicable_rules=applicable_rules,
        finding_counts=sev_counts,
        components=score.components,
        score_file=score_file,
        sarif_file=sarif_file,
        summary=score.summary,
    )


def write_score_summary(summary: ScoreSummary, dest_path: Path) -> Path:
    """Write lightweight ScoreSummary JSON to dest_path."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(summary.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return dest_path
