# 3. Recommended Remediation Roadmap

Remediation must execute in strict risk order: **P0** immediately closes all active remote exploitation vectors (hardcoded secret, SQL injection, XSS, CSRF, broken access control, and direct file access), **P1** modernizes runtime I/O, PHP 8.2+ strict typing, Composer PSR-4 packaging, and PHPUnit security regression tests, and **P2** locks in CI/CD governance and developer documentation.

```drawlib align=center code=fold file=remediation_roadmap.png caption="Phased P0 -> P1 -> P2 Remediation Roadmap for Member Analytics Portal"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Colors, Styles

setup(width=146, height=68, dpi=150)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=1.8, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=8.8),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="vertical",
    card_shape="rounded_rect",
    spacing=2.6,
)
rm.add(
    "P0-A: Secret Rotation & Direct-Access Containment",
    "Rotate map_webhook_secret (<REDACTED>); add ABSPATH guards to all 4 files; escape shortcode.",
    badge_text="P0-A",
    badge_style=Styles.DangerFlat,
    icon=phosphor.key,
    icon_style=Styles.Danger,
)
rm.add(
    "P0-B: SQLi, XSS, CSRF & Access Control Hardening",
    "Parameterize 3 SQL sinks with wpdb->prepare(); drop __return_true/nopriv; enforce nonces & esc_html().",
    badge_text="P0-B",
    badge_style=Styles.DangerFlat,
    icon=phosphor.shield_check,
    icon_style=Styles.Danger,
)
rm.add(
    "P1: PHP 8.2 Strict Types, WP APIs & PHPUnit Suite",
    "Use wp_remote_get(timeout=5); remove print_r(); adopt strict_types, PSR-4, wp_enqueue_script & PHPUnit.",
    badge_text="P1",
    badge_style=Styles.WarningFlat,
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
rm.add(
    "P2: CI/CD Governance, Static Gates & Documentation",
    "Add GitHub Actions (WPCS, PHPStan, PHPUnit + PCOV), .gitignore, LICENSE, SECURITY.md & full README.",
    badge_text="P2",
    badge_style=Styles.PrimaryFlat,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Primary,
)
rm.draw((4.0, 4.0), width=138.0, height=60.0)

save()
```

## Projected Score Recovery & Workload Split

Completing the 4 urgent `P0` security actions and 4 `P1` modernization/testing actions directly addresses the four lowest-scoring audit dimensions (`Security`, `Documentation`, `Typing`, and `Testing`), raising the plugin from Grade C (**60/100**) into Grade A/B readiness.

```drawlib align=center code=fold file=remediation_impact_matrix.png caption="Current vs. Post-Remediation Target Axis Scores and Action Plan Distribution"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=146, height=64, dpi=150)

text(
    (46.0, 59.5),
    "Score Uplift on Lagging Axes (Current vs. Post-P1/P2 Target)",
    style=Styles.DarkBold.patch(text_size=10.8),
)

bar = BarChart(
    categories=["Security", "Docs", "Typing", "Testing", "Overall"],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=10.0),
    grid_style=Styles.MutedThin,
    width=80.0,
    height=42.0,
    bar_mode="group",
    bar_r=0.8,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
bar.add_series("Current Audit", [30.0, 27.0, 36.0, 55.0, 60.0], style=Styles.DangerNeutral)
bar.add_series("Target Post-P1/P2", [85.0, 80.0, 85.0, 85.0, 86.0], style=Styles.PrimaryFlat)
bar.draw(xy=(6.0, 12.0))
bar.draw_legend(
    xy=(18.0, 4.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    orientation="horizontal",
    item_gap=6.0,
)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5, shape_fill_color=Colors.White, shape_line_color=Colors.Gray3),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=8.8),
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.25,
    spacing=2.8,
)
cards.add(
    "4 P0",
    "Urgent Security Fixes",
    "Secret, 3x SQLi, 3x XSS, auth",
    accent_style=Styles.DangerFlat,
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    icon=phosphor.shield_warning,
    icon_style=Styles.Danger,
)
cards.add(
    "4 P1",
    "Modernization & Tests",
    "wp_remote_get, PHP 8.2, PHPUnit",
    accent_style=Styles.WarningFlat,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
cards.add(
    "P2",
    "CI & Governance Gate",
    "WPCS, PHPStan, README, LICENSE",
    accent_style=Styles.PrimaryFlat,
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
    icon=phosphor.check_circle,
    icon_style=Styles.Primary,
)
cards.draw((90.0, 9.0), width=53.0, height=48.0, columns=1)

save()
```

## Action Plan Traceability Matrix (`P0 -> P1 -> P2`)

All 8 pre-sorted remediation actions from `action_plan` are traced directly to target files, rule IDs, and CWEs below (followed by the recommended `P2` governance and documentation milestone):

| # | Priority | Action Title & Category | Target Files | Expected Impact | Related Rules / CWEs |
| :-: | :-: | :--- | :--- | :--- | :--- |
| 1 | **P0** | **Add `ABSPATH` guard and escape shortcode output** (`security`) | `member-analytics-portal.php` | Eliminates reflected XSS in `[member_analytics_badge]` and blocks direct script execution. | `common/security` |
| 2 | **P0** | **Eliminate SQLi, XSS, CSRF, and broken access control across REST, AJAX, and Admin handlers** (`security`) | `includes/rest-endpoints.php`, `includes/ajax-handlers.php`, `admin/settings-page.php`, `member-analytics-portal.php` | Neutralizes all 5 HIGH `CWE-89`/`CWE-79` sinks, unauthenticated PII export, and destructive log purge. | `php/frameworks/wordpress`, `common/security_vulnerability`, `CWE-89`, `CWE-79`, `CWE-352`, `CWE-862` |
| 3 | **P0** | **Remediate all CWE-89 SQLi, CWE-79 XSS, hardcoded secret, and unauthenticated REST/AJAX endpoints** (`security`) | `includes/rest-endpoints.php`, `includes/ajax-handlers.php`, `admin/settings-page.php`, `member-analytics-portal.php` | Eliminates remote SQL injection, `wp_users` exfiltration, arbitrary log deletion, and XSS across all endpoints. | `common/security_vulnerability`, `SEC-03`, `SEC-04`, `SEC-05`, `CWE-89`, `CWE-79` |
| 4 | **P0** | **Remove hardcoded `$map_webhook_secret` (`<REDACTED_SECRET>`) and externalize via `wp-config`/env** (`security`) | `includes/rest-endpoints.php` | Eliminates CRITICAL credential exposure in source code and enforces secret rotation. | `common/security`, `common/supply_chain` |
| 5 | **P1** | **Replace `@file_get_contents` with timeout-bounded `wp_remote_get` and remove `print_r`** (`code_quality`) | `admin/settings-page.php`, `includes/rest-endpoints.php` | Eliminates hung PHP worker threads, silent failure suppression, and `?debug` data leaks. | `common/production_readiness`, `common/twelve_factor` |
| 6 | **P1** | **Adopt Composer PSR-4 packaging, PHP 8.2+, and CI governance** (`dependencies`) | `member-analytics-portal.php` | Transitions from unmanaged EOL PHP 7.4 raw includes to modern PHP 8.2+/8.3+ Composer & CI supply-chain controls. | `php/dependencies`, `php/modern_stack`, `common/supply_chain` |
| 7 | **P1** | **Add PHPUnit + WP_Mock/Brain Monkey security regression test suite with PCOV coverage** (`testing`) | `member-analytics-portal.php`, `includes/rest-endpoints.php`, `includes/ajax-handlers.php`, `admin/settings-page.php` | Establishes automated regression verification for capability checks, nonces, SQL preparation, and escaping. | `common/runtime_verification` |
| 8 | **P1** | **Modernize to PHP 8.2+ `strict_types`, PSR-4 classes, `wp_remote_get`, and `wp_enqueue_script`** (`typing`) | `member-analytics-portal.php`, `admin/settings-page.php` | Eliminates silent scalar coercion, unbounded HTTP calls, and hardcoded `<script src=...>` tags. | `php/typing`, `php/code_quality`, `php/modern_stack`, `php/frameworks/wordpress` |
| 9 | **P2** | **Complete `README.md`, PHPDoc coverage, `.gitignore`, `LICENSE`, `SECURITY.md`, & GitHub Actions WPCS/PHPStan** (`governance`) | `README.md`, `.github/workflows/*`, `composer.json` | Closes remaining `common/documentation`, `common/git_workflow`, and `common/supply_chain` gaps. | `common/documentation`, `common/git_workflow`, `common/supply_chain` |
