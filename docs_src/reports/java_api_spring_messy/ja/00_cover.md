# PNI ソフトウェア健全性診断レポート: `legacy-billing`

**監査対象リポジトリ**: `examples/java/api_spring_messy` (`java_api_spring_messy`)  
**言語・技術スタック**: Java 1.8（宣言値） / Spring Boot Web Starter (`LATEST`) / `javax.servlet-api` 4.0.1 / JUnit 4.13.2 / Maven

```drawlib align=center code=hide file=cover_scorecard.png caption="legacy-billing の PNI501 ソフトウェア健全性診断スコアカード（グレード C・66/100）"
from drawlib.canvas import save, setup
from drawlib.shapes import rectangle
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text
from drawlib.utils import draw_pni_logo

setup(width=146, height=72, dpi=150)

# Outer report cover frame with Google-styled dark blue header band
frame = Panel(
    "",
    style=Styles.Neutral.patch(shape_r=2.5),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=13.5),
    header_variant="filled",
    header_height=15.0,
)
frame.draw((4, 4), width=138, height=64)

# Left-aligned cover title & subtitle inside dark header, leaving right side clear for emblem
text(
    (8.5, 63.2),
    "PNI501 Software Health Diagnostic Report",
    style=Styles.WhiteBold.patch(text_size=13.5, halign="left"),
)
text(
    (8.5, 57.2),
    "legacy-billing  |  examples/java/api_spring_messy  |  Workflow: java_api_spring_messy (wf-8177454c)",
    style=Styles.White.patch(text_size=9.5, halign="left"),
)

# Official PNI501 emblem centered vertically in the right side of the dark header
draw_pni_logo((134.5, 60.5), width=9.0, dark=True)

# Left Hero Score & Grade card
hero_style = Styles.WarningNeutral.patch(
    shape_r=2.5,
    shape_line_color=Colors.GoogleOrange,
    shape_line_width=2.0,
)
rectangle((25.5, 29.0), width=35.0, height=40.0, style=hero_style)
rectangle(
    (25.5, 44.0),
    width=27.0,
    height=5.2,
    style=Styles.WarningFlat.patch(shape_r=2.0),
    text="OVERALL SCORE",
    text_style=Styles.WhiteBold.patch(text_size=9.5),
)
text((25.5, 32.5), "66 / 100", style=Styles.DarkBold.patch(text_size=18.0))
text((25.5, 22.5), "Grade C", style=Styles.WarningBold.patch(text_size=14.0))
text(
    (25.5, 14.0),
    "Baseline 76 (-10 AI Adj.)\n15 FAIL | 1 WARN | 0 PASS",
    style=Styles.Dark.patch(text_size=9.5),
)

# Right 2x2 executive headline KPIs
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="top_stack",
    spacing=2.8,
)
kpis.add(
    "0 / 16",
    "Rule Pass Rate",
    "15 FAIL, 1 WARN (0 PASS)",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=13.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "19 Findings",
    "14 Consolidated Locations",
    "6 CRIT | 8 HIGH | 4 MED | 1 LOW",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.0),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "BUILD FAIL",
    "Docker Maven Runtime",
    "Boot 4.2.0 (61.0) vs JDK 8 (52.0)",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=12.5),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "1 CRIT CVE",
    "Trivy SCA & IaC Posture",
    "CVE-2022-22965 + 3 Docker IaC",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.draw((46.5, 9.0), width=91.5, height=40.0, columns=2)

save()
```

---

## 監査メタデータ・証跡プロベナンス

| 項目 | 値 |
| :--- | :--- |
| **プロジェクト名** | `legacy-billing` (`com.example:legacy-billing:0.0.1-SNAPSHOT`) |
| **対象ルート** | `examples/java/api_spring_messy` |
| **主言語・規模** | `java`（Maven、本番コード 6 ファイル / 187 LOC、テスト 1 ファイル） |
| **ワークフロー ID・スコープ** | `java_api_spring_messy`（`category=audit`, `scope=repo`） |
| **実行 ID (`Run ID`)** | `wf-8177454c` |
| **評価日時 (UTC)** | `2026-11-22T11:29:02.337544+00:00` |
| **Git リビジョン** | `main@d1e02277 (dirty)` |
| **総合スコア・グレード** | **66 / 100（グレード C）** *（決定論的ベースライン: 76、AI 定性調整: -10）* |
| **ルール準拠率** | `0 / 16` ルール合格（`15 FAIL`、`1 WARN`、`0 PASS`） |
| **検出事項サマリー** | 計 `19` 件（決定論的 `7` 件・AI 定性 `12` 件）／統合済み `14` 箇所（`CRITICAL 6`、`HIGH 8`、`MEDIUM 4`、`LOW 1`） |
| **後続連携計画** | Clean Architecture 移行実行計画 `java_api_spring_messy_migration` へ直接連携 |

> **監査範囲と機密保護について**: 本レポートは、PNI501 Workflow v2 の下で実行された決定論的 AST 解析（`tree-sitter`）、マニフェスト診断、コンテナ化された Maven/Docker ビルド・ランタイム検証、Trivy ファイルシステム SCA/IaC スキャン、および動的 HTTP ペネトレーション検証準備の結果を統合したものです。ソースコード上で検出された認証情報リテラルはすべて `<REDACTED_SECRET>` としてマスク済みです。
