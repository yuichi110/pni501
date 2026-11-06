# PNI ソフトウェア健全性診断レポート

本レポートは、倉庫在庫引当およびサプライヤー自動補充通知を担う Spring Boot 3.3 + Java 21 マイクロサービス **`inventory-service` (`v1.1.0`)** に対して、PNI ステートフル監査ワークフロー `java_api_spring_clean`（ビルド・供給網検査、Java AST 静的解析、3側面アーキテクチャ記録、隔離コンテナでのマルチステージビルド・オフライン JUnit 5 / JaCoCo カバレッジ計測・起動スモーク検証、Trivy 脆弱性・IaC・秘密情報スキャン、および `.pni/pentests/` による動的 Web ペネトレーションテスト `web_pentest`）を実行した包括的診断結果である。

```drawlib file=cover_hero_scorecard.png caption="inventory-service (v1.1.0) PNI 総合健全性スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

panel = Panel(
    "inventory-service v1.1.0 — PNI 健全性診断スコアカード",
    "Run: wf-056bf7c2",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=11.5),
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
    "78 / 100",
    "総合スコア (Grade B)",
    "型92 / 設計86 / 文書86 / 保安58",
    icon=phosphor.chart_bar,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
)
kpis.add(
    "Java 21",
    "対象言語・マイクロサービス",
    "Spring Boot 3.3.4 / Maven (180 LOC)",
    icon=phosphor.terminal_window,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.Success,
)
kpis.add(
    "4 / 15",
    "ルール適合 (PASS)",
    "PASS 4 / WARN 10 / FAIL 1",
    icon=phosphor.check_circle,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "18 件",
    "検出指摘 (Findings)",
    "CRIT 1 / HIGH 2 / MED 9 / LOW 6",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 6.5), width=132, height=40, columns=2)

save()
```

## 診断メタデータ概要

- **対象プロジェクト**: `inventory-service` (`v1.1.0` / 対象ルート: `examples/java/api_spring_clean`)
- **対象言語・ビルド基盤**: `java` (`21`, Apache Maven `pom.xml`, Spring Boot `3.3.4` Web + Validation, JUnit Jupiter `5.10.3`)
- **診断ワークフロー / Run ID**: `java_api_spring_clean` / `wf-056bf7c2`
- **評価実施日時**: `2026-10-24T14:47:03.897244+00:00`
- **総合スコア・グレード**: **78 / 100 (Grade B)**
- **エンジニアリングルール適合率**: `4 / 15` ルール PASS（`WARN`: 10件、`FAIL`: 1件）
- **動的ペネトレーション検証 (`web_pentest`)**: `passed`（`16` プローブ実行：`12` PASS / `3` FAIL / `1` SKIP、CRITICAL・HIGH 脆弱性 `0` 件）
