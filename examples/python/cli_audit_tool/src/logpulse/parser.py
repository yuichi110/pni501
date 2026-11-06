"""Line-by-line JSONL log parser resilient to malformed lines."""

from __future__ import annotations

import json
from collections.abc import Iterable

from logpulse.models import LogEvent, SeverityLevel

_LEVEL_MAP: dict[str, SeverityLevel] = {
    "DEBUG": SeverityLevel.DEBUG,
    "INFO": SeverityLevel.INFO,
    "WARN": SeverityLevel.WARN,
    "WARNING": SeverityLevel.WARN,
    "ERROR": SeverityLevel.ERROR,
    "CRITICAL": SeverityLevel.CRITICAL,
    "FATAL": SeverityLevel.CRITICAL,
}


def parse_severity(raw_level: str) -> SeverityLevel:
    """Map a raw log level string to a normalized SeverityLevel enum.

    Args:
        raw_level: Case-insensitive log level label.

    Returns:
        SeverityLevel: Normalized severity level (defaults to INFO).
    """
    return _LEVEL_MAP.get(raw_level.strip().upper(), SeverityLevel.INFO)


def parse_jsonl_lines(lines: Iterable[str]) -> tuple[list[LogEvent], int]:
    """Parse an iterable of JSONL strings into LogEvent objects and count malformed lines.

    Args:
        lines: Raw text lines from a JSONL file or stream.

    Returns:
        tuple[list[LogEvent], int]: Parsed events and count of skipped malformed lines.
    """
    events: list[LogEvent] = []
    skipped = 0
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(payload, dict):
            skipped += 1
            continue
        events.append(
            LogEvent(
                timestamp=str(payload.get("ts") or payload.get("timestamp") or ""),
                level=parse_severity(str(payload.get("level", "INFO"))),
                service=str(payload.get("service", "unknown")),
                message=str(payload.get("msg") or payload.get("message") or ""),
            )
        )
    return events, skipped
