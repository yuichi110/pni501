"""Unit tests for metrics_kit.stats and metrics_kit.exceptions."""

from __future__ import annotations

import pytest

from metrics_kit.exceptions import EmptySampleError, InvalidParameterError
from metrics_kit.models import MetricPoint
from metrics_kit.stats import (
    compute_ewma,
    compute_mean,
    compute_percentile,
    compute_stddev,
    summarize_series,
)


def test_compute_mean_and_stddev() -> None:
    """Verify arithmetic mean and population standard deviation on deterministic samples."""
    values = [10.0, 20.0, 30.0, 40.0]
    assert compute_mean(values) == 25.0
    assert compute_stddev(values) == pytest.approx(11.18034, rel=1e-4)


def test_compute_percentile_and_ewma() -> None:
    """Verify percentile interpolation and EWMA smoothing."""
    samples = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert compute_percentile(samples, 50.0) == 30.0
    assert compute_percentile(samples, 95.0) == 48.0

    smoothed = compute_ewma([10.0, 20.0, 20.0], alpha=0.5)
    assert smoothed == [10.0, 15.0, 17.5]


def test_summarize_series_and_error_guards() -> None:
    """Verify summarize_series and typed exception guards on invalid inputs."""
    with pytest.raises(EmptySampleError):
        compute_mean([])

    with pytest.raises(InvalidParameterError):
        compute_percentile([1.0, 2.0], 120.0)

    with pytest.raises(InvalidParameterError):
        compute_ewma([1.0, 2.0], alpha=0.0)

    points = [MetricPoint(timestamp=1.0, value=12.0), MetricPoint(timestamp=2.0, value=28.0)]
    summary = summarize_series("db.query_ms", points)
    assert summary.count == 2
    assert summary.mean == 20.0
    assert summary.minimum == 12.0
    assert summary.maximum == 28.0
