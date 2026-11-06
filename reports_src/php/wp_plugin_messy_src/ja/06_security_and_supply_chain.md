# 6. セキュリティ・脆弱性・サプライチェーン分析

本章では、AST セキュリティ解析による WordPress 認可境界破綻（`SEC-05`）・CWE 危険コードシンク（`SEC-04`）・ハードコード秘密鍵（`SEC-03`）と、Trivy (`0.69.3`) によるファイルシステムおよび解決済みコンテナイメージ（Debian 12.15）の脆弱性スキャン結果（`SEC-01` / `SEC-02`）を統合して評価する。

```drawlib file=security_cve_and_sinks_chart.png caption="深刻度別 セキュリティ問題内訳 (WordPress認可/CWEシンク vs コンテナOS層CVE)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.0),
    value_text_style=Styles.DarkBold.patch(text_size=9.0),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.68,
    bar_r=0.8,
    width=78,
    height=54,
    title="プラグイン本体 (AST/WP境界) vs アプリSCA検出件数",
    title_style=Styles.DarkBold.patch(text_size=9.4),
)
chart.add_series("WP認可・SQLi・Secret", [7, 0, 0, 0], style=Styles.Danger)
chart.add_series("XSS・ABSPATH・Timeout", [0, 5, 2, 0], style=Styles.Warning)
chart.add_series("App CVE (composer不在)", [0, 0, 0, 1], style=Styles.Primary)
chart.draw(xy=(4, 6))

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=8.8),
    metric_width_ratio=0.35,
    spacing=2.8,
)
kpis.add(
    "__return_true",
    "無認証 REST PII 漏洩",
    "/export で全会員メール公開+SQLi",
    icon=phosphor.globe,
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
)
kpis.add(
    "nopriv + SQLi",
    "Admin-AJAX 境界崩壊",
    "search未認証SQLi / purge Nonce不在",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
)
kpis.add(
    "7 / 278 件",
    "Debian 12 OS層 CRIT/HIGH",
    "App CVE 0件 (composer.lock不在)",
    icon=phosphor.warning,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
    icon_style=Styles.Warning,
)
kpis.draw(xy=(85, 6), width=58, height=54, columns=1)

save()
```

## セキュリティゲート（SEC-01〜SEC-05）および WordPress 固有脆弱性の詳細

- **SEC-05（API 認可境界・CSRF・権限昇格）**:
  1. **無認証 REST 会員エクスポート (`includes/rest-endpoints.php:7-12`)**: `GET /wp-json/member-analytics/v1/export` が `'permission_callback' => '__return_true'` で公開されており、未認証の外部攻撃者が `{$wpdb->users}` の `ID, user_login, user_email` を一括取得できる。
  2. **未認証 Admin-AJAX 検索 (`includes/ajax-handlers.php:3,6-15`)**: `wp_ajax_nopriv_map_search_members` が未認証リクエストを受け付け、会員メールアドレスを返却する。
  3. **Admin-AJAX ログ削除の Nonce/権限欠落 (`includes/ajax-handlers.php:4,17-24`)**: `wp_ajax_map_purge_logs` に `check_ajax_referer()` と `current_user_can()` がなく、購読者アカウントや CSRF 罠ページから `wp_map_events` を削除できる。
  4. **購読者権限での設定画面登録と CSRF (`admin/settings-page.php:7-22`)**: `add_options_page()` の第3引数に `'read'`（購読者権限）を指定しており、かつ `check_admin_referer()` なしで `update_option('map_telemetry_url', ...)` と外部 HTTP 送信を実行する。
  5. **全4ファイルの `ABSPATH` ガード不在**: 直接 HTTP リクエストに対する防御が存在しない。
- **SEC-04（CWE-89 SQLi 3箇所 & CWE-79 XSS 4箇所）**: `$wpdb->prepare()` を1箇所も使用しておらず、`includes/rest-endpoints.php:18-19`（`LIKE '%$role_filter%'`）、`includes/ajax-handlers.php:10-12`（`LIKE '%$term%'`）、`includes/ajax-handlers.php:21`（`DELETE ... WHERE category = '$category'`）の3クエリすべてが直接 SQL インジェクション可能である。また `admin/settings-page.php:26,29`（`$_GET['tab']`）、`includes/ajax-handlers.php:22`（`$_POST['category']`）、`member-analytics-portal.php:20-21`（`$_GET['badge_label']`）の計4箇所で未エスケープ出力による反射型 XSS が成立する。
- **SEC-03（ハードコード秘密鍵）& SEC-01（Trivy スキャン）**: `includes/rest-endpoints.php:3` に `$map_webhook_secret = 'whsec_[REDACTED]'` が平文でハードコードされている。Trivy スキャンでは `composer.lock` 不在のため `app_vuln_counts=0` だが、検証用 Debian 12.15 ベースイメージ OS 層で `CRITICAL: 7`（`CVE-2026-6653` `libxml2` CVSS 9.8、`CVE-2023-45853` `zlib1g` CVSS 9.8、`CVE-2025-7458` `libsqlite3-0` CVSS 9.1 等）・`HIGH: 278`（`CVE-2026-111497` `libbrotli1` -> 修正版 `1.0.9-2+deb12u1` 等、総計 `2,910` 件）が検出された。

```drawlib file=security_boundary_details_table.png caption="WordPressエンドポイント攻撃面・CWE危険シンク・秘密鍵・Trivyスキャン統合マトリクス"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=112, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.3),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["ゲート / 深刻度", "識別子・CWE", "対象エンドポイント / 箇所", "攻撃面・脆弱性メカニズム", "必須緩和・修正策"],
    [
        "SEC-05 + 04\n[CRITICAL]",
        "Broken Auth +\nCWE-89 SQLi",
        "GET /wp-json/member-\nanalytics/v1/export",
        "permission_callback='__return_true'\nで会員PII露出 + role_filter SQL結合",
        "current_user_can('list_users')\n+ wpdb->prepare + esc_like",
    ],
    [
        "SEC-05 + 04\n[CRITICAL]",
        "Unauth AJAX +\nCWE-89 SQLi",
        "POST admin-ajax.php\n?action=map_search_members",
        "wp_ajax_nopriv 未認証公開 +\nPOST['term'] 生SQL結合・PII返却",
        "nopriv廃止・check_ajax_referer\n・権限検査・wpdb->prepare",
    ],
    [
        "SEC-05 + 04\n[CRITICAL]",
        "CSRF / SQLi +\nCWE-79 XSS",
        "POST admin-ajax.php\n?action=map_purge_logs",
        "Nonce/権限検査欠落 + wp_map_events\nDELETE SQLi + POST['category'] XSS",
        "check_ajax_referer + manage_options\n+ wpdb->prefix + prepare",
    ],
    [
        "SEC-05\n[CRITICAL]",
        "Privilege Esc\n+ CSRF + SSRF",
        "admin/settings-page.php\n:10-21 (cap='read')",
        "購読者権限で設定アクセス・Nonce不在\nで update_option と外部HTTP送信",
        "capability='manage_options' +\nwp_nonce_field / check_admin_referer",
    ],
    [
        "SEC-03\n[CRITICAL]",
        "Hardcoded Key\n(OWASP ASVS)",
        "includes/rest-endpoints\n.php:3",
        "map_webhook_secret に署名秘密鍵\n(whsec_[REDACTED]) を平文直書き",
        "既存キー失効・ローテーション・\nwp-config定数 + hash_equals検証",
    ],
    [
        "SEC-04\n[HIGH]",
        "CWE-79 XSS\n(Admin & Public)",
        "settings-page:26,29 /\nportal.php:20-21",
        "GET['tab'] とショートコードの\nGET['badge_label'] 未エスケープ出力",
        "sanitize_key / sanitize_text_field\n+ esc_html / esc_attr 適用",
    ],
    [
        "SEC-05\n[HIGH]",
        "Direct Access\n(No ABSPATH)",
        "全4 PHPファイル先頭\n(portal/rest/ajax/admin)",
        "if (!defined('ABSPATH')) exit; 不在で\n直接URL実行時にパス漏洩リスク",
        "全4ファイル先頭に ABSPATH 定数\nガードを必須配置",
    ],
    [
        "SEC-01\n[LOW / OS]",
        "Trivy 0.69.3\nSCA & OS Scan",
        "composer不在 / Debian\n12.15 (image.tar)",
        "App CVE 0件(lock不在) / OS層 CRIT 7\n・HIGH 278 (libxml2, zlib1g, brotli)",
        "composer.lock 導入によるSCA有効化\n・最小PHP 8.3+ ベースイメージ更新",
    ],
]
tbl.draw_flexible(
    xy=(3, 109),
    column_widths=[19, 21, 28, 38, 34],
    row_heights=[7.2] + [12.2] * 8,
    data=rows,
)

save()
```
