# metrics-kit

`metrics-kit` is a lightweight, zero-side-effect Python library for statistical time-series aggregation, exponentially weighted moving averages (EWMA), and declarative threshold alert evaluation.

## Installation & Quickstart Tutorial

Install with `uv` or `pip`:

```bash
uv add metrics-kit
```

Evaluate a latency sample series in five lines:

```python
from metrics_kit import ComparisonOp, MetricPoint, ThresholdRule, evaluate_rule, summarize_series

points = [MetricPoint(timestamp=1.0, value=42.0), MetricPoint(timestamp=2.0, value=95.0)]
stats = summarize_series("api.latency_ms", points)
rule = ThresholdRule(rule_id="slo-p95", metric_name="api.latency_ms", operator=ComparisonOp.GT, limit=80.0, stat_field="p95")
verdict = evaluate_rule(stats, rule)
```

## How-To Guides

### Smooth Noisy Telemetry with EWMA
Use `compute_ewma(values, alpha=0.3)` to dampen short spikes before threshold evaluation.

### Export Prometheus Exposition Lines
Use `to_prometheus_lines(stats)` to render `count`, `mean`, `p95`, and `max` gauges without pulling in heavy HTTP server dependencies.

## API Reference

- `models`: `MetricPoint`, `SummaryStats`, `ComparisonOp`, `ThresholdRule`, `AlertVerdict`
- `stats`: `compute_mean`, `compute_percentile`, `compute_stddev`, `compute_ewma`, `summarize_series`
- `rules`: `evaluate_rule`, `evaluate_ruleset`, `detect_zscore_anomalies`
- `formatting`: `format_markdown_summary`, `to_prometheus_lines`
- `exceptions`: `MetricsKitError`, `EmptySampleError`, `InvalidParameterError`

## Architecture & Design Explanation

`metrics-kit` enforces strict unidirectional layering (`formatting` / `rules` -> `stats` -> `models` -> `exceptions`):
- **Pure Functions & Immutable Value Objects**: All models use `ConfigDict(frozen=True)` and raise typed domain exceptions rather than calling `sys.exit()` or writing to standard output.
- **PEP 561 Type Marker**: Ships `py.typed` with 100% strict parameter and return annotations.
