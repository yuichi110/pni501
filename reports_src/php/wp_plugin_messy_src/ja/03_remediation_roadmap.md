# 3. 推奨する改善ロードマップ

検出された全21件の指摘事項（`CRITICAL` 7件、`HIGH` 7件、`MEDIUM` 6件、`LOW` 1件）を解消し、総合健全性スコアを Grade D (`20`) から本番 WordPress サイトへ安全に導入できる Grade A 水準（`85+`）へ引き上げるため、以下の **Phase 1（P0 緊急止血：認可・CSRF・SQLi・XSS・秘密鍵・ABSPATH 封じ込め） -> Phase 2（P1 構造刷新：Composer/PSR-4・`wp_enqueue_script`・`wp_safe_remote_get` タイムアウト化） -> Phase 3（P1/P2 品質保証：PHP 8.2+ `strict_types=1`・PHPUnit/`WP_UnitTestCase` 自動テスト・ガバナンス整備）** の3フェーズ改善計画を推奨する。

```drawlib file=remediation_priority_roadmap.png caption="3フェーズ推奨改善ロードマップ (Phase 1 P0封じ込め -> Phase 2 基盤近代化 -> Phase 3 型・自動テスト)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=8.9),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    direction="horizontal",
    spacing=3.2,
)
rm.add(
    "Phase 1: P0 脆弱性封じ込め",
    "current_user_can・Nonce検証\nprepare()・esc_html・ABSPATH",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
rm.add(
    "Phase 2: P1 WP基盤・通信刷新",
    "Composer PSR-4・wp_enqueue_script\nwp_safe_remote_get(timeout=3s)",
    badge_text="P1",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
rm.add(
    "Phase 3: P1/P2 型安全・自動検証",
    "PHP 8.2+ strict_types=1・Repository\nWP_UnitTestCase・README/CI整備",
    badge_text="P1-P2",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Primary,
)
rm.draw(xy=(4, 5), width=138, height=48)

save()
```

## フェーズ別実行計画とトレーサビリティ

- **Phase 1 (`P0` — 即時止血：認可・CSRF・SQLi・XSS・シークレット漏洩の完全封じ込め)**: 全4ファイル先頭に `if (!defined('ABSPATH')) { exit; }` を配置し、`includes/rest-endpoints.php` の `'__return_true'` を `current_user_can('list_users')` へ変更、`wp_ajax_nopriv_map_search_members` を廃止、`map_ajax_purge_logs` と `settings-page.php`（`capability => 'manage_options'`）に `check_ajax_referer()` / `check_admin_referer()` を導入する。同時に全3箇所の `$wpdb` クエリを `$wpdb->prepare()` + `{$wpdb->prefix}map_events` へ書き換え、全4箇所の HTML/属性出力に `esc_html()` / `esc_attr()` を適用し、直書き `$map_webhook_secret` を失効・外部注入化する。
- **Phase 2 (`P1` — 短期優先：Composer/PSR-4・WordPress 標準 API 移行・ワーカー枯渇防止)**: `composer.json`（`php: ^8.2`、PSR-4 オートローディング）と `composer.lock` を作成し、`Requires PHP: 8.2` へ引き上げる。管理画面の直書き `<script>` タグを `admin_enqueue_scripts` + `wp_enqueue_script()` に移行し、`@file_get_contents()` を `timeout => 3` 秒・`is_wp_error()` 検査付きの `wp_safe_remote_get()`（または WP-Cron 非同期ジョブ）へ置換、`print_r()` デバッグ出力を除去して PSR-3 構造化ログへ統一する。
- **Phase 3 (`P1/P2` — 中期定着：厳格型宣言・PHPUnit/`WP_UnitTestCase` 自動テスト・ガバナンス確立)**: 全ファイルに `declare(strict_types=1);`・ネイティブ型宣言・PHPDoc を整備して `$wpdb` を Repository クラスへ分離し、PHPUnit 11 + `WP_UnitTestCase` / `WP_Ajax_UnitTestCase` + PCOV によりオフライン（`--network=none`）で 80% 以上のカバレッジを計測する。併せて `README.md`・`LICENSE`・`SECURITY.md`・`.gitignore`・GitHub Actions CI を整備する。

```drawlib file=remediation_action_table.png caption="優先度順 改善アクション計画トレーサビリティマトリクス (P0 -> P1 -> P2 全10施策)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=118, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["優先度", "改善施策タイトル", "対象ファイル", "期待効果 (Expected Impact)", "関連ルール / CWE"],
    [
        "P0",
        "$wpdb->prepare 全SQL化と\nesc_html/esc_attr 遅延エスケープ",
        "全4 PHPファイル",
        "CWE-89 SQLi (3件) と\nCWE-79 XSS (全経路) を根絶",
        "common/security_vulnerability\nCWE-89 / CWE-79",
    ],
    [
        "P0",
        "REST/AJAX/設定画面の権限・\nCSRF Nonce・ABSPATH 全面実装",
        "全4 PHPファイル",
        "未認証PII漏洩・権限昇格・\nCSRFデータ破壊を即時遮断",
        "php/frameworks/wordpress\ncommon/security",
    ],
    [
        "P0",
        "SEC-03/04/05 全脆弱性の一括\n封じ込めとテーブル接頭辞修正",
        "全4 PHPファイル",
        "無認証公開・インジェクション・\n直接ファイル実行を一括解消",
        "common/security_vulnerability\nphp/frameworks/wordpress",
    ],
    [
        "P0",
        "ハードコード Webhook 秘密鍵の\n除去・失効と外部注入化",
        "includes/\nrest-endpoints.php",
        "ソース流出時の Webhook 偽装\n・認証バイパスリスクを排除",
        "common/security\nSEC-03",
    ],
    [
        "P1",
        "wp_safe_remote_get(timeout=3s)\n移行と PSR-3 構造化ログ整備",
        "admin/settings-page.php\nrest-endpoints.php",
        "外部遅延時のPHP-FPM枯渇防止\nと print_r JSON破壊の解消",
        "common/production_readiness\ncommon/twelve_factor",
    ],
    [
        "P1",
        "Composer + PSR-4 導入と\nRequires PHP: 8.2+ への刷新",
        "member-analytics-\nportal.php",
        "composer.lock による決定論的\n管理と EOL PHP 7.4 脱却",
        "php/dependencies\nphp/modern_stack",
    ],
    [
        "P1",
        "PHPUnit + WP_UnitTestCase /\nWP_Ajax 自動テストスイート導入",
        "全4 PHPファイル\n(tests/ 新設)",
        "401/403認可拒否・Nonce検証・\nSQL安全性のCI自動回帰防止",
        "php/testing",
    ],
    [
        "P1",
        "オフライン実行可能な PHPUnit\n+ PCOV カバレッジ検証構築",
        "member-analytics-\nportal.php",
        "RV-02 オフラインテスト合格と\nRV-03 実測網羅率 80%+ 達成",
        "common/runtime_verification\nphp/testing",
    ],
    [
        "P1",
        "PSR-4 Repository 分離・strict_types\n型宣言・wp_enqueue_script 化",
        "全4 PHPファイル",
        "型安全率・PHPDoc率 0%->100%\nと <script> 直書きの解消",
        "php/typing\nphp/code_quality",
    ],
    [
        "P2",
        "README 仕様拡充と LICENSE /\nSECURITY / .gitignore / CI 整備",
        "README.md",
        "オンボーディング改善と\nサプライチェーン監査基準適合",
        "common/documentation\ncommon/supply_chain",
    ],
]
tbl.draw_flexible(
    xy=(3, 115),
    column_widths=[11, 35, 28, 36, 30],
    row_heights=[7.4] + [10.4] * 10,
    data=rows,
)

save()
```
