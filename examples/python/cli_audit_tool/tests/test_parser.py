"""Unit tests for logpulse.parser and logpulse.models."""

from __future__ import annotations

from logpulse.models import SeverityLevel
from logpulse.parser import parse_jsonl_lines, parse_severity


def test_parse_jsonl_lines_handles_valid_and_malformed_rows() -> None:
    """Verify valid JSONL lines parse cleanly while broken lines increment skipped count."""
    raw = [
        '{"ts": "2026-10-01T00:00:00Z", "level": "error", "service": "auth", "msg": "User 42 token expired"}',
        "not-json-at-all",
        '{"ts": "2026-10-01T00:00:01Z", "level": "INFO", "service": "api", "msg": "Health ok"}',
    ]
    events, skipped = parse_jsonl_lines(raw)
    assert skipped == 1
    assert len(events) == 2
    assert events[0].level == SeverityLevel.ERROR
    assert parse_severity("fatal") == SeverityLevel.CRITICAL
