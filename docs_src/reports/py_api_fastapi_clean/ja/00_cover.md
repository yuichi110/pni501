# PNI ソフトウェア健全性診断レポート

**対象リポジトリ**: `order-dispatch`（`examples/python/api_fastapi_clean`）— Python 3.11+ 非同期 FastAPI + Pydantic v2 受注処理マイクロサービス

```drawlib align=center code=fold file=cover_scorecard.png caption="PNI501 エグゼクティブ健全性スコアカード — order-dispatch（グレード S・94/100）"
from drawlib.canvas import save, setup
from drawlib.shapes import rectangle
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles
from drawlib.text import text
from drawlib.utils import draw_pni_logo

setup(width=146, height=64, dpi=150)

panel = Panel(
    "",
    "",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=Styles.WhiteBold.patch(text_size=13.5),
    header_height=16.0,
    header_align="left",
)
panel.draw((2.0, 2.0), width=142.0, height=60.0)

text(
    (6.5, 56.8),
    "PNI501 Software Health Audit — order-dispatch",
    style=Styles.WhiteBold.patch(text_size=13.5, halign="left"),
)
text(
    (6.5, 50.8),
    "examples/python/api_fastapi_clean  |  FastAPI + Pydantic v2  |  Run wf-f819234f",
    style=Styles.White.patch(text_size=9.8, halign="left"),
)

# Official PNI501 emblem positioned on the right of the dark primary header
draw_pni_logo((135.5, 54.0), width=8.5, dark=True)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.DarkBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
cards.add(
    "94 / 100",
    "Grade S",
    "7-Axis Composite Score",
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=15.0),
    accent_style=Styles.PrimaryFlat,
)
cards.add(
    "12 / 16",
    "Rule Pass Rate",
    "0 FAIL | 4 WARN | 12 PASS",
    accent_style=Styles.SuccessFlat,
)
cards.add(
    "4 / 4",
    "Docker Tests",
    "85.2% Line | 62.5% Branch",
    accent_style=Styles.SecondaryFlat,
)
cards.add(
    "0 CRIT/HIGH",
    "Declared App CVEs",
    "3 Med / 9 Low Total Findings",
    accent_style=Styles.WarningFlat,
)
cards.draw((6.0, 15.0), width=134.0, height=28.0, columns=4)

rectangle(
    (73.0, 8.0),
    width=134.0,
    height=7.5,
    style=Styles.PrimaryNeutral.patch(shape_r=1.2),
)
text(
    (73.0, 8.0),
    "Python >=3.11 (uv)  |  4-Layer Clean Architecture  |  Trivy SCA + Live HTTP DAST (15/19 Probes)  |  2026-11-22 UTC",
    style=Styles.Dark.patch(text_size=9.8),
)

save()
```

| 監査属性 | 実測・検証値 |
| :--- | :--- |
| **プロジェクト / 対象パス** | `order-dispatch`（`examples/python/api_fastapi_clean`） |
| **主要言語・技術スタック** | `python`（`>=3.11`, `uv_build` + `uv.lock`, FastAPI `>=0.115.0`, Pydantic v2, `httpx`, Uvicorn） |
| **ランタイム類型** | `web_api`, `library`（ソース 14 モジュール・435 LOC、テスト 3 ファイル） |
| **ワークフロー ID / 実行 ID** | `py_api_fastapi_clean` / `wf-f819234f`（PNI Workflow v2, scope=`repo`） |
| **評価日時（UTC）** | `2026-11-22T11:29:00.803894+00:00`（`main@d1e02277`, dirty） |
| **総合スコア・グレード** | **94 / 100（グレード S）** — ルール合格率 `12/16`（`0 FAIL`, `4 WARN`, `12 PASS`） |
| **コンテナランタイム検証** | `passed` — Dockerfile・`uv` ハーネスともにビルド成功、オフラインテスト `4/4`（`--network=none`）、行カバレッジ `85.2%`、`/healthz -> 200` |
| **セキュリティ・動的診断** | Trivy `passed`（宣言依存の CRIT/HIGH `0` 件、シークレット `0` 件、AST 危険シンク `0` 件）・ライブ DAST `15/19` プローブ合格（検出 `3` 件） |
