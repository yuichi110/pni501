"""Unit tests for metrics_kit.rules and metrics_kit.models."""

from __future__ import annotations

import pytest

from metrics_kit.exceptions import InvalidParameterError
from metrics_kit.models import ComparisonOp, MetricPoint, ThresholdRule
from metrics_kit.rules import detect_zscore_anomalies, evaluate_rule, evaluate_ruleset
from metrics_kit.stats import summarize_series


def test_evaluate_rule_and_ruleset() -> None:
    """Verify threshold rule evaluation across operators and rulesets."""
    pts = [MetricPoint(timestamp=float(i), value=float(v)) for i, v in enumerate([10, 20, 30, 100])]
    stats = summarize_series("http.latency_ms", pts)

    breached_rule = ThresholdRule(
        rule_id="slo-p95",
        metric_name="http.latency_ms",
        stat_field="p95",
        operator=ComparisonOp.GT,
        limit=80.0,
        severity="critical",
    )
    ok_rule = ThresholdRule(
        rule_id="mean-cap",
        metric_name="http.latency_ms",
        stat_field="mean",
        operator=ComparisonOp.LTE,
        limit=20.0,
    )

    verdict = evaluate_rule(stats, breached_rule)
    assert verdict.triggered is True
    assert verdict.severity == "critical"

    batch = evaluate_ruleset({"http.latency_ms": stats}, [breached_rule, ok_rule])
    assert [v.triggered for v in batch] == [True, False]


def test_detect_zscore_anomalies_and_mismatch_guard() -> None:
    """Verify z-score outlier detection and metric name mismatch validation."""
    pts = [MetricPoint(timestamp=float(i), value=10.0) for i in range(15)]
    pts.append(MetricPoint(timestamp=99.0, value=250.0))

    outliers = detect_zscore_anomalies(pts, z_threshold=2.5)
    assert len(outliers) == 1
    assert outliers[0].value == 250.0

    stats = summarize_series("cpu.load", pts)
    wrong_rule = ThresholdRule(rule_id="wrong", metric_name="mem.used", limit=50.0)
    with pytest.raises(InvalidParameterError):
        evaluate_rule(stats, wrong_rule)
