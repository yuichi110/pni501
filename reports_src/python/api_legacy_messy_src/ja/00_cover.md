# PNI ソフトウェア健全性診断レポート

対象プロジェクト **`legacy-order-hub` (`v0.1.0`)**（`examples/python/api_legacy_messy`）に対する PNI (Project Normalized Inspection) ステートフル健全性診断レポートです。3観点のアーキテクチャ構造記録・静的 Python AST 解析・Docker 隔離環境での動的ビルド／オフライン単体テスト／カバレッジ／起動スモーク検証・Trivy 脆弱性スキャン・隔離ループバック動的 HTTP ペネトレーション検証（`web_pentest`）を統合し、7軸で定量評価を実施しました。

```drawlib file=00_cover_scorecard.png caption="図0-1: legacy-order-hub 総合健全性スコアカード (20/100・Grade D)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

hero = Panel(
    "legacy-order-hub (v0.1.0) — 総合エンジニアリング健全性スコアカード",
    description="対象: examples/python/api_legacy_messy  |  ワークフロー: py_api_legacy_messy (wf-fe76f694)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.Danger,
    text_style=Styles.WhiteBold.patch(text_size=11.5),
    description_style=Styles.White.patch(text_size=9.5),
    icon=phosphor.warning_octagon,
    icon_style=Styles.WhiteBold,
)
hero.draw((2, 2), width=142, height=58)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.DangerBold.patch(text_size=18.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.2),
    accent_style=Styles.Danger,
)
kpis.add("20 / 100", "総合健全性 (Grade D)", "全7軸で重大な技術的負債・リスク検出")
kpis.add("Python 3.12", "FastAPI + Flask 混在", "全12ファイル (149 LOC) + Bash 106行")
kpis.add("0 / 15 適合", "ルール適合率 (0.0%)", "FAIL 14件 / WARN 1件 / PASS 0件")
kpis.add("28 件", "検出された改善指摘", "CRIT 8 / HIGH 14 / MED 5 / LOW 1")
kpis.draw((5, 5), width=136, height=32, columns=4)

save()
```

## 診断メタデータ概要

| 項目 | 診断記録内容 |
| :--- | :--- |
| **対象プロジェクト / バージョン** | `legacy-order-hub` (`0.1.0` / `setup.py`) — 顧客注文バッチ処理 HTTP サービスおよび CSV 同期スクリプト |
| **対象リポジトリ相対パス** | `examples/python/api_legacy_messy`（`order_app/**` 12ファイル、`tests/**` 1ファイル、`scripts/legacy_sync.sh`） |
| **主要技術スタック** | Python、FastAPI、Flask、Pydantic、Requests、PyYAML、urllib3、Uvicorn、Bash、`python:latest` |
| **実行ワークフロー / Run ID** | `py_api_legacy_messy` / `wf-fe76f694`（全18ステップ完遂・状態DB記録済） |
| **診断実行日時 (UTC)** | `2026-10-24T15:06:19Z` |
| **コンテナ動的検証結果** | `failed` — ビルド成功（`1.00s`、ハーネス `0.96s`）、単体テスト `1/1` 成功（`2.13s`）、実測行カバレッジ **`6.6%`**、起動スモーク **`PydanticUserError` で異常終了（`1.92s`）** |
| **セキュリティ & DAST 検査結果** | `failed` / `error` — Python CVE **`7件`（HIGH 4件）**、Debian 13.7 OS CVE **`3,554件`（CRIT 24 / HIGH 436）**、CWE シンク **`2件`**、動的 `web_pentest` **起動失敗（`server_booted=false`, `3.52s`）** |
| **総合評価 (Overall Grade)** | **20 / 100 (Grade D)** — 起動不能障害・RCE/コマンド注入シンク・特権 CI・肥大 `python:latest` 基盤・DAST ゲート遮断の即時是正が必須 |
