# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic Pre-Findings, Pre-RuleChecks, and 7-axis Baseline Score anchoring engine."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Final

from pydantic import BaseModel, Field

from pni._actions.ast_analyze.models import AstFacts
from pni._actions.base_model import (
    CategoryScores,
    Finding,
    FindingAdjustment,
    RuleCheckResult,
    SeverityLevel,
)
from pni._actions.project_inspect import ProjectFacts
from pni._actions.runtime_check.models import RuntimeFacts
from pni._actions.security_scan.models import SecurityFacts
from pni._workflows.base_model import WorkflowFactsBundle

MAX_BASELINE_AI_DELTA: Final[int] = 10


class BaselineEvaluation(BaseModel):
    """Deterministic pre-findings, rule verdicts, and objective 7-axis baseline scores."""

    baseline_scores: CategoryScores
    overall_baseline: int = Field(ge=0, le=100)
    pre_findings: list[Finding] = Field(default_factory=list)
    pre_rule_checks: list[RuleCheckResult] = Field(default_factory=list)
    rationale_notes: dict[str, str] = Field(default_factory=dict)


def _det_id(rule_id: str, file_path: str | None, line: int | None, key: str) -> str:
    """Compute a stable deterministic finding_id ('det-xxxxxxxx')."""
    raw = f"{rule_id}|{file_path or ''}|{line or 0}|{key}"
    return f"det-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:8]}"


def _clamp(val: float) -> int:
    """Clamp a numeric score into [0, 100] integer range."""
    return max(0, min(100, round(val)))


def _collect_project_findings(
    pf: ProjectFacts,
    findings: list[Finding],
    checks: list[RuleCheckResult],
    *,
    component_scope: bool,
) -> tuple[int, int, int]:
    """Derive deterministic dependency, documentation, and governance findings/deductions."""
    dep_ded = 0
    doc_ded = 0
    sec_ded = 0

    if not pf.lockfiles_found and pf.dependencies:
        dep_ded += 15
        findings.append(
            Finding(
                finding_id=_det_id("common/supply_chain", None, None, "missing_lockfile"),
                source="deterministic",
                severity="medium",
                category="dependencies",
                rule_id="common/supply_chain",
                evidence=f"manifests={pf.manifest_files}, lockfiles=[]",
                description="No dependency lockfile found despite declared dependencies.",
                recommendation="Commit a deterministic lockfile (e.g. uv.lock, package-lock.json, Cargo.lock).",
            )
        )
    if pf.unpinned_dependencies:
        dep_ded += min(20, len(pf.unpinned_dependencies) * 3)
        findings.append(
            Finding(
                finding_id=_det_id("common/supply_chain", None, None, "unpinned_deps"),
                source="deterministic",
                severity="low",
                category="dependencies",
                rule_id="common/supply_chain",
                evidence=f"unpinned={pf.unpinned_dependencies[:10]}",
                description=f"{len(pf.unpinned_dependencies)} dependency specifiers lack upper/exact bounds.",
                recommendation="Pin dependency versions or enforce lockfile-based reproducible builds.",
            )
        )

    if not component_scope:
        if not pf.has_license:
            doc_ded += 8
            checks.append(
                RuleCheckResult(
                    rule_id="common/supply_chain",
                    status="warn",
                    source_action="deterministic_baseline",
                    evidence="LICENSE file missing at repository root",
                    summary="Repository lacks a root LICENSE file.",
                )
            )
        if not pf.has_readme or pf.readme_line_count < 10:
            doc_ded += 15
            findings.append(
                Finding(
                    finding_id=_det_id("common/documentation", None, None, "missing_readme"),
                    source="deterministic",
                    severity="medium",
                    category="documentation",
                    rule_id="common/documentation",
                    evidence=f"has_readme={pf.has_readme}, lines={pf.readme_line_count}",
                    description="README documentation is missing or minimal (< 10 lines).",
                    recommendation="Document architecture overview, setup instructions, and usage in README.md.",
                )
            )
        for sec_file in pf.committed_secret_files:
            sec_ded += 25
            findings.append(
                Finding(
                    finding_id=_det_id("common/security", sec_file, 1, "committed_secret_file"),
                    source="deterministic",
                    severity="critical",
                    category="security",
                    rule_id="common/security",
                    file_path=sec_file,
                    line=1,
                    evidence=f"Committed sensitive file: {sec_file}",
                    description=f"Sensitive credential or key file '{sec_file}' is tracked in repository.",
                    recommendation="Remove the file from Git history, rotate credentials, and ignore via .gitignore.",
                )
            )
    return dep_ded, doc_ded, sec_ded


def _collect_ast_findings(
    af: AstFacts,
    findings: list[Finding],
) -> dict[str, int]:
    """Derive deterministic architecture, quality, typing, testing, security, and docs deductions."""
    ded = {"architecture": 0, "code_quality": 0, "typing": 0, "testing": 0, "security": 0, "documentation": 0}

    if af.circular_dependencies:
        ded["architecture"] += min(30, len(af.circular_dependencies) * 10)
        for cyc in af.circular_dependencies[:5]:
            chain = " -> ".join(cyc)
            findings.append(
                Finding(
                    finding_id=_det_id("common/architecture", None, None, chain),
                    source="deterministic",
                    severity="high",
                    category="architecture",
                    rule_id="common/architecture",
                    evidence=f"Circular import cycle: {chain}",
                    description=f"Runtime circular dependency detected: {chain}.",
                    recommendation="Break the cycle by extracting shared interfaces/models into a lower layer.",
                )
            )

    for loc in af.complex_functions:
        ded["code_quality"] += 4
        findings.append(
            Finding(
                finding_id=_det_id("common/maintainability", loc.file, loc.line, f"complex:{loc.symbol}"),
                source="deterministic",
                severity="medium",
                category="code_quality",
                rule_id="common/maintainability",
                file_path=loc.file,
                line=loc.line,
                symbol=loc.symbol,
                evidence=loc.detail,
                description=f"High cyclomatic complexity or length in `{loc.symbol}` ({loc.detail}).",
                recommendation="Decompose into cohesive helper functions with clear single responsibilities.",
            )
        )

    for loc in af.hardcoded_secrets:
        ded["security"] += 20
        findings.append(
            Finding(
                finding_id=_det_id("common/security", loc.file, loc.line, f"secret:{loc.symbol}"),
                source="deterministic",
                severity="critical",
                category="security",
                rule_id="common/security",
                file_path=loc.file,
                line=loc.line,
                symbol=loc.symbol,
                evidence=loc.detail,
                description=f"Potential hardcoded secret detected in `{loc.file}:{loc.line}`.",
                recommendation="Move secrets to environment variables or a secret manager and rotate exposed keys.",
            )
        )

    for sink in af.dangerous_sinks:
        sev: SeverityLevel = sink.severity if sink.severity in {"critical", "high", "medium", "low", "info"} else "high"
        ded["security"] += 15 if sev in {"critical", "high"} else 6
        findings.append(
            Finding(
                finding_id=_det_id(sink.cwe_id or "common/security", sink.file, sink.line, sink.category),
                source="deterministic",
                severity=sev,
                category="security",
                rule_id=sink.cwe_id or "common/security",
                file_path=sink.file,
                line=sink.line,
                symbol=sink.symbol or None,
                evidence=sink.detail,
                description=f"Dangerous sink ({sink.cwe_id} {sink.category}): {sink.detail}",
                recommendation="Replace with parameterized/safe APIs or enforce strict allow-list validation.",
            )
        )

    if af.type_safety_coverage_pct is not None and af.type_safety_coverage_pct < 90.0:
        ded["typing"] += _clamp((90.0 - af.type_safety_coverage_pct) * 0.6)
    ded["typing"] += min(20, len(af.weak_type_usages) * 2 + len(af.unscoped_type_ignores) * 4)

    if af.docstring_coverage_pct is not None and af.docstring_coverage_pct < 80.0:
        ded["documentation"] += _clamp((80.0 - af.docstring_coverage_pct) * 0.5)

    if af.test_functions_count == 0:
        ded["testing"] += 35
    elif af.assertion_free_tests:
        ded["testing"] += min(20, len(af.assertion_free_tests) * 4)
    return {k: min(60, v) for k, v in ded.items()}


def _collect_runtime_and_security_findings(
    rf: RuntimeFacts | None,
    sf: SecurityFacts | None,
    findings: list[Finding],
    checks: list[RuleCheckResult],
) -> tuple[int, int]:
    """Derive deterministic runtime testing and Trivy supply-chain security findings/deductions."""
    test_ded = 0
    sec_ded = 0

    if rf is not None and rf.status not in {"skipped"}:
        if rf.harness_build.status != "passed":
            test_ded += 35
            checks.append(
                RuleCheckResult(
                    rule_id="common/runtime_verification",
                    status="fail",
                    source_action="deterministic_baseline",
                    evidence=f"harness_build={rf.harness_build.status}",
                    summary="Containerized harness build failed.",
                )
            )
        elif rf.test_execution.status != "passed":
            test_ded += 30
            checks.append(
                RuleCheckResult(
                    rule_id="common/runtime_verification",
                    status="fail",
                    source_action="deterministic_baseline",
                    evidence=(
                        f"tests={rf.test_execution.passed_tests}/{rf.test_execution.total_tests}, "
                        f"failed={rf.test_execution.failed_tests}"
                    ),
                    summary="Offline containerized unit test suite failed.",
                )
            )
        else:
            checks.append(
                RuleCheckResult(
                    rule_id="common/runtime_verification",
                    status="pass",
                    source_action="deterministic_baseline",
                    evidence=(
                        f"build=passed, tests={rf.test_execution.passed_tests}/{rf.test_execution.total_tests}, "
                        f"smoke={rf.smoke_check.status}"
                    ),
                    summary="Container build, offline tests, and smoke check passed.",
                )
            )
        if rf.coverage.measured and rf.coverage.line_coverage_pct is not None and rf.coverage.line_coverage_pct < 70.0:
            test_ded += min(25, _clamp((70.0 - rf.coverage.line_coverage_pct) * 0.4))

    if sf is not None and sf.status not in {"skipped"}:
        cc = sf.core_app_vuln_counts
        sec_ded += min(50, cc.critical * 20 + cc.high * 10 + cc.medium * 3)
        for v in (sf.app_vulnerabilities or sf.vulnerabilities)[:25]:
            if v.scope != "runtime_core":
                continue
            sev: SeverityLevel = (
                "critical"
                if v.severity == "CRITICAL"
                else "high"
                if v.severity == "HIGH"
                else "medium"
                if v.severity == "MEDIUM"
                else "low"
            )
            fix_hint = (
                f"Upgrade `{v.pkg_name}` to `{v.fixed_version}`." if v.fixed_version else "Apply vendor mitigation."
            )
            findings.append(
                Finding(
                    finding_id=_det_id(v.vuln_id, v.target, None, v.pkg_name),
                    source="deterministic",
                    severity=sev,
                    category="security",
                    rule_id=v.vuln_id,
                    evidence=f"{v.pkg_name}@{v.installed_version} ({v.pkg_type})",
                    description=f"Core runtime dependency vulnerability {v.vuln_id}: {v.title[:160]}",
                    recommendation=fix_hint,
                )
            )
    return min(60, test_ded), min(60, sec_ded)


def compute_baseline_evaluation(
    bundle: WorkflowFactsBundle,
    *,
    component_scope: bool = False,
) -> BaselineEvaluation:
    """Compute deterministic Pre-Findings, Pre-RuleChecks, and anchored 7-axis Baseline Scores."""
    findings: list[Finding] = []
    checks: list[RuleCheckResult] = []
    deds: dict[str, int] = {
        "architecture": 0,
        "code_quality": 0,
        "typing": 0,
        "testing": 0,
        "dependencies": 0,
        "security": 0,
        "documentation": 0,
    }

    if bundle.project_facts is not None:
        dep_d, doc_d, sec_d = _collect_project_findings(
            bundle.project_facts,
            findings,
            checks,
            component_scope=component_scope,
        )
        deds["dependencies"] += dep_d
        deds["documentation"] += doc_d
        deds["security"] += sec_d

    if bundle.ast_facts is not None:
        ast_deds = _collect_ast_findings(bundle.ast_facts, findings)
        for k, v in ast_deds.items():
            deds[k] += v

    rt_d, sec_rt_d = _collect_runtime_and_security_findings(
        bundle.runtime_facts,
        bundle.security_facts,
        findings,
        checks,
    )
    deds["testing"] += rt_d
    deds["security"] += sec_rt_d

    scores = CategoryScores(
        architecture=_clamp(100 - deds["architecture"]),
        code_quality=_clamp(100 - deds["code_quality"]),
        typing=_clamp(100 - deds["typing"]),
        testing=_clamp(100 - deds["testing"]),
        dependencies=_clamp(100 - deds["dependencies"]),
        security=_clamp(100 - deds["security"]),
        documentation=_clamp(100 - deds["documentation"]),
    )
    overall = _clamp(
        (
            scores.architecture
            + scores.code_quality
            + scores.typing
            + scores.testing
            + scores.dependencies
            + scores.security
            + scores.documentation
        )
        / 7.0
    )
    notes = {k: f"baseline={getattr(scores, k)} (deduction=-{deds[k]})" for k in deds}
    return BaselineEvaluation(
        baseline_scores=scores,
        overall_baseline=overall,
        pre_findings=findings,
        pre_rule_checks=checks,
        rationale_notes=notes,
    )


def apply_finding_adjustments(
    findings: list[Finding],
    adjustments: Sequence[FindingAdjustment],
) -> list[Finding]:
    """Apply AI false-positive waivers or severity reclassifications to deterministic findings."""
    if not adjustments:
        return findings
    adj_map = {a.finding_id.strip(): a for a in adjustments if a.finding_id.strip()}
    out: list[Finding] = []
    for item in findings:
        adj = adj_map.get(item.finding_id)
        if adj is None:
            out.append(item)
            continue
        if adj.action == "waive":
            continue
        if adj.action == "reclassify" and adj.new_severity is not None:
            out.append(
                item.model_copy(
                    update={
                        "severity": adj.new_severity,
                        "evidence": f"{item.evidence} [AI reclassified: {adj.reason}]".strip(),
                    }
                )
            )
            continue
        out.append(item)
    return out
