"""Unit tests for metrics_kit.formatting."""

from __future__ import annotations

from metrics_kit.formatting import format_markdown_summary, sanitize_prometheus_name, to_prometheus_lines
from metrics_kit.models import ComparisonOp, MetricPoint, ThresholdRule
from metrics_kit.rules import evaluate_rule
from metrics_kit.stats import summarize_series


def test_prometheus_and_markdown_formatting() -> None:
    """Verify Prometheus metric sanitization and Markdown report rendering."""
    assert sanitize_prometheus_name("api.v2/latency-ms") == "api_v2_latency_ms"

    stats = summarize_series(
        "api.latency_ms",
        [MetricPoint(timestamp=1.0, value=25.0), MetricPoint(timestamp=2.0, value=75.0)],
    )
    prom_lines = to_prometheus_lines(stats)
    assert "api_latency_ms_count 2" in prom_lines
    assert "api_latency_ms_mean 50.0" in prom_lines

    rule = ThresholdRule(
        rule_id="lat-high",
        metric_name="api.latency_ms",
        stat_field="maximum",
        operator=ComparisonOp.GTE,
        limit=70.0,
        severity="warning",
    )
    verdict = evaluate_rule(stats, rule)
    md = format_markdown_summary([stats], [verdict])
    assert "| `api.latency_ms` |" in md
    assert "### Triggered Alerts" in md
    assert "`lat-high`" in md
