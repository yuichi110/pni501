# 6. 詳細分析：セキュリティ・サプライチェーン・API 攻撃面

セキュリティは本監査における最大の支配的リスク要因です（**Security 30/100・グレード D**、`security_vulnerability_audit` **14/100**）。Trivy SCA による**宣言済み Composer アプリ依存 CVE は 0 件**であり、非出荷のテストハーネス OS CVE もスコアから適切に分離されていますが、`examples/php/wp_plugin_messy` の全 4 モジュールに `CWE-89` SQL インジェクション、`CWE-79` 反射型 XSS、`CWE-352` CSRF、`CWE-862` 認可欠如、およびハードコード秘密鍵漏洩が実在します。

```drawlib align=center code=fold file=security_attack_surface_map.png caption="WordPress 4 モジュール攻撃面マップ：脅威アクター・脆弱エンドポイント・シンク・侵害対象資産"
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

## アプリ層セキュリティ検出内訳とハーネス OS CVE の厳格分離

PNI は**出荷されるアプリ依存およびプロジェクト Dockerfile 脆弱性**と、**非出荷のテストハーネス基盤 OS パッケージ**を厳格に分離して集計します。`wp_plugin_messy` には `composer.json` もプロジェクト `Dockerfile` も存在しないため、Trivy は**アプリ CVE 0 件**・**プロジェクト OS CVE 0 件**と判定しつつ、テストハーネス（`.pni/dockerfiles/examples/php/wp_plugin_messy/Dockerfile`）由来の **3,512 件の OS CVE**（`CRITICAL 6`、`HIGH 355`、`MEDIUM 2,005`、`LOW 1,125`）をスコア計算から完全に除外しました。

```drawlib align=center code=fold file=security_sinks_and_cve_isolation.png caption="アプリケーション層セキュリティ指摘件数と Trivy SCA / ハーネス OS CVE 分離状況"
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

## セキュリティ制御ゲート評価（`SEC-01` .. `SEC-05`）

| ゲート | 判定 | 評価詳細 |
| :-: | :-: | :--- |
| **SEC-01** | **PASS（未管理）** | 宣言済み Composer ランタイム/開発 CVE は `0` 件（`composer.json`/`composer.lock` 不在の生 PHP）。テストハーネス由来 OS CVE `3,512` 件はプロジェクト評価から適切に除外。 |
| **SEC-02** | **N/A** | 出荷対象のプロジェクト `Dockerfile` や IaC マニフェストは存在しない（`misconfig_count=0`）。 |
| **SEC-03** | **FAIL（CRITICAL）** | `includes/rest-endpoints.php:3` にてグローバル変数 `$map_webhook_secret = '<REDACTED_SECRET>'` へ Webhook 秘密鍵をハードコード。 |
| **SEC-04** | **FAIL（HIGH）** | **HIGH CWE 危険シンク 5 件**（`CWE-89` SQLi ×3、`CWE-79` 反射型 XSS ×2）に加え、`member-analytics-portal.php:20-21` のショートコード `$_GET['badge_label']` XSS を検出。 |
| **SEC-05** | **FAIL（CRITICAL）** | **抽出エンドポイント 5 件中 4 件で認証ヒントが欠落**（REST `__return_true`、`wp_ajax_nopriv`、`ABSPATH` 欠落による直接実行）。さらに `'read'` 権限での管理設定変更・CSRF 不備あり。 |

## AST 危険コードシンクおよびハードコード秘密鍵一覧

| 重要度 | CWE / ルール | 該当箇所・シンボル | 脆弱パターン | 必須是正策 |
| :-: | :-: | :--- | :--- | :--- |
| **CRITICAL** | `common/security` | `includes/rest-endpoints.php:3`（`$map_webhook_secret`） | グローバルスコープでの Webhook 秘密鍵ハードコード（`<REDACTED_SECRET>`）。 | リテラル即時削除・鍵ローテーション後、`wp-config.php` 定数または環境変数から読込。 |
| **HIGH** | `CWE-89`（`sql_injection`） | `includes/rest-endpoints.php:19`（`map_export_all_members`） | `$wpdb->get_results($sql)` に生の `$_GET['role_filter']` を `LIKE` 句へ直接文字列結合。 | `$request->get_param('role_filter')`、`$wpdb->esc_like()`、`$wpdb->prepare()` を適用。 |
| **HIGH** | `CWE-89`（`sql_injection`） | `includes/ajax-handlers.php:10`（`map_ajax_search_members`） | `$wpdb->get_results("SELECT ID, display_name, user_email FROM {$wpdb->users} WHERE display_name LIKE '%" . $term . "%'")`。 | `$wpdb->prepare()` + `$wpdb->esc_like()` でパラメータ化し、`wp_ajax_nopriv` を削除。 |
| **HIGH** | `CWE-89`（`sql_injection`） | `includes/ajax-handlers.php:21`（`map_ajax_purge_logs`） | `$wpdb->query("DELETE FROM wp_map_events WHERE category = '" . $category . "'")`。 | `$wpdb->prepare()` 化に加え `check_ajax_referer()` と `current_user_can('manage_options')` を強制。 |
| **HIGH** | `CWE-79`（`xss`） | `includes/ajax-handlers.php:22`（`map_ajax_purge_logs`） | `echo "Purged category: " . $_POST['category'];` の未エスケープ出力。 | `esc_html()` 適用の上で `wp_send_json_success()` による構造化 JSON を返却。 |
| **HIGH** | `CWE-79`（`xss`） | `admin/settings-page.php:26`（`map_render_settings_page`） | `echo $_GET['tab'] ?? 'general';`（および 29 行目の未エスケープ `$active_tab` 属性）。 | 許可リスト検証と `esc_html()` / `esc_attr()` による出力エスケープを実施。 |
| **HIGH** | `common/security`（`xss`） | `member-analytics-portal.php:20-21`（`map_render_badge_shortcode`） | 生の `$_GET['badge_label']` を `<span class="map-badge">` へ直接結合。 | `shortcode_atts()` から取得し `sanitize_text_field()` と `esc_html()` を適用。 |

## 抽出 HTTP API・直接アクセス攻撃面一覧（`api_endpoints`）

| メソッド | エンドポイント / 直接アクセス経路 | ハンドラ・箇所 | 認証境界ステータス | セキュリティ影響 |
| :-: | :--- | :--- | :--- | :--- |
| `GET` | `/wp-json/member-analytics/v1/export` | `map_export_all_members`（`includes/rest-endpoints.php:7`） | **なし**（`__return_true`） | 未認証での `wp_users` PII 流出 + `CWE-89` SQLi + `?debug` `print_r()` 漏洩。 |
| `POST` | `/wp-admin/admin-ajax.php?action=map_search_members` | `map_ajax_search_members`（`includes/ajax-handlers.php:3`） | **なし**（`wp_ajax_nopriv`） | 未認証での `wp_users` 検索 + `CWE-89` SQLi + Nonce 検証ゼロ。 |
| `POST` | `/wp-admin/admin-ajax.php?action=map_purge_logs` | `map_ajax_purge_logs`（`includes/ajax-handlers.php:4`） | `wp_ajax_session` のみ | ログイン済み購読者から CSRF 経由の `DELETE` SQLi（`CWE-89`）と反射型 XSS（`CWE-79`）が可能。 |
| `ANY` | `/examples/php/wp_plugin_messy/admin/settings-page.php` | `settings-page.php`（`admin/settings-page.php:1`） | **なし**（`ABSPATH` 欠落） | PHP 直接実行リスクに加え、WP 管理画面経由でも `'read'` 権限で設定改ざん・`@file_get_contents()` 外部通信・`CWE-79` XSS が発生。 |
| `GET` | `/examples/php/wp_plugin_messy/member-analytics-portal.php` | `member-analytics-portal.php`（`member-analytics-portal.php:1`） | **なし**（`ABSPATH` 欠落） | PHP 直接実行リスクおよびショートコードの `$_GET['badge_label']` 反射型 XSS。 |

## サプライチェーン・ガバナンス基盤状況

- **依存関係管理**: `has_manifest=False`、`has_lockfile=False`、`dependencies_count=0`（手動 `require_once` の生 PHP）。アプリ CVE 0 件はロックファイル監査済みではなく未管理構成に起因します。
- **ランタイムサポート**: プラグインヘッダは `Requires PHP: 7.4`（2022 年 11 月 EOL）を宣言しており、PHP `8.2+` / `8.3+` への引き上げが必須です。
- **リポジトリガバナンス**: `LICENSE`、`SECURITY.md`、`.gitignore`、GitHub Actions CI、および Dependabot/Renovate がすべて未設定（`has_security_policy=False`、`has_dependency_automation=False`）。
