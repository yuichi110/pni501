# PNI Software Health Diagnostic Report

**Member Analytics Portal (`wp_plugin_messy` v1.3.0) — WordPress Plugin Audit**

```drawlib align=center code=fold file=cover_scorecard.png caption="PNI501 Executive Diagnostic Scorecard for Member Analytics Portal (wp_plugin_messy v1.3.0)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.utils import draw_pni_logo

setup(width=146, height=68, dpi=150)

hero = Panel(
    text="PNI501 Diagnostic Scorecard  —  Member Analytics Portal (v1.3.0)",
    description="",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=Styles.WhiteBold.patch(text_size=12.0),
    header_variant="filled",
    header_height=13.5,
    header_align="left",
)
hero.draw((3.0, 4.0), width=140.0, height=60.0)

draw_pni_logo((135.5, 57.2), width=8.5, dark=True)

primary_kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    metric_style=Styles.DarkBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.2),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
primary_kpis.add(
    "60 / 100",
    "Overall Score (Grade C)",
    "Baseline 70  |  AI -10pt",
    accent_style=Styles.WarningFlat,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon=phosphor.chart_bar,
    icon_style=Styles.Warning,
)
primary_kpis.add(
    "30 / 100",
    "Security Axis (Grade D)",
    "5 HIGH CWE + 1 Secret",
    accent_style=Styles.DangerFlat,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon=phosphor.shield_warning,
    icon_style=Styles.Danger,
)
primary_kpis.add(
    "0 / 16",
    "Applicable Rules Passed",
    "12 FAIL | 4 WARN | 1 N/A",
    accent_style=Styles.DangerFlat,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon=phosphor.list_checks,
    icon_style=Styles.Danger,
)
primary_kpis.add(
    "15 Total",
    "Audit Findings",
    "4 CRIT | 10 HIGH | 1 MED",
    accent_style=Styles.PrimaryFlat,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
    icon=phosphor.warning_octagon,
    icon_style=Styles.Primary,
)
primary_kpis.draw((6.0, 25.0), width=134.0, height=22.0, columns=4)

meta_kpis = KpiCards(
    style=Styles.PrimaryNeutral.patch(shape_r=1.5, shape_line_color=Colors.Gray3),
    metric_style=Styles.PrimaryBold.patch(text_size=11.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=8.8),
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.31,
    spacing=3.0,
)
meta_kpis.add(
    "4 Files",
    "Codebase (84 LOC)",
    "7 funcs, 0 classes, 0 tests",
    accent_style=Styles.PrimaryFlat,
)
meta_kpis.add(
    "PHP 8.2",
    "Runtime Smoke OK",
    "php -l OK; 5 hooks loaded",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=11.0),
)
meta_kpis.add(
    "0 CVEs",
    "Declared App CVEs",
    "Raw PHP (harness OS excl.)",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=11.0),
)
meta_kpis.draw((6.0, 7.5), width=134.0, height=14.5, columns=3)

save()
```

## Audit Identification & Provenance

| Attribute | Value |
| :--- | :--- |
| **Project / Plugin Name** | Member Analytics Portal (`wp_plugin_messy` v1.3.0) |
| **Target Directory** | `examples/php/wp_plugin_messy` |
| **Primary Language & Framework** | PHP (declared `Requires PHP: 7.4` EOL; tested on PHP 8.2) / WordPress Plugin |
| **Workflow & Run ID** | `php_wp_plugin_messy` / `wf-3389d5e7` (`category=audit`, `scope=repo`) |
| **Evaluated At (UTC)** | `2026-11-22T11:29:03.792183+00:00` |
| **Git Provenance** | `main@d1e02277 (dirty)` |
| **Overall Health Score** | **60 / 100 (Grade C)** *(Deterministic Baseline: 70 -> AI Adjustment: −10pt)* |
| **Security Axis Score** | **30 / 100 (Grade D)** *(5 HIGH CWE sinks, 1 hardcoded secret, 4/5 unauthenticated endpoints)* |
| **Rule Compliance Rate** | **`0 / 16` applicable rules passed** (`12 FAIL`, `4 WARN`, `1 NOT_APPLICABLE` of 17 evaluated) |
| **Findings Distribution** | **15 total findings** across 11 unique locations (`4 CRITICAL`, `10 HIGH`, `1 MEDIUM`) |
