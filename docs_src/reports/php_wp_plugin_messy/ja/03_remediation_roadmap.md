# 3. 推奨改善ロードマップ

是正作業は厳格なリスク優先順位で進める必要があります。**P0** で即座に悪用可能なリモート攻撃経路（ハードコード秘密鍵、SQLi、XSS、CSRF、認可不備、直接アクセス）を遮断し、**P1** でタイムアウト付き HTTP I/O、PHP 8.2+ 厳格型・Composer PSR-4 化および PHPUnit セキュリティ回帰テストを整備し、**P2** で CI/CD ガバナンスとドキュメントを定着させます。

```drawlib align=center code=fold file=remediation_roadmap.png caption="Member Analytics Portal 向け P0 -> P1 -> P2 段階的是正ロードマップ"
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

## スコア改善見込みと施策構成

緊急対応 `P0` の 4 施策とモダナイゼーション・テスト基盤構築 `P1` の 4 施策を実行することで、低評価の 4 軸（`Security`・`Documentation`・`Typing`・`Testing`）が大幅に改善し、総合評価はグレード C（**60/100**）からグレード A/B 水準へ引き上がります。

```drawlib align=center code=fold file=remediation_impact_matrix.png caption="低評価軸における現状 vs. 是正後目標スコアとアクションプラン優先度分布"
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

## アクションプラン・トレーサビリティマトリクス（`P0 -> P1 -> P2`）

`action_plan` の優先順位付き 8 項目と推奨 `P2` ガバナンス施策について、対象ファイル・期待効果・関連ルール / CWE との対応を以下に整理します。

| # | 優先度 | 施策タイトル・カテゴリ | 対象ファイル | 期待される改善効果 | 関連ルール / CWE |
| :-: | :-: | :--- | :--- | :--- | :--- |
| 1 | **P0** | **`ABSPATH` ガード追加とショートコード出力エスケープ**（`security`） | `member-analytics-portal.php` | 公開ショートコード `[member_analytics_badge]` の反射型 XSS と直接スクリプト実行を排除。 | `common/security` |
| 2 | **P0** | **REST・AJAX・Admin 全ハンドラの SQLi・XSS・CSRF・認可不備解消**（`security`） | `includes/rest-endpoints.php`, `includes/ajax-handlers.php`, `admin/settings-page.php`, `member-analytics-portal.php` | HIGH `CWE-89`/`CWE-79` シンク全 5 件、未認証 PII 流出、破壊的ログ削除を一括無力化。 | `php/frameworks/wordpress`, `common/security_vulnerability`, `CWE-89`, `CWE-79`, `CWE-352`, `CWE-862` |
| 3 | **P0** | **CWE-89 SQLi・CWE-79 XSS・秘密鍵・未認証エンドポイントの完全是正**（`security`） | `includes/rest-endpoints.php`, `includes/ajax-handlers.php`, `admin/settings-page.php`, `member-analytics-portal.php` | リモート SQL インジェクション、`wp_users` 情報漏洩、任意ログ削除および XSS リスクを解消。 | `common/security_vulnerability`, `SEC-03`, `SEC-04`, `SEC-05`, `CWE-89`, `CWE-79` |
| 4 | **P0** | **ハードコード `$map_webhook_secret`（`<REDACTED_SECRET>`）削除と外部化**（`security`） | `includes/rest-endpoints.php` | ソースコード内の CRITICAL 認証情報漏洩を解消し、鍵ローテーションおよび環境変数/`wp-config.php` 管理へ移行。 | `common/security`, `common/supply_chain` |
| 5 | **P1** | **`@file_get_contents` の `wp_remote_get` 置換と `print_r` 削除**（`code_quality`） | `admin/settings-page.php`, `includes/rest-endpoints.php` | PHP ワーカーのスレッドハング、サイレントエラー隠蔽、および `?debug` デバッグ漏洩を排除。 | `common/production_readiness`, `common/twelve_factor` |
| 6 | **P1** | **Composer PSR-4 パッケージ化・PHP 8.2+ 対応・CI ガバナンス導入**（`dependencies`） | `member-analytics-portal.php` | EOL PHP 7.4 の生 PHP 構成から、サポート対象 PHP 8.2+/8.3+ および Composer サプライチェーン管理へ移行。 | `php/dependencies`, `php/modern_stack`, `common/supply_chain` |
| 7 | **P1** | **PHPUnit + WP_Mock/Brain Monkey セキュリティ回帰テストと PCOV 計測導入**（`testing`） | `member-analytics-portal.php`, `includes/rest-endpoints.php`, `includes/ajax-handlers.php`, `admin/settings-page.php` | 権限検証・Nonce・`$wpdb->prepare()`・`esc_html()` の自動回帰テストとカバレッジ計測を確立。 | `common/runtime_verification` |
| 8 | **P1** | **PHP 8.2+ `strict_types`・PSR-4 クラス化・`wp_remote_get`・`wp_enqueue_script` 化**（`typing`） | `member-analytics-portal.php`, `admin/settings-page.php` | 暗黙型変換、タイムアウト無指定 HTTP 呼び出し、ハードコード `<script src=...>` を排除。 | `php/typing`, `php/code_quality`, `php/modern_stack`, `php/frameworks/wordpress` |
| 9 | **P2** | **`README.md`・PHPDoc・`.gitignore`・`LICENSE`・`SECURITY.md`・GitHub Actions 整備**（`governance`） | `README.md`, `.github/workflows/*`, `composer.json` | 残存する `common/documentation`・`common/git_workflow`・`common/supply_chain` ギャップを解消。 | `common/documentation`, `common/git_workflow`, `common/supply_chain` |
