"""Error signature normalization and frequency grouping engine."""

from __future__ import annotations

import re
from collections.abc import Sequence

from logpulse.models import LogEvent, ScanReport, SeverityLevel, SignatureGroup

_DIGITS_RE = re.compile(r"\b\d+\b")


def normalize_signature(message: str) -> str:
    """Replace volatile numeric IDs in a log message with '<N>' placeholders.

    Args:
        message: Raw log event message text.

    Returns:
        str: Normalized message template for deduplication.
    """
    return _DIGITS_RE.sub("<N>", message.strip())


def build_scan_report(
    events: Sequence[LogEvent],
    skipped_lines: int,
    min_level: SeverityLevel = SeverityLevel.ERROR,
    limit: int = 10,
) -> ScanReport:
    """Filter events by severity and group top recurring signatures.

    Args:
        events: Parsed LogEvent sequence.
        skipped_lines: Number of malformed JSONL lines skipped during parsing.
        min_level: Minimum severity threshold to include.
        limit: Maximum number of SignatureGroup rows to return.

    Returns:
        ScanReport: Aggregated scan summary.
    """
    filtered = [ev for ev in events if ev.level >= min_level]
    buckets: dict[tuple[str, SeverityLevel], tuple[int, str]] = {}
    for ev in filtered:
        key = (normalize_signature(ev.message), ev.level)
        prev_count, sample_svc = buckets.get(key, (0, ev.service))
        buckets[key] = (prev_count + 1, sample_svc)

    ranked = sorted(
        (
            SignatureGroup(signature=sig, level=lvl, occurrences=cnt, sample_service=svc)
            for (sig, lvl), (cnt, svc) in buckets.items()
        ),
        key=lambda item: (-item.occurrences, -int(item.level), item.signature),
    )
    return ScanReport(
        total_lines=len(events) + skipped_lines,
        skipped_lines=skipped_lines,
        matched_events=len(filtered),
        top_groups=tuple(ranked[: max(1, limit)]),
    )
