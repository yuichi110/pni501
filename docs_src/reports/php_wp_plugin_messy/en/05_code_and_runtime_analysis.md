# 5. Deep Dive: Code Quality, Testing & Runtime

Static PHP AST inspection across all 4 modules (`84` LOC, `7` procedural functions, `0` classes) exposes a stark split between superficial syntax validity and deep engineering debt: every file passes `php -l` and registers its WordPress hooks cleanly under PHP 8.2, yet type safety (`0.0%`), PHPDoc (`0.0%`), WordPress framework hygiene (`16` violations), and automated test coverage (`0` PHPUnit tests) all sit at zero.

```drawlib align=center code=fold file=module_quality_heatmap.png caption="Module x Quality & Security Fitness Matrix (0 = Critical Gap, 100 = Healthy)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

hm = HeatmapChart(
    styles=[Styles.DangerFlat, Styles.WarningNeutral, Styles.SuccessNeutral],
    x_categories=["Modularity", "Strict Types", "PHPDoc", "ABSPATH", "Sec Hygiene", "Test Cov"],
    axis_line_style=Styles.MutedThin,
    width=104.0,
    height=44.0,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format="{:.0f}",
    auto_contrast_text=True,
    x_label_position="top",
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    title="Module x Quality/Security Fitness Matrix (0-100 Score per Dimension)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
hm.add_row("member-analytics-portal.php", [80, 0, 0, 0, 20, 0])
hm.add_row("includes/rest-endpoints.php", [85, 0, 0, 0, 5, 0])
hm.add_row("includes/ajax-handlers.php", [85, 0, 0, 0, 5, 0])
hm.add_row("admin/settings-page.php", [75, 0, 0, 0, 15, 0])
hm.draw(xy=(38.0, 6.0))

save()
```

## PHP 8.2 Runtime Smoke vs. Zero-Test Coverage Diagnostic

PNI executed the isolated Docker PHP 8.2 runtime harness (`.pni/dockerfiles/examples/php/wp_plugin_messy/Dockerfile`, template `php/raw.dockerfile`). While the container build (`49.1s`), syntax gate (`php -l`, `0.72s`), and stubbed WordPress hook-load smoke probe (`0.64s`, 5 hooks registered) passed, **zero PHPUnit/Pest tests exist**, leaving `coverage.measured=False` and giving zero regression protection for any future security patch.

```drawlib align=center code=fold file=runtime_vs_coverage_diagnostic.png caption="Docker PHP 8.2 Runtime Gate Results vs. Static AST Hygiene & Coverage Metrics"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=148, height=66, dpi=150)

left = Panel(
    text="Docker PHP 8.2 Runtime Harness Gates (RV-01 .. RV-04)",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    header_variant="filled",
    header_height=9.0,
)
left.draw((3.0, 4.0), width=68.0, height=58.0)

gates = CardList(
    style=Styles.Neutral.patch(shape_r=1.4, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Muted.patch(text_size=8.6),
    badge_shape="rounded_rect",
    direction="vertical",
    spacing=2.2,
)
gates.add(
    "RV-01 Harness Build (49.1s)",
    "php/raw.dockerfile (PHP 8.2) built, exit 0",
    badge_text="PASS",
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.0),
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
gates.add(
    "RV-02 Syntax Lint vs. Tests (0.72s)",
    "php -l OK (4/4 files); 0 PHPUnit tests found",
    badge_text="WARN",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=9.0),
    icon=phosphor.warning_circle,
    icon_style=Styles.Warning,
)
gates.add(
    "RV-03 PCOV Line Coverage",
    "coverage.measured=False (no tests/ suite)",
    badge_text="FAIL",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=9.0),
    icon=phosphor.x_circle,
    icon_style=Styles.Danger,
)
gates.add(
    "RV-04 WP Hook Smoke Probe (0.64s)",
    "Entrypoint loaded cleanly; 5 hooks active",
    badge_text="PASS",
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.0),
    icon=phosphor.plug,
    icon_style=Styles.Success,
)
gates.draw((5.5, 6.5), width=63.0, height=44.5)

text(
    (116.0, 59.0),
    "Static Quality & Coverage Metrics (%)",
    style=Styles.DarkBold.patch(text_size=10.5),
)

bar = BarChart(
    categories=[
        "Import Hygiene",
        "Strict Typing",
        "PHPDoc",
        "ABSPATH Guard",
        "Unit Test Cov",
    ],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    grid_style=Styles.MutedThin,
    width=46.0,
    height=46.0,
    orientation="horizontal",
    bar_r=0.7,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}%",
)
bar.add_series("Measured %", [75.0, 0.0, 0.0, 0.0, 0.0], style=Styles.PrimaryFlat)
bar.draw(xy=(96.0, 8.0))

save()
```

## Quantitative Static AST & Operational Readiness Telemetry

| Metric Category | Metric | Observed Value | Assessment |
| :--- | :--- | :---: | :--- |
| **Codebase Scale** | Total PHP Files / LOC / Functions / Classes | `4` / `84` / `7` / `0` | Compact procedural footprint; no OOP namespaces or classes. |
| **Import Hygiene** | `import_hygiene_coverage_pct` / Circular Deps | `75.0%` / `0` | Acyclic, but `member-analytics-portal.php:11-13` uses 3 manual `require_once` statements instead of Composer PSR-4 autoloading. |
| **Type Safety** | `type_safety_coverage_pct` / Issues | `0.0%` / `11` | Missing `declare(strict_types=1)` in all 4 files; missing return types on all 7 functions; untyped `$request` and `$atts` params. |
| **Documentation** | `docstring_coverage_pct` / Missing PHPDocs | `0.0%` / `7` | Zero `/** ... */` PHPDoc blocks on any public callable; `README.md` is 2 lines. |
| **SIG Maintainability** | Complex Functions / Excessive Params / Global State | `0` / `0` / `13` | Functions remain short, but `3` `global $wpdb` + `10` direct `$_GET`/`$_POST` accesses tightly couple business logic to globals. |
| **WordPress Hygiene** | `framework_issues_count` / `modernization_hints_count` | `16` / `1` | 4 missing `ABSPATH` guards, 3 handlers missing CSRF nonces, 3 missing `current_user_can()`, 6 unsanitized superglobals, 1 hardcoded `<script src=...>`. |
| **12-Factor / SRE PRR** | Bug-Risk Idioms / Missing I/O Timeouts / Unstructured Log | `1` / `1` / `1` | `@file_get_contents()` suppresses failures without stream timeout (`admin/settings-page.php:21`); `print_r($rows)` leaks raw rows (`includes/rest-endpoints.php:21`). |

## Container Runtime Verification & Hook Smoke Breakdown

| Gate | Status | Duration | Executed Check & Observed Detail |
| :--- | :-: | :-: | :--- |
| **RV-01 Harness Build** | **PASS** | `49.1s` | Built `.pni/dockerfiles/examples/php/wp_plugin_messy/Dockerfile` (`php/raw.dockerfile`, `PHP_VERSION=8.2`, exit `0`). Note: plugin header still declares EOL `Requires PHP: 7.4`. |
| **RV-02 Syntax & Unit Tests** | **WARN** | `0.72s` | `php -l` passed across all 4 `.php` files; no `tests/` directory or `*Test.php` files exist (`total_tests=0`, `passed=0`, `failed=0`). |
| **RV-03 Measured Coverage** | **FAIL** | — | `coverage.measured=False` (PCOV could not run without a PHPUnit suite). |
| **RV-04 WP Hook Smoke** | **PASS** | `0.64s` | Loaded `member-analytics-portal.php` with stubbed WordPress registration APIs (`HTTP 200` probe equivalent); registered **5 hooks** cleanly: `rest_api_init`, shortcode `member_analytics_badge`, `wp_ajax_nopriv_map_search_members`, `wp_ajax_map_purge_logs`, and `admin_menu`. |
