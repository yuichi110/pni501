"""Declarative threshold policy evaluation and z-score anomaly detection."""

from __future__ import annotations

from collections.abc import Sequence

from metrics_kit.exceptions import InvalidParameterError
from metrics_kit.models import AlertVerdict, ComparisonOp, MetricPoint, SummaryStats, ThresholdRule
from metrics_kit.stats import compute_mean, compute_stddev


def _compare_value(observed: float, operator: ComparisonOp, limit: float) -> bool:
    """Evaluate a relational comparison between observed metric value and rule limit.

    Args:
        observed: Measured statistic value.
        operator: Relational comparison operator.
        limit: Configured threshold boundary.

    Returns:
        bool: True when the threshold condition is breached.
    """
    if operator == ComparisonOp.GT:
        return observed > limit
    if operator == ComparisonOp.GTE:
        return observed >= limit
    if operator == ComparisonOp.LT:
        return observed < limit
    return observed <= limit


def evaluate_rule(stats: SummaryStats, rule: ThresholdRule) -> AlertVerdict:
    """Evaluate a single ThresholdRule against a computed SummaryStats snapshot.

    Args:
        stats: Aggregated metric statistics.
        rule: Threshold rule definition to evaluate.

    Returns:
        AlertVerdict: Structured verdict describing whether the rule triggered.
    """
    if stats.metric_name != rule.metric_name:
        raise InvalidParameterError(
            f"Metric mismatch: stats is '{stats.metric_name}' but rule expects '{rule.metric_name}'."
        )
    observed = float(getattr(stats, rule.stat_field))
    triggered = _compare_value(observed, rule.operator, rule.limit)
    state_label = "BREACHED" if triggered else "OK"
    reason = f"{rule.metric_name}.{rule.stat_field}={observed} ({rule.operator.value} {rule.limit}) -> {state_label}"

    return AlertVerdict(
        rule_id=rule.rule_id,
        metric_name=rule.metric_name,
        triggered=triggered,
        observed_value=observed,
        limit=rule.limit,
        severity=rule.severity,
        reason=reason,
    )


def evaluate_ruleset(stats_by_metric: dict[str, SummaryStats], rules: Sequence[ThresholdRule]) -> list[AlertVerdict]:
    """Evaluate a batch of threshold rules against a dictionary of metric summaries.

    Args:
        stats_by_metric: Mapping of metric_name to SummaryStats.
        rules: Sequence of threshold rules to evaluate in order.

    Returns:
        list[AlertVerdict]: Ordered list of verdicts for rules whose metrics are present.
    """
    verdicts: list[AlertVerdict] = []
    for rule in rules:
        target_stats = stats_by_metric.get(rule.metric_name)
        if target_stats is not None:
            verdicts.append(evaluate_rule(target_stats, rule))
    return verdicts


def detect_zscore_anomalies(points: Sequence[MetricPoint], z_threshold: float = 2.5) -> list[MetricPoint]:
    """Return telemetry points whose absolute z-score exceeds z_threshold.

    Args:
        points: Sequence of timestamped metric observations.
        z_threshold: Positive z-score cutoff for anomaly classification.

    Returns:
        list[MetricPoint]: Subset of points exceeding the z-score cutoff.
    """
    if z_threshold <= 0.0:
        raise InvalidParameterError(f"z_threshold must be positive, got {z_threshold}.")
    if len(points) < 2:
        return []

    values = [pt.value for pt in points]
    mean_val = compute_mean(values)
    stddev_val = compute_stddev(values)
    if stddev_val == 0.0:
        return []

    return [pt for pt in points if abs(pt.value - mean_val) / stddev_val > z_threshold]
