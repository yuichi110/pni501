"""Pure string formatters for Markdown reports and Prometheus text exposition."""

from __future__ import annotations

import re
from collections.abc import Sequence

from metrics_kit.models import AlertVerdict, SummaryStats

_PROM_NAME_RE = re.compile(r"[^a-zA-Z0-9_:]")


def sanitize_prometheus_name(metric_name: str) -> str:
    """Convert dotted metric names into valid Prometheus metric identifiers.

    Args:
        metric_name: Raw metric identifier.

    Returns:
        str: Sanitized Prometheus-safe metric name.
    """
    cleaned = _PROM_NAME_RE.sub("_", metric_name.strip())
    return cleaned or "unnamed_metric"


def to_prometheus_lines(stats: SummaryStats) -> list[str]:
    """Render a SummaryStats snapshot into Prometheus gauge exposition lines.

    Args:
        stats: Aggregated metric statistics to format.

    Returns:
        list[str]: Prometheus exposition lines without trailing newlines.
    """
    base = sanitize_prometheus_name(stats.metric_name)
    return [
        f"{base}_count {stats.count}",
        f"{base}_mean {stats.mean}",
        f"{base}_min {stats.minimum}",
        f"{base}_max {stats.maximum}",
        f"{base}_p50 {stats.p50}",
        f"{base}_p95 {stats.p95}",
    ]


def format_markdown_summary(
    summaries: Sequence[SummaryStats],
    verdicts: Sequence[AlertVerdict] = (),
) -> str:
    """Format metric summaries and optional alert verdicts as a Markdown table.

    Args:
        summaries: Metric statistical summaries to tabulate.
        verdicts: Optional evaluated alert verdicts to append.

    Returns:
        str: Multi-line Markdown summary string.
    """
    lines = [
        "| Metric | Count | Mean | P50 | P95 | Max |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in summaries:
        lines.append(
            f"| `{item.metric_name}` | {item.count} | {item.mean:.2f} | "
            f"{item.p50:.2f} | {item.p95:.2f} | {item.maximum:.2f} |"
        )

    triggered = [v for v in verdicts if v.triggered]
    if triggered:
        lines.append("")
        lines.append("### Triggered Alerts")
        for alert in triggered:
            lines.append(f"- **[{alert.severity.upper()}]** `{alert.rule_id}`: {alert.reason}")

    return "\n".join(lines)
