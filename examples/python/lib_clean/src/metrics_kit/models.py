"""Immutable Pydantic v2 data models for telemetry samples, summaries, and threshold rules."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ComparisonOp(StrEnum):
    """Supported relational operators for threshold rule evaluation."""

    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"


StatFieldName = Literal["mean", "minimum", "maximum", "p50", "p95", "stddev"]


class MetricPoint(BaseModel):
    """Single timestamped numeric telemetry observation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    timestamp: float
    value: float
    labels: dict[str, str] = Field(default_factory=dict)


class SummaryStats(BaseModel):
    """Aggregated descriptive statistics computed over a metric series."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric_name: str
    count: int
    mean: float
    minimum: float
    maximum: float
    p50: float
    p95: float
    stddev: float


class ThresholdRule(BaseModel):
    """Declarative threshold policy evaluated against a SummaryStats field."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str
    metric_name: str
    stat_field: StatFieldName = "p95"
    operator: ComparisonOp = ComparisonOp.GT
    limit: float
    severity: Literal["warning", "critical"] = "warning"


class AlertVerdict(BaseModel):
    """Immutable outcome produced by evaluating a ThresholdRule."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str
    metric_name: str
    triggered: bool
    observed_value: float
    limit: float
    severity: Literal["warning", "critical"]
    reason: str
