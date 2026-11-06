"""Unit tests for logpulse.analyzer and logpulse.formatter."""

from __future__ import annotations

import json

from logpulse.analyzer import build_scan_report, normalize_signature
from logpulse.formatter import render_json_report
from logpulse.models import LogEvent, SeverityLevel


def test_signature_grouping_and_json_render() -> None:
    """Verify numeric ID normalization and frequency ranking."""
    assert normalize_signature("Timeout on shard 12 after 5000 ms") == "Timeout on shard <N> after <N> ms"

    events = [
        LogEvent(timestamp="t1", level=SeverityLevel.ERROR, service="db", message="Deadlock on tx 101"),
        LogEvent(timestamp="t2", level=SeverityLevel.ERROR, service="db", message="Deadlock on tx 202"),
        LogEvent(timestamp="t3", level=SeverityLevel.INFO, service="web", message="200 OK"),
    ]
    report = build_scan_report(events, skipped_lines=0, min_level=SeverityLevel.ERROR)
    assert report.matched_events == 2
    assert len(report.top_groups) == 1
    assert report.top_groups[0].occurrences == 2

    rendered = json.loads(render_json_report(report))
    assert rendered["groups"][0]["signature"] == "Deadlock on tx <N>"
