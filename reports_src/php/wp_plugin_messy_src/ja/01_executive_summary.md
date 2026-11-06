# 1. エグゼクティブサマリー

WordPress プラグイン `Member Analytics Portal` (`examples/php/wp_plugin_messy`, v1.3.0) の総合健全性スコアは **20/100 (Grade D)** と診断された。PHP 8.2 隔離コンテナでの `php -l` 構文検証と5フック登録スモークテスト自体は通過するものの、REST API (`/wp-json/member-analytics/v1/export`) の `permission_callback => '__return_true'` による会員 PII 無認証露出、`wp_ajax_nopriv_map_search_members` の未認証 SQL インジェクション、`wp_ajax_map_purge_logs` および設定画面（`capability => 'read'`）の Nonce/権限検証欠落、3箇所の `$wpdb` 生 SQL 文字列結合（`CWE-89`）、4箇所の未エスケープ XSS（`CWE-79`）、Webhook シークレット直書き、全4ファイルの `ABSPATH` ガード不在など、即時悪用可能な致命的脆弱性が集中している。

```drawlib file=exec_radar_summary.png caption="7軸エンジニアリング健全性レーダーと強み・最優先リスク (P0) 要約"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

radar = RadarChart(
    categories=[
        "アーキテクチャ",
        "コード品質",
        "型安全性",
        "テスト健全性",
        "依存関係",
        "セキュリティ",
        "ドキュメント",
    ],
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    scale_text_style=Styles.Neutral.patch(text_size=8.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    min_value=0.0,
    max_value=100.0,
    levels=5,
    radius=18.5,
    title="7軸健全性バランス (Overall: 20 / Grade D)",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)
radar.add_series(
    "wp_plugin_messy",
    [24, 26, 12, 18, 22, 10, 22],
    style=Styles.Danger,
    fill_alpha=0.28,
    line_width=2.2,
)
radar.add_series(
    "推奨基準(80)",
    [80, 80, 80, 80, 80, 80, 80],
    style=Styles.SuccessDashed,
    fill_alpha=0.04,
    line_width=1.4,
)
radar.draw(xy=(3, 4), width=66, height=60)

cards = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.4),
    description_style=Styles.Dark.patch(text_size=8.9),
    badge_shape="rounded_rect",
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=8.8),
    spacing=2.0,
)
cards.add(
    "強み1: PHP 8.2構文 & WP 5フック登録合格",
    "php -l 全4ファイル通過・スタブ環境で正常ロード",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
cards.add(
    "強み2: 小規模84 LOC・CMDi/秘密ファイル0件",
    "循環依存0・CWE-78/502ゼロ・.envコミットなし",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.shield_check,
    icon_style=Styles.Success,
)
cards.add(
    "課題1 [CRIT]: 無認証REST漏洩・nopriv SQLi",
    "__return_trueで会員PII露出・$wpdb生SQL結合3件",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.x_circle,
    icon_style=Styles.Danger,
)
cards.add(
    "課題2 [CRIT]: Nonce/権限欠落・XSS・秘密直書き",
    "read権限昇格・CSRF・未エスケープXSS・whsec直書き",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
cards.draw(xy=(72, 4), width=71, height=60)

save()
```

## 7軸評価サマリーと主要診断結論

- **全7軸が基準値（80点）を大幅に下回る緊急リスク集中プロファイル**: セキュリティ（`10`）・型安全性（`12`）・テスト健全性（`18`）が危機的水準にあり、依存関係（`22`）・ドキュメント（`22`）・アーキテクチャ（`24`）・コード品質（`26`）を含め、WordPress プラグイン審査基準（Plugin Check / OWASP ASVS）に対して抜本的な改修を要する。
- **最低スコア評価ステップ（昇順）**: `php_test_audit`（`5/100`：自動テスト0件）、`security_vulnerability_audit`（`8/100`：無認証 REST/AJAX SQLi・XSS・秘密鍵直書き）、`php_ast_audit`（`14/100`：`strict_types=1` 0%・WordPress 規約違反16件）が総合スコアを大きく押し下げている。

```drawlib file=exec_runtime_security_kpis.png caption="動的プラグイン検証 & Trivy セキュリティ監査ヘッドライン指標"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

panel = Panel(
    "動的WordPressプラグイン検証 & Trivy / AST セキュリティヘッドライン",
    "Docker PHP 8.2 Harness (php -l + WP Hook Stub) / Trivy 0.69.3",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.6),
    description_style=Styles.White.patch(text_size=9.0),
    header_height=11.0,
)
panel.draw(xy=(3, 3), width=140, height=54)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Neutral.patch(text_size=8.9),
    metric_width_ratio=0.36,
    spacing=3.0,
)
kpis.add(
    "PASSED (5)",
    "構文検査 & WPフック起動",
    "php -l 0.80s / 5フック登録 0.59s",
    icon=phosphor.check_circle,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=12.8),
    icon_style=Styles.Success,
)
kpis.add(
    "0 / N/A",
    "PHPUnit単体テスト・網羅率",
    "テスト0件・PCOV実測カバレッジ未計測",
    icon=phosphor.warning,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=13.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "3 SQLi / 4 XSS",
    "AST危険シンク & 認可破綻",
    "__return_true・nopriv・Nonce欠落",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=12.2),
    icon_style=Styles.Danger,
)
kpis.add(
    "0 / 285 CVE",
    "Trivy CVE (App / OS高深刻)",
    "composer不在 / Debian OS CRIT7・HIGH278",
    icon=phosphor.shield_warning if hasattr(phosphor, "shield_warning") else phosphor.warning,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=11.6),
    icon_style=Styles.Warning,
)
kpis.draw(xy=(7, 6), width=132, height=37.5, columns=2)

save()
```

## エグゼクティブ結論

- **強み (Verified Strengths)**: 標準プラグインヘッダを備え、PHP 8.2 コンテナ上での `php -l` 構文検査（`0.80s`）と WordPress フック登録スモークテスト（`0.59s`、5フック登録）が通過している。またコード全体が `4` ファイル・`84` LOC と小規模で、OS コマンド実行（`CWE-78`）・危険な `unserialize`（`CWE-502`）・`.env`/秘密鍵ファイルの誤コミットも `0` 件であるため、短期間で完全な改修が可能である。
- **最優先アクション (P0 Priorities)**: 本番 WordPress サイトへの有効化前に、(1) 全4ファイルへの `ABSPATH` ガード追加、(2) REST `/export` の `current_user_can('list_users')` 化・`wp_ajax_nopriv_map_search_members` 廃止・設定画面の `'manage_options'` 化と `check_ajax_referer` / `check_admin_referer` 強制、(3) 全3クエリの `$wpdb->prepare()` パラメータ化と全出力の `esc_html()` / `esc_attr()` 遅延エスケープ、(4) `includes/rest-endpoints.php:3` のハードコード Webhook シークレット失効・外部化を即時断行すべきである。
