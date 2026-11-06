"""Pure statistical aggregation and EWMA smoothing functions."""

from __future__ import annotations

import math
from collections.abc import Sequence

from metrics_kit.exceptions import EmptySampleError, InvalidParameterError
from metrics_kit.models import MetricPoint, SummaryStats


def _require_non_empty(values: Sequence[float]) -> None:
    """Validate that a numeric sequence contains at least one element.

    Args:
        values: Numeric observations to validate.
    """
    if not values:
        raise EmptySampleError("Sample sequence must contain at least one numeric observation.")


def compute_mean(values: Sequence[float]) -> float:
    """Compute the arithmetic mean of a non-empty numeric sequence.

    Args:
        values: Numeric observations to average.

    Returns:
        float: Arithmetic mean rounded to 6 decimal places.
    """
    _require_non_empty(values)
    return round(math.fsum(values) / len(values), 6)


def compute_stddev(values: Sequence[float]) -> float:
    """Compute population standard deviation for a non-empty numeric sequence.

    Args:
        values: Numeric observations to inspect.

    Returns:
        float: Population standard deviation rounded to 6 decimal places.
    """
    _require_non_empty(values)
    mean_val = math.fsum(values) / len(values)
    variance = math.fsum((item - mean_val) ** 2 for item in values) / len(values)
    return round(math.sqrt(variance), 6)


def compute_percentile(values: Sequence[float], percentile: float) -> float:
    """Compute linear-interpolated percentile over a numeric sequence.

    Args:
        values: Numeric observations to rank.
        percentile: Target percentile in the closed range [0.0, 100.0].

    Returns:
        float: Interpolated percentile value rounded to 6 decimal places.
    """
    _require_non_empty(values)
    if percentile < 0.0 or percentile > 100.0:
        raise InvalidParameterError(f"Percentile must be within [0.0, 100.0], got {percentile}.")

    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 6)

    rank = (percentile / 100.0) * (len(ordered) - 1)
    lower_idx = math.floor(rank)
    upper_idx = math.ceil(rank)
    weight = rank - lower_idx
    interpolated = ordered[lower_idx] * (1.0 - weight) + ordered[upper_idx] * weight
    return round(interpolated, 6)


def compute_ewma(values: Sequence[float], alpha: float = 0.3) -> list[float]:
    """Compute exponentially weighted moving average (EWMA) across ordered samples.

    Args:
        values: Ordered numeric observations.
        alpha: Smoothing factor in the half-open interval (0.0, 1.0].

    Returns:
        list[float]: Smoothed series matching the input length.
    """
    _require_non_empty(values)
    if alpha <= 0.0 or alpha > 1.0:
        raise InvalidParameterError(f"EWMA smoothing alpha must be within (0.0, 1.0], got {alpha}.")

    smoothed: list[float] = [round(values[0], 6)]
    current = values[0]
    for item in values[1:]:
        current = alpha * item + (1.0 - alpha) * current
        smoothed.append(round(current, 6))
    return smoothed


def summarize_series(metric_name: str, points: Sequence[MetricPoint]) -> SummaryStats:
    """Aggregate a sequence of MetricPoint items into an immutable SummaryStats record.

    Args:
        metric_name: Canonical metric identifier.
        points: Timestamped telemetry observations.

    Returns:
        SummaryStats: Descriptive summary statistics for the metric series.
    """
    if not metric_name.strip():
        raise InvalidParameterError("metric_name must not be empty.")
    raw_values = [pt.value for pt in points]
    _require_non_empty(raw_values)

    return SummaryStats(
        metric_name=metric_name,
        count=len(raw_values),
        mean=compute_mean(raw_values),
        minimum=round(min(raw_values), 6),
        maximum=round(max(raw_values), 6),
        p50=compute_percentile(raw_values, 50.0),
        p95=compute_percentile(raw_values, 95.0),
        stddev=compute_stddev(raw_values),
    )
