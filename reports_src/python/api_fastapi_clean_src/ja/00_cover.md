# PNI ソフトウェア健全性診断レポート

対象プロジェクト **`order-dispatch` (`v1.2.0`)** に対する PNI (Project Normalized Inspection) ステートフル診断レポートです。静的 AST 構造解析・アーキテクチャ境界検証・コンテナ隔離下の動的テスト／カバレッジ計測・Trivy 脆弱性スキャン・動的 Web ペネトレーションテスト（`web_pentest`）を統合し、7軸のエンジニアリング健全性を定量評価しています。

```drawlib file=00_cover_scorecard.png caption="図0-1: order-dispatch 総合健全性スコアカード (89/100・Grade A)"
from drawlib.canvas import setup
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

Panel(
    "order-dispatch (v1.2.0) — 総合健全性スコアカード",
    description="Run: wf-ee9a9eb6",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
    description_style=Styles.White.patch(text_size=9.5),
).draw((2, 2), width=142, height=56)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.PrimaryBold.patch(text_size=16.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.Primary,
)
kpis.add("89 / 100", "総合健全性 (Grade A)", "7軸加重評価・全18工程完了")
kpis.add("Python 3.12", "FastAPI 非同期API", "14ファイル・435 LOC")
kpis.add("9 / 16 適合", "ルール適合率 (56%)", "FAIL 0件 / WARN 7件")
kpis.add("20 件", "検出された改善指摘", "H:1 / M:7 / L:12")
kpis.draw((5, 5), width=136, height=31, columns=4)
```

## 診断メタデータ概要

| 項目 | 診断記録内容 |
| :--- | :--- |
| **対象プロジェクト / バージョン** | `order-dispatch` (`1.2.0`) — 顧客注文受付・整数セント価格計算・非同期パートナー Webhook 配送サービス |
| **対象リポジトリ相対パス** | `examples/python/api_fastapi_clean` (`src/order_dispatch/**` 14ファイル、`tests/**` 3ファイル) |
| **主要技術スタック** | Python `>=3.11` (`python:3.12.6-slim-bookworm`)、FastAPI `>=0.115.0`、Pydantic v2、httpx、uvicorn、uv |
| **実行ワークフロー / Run ID** | `py_api_fastapi_clean` / `wf-ee9a9eb6`（全18ステップ完遂・状態DB記録済） |
| **診断実行日時 (UTC)** | `2026-10-24T14:48:14Z` |
| **コンテナ動的検証結果** | `passed` — Dockerfileビルド成功 (`28.40s`)、オフライン単体テスト `4/4` 成功 (`5.40s`)、行カバレッジ `85.2%`、`/healthz` HTTP `200` (`2.49s`) |
| **セキュリティ・DAST検査結果** | `passed` — Python実行時依存CVE `0件`（`pip@24.2` 6件、Debian 12.7 OS 508件）、動的侵入検証 `15/19` 合格（CRIT/HIGH `0件`、MED/LOW `3件`） |
| **総合評価 (Overall Grade)** | **89 / 100 (Grade A)** — クリーン4層設計・型安全性100%・CWE危険シンク0件・ライブ注入耐性を達成。基盤イメージ刷新とAPI認証追加が優先課題 |
