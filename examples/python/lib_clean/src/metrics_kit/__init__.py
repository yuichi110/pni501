"""Public package API for metrics_kit."""

from __future__ import annotations

from metrics_kit.exceptions import EmptySampleError, InvalidParameterError, MetricsKitError
from metrics_kit.formatting import format_markdown_summary, sanitize_prometheus_name, to_prometheus_lines
from metrics_kit.models import AlertVerdict, ComparisonOp, MetricPoint, SummaryStats, ThresholdRule
from metrics_kit.rules import detect_zscore_anomalies, evaluate_rule, evaluate_ruleset
from metrics_kit.stats import (
    compute_ewma,
    compute_mean,
    compute_percentile,
    compute_stddev,
    summarize_series,
)

__all__ = [
    "AlertVerdict",
    "ComparisonOp",
    "EmptySampleError",
    "InvalidParameterError",
    "MetricPoint",
    "MetricsKitError",
    "SummaryStats",
    "ThresholdRule",
    "compute_ewma",
    "compute_mean",
    "compute_percentile",
    "compute_stddev",
    "detect_zscore_anomalies",
    "evaluate_rule",
    "evaluate_ruleset",
    "format_markdown_summary",
    "sanitize_prometheus_name",
    "summarize_series",
    "to_prometheus_lines",
]
