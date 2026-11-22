# 1. エグゼクティブサマリー

`order-dispatch` は、Python 3.11+ と FastAPI / Pydantic v2 を用いたクリーンなマイクロサービスの基準実装として **グレード S（94/100）** を達成しました。型安全性・インポート衛生・Google スタイル docstring カバレッジのすべてで 100% を記録し、循環依存ゼロの厳格な 4 層クリーンアーキテクチャ、オフライン Docker テスト `4/4` 全件合格（行カバレッジ `85.2%`・`/healthz` ASGI 起動成功）、宣言済みアプリ依存の CVE ゼロ、および SHA 固定の OpenSSF CI ガバナンスを備えています。一方で、ライブ HTTP DAST と Trivy コンテナイメージ検査により、本番投入に向けた 4 つの具体的な強化項目が特定されました。すなわち、`/v1/orders` への OAuth2/JWT 認証追加（`CWE-306`）、`python:3.12.6-slim-bookworm` ベースイメージの更新および `pip` を除いたマルチステージビルド化と `HEALTHCHECK` 追加、本番環境での HTTP セキュリティヘッダー付与と `/openapi.json` 非公開化、そして `TestClient` / `MockTransport` による分岐カバレッジの `62.5%` から `80%` 以上への引き上げです。

```drawlib align=center code=fold file=health_radar.png caption="7 軸エンジニアリング健全性レーダー（グレード S 基準 90 との比較）および主要 KPI"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=68, dpi=150)

radar = RadarChart(
    categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Documentation",
    ],
    axis_line_style=Styles.MutedThin,
    radius=21.0,
    min_value=0.0,
    max_value=100.0,
    levels=5,
    grid_shape="polygon",
    axis_text_style=Styles.DarkBold.patch(text_size=10.0),
    grid_style=Styles.MutedDashedThin,
    scale_text_style=Styles.Transparent,
    value_text_style=Styles.PrimaryBold.patch(text_size=9.8),
    value_format="{:.0f}",
)
radar.add_series(
    "Final Score",
    [96, 98, 100, 90, 95, 84, 98],
    style=Styles.PrimaryFlat,
    fill_alpha=0.26,
    line_width=2.2,
    point_size=0.9,
)
radar.add_series(
    "Grade S Bar (90)",
    [90, 90, 90, 90, 90, 90, 90],
    style=Styles.SuccessDashed,
    fill_alpha=0.0,
    line_width=1.4,
    point_size=0.0,
)
radar.draw((42.0, 37.5), align="center")
radar.draw_legend(
    (11.0, 4.0),
    text_style=Styles.Dark.patch(text_size=10.0),
    orientation="horizontal",
    item_gap=7.0,
)

text((113.0, 62.0), "Headline Diagnostic Telemetry", style=Styles.DarkBold.patch(text_size=11.5))

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.DarkBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
kpis.add(
    "94 / 100",
    "Overall Grade S",
    "12/16 Rules Passed",
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=14.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.add(
    "85.2%",
    "Line Coverage",
    "4/4 Tests | 62.5% Br",
    accent_style=Styles.SuccessFlat,
)
kpis.add(
    "0 CRIT/HIGH",
    "Declared App CVEs",
    "6 pip@24.2 + 612 OS",
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "15 / 19",
    "Live DAST Probes",
    "3 Findings (0 Crit/Hi)",
    accent_style=Styles.SecondaryFlat,
)
kpis.draw((84.0, 8.0), width=59.0, height=50.0, columns=2)

save()
```

## 主要な強みと本番運用に向けた優先リスク

本コードベースは、静的保守性・厳格な型付け・コンテナビルド再現性・CI サプライチェーン統制のいずれも極めて高い水準にあります。検出された `MEDIUM` 3 件および `LOW` 9 件（ビルド専用 `pip@24.2` CVE 5 件の AI トリアージ再分類後）は、アーキテクチャの構造的欠陥ではなく、すべて配備境界のセキュリティ強化と HTTP 境界テスト拡充に集中しています。

```drawlib align=center code=fold file=strengths_and_risks.png caption="エグゼクティブ対比：検証済みの強み vs. 優先すべき本番強化リスク"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

left_panel = Panel(
    "Verified Engineering Strengths",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.SuccessNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=11.5),
    header_height=9.0,
)
left_panel.draw((2.0, 2.0), width=69.0, height=64.0)

strengths = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    spacing=2.2,
)
strengths.add(
    "Strict 4-Layer Acyclic Architecture",
    "api -> services -> domain + infra; 0 cycles, pure domain",
    badge_text="ARCH",
)
strengths.add(
    "100% Typing, Imports & Docstrings",
    "py.typed, zero Any, 0 complex functions across 435 LOC",
    badge_text="CODE",
)
strengths.add(
    "OpenSSF CI & Non-Root Governance",
    "SHA-pinned Actions, contents: read, uv.lock, uid 10001",
    badge_text="CI",
)
strengths.add(
    "Offline Docker Build & 4/4 Tests",
    "85.2% line cov (100% core), clean /healthz ASGI boot",
    badge_text="TEST",
)
strengths.draw((5.0, 5.0), width=63.0, height=50.0)

right_panel = Panel(
    "Top Production Hardening Targets",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.WarningNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=11.5),
    header_height=9.0,
)
right_panel.draw((75.0, 2.0), width=69.0, height=64.0)

risks = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    spacing=2.8,
)
risks.add(
    "Unauthenticated /v1/orders (CWE-306)",
    "POST /v1/orders -> HTTP 201 (routes.py:73 TODO)",
    badge_text="MED",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
)
risks.add(
    "Aged Debian 12.7 Base & pip@24.2",
    "9 CRIT/158 HIGH OS, 6 pip CVEs, no HEALTHCHECK",
    badge_text="MED",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
)
risks.add(
    "DAST Headers, OpenAPI & Branch Cov",
    "CWE-693/200 gaps; routes/webhook 62.5% branch",
    badge_text="LOW",
    badge_style=Styles.SecondaryFlat,
)
risks.draw((78.0, 6.0), width=63.0, height=48.0)

save()
```

## 診断スコアカード概要

| 評価領域 | 測定結果 | 要約 |
| :--- | :--- | :--- |
| **総合スコア** | **94 / 100（グレード S）** | 16 ルール中 `12` 件 `PASS`、`4` 件 `WARN`、`0` 件 `FAIL` |
| **7 軸バランス** | 設計 `96`・品質 `98`・型 `100`・テスト `90`・依存 `95`・セキュリティ `84`・文書 `98` | 6 軸がグレード S（`>=90`）。セキュリティ（`84`）が最大の伸長余地 |
| **低スコア監査ステップ** | `security_vulnerability_audit`（`82`, A）・`web_penetration_audit`（`86`, A）・`python_test_audit`（`88`, A） | ベースイメージ CVE、`/v1/orders` 未認証、分岐カバレッジに集中 |
| **深刻度別検出数** | Critical `0` / High `0` / Medium `3` / Low `9` | 決定論ツール `6` 件 + AI 定性評価 `6` 件（ビルド専用 `pip@24.2` CVE 5 件を `low` に再分類） |
| **コンテナランタイム検証** | `passed`（テスト `4/4`、行 `85.2%` / 分岐 `62.5%`、`/healthz -> 200`） | プロジェクト `Dockerfile`（`31.33s`）と `uv` ハーネス（`0.48s`）両方のビルド・オフライン実行に成功 |
| **Trivy SCA & ライブ DAST** | Trivy `passed`（宣言依存 CRIT/HIGH `0`、IaC `DS-0026` 1 件、シークレット `0`）・DAST `15/19` プローブ | 重大な悪用可能欠陥ゼロ。`CWE-306`・`CWE-200`・`CWE-693` を実機検証で確認 |
| **承認済み監査計画** | 自動承認（`plan_gate=false`） | `src`、`tests`、`README.md`、`Dockerfile`、およびライブ ASGI コンテナを対象としたリポジトリ全体監査 |
