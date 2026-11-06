# PNI ソフトウェア健全性診断レポート

本レポートは、Composer・フレームワーク不使用の手続き型レガシー素PHP EC・管理アプリケーション **`legacy_shop_messy` (`v0.0.0`, `raw_php`)** に対して、PNI ステートフル監査ワークフロー `php_legacy_shop_messy`（3観点アーキテクチャ記録・PHP AST 静的解析・隔離 Docker コンテナによるビルド/構文/起動スモーク検証・Trivy 脆弱性/IaC/Secret スキャン・`.pni/pentests/` 隔離ループバック動的 Web ペネトレーションテスト）を実行した包括的診断結果である。

```drawlib file=cover_hero_scorecard.png caption="legacy_shop_messy (raw_php) PNI 総合健全性スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

panel = Panel(
    "legacy_shop_messy — PNI 健全性診断スコアカード",
    "Workflow: php_legacy_shop_messy | Run: wf-1abc5e13",
    style=Styles.Neutral,
    header_style=Styles.Danger,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
    description_style=Styles.White.patch(text_size=9.2),
    icon=phosphor.warning,
    icon_style=Styles.White,
    header_height=11.5,
)
panel.draw(xy=(3, 3), width=140, height=58)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Neutral.patch(text_size=9.2),
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
    metric_width_ratio=0.36,
    spacing=3.5,
)
kpis.add(
    "15 / 100",
    "総合スコア (Grade D)",
    "設計18 / 型12 / 試験10 / 保安5",
    icon=phosphor.chart_bar,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
)
kpis.add(
    "PHP 7.4*",
    "対象言語・構成 (EOL)",
    "素PHP raw_php / Composerなし (107 LOC)",
    icon=phosphor.code,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    icon_style=Styles.Primary,
)
kpis.add(
    "0 / 17",
    "ルール適合 (PASS)",
    "PASS 0 / FAIL 15 / N/A 2",
    icon=phosphor.x_circle,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "33 件",
    "検出指摘 (Findings)",
    "CRIT 10 / HIGH 12 / MED 9 / LOW 2",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 6.5), width=132, height=40, columns=2)

save()
```

## 診断メタデータ概要

- **対象プロジェクト**: `legacy_shop_messy` (`v0.0.0` / 対象ルート: `examples/php/legacy_shop_messy`)
- **対象言語・ビルド基盤**: `php` (`raw_php`：Composer 未導入、`Dockerfile` は EOL の `php:7.4-apache` + `ext-mysqli`、本番6ファイル・計 `107` LOC)
- **診断ワークフロー / Run ID**: `php_legacy_shop_messy` / `wf-1abc5e13`
- **評価実施日時**: `2026-10-24T15:02:00.000000+00:00`
- **総合スコア・グレード**: **15 / 100 (Grade D)**
- **エンジニアリングルール適合率**: `0 / 17` ルール PASS（`FAIL`: 15件、`NOT_APPLICABLE`: 2件［Laravel / WordPress］）
- **動的Webペネトレーションテスト (`web_pentest`)**: `FAILED`（全`19`プローブ中 `9` PASS / `10` FAIL：`CRITICAL: 2`［無認証RCE `PNI_RCE_CANARY_8842`・マジックハッシュ `'240610708'` 管理者突破］、`HIGH: 4`、`MEDIUM: 2`、`LOW: 2`）
