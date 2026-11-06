# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic Python aggregator and canonical sorter for stateful workflow step outputs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from pydantic import BaseModel, Field

from pni._actions.ast_analyze.models import AstFacts
from pni._actions.base_model import (
    ActionItem,
    AppliedOptOut,
    AuditDimensionScore,
    ConsolidatedFinding,
    Finding,
    HealthGrade,
    InterpretationInput,
    ModuleHotspot,
    ModuleSummary,
    PrimitiveType,
    RuleCheckResult,
    RuleComplianceStatus,
    consolidate_findings_by_location,
)
from pni._actions.runtime_check.models import RuntimeFacts
from pni._actions.security_scan.models import SecurityFacts
from pni._cache import normalize_target_subpath
from pni._config import OptOutEntry, match_opt_out, matches_opt_out_scope
from pni._workflows.base_model import ActionRunRecord, WorkflowFactsBundle

SEVERITY_RANK: Final[dict[str, int]] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}
STATUS_RANK: Final[dict[str, int]] = {
    "fail": 0,
    "warn": 1,
    "pass": 2,
    "not_applicable": 3,
}
PRIORITY_RANK: Final[dict[str, int]] = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
}
SEVERITY_RISK_WEIGHT: Final[dict[str, float]] = {
    "critical": 0.45,
    "high": 0.28,
    "medium": 0.15,
    "low": 0.06,
    "info": 0.02,
}
SEVERITY_DEDUCTION: Final[dict[str, int]] = {
    "critical": 35,
    "high": 20,
    "medium": 10,
    "low": 3,
    "info": 1,
}
_BASE_HEALTHY_RISK: Final[float] = 0.06


class CompiledAuditDigest(BaseModel):
    """Deterministically aggregated, deduplicated, and sorted digest of all completed workflow actions."""

    audit_dimensions: list[AuditDimensionScore] = Field(default_factory=list)
    rule_compliance: list[RuleCheckResult] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    consolidated_findings: list[ConsolidatedFinding] = Field(default_factory=list)
    action_plan: list[ActionItem] = Field(default_factory=list)
    module_hotspots: list[ModuleHotspot] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    modules: list[ModuleSummary] = Field(default_factory=list)
    suggested_category_scores: dict[str, int] = Field(default_factory=dict)
    category_rationales: dict[str, str] = Field(default_factory=dict)
    opt_outs: list[AppliedOptOut] = Field(default_factory=list)


def score_to_grade(score: int) -> HealthGrade:
    """Convert a 0-100 integer score into a canonical PNI HealthGrade ('S'..'D')."""
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def _match_finding_opt_out(
    finding: Finding,
    opt_outs: Sequence[OptOutEntry],
) -> OptOutEntry | None:
    """Return matching OptOutEntry if finding matches by rule_id or embedded check ID."""
    if not opt_outs:
        return None
    direct = match_opt_out(opt_outs, (finding.rule_id,), finding.file_path)
    if direct is not None:
        return direct
    haystack = " ".join(
        part
        for part in (finding.rule_id, finding.symbol or "", finding.description, finding.evidence)
        if part
    ).lower()
    for entry in opt_outs:
        cid = entry.id.strip().lower()
        if cid and cid in haystack and matches_opt_out_scope(finding.file_path, entry.scope):
            return entry
    return None


def _filter_findings_by_opt_out(
    findings: list[Finding],
    opt_outs: Sequence[OptOutEntry],
    ai_counts: dict[str, int],
) -> list[Finding]:
    """Filter Finding list against [[opt_out]] entries and record AI-level match counts."""
    if not opt_outs or not findings:
        return findings
    kept: list[Finding] = []
    for item in findings:
        matched = _match_finding_opt_out(item, opt_outs)
        if matched is not None:
            ai_counts[matched.id] = ai_counts.get(matched.id, 0) + 1
        else:
            kept.append(item)
    return kept


def _filter_actions_by_opt_out(
    actions: list[ActionItem],
    opt_outs: Sequence[OptOutEntry],
) -> list[ActionItem]:
    """Filter ActionItem list when an action item targets a repo-wide opted-out check/rule."""
    if not opt_outs or not actions:
        return actions
    kept: list[ActionItem] = []
    for item in actions:
        text = f"{item.title} {item.action}".lower()
        waived = False
        for entry in opt_outs:
            if not entry.scope and entry.id.strip().lower() in text:
                waived = True
                break
        if not waived:
            kept.append(item)
    return kept


def _infer_rule_check(rule_id: str, source_action: str, findings: list[Finding]) -> RuleCheckResult:
    """Infer a fallback RuleCheckResult from step findings when not explicitly submitted."""
    matched = [f for f in findings if f.rule_id == rule_id]
    if not matched:
        return RuleCheckResult(
            rule_id=rule_id,
            status="pass",
            source_action=source_action,
            evidence="0 rule violations detected in step",
            summary=f"Compliant with {rule_id}.",
        )
    worst_sev = min(matched, key=lambda f: SEVERITY_RANK.get(f.severity, 99)).severity
    status: RuleComplianceStatus = "fail" if worst_sev in {"critical", "high"} else "warn"
    ev = matched[0].evidence or matched[0].description
    return RuleCheckResult(
        rule_id=rule_id,
        status=status,
        source_action=source_action,
        evidence=ev,
        summary=f"{len(matched)} finding(s) recorded (highest: {worst_sev.upper()}).",
    )


def normalize_step_rule_checks(
    act: ActionRunRecord,
    parsed: InterpretationInput,
    opt_outs: Sequence[OptOutEntry] = (),
) -> list[RuleCheckResult]:
    """Ensure every active rule on an ai_interpret action has a stamped RuleCheckResult."""
    src_id = act.source_action or act.action_id
    by_rule: dict[str, RuleCheckResult] = {}
    for chk in parsed.rule_checks:
        stamped = chk.model_copy(update={"source_action": chk.source_action or src_id})
        by_rule[stamped.rule_id] = stamped

    for rule_id in act.rules:
        if rule_id not in by_rule:
            by_rule[rule_id] = _infer_rule_check(rule_id, src_id, parsed.findings)

    if opt_outs:
        for rule_id, chk in list(by_rule.items()):
            repo_wide_match = next(
                (
                    entry
                    for entry in opt_outs
                    if not entry.scope and match_opt_out((entry,), rule_id, None) is not None
                ),
                None,
            )
            if repo_wide_match is not None:
                by_rule[rule_id] = chk.model_copy(
                    update={
                        "status": "not_applicable",
                        "evidence": f"Opted out via pni.toml ({repo_wide_match.id}): {repo_wide_match.reason}",
                        "summary": f"Waived by pni.toml ({repo_wide_match.id}).",
                    }
                )
    return list(by_rule.values())


def _compute_step_score(parsed: InterpretationInput) -> int:
    """Resolve the 0-100 score for an ai_interpret step from explicit step_score or fallbacks."""
    if parsed.step_score is not None:
        return max(0, min(100, parsed.step_score))
    if parsed.suggested_scores:
        vals = list(parsed.suggested_scores.values())
        return max(0, min(100, round(sum(vals) / len(vals))))
    deduction = sum(SEVERITY_DEDUCTION.get(f.severity, 2) for f in parsed.findings)
    return max(0, min(100, 100 - deduction))


def _build_audit_dimension(
    act: ActionRunRecord,
    parsed: InterpretationInput,
    checks: list[RuleCheckResult],
) -> tuple[int, AuditDimensionScore]:
    """Construct a single AuditDimensionScore paired with its workflow sequence number."""
    score = _compute_step_score(parsed)
    audit_id = act.source_action or act.action_id
    pass_cnt = sum(1 for c in checks if c.status == "pass")
    warn_cnt = sum(1 for c in checks if c.status == "warn")
    fail_cnt = sum(1 for c in checks if c.status == "fail")
    dim = AuditDimensionScore(
        action_id=act.action_id,
        audit_id=audit_id,
        title=act.name,
        score=score,
        grade=score_to_grade(score),
        rules_evaluated=[c.rule_id for c in checks] or list(act.rules),
        pass_count=pass_cnt,
        warn_count=warn_cnt,
        fail_count=fail_cnt,
        summary=parsed.summary,
    )
    return act.seq, dim


def merge_and_sort_rule_compliance(checks: list[RuleCheckResult]) -> list[RuleCheckResult]:
    """Deduplicate RuleCheckResult items by rule_id (strictest status wins) and sort FAIL -> PASS."""
    merged: dict[str, RuleCheckResult] = {}
    for chk in checks:
        existing = merged.get(chk.rule_id)
        if existing is None:
            merged[chk.rule_id] = chk
            continue
        if chk.status == "not_applicable" or existing.status == "not_applicable":
            na_winner = chk if chk.status == "not_applicable" else existing
            merged[chk.rule_id] = na_winner
            continue
        cur_rank = STATUS_RANK.get(existing.status, 99)
        new_rank = STATUS_RANK.get(chk.status, 99)
        winner = chk if new_rank < cur_rank else existing
        combined_ev = existing.evidence
        if chk.evidence and chk.evidence not in combined_ev:
            combined_ev = f"{combined_ev}; {chk.evidence}".strip("; ")
        merged[chk.rule_id] = winner.model_copy(update={"evidence": combined_ev})

    return sorted(
        merged.values(),
        key=lambda c: (STATUS_RANK.get(c.status, 99), c.rule_id),
    )


def deduplicate_and_sort_findings(findings: list[Finding]) -> list[Finding]:
    """Deduplicate findings and sort deterministically by CRITICAL -> HIGH -> MEDIUM -> LOW -> INFO."""
    seen: dict[tuple[str, str, int, str], Finding] = {}
    for item in findings:
        norm_key = (
            item.rule_id.strip(),
            (item.file_path or "").strip(),
            item.line or 0,
            (item.symbol or item.description[:48]).strip(),
        )
        existing = seen.get(norm_key)
        if existing is None or SEVERITY_RANK.get(item.severity, 99) < SEVERITY_RANK.get(existing.severity, 99):
            seen[norm_key] = item

    return sorted(
        seen.values(),
        key=lambda f: (
            SEVERITY_RANK.get(f.severity, 99),
            f.category,
            f.rule_id,
            f.file_path or "~",
            f.line or 0,
        ),
    )


def deduplicate_and_sort_actions(items: list[ActionItem]) -> list[ActionItem]:
    """Deduplicate ActionItem entries and sort deterministically by P0 -> P1 -> P2."""
    seen: dict[tuple[str, str], ActionItem] = {}
    for item in items:
        key = (item.priority, item.title.strip().lower())
        if key not in seen:
            seen[key] = item

    return sorted(
        seen.values(),
        key=lambda a: (PRIORITY_RANK.get(a.priority, 99), a.category, a.title),
    )


def _ast_structural_risk_bonus(file_path: str, ast_facts: AstFacts | None) -> float:
    """Compute extra risk density from deterministic AST complexity, global state, secrets, and sinks."""
    if ast_facts is None:
        return 0.0
    bonus = 0.0
    if any(loc.file == file_path for loc in ast_facts.complex_functions):
        bonus += 0.12
    if any(loc.file == file_path for loc in ast_facts.global_state_usages):
        bonus += 0.14
    if any(loc.file == file_path for loc in ast_facts.hardcoded_secrets):
        bonus += 0.25
    sink_count = sum(1 for sink in ast_facts.dangerous_sinks if sink.file == file_path)
    if sink_count > 0:
        bonus += min(0.30, 0.12 * sink_count)
    return bonus


def _build_low_coverage_bonus_map(
    runtime_facts: RuntimeFacts | None,
    target_root: str = ".",
) -> dict[str, float]:
    """Build file_path -> risk bonus map for modules with < 50% measured line coverage."""
    if runtime_facts is None or not runtime_facts.coverage.measured:
        return {}
    norm_root = normalize_target_subpath(target_root)
    bonuses: dict[str, float] = {}
    for item in runtime_facts.coverage.lowest_covered_modules:
        if item.total_statements < 5 or item.line_coverage_pct >= 50.0:
            continue
        bonus = 0.16 if item.line_coverage_pct == 0.0 else 0.10
        bonuses[item.file_path] = bonus
        if norm_root:
            bonuses[f"{norm_root}/{item.file_path}"] = bonus
    return bonuses


def _build_security_scan_bonus_map(
    security_facts: SecurityFacts | None,
    target_root: str = ".",
) -> dict[str, float]:
    """Build file_path -> risk bonus map from Trivy secret and misconfiguration findings."""
    if security_facts is None:
        return {}
    norm_root = normalize_target_subpath(target_root)
    bonuses: dict[str, float] = {}
    for raw_path in [s.file_path for s in security_facts.secrets] + [
        m.file_path for m in security_facts.misconfigurations
    ]:
        if not raw_path:
            continue
        bonuses[raw_path] = min(0.30, bonuses.get(raw_path, 0.0) + 0.15)
        if norm_root:
            prefixed = f"{norm_root}/{raw_path}"
            bonuses[prefixed] = min(0.30, bonuses.get(prefixed, 0.0) + 0.15)
    return bonuses


def compute_module_hotspots(
    findings: list[Finding],
    ast_facts: AstFacts | None,
    runtime_facts: RuntimeFacts | None = None,
    target_root: str = ".",
    security_facts: SecurityFacts | None = None,
) -> list[ModuleHotspot]:
    """Compute deterministic per-file risk scores (0.0-1.0) sorted highest-risk first."""
    loc_by_file: dict[str, int] = {}
    candidate_files: set[str] = set()
    if ast_facts is not None:
        for mod in ast_facts.module_inventory:
            loc_by_file[mod.file] = mod.loc
            candidate_files.add(mod.file)

    for finding in findings:
        if finding.file_path:
            candidate_files.add(finding.file_path)

    cov_bonuses = _build_low_coverage_bonus_map(runtime_facts, target_root)
    sec_bonuses = _build_security_scan_bonus_map(security_facts, target_root)
    candidate_files.update(k for k in sec_bonuses if "/" in k or k in {"Dockerfile", "Containerfile"})

    hotspots: list[ModuleHotspot] = []
    for fpath in candidate_files:
        matched = [f for f in findings if f.file_path == fpath]
        counts: dict[str, int] = {}
        rules: list[str] = []
        raw_weight = 0.0
        for f in matched:
            counts[f.severity] = counts.get(f.severity, 0) + 1
            raw_weight += SEVERITY_RISK_WEIGHT.get(f.severity, 0.02)
            if f.rule_id not in rules:
                rules.append(f.rule_id)

        extra_bonus = (
            _ast_structural_risk_bonus(fpath, ast_facts)
            + cov_bonuses.get(fpath, 0.0)
            + sec_bonuses.get(fpath, 0.0)
        )
        total = _BASE_HEALTHY_RISK if (raw_weight == 0.0 and extra_bonus == 0.0) else min(1.0, raw_weight + extra_bonus)
        hotspots.append(
            ModuleHotspot(
                file_path=fpath,
                loc=loc_by_file.get(fpath, 0),
                risk_score=round(total, 2),
                finding_counts=counts,
                top_rules=rules[:4],
            )
        )

    return sorted(hotspots, key=lambda h: (-h.risk_score, -h.loc, h.file_path))


def _deduplicate_strings(items: list[str]) -> list[str]:
    """Preserve insertion order while removing case-insensitive duplicate strings."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        clean = item.strip()
        if clean and clean.lower() not in seen:
            seen.add(clean.lower())
            result.append(clean)
    return result


def _collect_applied_opt_outs(
    opt_outs: Sequence[OptOutEntry],
    bundle: WorkflowFactsBundle,
    ai_counts: dict[str, int],
) -> list[AppliedOptOut]:
    """Assemble AppliedOptOut records combining deterministic fact counts and AI-level filter counts."""
    if not opt_outs:
        return []
    det_counts: dict[str, int] = {}
    for source_counts in (
        bundle.project_facts.opt_out_counts if bundle.project_facts is not None else {},
        bundle.ast_facts.opt_out_counts if bundle.ast_facts is not None else {},
        bundle.security_facts.opt_out_counts if bundle.security_facts is not None else {},
    ):
        for key, count in source_counts.items():
            det_counts[key] = det_counts.get(key, 0) + count

    applied: list[AppliedOptOut] = []
    for entry in opt_outs:
        count = det_counts.get(entry.id, 0) or ai_counts.get(entry.id, 0)
        applied.append(
            AppliedOptOut(
                id=entry.id,
                scope=list(entry.scope),
                reason=entry.reason,
                matched_count=count,
            )
        )
    return applied


def compile_workflow_digest(
    actions: list[ActionRunRecord],
    bundle: WorkflowFactsBundle,
    extra_findings: list[Finding] | None = None,
    extra_actions: list[ActionItem] | None = None,
    extra_strengths: list[str] | None = None,
    opt_outs: Sequence[OptOutEntry] = (),
) -> CompiledAuditDigest:
    """Compile and deterministically sort all step outputs from a stateful workflow run."""
    seq_dims: list[tuple[int, AuditDimensionScore]] = []
    all_checks: list[RuleCheckResult] = []
    raw_findings: list[Finding] = []
    raw_actions: list[ActionItem] = []
    raw_strengths: list[str] = []
    mod_map: dict[str, ModuleSummary] = {}
    cat_buckets: dict[str, list[int]] = {}
    cat_rationales: dict[str, str] = {}
    ai_opt_out_counts: dict[str, int] = {}

    if bundle.architecture_record and bundle.architecture_record.structure_map:
        for mod in bundle.architecture_record.structure_map.modules:
            mod_map[mod.path] = mod

    for act in actions:
        if act.primitive_type != PrimitiveType.AI_INTERPRET or act.agent_input_json is None:
            continue
        parsed = InterpretationInput.model_validate_json(act.agent_input_json)
        filtered_step_findings = _filter_findings_by_opt_out(parsed.findings, opt_outs, ai_opt_out_counts)
        parsed = parsed.model_copy(update={"findings": filtered_step_findings})
        step_checks = normalize_step_rule_checks(act, parsed, opt_outs)
        all_checks.extend(step_checks)
        seq_dims.append(_build_audit_dimension(act, parsed, step_checks))
        raw_findings.extend(filtered_step_findings)
        raw_actions.extend(_filter_actions_by_opt_out(parsed.action_items, opt_outs))
        raw_strengths.extend(parsed.strengths)
        for mod in parsed.modules:
            mod_map.setdefault(mod.path, mod)
        for cat, val in parsed.suggested_scores.items():
            cat_buckets.setdefault(cat, []).append(val)
        for cat, text in parsed.category_rationales.items():
            if text.strip():
                cat_rationales[cat] = text.strip()

    raw_findings.extend(_filter_findings_by_opt_out(list(extra_findings or []), opt_outs, ai_opt_out_counts))
    raw_actions.extend(_filter_actions_by_opt_out(list(extra_actions or []), opt_outs))
    raw_strengths.extend(extra_strengths or [])

    sorted_dims = [
        dim
        for _, dim in sorted(
            seq_dims,
            key=lambda pair: (pair[1].score, -pair[1].fail_count, -pair[1].warn_count, pair[0]),
        )
    ]
    sorted_findings = deduplicate_and_sort_findings(raw_findings)
    consolidated = consolidate_findings_by_location(sorted_findings)
    sorted_actions = deduplicate_and_sort_actions(raw_actions)
    sorted_rules = merge_and_sort_rule_compliance(all_checks)
    hotspots = compute_module_hotspots(
        sorted_findings,
        bundle.ast_facts,
        bundle.runtime_facts,
        bundle.targets.root,
        bundle.security_facts,
    )
    avg_cats = {cat: round(sum(vals) / len(vals)) for cat, vals in cat_buckets.items() if vals}
    applied_opt_outs = _collect_applied_opt_outs(opt_outs, bundle, ai_opt_out_counts)

    return CompiledAuditDigest(
        audit_dimensions=sorted_dims,
        rule_compliance=sorted_rules,
        findings=sorted_findings,
        consolidated_findings=consolidated,
        action_plan=sorted_actions,
        module_hotspots=hotspots,
        strengths=_deduplicate_strings(raw_strengths),
        modules=list(mod_map.values()),
        suggested_category_scores=avg_cats,
        category_rationales=cat_rationales,
        opt_outs=applied_opt_outs,
    )


def _render_opt_outs_digest_lines(opt_outs: list[AppliedOptOut]) -> list[str]:
    """Render active [[opt_out]] design waivers for the pre-score digest."""
    if not opt_outs:
        return []
    lines = [f"- **Active Design Waivers (`pni.toml [[opt_out]]`, {len(opt_outs)})**:"]
    for wv in opt_outs:
        scope_str = ", ".join(wv.scope) if wv.scope else "repo-wide"
        lines.append(f"  - `{wv.id}` (scope: `{scope_str}`, matched={wv.matched_count}) — {wv.reason}")
    return lines


def render_pre_score_digest_markdown(digest: CompiledAuditDigest) -> list[str]:
    """Render pre-sorted step outputs for the emit_score prompt so AI never drops prior evidence."""
    lines = ["\n## Pre-Sorted Programmatic Audit Digest (Auto-Merged into `ScoreResult`)"]
    if digest.suggested_category_scores:
        lines.append(f"- **Suggested Category Averages**: `{digest.suggested_category_scores}`")
    lines.extend(_render_opt_outs_digest_lines(digest.opt_outs))
    if digest.audit_dimensions:
        lines.append(f"- **Audit Step Scores (Weakest First, {len(digest.audit_dimensions)})**:")
        for dim in digest.audit_dimensions:
            lines.append(
                f"  - `{dim.audit_id}` (`{dim.action_id}`): **{dim.score}/100 ({dim.grade})** "
                f"[pass={dim.pass_count}, warn={dim.warn_count}, fail={dim.fail_count}] — {dim.summary}"
            )
    if digest.rule_compliance:
        lines.append(f"- **Sorted Rule Compliance Matrix (`FAIL -> WARN -> PASS`, {len(digest.rule_compliance)})**:")
        for rc in digest.rule_compliance:
            lines.append(f"  - `[{rc.status.upper()}]` `{rc.rule_id}`: {rc.evidence}")
    if digest.findings:
        lines.append(f"- **Pre-Sorted Findings (`CRITICAL -> INFO`, {len(digest.findings)})**:")
        for f in digest.findings:
            loc = f" (`{f.file_path}:{f.line}`)" if f.file_path else ""
            lines.append(f"  - `[{f.severity.upper()}]` `{f.rule_id}`{loc}: {f.description}")
    if digest.action_plan:
        lines.append(f"- **Pre-Sorted Action Items (`P0 -> P2`, {len(digest.action_plan)})**:")
        for item in digest.action_plan:
            lines.append(f"  - `[{item.priority}]` **{item.title}** (`{item.category}`): {item.action}")
    lines.append(
        "- *Note*: PNI automatically merges and deterministically re-sorts all prior `findings`, "
        "`rule_compliance`, `audit_dimensions`, `module_hotspots`, `action_plan`, `runtime_facts`, "
        "and `architecture_record` into `<target>_score.json` when you push `ScoreResult`."
    )
    return lines
