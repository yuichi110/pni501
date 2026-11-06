# PNI ソフトウェア健全性診断レポート

本レポートは、注文作成（数量10件以上の10%ボリュームディスカウント自動適用）・直近注文照会・パラメータ化 PDO SQLite 永続化・定数時間 HMAC-SHA256 Webhook 署名検証を担う厳格型 PHP 8.3 API マイクロサービス **`acme/order-fulfillment-api` (`v1.0.0`)** に対して、PNI ステートフル監査ワークフロー `php_api_laravel_clean`（Composer / 供給網ガバナンス検査、PHP AST 静的解析、3側面アーキテクチャ記録、隔離 Docker コンテナ上でのクリーンビルド・`php -l` 構文検査・オフライン PHPUnit + PCOV 実測カバレッジ・`/up` 起動スモーク検証、Trivy 脆弱性・IaC・秘密情報スキャン、および `.pni/pentests/` による動的Webペネトレーションテスト）を実行した包括的診断結果である。

```drawlib file=cover_hero_scorecard.png caption="acme/order-fulfillment-api (v1.0.0) PNI 総合健全性スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

panel = Panel(
    "acme/order-fulfillment-api v1.0.0 — PNI 健全性診断スコアカード",
    "Run: wf-42f8fbd7",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
    description_style=Styles.White.patch(text_size=9.5),
    icon=phosphor.shield_check,
    icon_style=Styles.White,
    header_height=11.5,
)
panel.draw(xy=(3, 3), width=140, height=58)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Neutral.patch(text_size=9.5),
    accent_style=Styles.Primary,
    icon_style=Styles.Primary,
    metric_width_ratio=0.35,
    spacing=3.5,
)
kpis.add(
    "94 / 100",
    "総合スコア (Grade S)",
    "型98 / 品質96 / 設計・検証95 / 保安91",
    icon=phosphor.chart_bar,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=14.0),
    icon_style=Styles.Success,
)
kpis.add(
    "PHP 8.3",
    "対象言語・マイクロサービス",
    "Composer PSR-4 / PDO SQLite (252 LOC)",
    icon=phosphor.terminal_window,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    icon_style=Styles.Primary,
)
kpis.add(
    "12 / 17",
    "ルール適合 (PASS)",
    "PASS 12 / WARN 4 / N/A 1 (FAIL 0)",
    icon=phosphor.check_circle,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=14.0),
    icon_style=Styles.Success,
)
kpis.add(
    "12 件",
    "検出指摘 (Findings)",
    "CRIT 0 / HIGH 0 / MED 1 / LOW 6 / INFO 5",
    icon=phosphor.magnifying_glass,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
    icon_style=Styles.Primary,
)
kpis.draw(xy=(7, 6.5), width=132, height=40, columns=2)

save()
```

## 診断メタデータ概要

- **対象プロジェクト**: `acme/order-fulfillment-api` (`v1.0.0` / 対象ルート: `examples/php/api_laravel_clean`)
- **対象言語・ビルド基盤**: `php` (`^8.3`, Composer `2.6` PSR-4, `ext-pdo` / `pdo_sqlite`, Laravel 11.x ルーティング規約, PHPUnit `10.5.66` + PCOV `1.0.12`)
- **診断ワークフロー / Run ID**: `php_api_laravel_clean` / `wf-42f8fbd7`（全8監査ディメンション）
- **評価実施日時**: `2026-10-24T14:45:51.621334+00:00`
- **総合スコア・グレード**: **94 / 100 (Grade S)**
- **エンジニアリングルール適合率**: `12 / 17` ルール PASS（`WARN`: 4件、`NOT_APPLICABLE`: 1件、`FAIL`: **0件**）
