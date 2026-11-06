# PNI ソフトウェア健全性診断レポート

本レポートは、WordPress 会員分析プラグイン **`Member Analytics Portal` (`wp_plugin_messy` v1.3.0)** に対して、PNI ステートフル監査ワークフロー `php_wp_plugin_messy`（3観点アーキテクチャ記録・PHP/WordPress AST 静的解析・隔離 Docker コンテナによる PHP 8.2 構文および WordPress フック登録スモーク検証・Trivy 脆弱性スキャン）を実行した包括的診断結果である。

```drawlib file=cover_hero_scorecard.png caption="Member Analytics Portal (v1.3.0) PNI 総合健全性スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=52, dpi=150)

panel = Panel(
    "Member Analytics Portal v1.3.0 — PNI 健全性診断スコアカード",
    "Workflow: php_wp_plugin_messy | Run: wf-31a8fefa",
    style=Styles.Neutral,
    header_style=Styles.Danger,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
    description_style=Styles.White.patch(text_size=9.0),
    icon=phosphor.warning,
    icon_style=Styles.White,
    header_height=10.5,
)
panel.draw(xy=(3, 2.5), width=140, height=47)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.DangerBold.patch(text_size=13.4),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Neutral.patch(text_size=9.0),
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
    metric_width_ratio=0.36,
    spacing=2.8,
)
kpis.add(
    "20 / 100",
    "総合スコア (Grade D)",
    "品質26 / 設計24 / テスト18 / 保安10",
    icon=phosphor.chart_bar,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.4),
)
kpis.add(
    "PHP 7.4*",
    "対象言語・構成 (EOL指定)",
    "WordPress Plugin / raw_php (84 LOC)",
    icon=phosphor.code,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=12.6),
    icon_style=Styles.Primary,
)
kpis.add(
    "0 / 17",
    "ルール適合 (PASS)",
    "PASS 0 / WARN 2 / FAIL 14 / N/A 1",
    icon=phosphor.x_circle,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=13.4),
    icon_style=Styles.Warning,
)
kpis.add(
    "21 件",
    "検出指摘 (Findings)",
    "CRIT 7 / HIGH 7 / MED 6 / LOW 1",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.4),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 5.2), width=132, height=32.5, columns=2)

save()
```

## 診断メタデータ概要

- **対象プロジェクト**: `Member Analytics Portal (wp_plugin_messy)` (`v1.3.0` / 対象ルート: `examples/php/wp_plugin_messy`)
- **対象言語・ビルド基盤**: `php`（プラグインヘッダ指定 `Requires PHP: 7.4`、`Requires at least: 5.8`、`composer.json` 不在の `raw_php` 構成）
- **検出フレームワーク**: `wordpress`（WP REST API v1、Admin-AJAX、Shortcode API、Options API、`$wpdb`）
- **診断ワークフロー / Run ID**: `php_wp_plugin_messy` / `wf-31a8fefa`
- **評価実施日時**: `2026-10-24T09:20:09.804814+00:00`
- **総合スコア・グレード**: **20 / 100 (Grade D)**
- **エンジニアリングルール適合率**: `0 / 17` ルール PASS（`FAIL`: 14件、`WARN`: 2件、`NOT_APPLICABLE`: 1件）
