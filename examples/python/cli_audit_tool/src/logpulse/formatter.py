"""Output formatters for JSON and Rich terminal tables."""

from __future__ import annotations

import json
from typing import Any

from rich.table import Table

from logpulse.models import ScanReport


def report_to_dict(report: ScanReport) -> dict[str, Any]:
    return {
        "total_lines": report.total_lines,
        "skipped_lines": report.skipped_lines,
        "matched_events": report.matched_events,
        "groups": [
            {
                "signature": grp.signature,
                "level": grp.level.name,
                "occurrences": grp.occurrences,
                "service": grp.sample_service,
            }
            for grp in report.top_groups
        ],
    }


def render_json_report(report: ScanReport) -> str:
    return json.dumps(report_to_dict(report), indent=2)


def build_rich_table(report: ScanReport) -> Table:
    """Build a Rich Table summarizing top recurring error signatures.

    Args:
        report: Aggregated ScanReport to render.

    Returns:
        Table: Configured Rich Table ready for stdout rendering.
    """
    table = Table(title=f"Logpulse Summary ({report.matched_events} matched / {report.total_lines} lines)")
    table.add_column("Level", style="bold red")
    table.add_column("Count", justify="right")
    table.add_column("Service", style="cyan")
    table.add_column("Normalized Signature")
    for grp in report.top_groups:
        table.add_row(grp.level.name, str(grp.occurrences), grp.sample_service, grp.signature)
    return table
