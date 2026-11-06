# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic extractor for 'Spec vs. Bug' stakeholder decision candidates."""

from __future__ import annotations

import re
from typing import Final

from pni._actions.ast_analyze.models import AstFacts, SecuritySinkLocation
from pni._actions.migration_analyze.models import SpecVsBugCandidate

_RETRY_MAGIC_RE: Final[re.Pattern[str]] = re.compile(r"\bsendCharge\([^,]+,\s*(\d+[Ll]?)\s*\)")
_DIAG_OUTPUT_RE: Final[re.Pattern[str]] = re.compile(r'\.put\(\s*"(controllerPing|debug\w*|trace\w*)"')


def _candidate_from_sink(idx: int, sink: SecuritySinkLocation) -> SpecVsBugCandidate | None:
    """Convert auth/crypto/deserialization sinks with migration compatibility implications into candidates."""
    if sink.category == "loose_comparison_or_auth":
        return SpecVsBugCandidate(
            candidate_id=f"DEC-{idx:02d}",
            file=sink.file,
            line=sink.line,
            symbol=sink.symbol or "",
            observed_behavior=f"Loose equality / auth comparison (`{sink.cwe_id}`): {sink.detail}",
            risk_if_changed_silently=(
                "Switching to strict comparison or new password hashing without dual-read migration "
                "can lock out existing users or alter edge-case request matching."
            ),
            options=[
                "Option A (Recommended): Preserve legacy hash verification via dual-verify rehash-on-login in Phase 3.",
                "Option B: Force password reset / immediate strict check at cutover.",
            ],
        )
    if sink.category == "weak_cryptography":
        return SpecVsBugCandidate(
            candidate_id=f"DEC-{idx:02d}",
            file=sink.file,
            line=sink.line,
            symbol=sink.symbol or "",
            observed_behavior=f"Legacy weak digest (`{sink.cwe_id}`): {sink.detail}",
            risk_if_changed_silently=(
                "Existing stored digests in the database will fail authentication if replaced with bcrypt/Argon2id "
                "without an online upgrade wrapper."
            ),
            options=[
                "Option A (Recommended): Wrap legacy digest in bcrypt(`md5(pw)`) or rehash on next login.",
                "Option B: Invalidate legacy credentials and require credential rotation.",
            ],
        )
    if sink.category == "unsafe_deserialization":
        return SpecVsBugCandidate(
            candidate_id=f"DEC-{idx:02d}",
            file=sink.file,
            line=sink.line,
            symbol=sink.symbol or "",
            observed_behavior=f"Untrusted payload/cookie deserialization (`{sink.cwe_id}`): {sink.detail}",
            risk_if_changed_silently=(
                "In-flight browser cookies or cached payloads serialized in legacy format will fail to parse "
                "during rolling/Strangler Fig cutover."
            ),
            options=[
                "Option A (Recommended): Replace with signed JSON / server-side Redis session and gracefully reset "
                "unparseable legacy cookies to empty cart.",
                "Option B: Hard-cut cookie format during maintenance window.",
            ],
        )
    return None


def _scan_source_quirks(source_files: dict[str, str], start_idx: int) -> list[SpecVsBugCandidate]:
    """Scan source files for hardcoded fallback charges and debug/internal response keys."""
    extra: list[SpecVsBugCandidate] = []
    idx = start_idx
    for rel_path in sorted(source_files):
        for line_no, line in enumerate(source_files[rel_path].splitlines(), start=1):
            m_charge = _RETRY_MAGIC_RE.search(line)
            if m_charge is not None:
                amt = m_charge.group(1)
                extra.append(
                    SpecVsBugCandidate(
                        candidate_id=f"DEC-{idx:02d}",
                        file=rel_path,
                        line=line_no,
                        symbol="sendCharge",
                        observed_behavior=(
                            f"Non-positive invoice retry path charges fixed literal `{amt}` instead of invoice amount."
                        ),
                        risk_if_changed_silently=(
                            "Downstream settlement or minimum-authorization verification flows may rely on this "
                            "fixed authorization probe amount."
                        ),
                        options=[
                            "Option A (Recommended): Preserve in Phase 0-2 characterization tests; confirm with "
                            "Billing Product Owner before changing in Phase 3.",
                            "Option B: Treat as intentional authorization probe and extract named domain policy.",
                        ],
                    )
                )
                idx += 1
            m_diag = _DIAG_OUTPUT_RE.search(line)
            if m_diag is not None:
                key = m_diag.group(1)
                extra.append(
                    SpecVsBugCandidate(
                        candidate_id=f"DEC-{idx:02d}",
                        file=rel_path,
                        line=line_no,
                        symbol=key,
                        observed_behavior=f"Response payload conditionally includes internal diagnostic key `{key}`.",
                        risk_if_changed_silently=(
                            "Removing internal diagnostic field when severing controller back-reference may break "
                            "strict schema consumers if they read this key."
                        ),
                        options=[
                            "Option A (Recommended): Populate `" + key + "` from request metadata passed into UseCase "
                            "DTO if strict compatibility is required, or deprecate after client audit.",
                            "Option B: Drop `" + key + "` once external consumers confirm unused.",
                        ],
                    )
                )
                idx += 1
    return extra


def extract_spec_vs_bug_candidates(
    ast_facts: AstFacts | None,
    source_files: dict[str, str],
) -> list[SpecVsBugCandidate]:
    """Extract deterministic 'Spec vs. Bug' candidates requiring stakeholder sign-off.

    Args:
        ast_facts: Deterministic AST facts (bug_risk_idioms and dangerous_sinks).
        source_files: Workspace-relative source file contents.

    Returns:
        list[SpecVsBugCandidate]: Ordered stakeholder decision items.
    """
    candidates: list[SpecVsBugCandidate] = []
    seen_locs: set[tuple[str, int]] = set()
    idx = 1

    if ast_facts is not None:
        for loc in ast_facts.bug_risk_idioms:
            if (loc.file, loc.line) in seen_locs:
                continue
            seen_locs.add((loc.file, loc.line))
            candidates.append(
                SpecVsBugCandidate(
                    candidate_id=f"DEC-{idx:02d}",
                    file=loc.file,
                    line=loc.line,
                    symbol=loc.symbol,
                    observed_behavior=loc.detail,
                    risk_if_changed_silently=(
                        "Fixing bug-risk idiom (e.g. Java `==` string reference comparison, swallowed exception, "
                        "or `extract($_POST)`) alters runtime branch/error behavior(Hyrum's Law)."
                    ),
                    options=[
                        "Option A (Recommended): Lock current behavior in Phase 0 characterization test, obtain "
                        "Product Owner sign-off, and apply fix in dedicated Phase 3 PR.",
                        "Option B: Preserve exact legacy behavior behind feature flag during initial cutover.",
                    ],
                )
            )
            idx += 1

        for sink in ast_facts.dangerous_sinks:
            if (sink.file, sink.line) in seen_locs:
                continue
            cand = _candidate_from_sink(idx, sink)
            if cand is not None:
                seen_locs.add((sink.file, sink.line))
                candidates.append(cand)
                idx += 1

    for extra in _scan_source_quirks(source_files, idx):
        if (extra.file, extra.line) not in seen_locs:
            seen_locs.add((extra.file, extra.line))
            candidates.append(extra)

    for new_idx, item in enumerate(candidates, start=1):
        item.candidate_id = f"DEC-{new_idx:02d}"
    return candidates
