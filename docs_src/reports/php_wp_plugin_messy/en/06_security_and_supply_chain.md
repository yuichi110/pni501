# 6. Deep Dive: Security, Supply Chain & API Surface

Security is the decisive risk driver of this audit (**30/100 — Grade D**, `security_vulnerability_audit` **14/100**). Although Trivy SCA reported **0 declared Composer application CVEs** and cleanly isolated non-shipped test-harness OS CVEs, every module in `examples/php/wp_plugin_messy` contains exploitable application-layer vulnerabilities spanning `CWE-89` SQL injection, `CWE-79` reflected XSS, `CWE-352` CSRF, `CWE-862` missing authorization, and hardcoded credential leakage.

```drawlib align=center code=fold file=security_attack_surface_map.png caption="4-Module WordPress Attack Surface Map: Threat Actors, Vulnerable Endpoints, Sinks, and Compromised Assets"
from drawlib.canvas import save, setup
from drawlib.lines import line
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Colors, Styles

setup(width=168, height=82, dpi=150)

actors = Panel(
    text="Threat Actors",
    style=Styles.Neutral.patch(shape_r=1.8, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.DangerNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=8.5,
)
actors.draw((3.0, 6.0), width=40.0, height=70.0)

actor_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.2, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    text_style=Styles.DarkBold.patch(text_size=9.4),
    description_style=Styles.Muted.patch(text_size=8.6),
    badge_shape="rounded_rect",
    direction="vertical",
    spacing=4.5,
)
actor_cards.add(
    "Unauthenticated User",
    "REST export, nopriv,\ndirect PHP, shortcode",
    badge_text="EXT",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=8.4),
)
actor_cards.add(
    "WP Subscriber ('read')",
    "Admin options POST &\nwp_ajax_purge_logs",
    badge_text="SUB",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=8.4),
)
actor_cards.draw((5.5, 16.0), width=35.0, height=44.0)

modules = Panel(
    text="4 Vulnerable Plugin Modules (5 CWE Sinks + 1 Secret)",
    style=Styles.Neutral.patch(shape_r=1.8, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    header_variant="filled",
    header_height=8.5,
)
modules.draw((50.0, 6.0), width=68.0, height=70.0)

mod_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.2, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Muted.patch(text_size=8.4),
    badge_shape="rounded_rect",
    direction="vertical",
    spacing=2.2,
)
mod_cards.add(
    "includes/rest-endpoints.php",
    "__return_true + CWE-89 SQLi (L19)\n+ <REDACTED_SECRET> (L3)",
    badge_text="CRIT",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=8.4),
)
mod_cards.add(
    "includes/ajax-handlers.php",
    "nopriv SQLi (L10) + DELETE SQLi (L21)\n+ CWE-79 XSS (L22); zero nonces",
    badge_text="CRIT",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=8.4),
)
mod_cards.add(
    "admin/settings-page.php",
    "'read' cap + CSRF + CWE-79 XSS (L26)\n+ unbounded @file_get_contents (L21)",
    badge_text="HIGH",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=8.4),
)
mod_cards.add(
    "member-analytics-portal.php",
    "Missing ABSPATH guard + shortcode\nGET['badge_label'] reflected XSS",
    badge_text="HIGH",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=8.4),
)
mod_cards.draw((52.5, 8.8), width=63.0, height=56.0)

assets = Panel(
    text="Compromised Assets",
    style=Styles.Neutral.patch(shape_r=1.8, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=8.5,
)
assets.draw((125.0, 6.0), width=40.0, height=70.0)

asset_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.2, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Muted.patch(text_size=8.4),
    badge_shape="rounded_rect",
    direction="vertical",
    spacing=2.2,
)
asset_cards.add(
    "wp_users PII",
    "user_login & user_email\ndirectory dump",
    badge_text="DB",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=8.4),
)
asset_cards.add(
    "wp_map_events",
    "Arbitrary DELETE via\nCWE-89 SQL injection",
    badge_text="DB",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=8.4),
)
asset_cards.add(
    "wp_options & Egress",
    "Option overwrite +\nunbounded HTTP ping",
    badge_text="CFG",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=8.4),
)
asset_cards.add(
    "Admin / Visitor DOM",
    "3 reflected XSS vectors\nacross admin & frontend",
    badge_text="DOM",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=8.4),
)
asset_cards.draw((127.5, 8.8), width=35.0, height=56.0)

line((43.0, 52.0), (50.0, 58.0), arrow_head="->", style=Styles.DangerBold)
line((43.0, 48.0), (50.0, 44.0), arrow_head="->", style=Styles.DangerBold)
line((43.0, 27.0), (50.0, 29.0), arrow_head="->", style=Styles.WarningBold)
line((43.0, 45.0), (50.0, 16.0), arrow_head="->", style=Styles.WarningDashed)

line((118.0, 58.0), (125.0, 58.0), arrow_head="->", style=Styles.DangerBold)
line((118.0, 44.0), (125.0, 44.0), arrow_head="->", style=Styles.DangerBold)
line((118.0, 29.0), (125.0, 29.0), arrow_head="->", style=Styles.WarningBold)
line((118.0, 15.0), (125.0, 15.0), arrow_head="->", style=Styles.WarningBold)

save()
```

## Security Findings Breakdown & Harness OS CVE Isolation

PNI separates **shipped application & project Dockerfile vulnerabilities** from **non-shipped test-harness base-OS packages**. Because `wp_plugin_messy` has no `composer.json` and no project `Dockerfile`, Trivy reported **0 application CVEs** and **0 project OS CVEs**, while cleanly isolating **3,512 harness-only Debian/PHP OS CVEs** (`6` CRITICAL, `355` HIGH, `2,005` MEDIUM, `1,125` LOW in `.pni/dockerfiles/examples/php/wp_plugin_messy/Dockerfile`) from the project score.

```drawlib align=center code=fold file=security_sinks_and_cve_isolation.png caption="Application Security Sinks vs. Trivy SCA and Harness-Only OS CVE Isolation"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=148, height=64, dpi=150)

text(
    (51.0, 59.5),
    "Application-Layer Security Finding Counts",
    style=Styles.DarkBold.patch(text_size=10.8),
)

bar = BarChart(
    categories=[
        "WP Violations",
        "Unauth Routes",
        "CWE-89 SQLi",
        "CWE-79 (AST)",
        "Shortcode XSS",
        "Hardcoded Sec",
        "App CVEs",
    ],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    grid_style=Styles.MutedThin,
    width=57.0,
    height=46.0,
    orientation="horizontal",
    bar_r=0.7,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
bar.add_series("Count", [16.0, 4.0, 3.0, 2.0, 1.0, 1.0, 0.0], style=Styles.DangerFlat)
bar.draw(xy=(25.0, 8.0))

panel = Panel(
    text="Trivy SCA & Harness CVE Isolation (v0.69.3)",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=8.8,
)
panel.draw((87.0, 5.0), width=58.0, height=54.0)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.4, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    metric_style=Styles.DarkBold.patch(text_size=11.0),
    text_style=Styles.DarkBold.patch(text_size=9.4),
    description_style=Styles.Muted.patch(text_size=8.6),
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.28,
    spacing=2.4,
)
cards.add(
    "0 CVEs",
    "Declared App Dependencies",
    "Raw PHP (no composer.json)",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=11.0),
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
cards.add(
    "0 / 0",
    "Project OS & IaC Misconfigs",
    "No project Dockerfile (N/A)",
    accent_style=Styles.PrimaryFlat,
    metric_style=Styles.PrimaryBold.patch(text_size=11.0),
    icon=phosphor.shield_check,
    icon_style=Styles.Primary,
)
cards.add(
    "3,512",
    "Harness Base-OS (Excluded)",
    "6 CRIT, 355 HIGH (non-shipped)",
    accent_style=Styles.WarningFlat,
    metric_style=Styles.WarningBold.patch(text_size=11.0),
    icon=phosphor.warning_circle,
    icon_style=Styles.Warning,
)
cards.draw((89.5, 8.0), width=53.0, height=41.5, columns=1)

save()
```

## Security Control Gates (`SEC-01` .. `SEC-05`)

| Gate | Status | Evaluation Detail |
| :-: | :-: | :--- |
| **SEC-01** | **PASS (Unmanaged)** | `0` declared Composer runtime/dev CVEs (raw PHP without `composer.json`/`composer.lock`); `3,512` harness-only OS CVEs cleanly excluded. |
| **SEC-02** | **N/A** | No project `Dockerfile` or IaC manifest shipped (`misconfig_count=0`). |
| **SEC-03** | **FAIL (CRITICAL)** | Hardcoded webhook secret assigned to global `$map_webhook_secret = '<REDACTED_SECRET>'` at `includes/rest-endpoints.php:3`. |
| **SEC-04** | **FAIL (HIGH)** | **5 HIGH CWE AST sinks** (`3× CWE-89` SQL injection, `2× CWE-79` reflected XSS) plus shortcode `$_GET['badge_label']` XSS in `member-analytics-portal.php:20-21`. |
| **SEC-05** | **FAIL (CRITICAL)** | **4 of 5 extracted endpoints lack auth hints**: public REST `__return_true` export, `wp_ajax_nopriv` member search, and direct PHP entrypoints lacking `ABSPATH`; plus `'read'`-cap admin settings escalation without nonces. |

## AST Dangerous Code Sinks & Hardcoded Secret Inventory

| Severity | CWE / Rule | Location & Symbol | Vulnerable Pattern | Required Fix |
| :-: | :-: | :--- | :--- | :--- |
| **CRITICAL** | `common/security` | `includes/rest-endpoints.php:3` (`$map_webhook_secret`) | Hardcoded webhook secret literal (`<REDACTED_SECRET>`) in global scope. | Delete literal, rotate credential, load from `wp-config.php` constant or environment secret. |
| **HIGH** | `CWE-89` (`sql_injection`) | `includes/rest-endpoints.php:19` (`map_export_all_members`) | `$wpdb->get_results($sql)` interpolating raw `$_GET['role_filter']` into `LIKE` on `$wpdb->users`. | Use `$request->get_param('role_filter')`, `$wpdb->esc_like()`, and `$wpdb->prepare()`. |
| **HIGH** | `CWE-89` (`sql_injection`) | `includes/ajax-handlers.php:10` (`map_ajax_search_members`) | `$wpdb->get_results("SELECT ID, display_name, user_email FROM {$wpdb->users} WHERE display_name LIKE '%" . $term . "%'")`. | Parameterize with `$wpdb->prepare()` + `$wpdb->esc_like()` and remove `wp_ajax_nopriv`. |
| **HIGH** | `CWE-89` (`sql_injection`) | `includes/ajax-handlers.php:21` (`map_ajax_purge_logs`) | `$wpdb->query("DELETE FROM wp_map_events WHERE category = '" . $category . "'")`. | Parameterize with `$wpdb->prepare()`, enforce `check_ajax_referer()` + `current_user_can('manage_options')`. |
| **HIGH** | `CWE-79` (`xss`) | `includes/ajax-handlers.php:22` (`map_ajax_purge_logs`) | `echo "Purged category: " . $_POST['category'];` rendered unescaped. | Return structured JSON via `wp_send_json_success()` with `esc_html()`. |
| **HIGH** | `CWE-79` (`xss`) | `admin/settings-page.php:26` (`map_render_settings_page`) | `echo $_GET['tab'] ?? 'general';` (and unescaped `$active_tab` attribute at line 29). | Validate against allow-list and escape with `esc_html()` / `esc_attr()`. |
| **HIGH** | `common/security` (`xss`) | `member-analytics-portal.php:20-21` (`map_render_badge_shortcode`) | Concatenates raw `$_GET['badge_label']` directly into `<span class="map-badge">`. | Read from `shortcode_atts()`, sanitize with `sanitize_text_field()`, escape with `esc_html()`. |

## Extracted HTTP API & Direct-Access Attack Surface (`api_endpoints`)

| Method | Endpoint / Direct Entry | Handler & Location | Auth Boundary Status | Security Impact |
| :-: | :--- | :--- | :--- | :--- |
| `GET` | `/wp-json/member-analytics/v1/export` | `map_export_all_members` (`includes/rest-endpoints.php:7`) | **NONE** (`__return_true`) | Unauthenticated `wp_users` PII export + `CWE-89` SQLi + `?debug` `print_r()` leak. |
| `POST` | `/wp-admin/admin-ajax.php?action=map_search_members` | `map_ajax_search_members` (`includes/ajax-handlers.php:3`) | **NONE** (`wp_ajax_nopriv`) | Unauthenticated `wp_users` search + `CWE-89` SQLi + zero nonce check. |
| `POST` | `/wp-admin/admin-ajax.php?action=map_purge_logs` | `map_ajax_purge_logs` (`includes/ajax-handlers.php:4`) | `wp_ajax_session` only | Any logged-in subscriber can trigger CSRF `DELETE` SQLi (`CWE-89`) + reflected XSS (`CWE-79`). |
| `ANY` | `/examples/php/wp_plugin_messy/admin/settings-page.php` | `settings-page.php` (`admin/settings-page.php:1`) | **NONE** (missing `ABSPATH`) | Direct PHP execution risk; via WP admin, `'read'` cap allows subscriber option overwrite + `@file_get_contents()` ping + `CWE-79` XSS. |
| `GET` | `/examples/php/wp_plugin_messy/member-analytics-portal.php` | `member-analytics-portal.php` (`member-analytics-portal.php:1`) | **NONE** (missing `ABSPATH`) | Direct PHP execution risk; shortcode reflects raw `$_GET['badge_label']`. |

## Supply-Chain & Governance Baseline

- **Dependency Management**: `has_manifest=False`, `has_lockfile=False`, `dependencies_count=0` (Composer-less raw PHP with manual `require_once`). Zero CVEs reflect unmanaged packaging rather than audited lockfile coverage.
- **Runtime Support Lifecycle**: Plugin header declares `Requires PHP: 7.4` (end-of-life since November 2022); must upgrade minimum requirement to PHP `8.2+` / `8.3+`.
- **Repository Governance**: Missing `LICENSE`, `SECURITY.md`, `.gitignore`, GitHub Actions CI workflows, and Dependabot/Renovate automation (`has_security_policy=False`, `has_dependency_automation=False`).
