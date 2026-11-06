# PNI ソフトウェア健全性診断レポート

本レポートは、レガシー請求処理 Spring Boot API サービス **`legacy-billing` (`0.0.1-SNAPSHOT`)** に対して、PNI ステートフル監査ワークフロー `java_api_spring_messy`（3観点アーキテクチャ記録・Java AST 静的解析・隔離 Docker コンテナによる Maven ビルド/テスト検証・Trivy 脆弱性/IaC スキャン・隔離ループバック動的 Web ペネトレーション監査）を実行した包括的診断結果である。

```drawlib file=cover_hero_scorecard.png caption="legacy-billing (0.0.1-SNAPSHOT) PNI 総合健全性スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

panel = Panel(
    "legacy-billing v0.0.1-SNAPSHOT — PNI 健全性診断スコアカード",
    "Workflow: java_api_spring_messy | Run: wf-da941741",
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
    "23 / 100",
    "総合スコア (Grade D)",
    "型35 / 設計29 / テスト14 / 保安17",
    icon=phosphor.chart_bar,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
)
kpis.add(
    "Java 1.8*",
    "対象言語・構成 (不整合)",
    "Maven / Spring Boot LATEST (187 LOC)",
    icon=phosphor.code,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    icon_style=Styles.Primary,
)
kpis.add(
    "0 / 15",
    "ルール適合 (PASS)",
    "PASS 0 / WARN 1 / FAIL 14",
    icon=phosphor.x_circle,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "24 件",
    "検出指摘 (Findings)",
    "CRIT 6 / HIGH 12 / MED 4 / LOW 2",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 6.5), width=132, height=40, columns=2)

save()
```

## 診断メタデータ概要

- **対象プロジェクト**: `legacy-billing` (`0.0.1-SNAPSHOT` / 対象ルート: `examples/java/api_spring_messy`)
- **対象言語・ビルド基盤**: `java` (`pom.xml` 指定 `1.8`、Apache Maven、`spring-boot-starter-web:LATEST`、`junit:4.13.2`)
- **診断ワークフロー / Run ID**: `java_api_spring_messy` / `wf-da941741`
- **評価実施日時**: `2026-10-24T14:59:08.282916+00:00`
- **総合スコア・グレード**: **23 / 100 (Grade D)**
- **エンジニアリングルール適合率**: `0 / 15` ルール PASS（`FAIL`: 14件、`WARN`: 1件）
