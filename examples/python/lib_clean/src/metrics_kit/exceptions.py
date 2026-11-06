"""Typed domain exceptions for metrics_kit."""

from __future__ import annotations


class MetricsKitError(Exception):
    """Base exception raised by all metrics_kit operations."""


class EmptySampleError(MetricsKitError):
    """Raised when statistical aggregation receives an empty sample sequence."""


class InvalidParameterError(MetricsKitError):
    """Raised when smoothing alpha, percentile bounds, or z-score parameters are invalid."""
