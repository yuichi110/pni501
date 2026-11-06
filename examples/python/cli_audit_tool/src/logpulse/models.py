"""Typed data structures for parsed log entries and aggregated burst reports."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class SeverityLevel(IntEnum):
    """Ordered log severity levels supporting numeric comparison."""

    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    CRITICAL = 50


@dataclass(frozen=True)
class LogEvent:
    """Single normalized log event parsed from a JSONL line."""

    timestamp: str
    level: SeverityLevel
    service: str
    message: str


@dataclass(frozen=True)
class SignatureGroup:
    """Counted group of recurring log messages sharing a normalized signature."""

    signature: str
    level: SeverityLevel
    occurrences: int
    sample_service: str


@dataclass(frozen=True)
class ScanReport:
    """Complete result of scanning a JSONL log stream."""

    total_lines: int
    skipped_lines: int
    matched_events: int
    top_groups: tuple[SignatureGroup, ...]
