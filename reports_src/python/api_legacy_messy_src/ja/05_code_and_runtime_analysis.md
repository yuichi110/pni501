# 5. 詳細分析：コード品質・テスト・動的検証

Python AST 静的解析（全12ファイル・`149 LOC`・2クラス・9関数）では、**Import衛生 `75.0%`・型安全性 `44.4%`・Docstring網羅率 `40.9%`** に留まり、`order_app/services/processor.py` の `process_order_batch`（58行・16分岐・**認知的複雑度 `44`**・8引数・可変デフォルト `tags=[]`・`global ORDER_STATE_CACHE`）に深刻な保守性負債が集中しています。さらに Docker 隔離環境での動的検証（`run_check`）では、`Dockerfile` ビルド（`1.00s`）とテストハーネス構築（`0.96s`）および1件のオフライン `pytest`（`2.13s`）こそ終了コード `0` で通過したものの、**実測カバレッジは行 `6.6%`（`7/106` 文）・分岐 `0.0%`** に過ぎず、続く **ASGI 起動スモーク検証（`smoke_check`, `1.92s`）および隔離ループバック HTTP 動的検証（`web_pentest`, `3.52s`）の双方が `order_app/schemas.py:9` の `PydanticUserError` で即座にクラッシュ** しました。

```drawlib file=05_module_quality_heatmap.png caption="図5-1: 主要7モジュール × 5品質指標の健全性ヒートマップ（静的AST指標 vs 実測行・分岐カバレッジ）"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    styles=[Styles.Danger, Styles.Warning, Styles.Success],
    x_categories=["型安全性", "Docstring", "Import衛生", "実測行Cov", "SIG保守健全度"],
    y_categories=[
        "services/processor.py",
        "schemas.py",
        "infra/gateway.py",
        "api/handlers.py",
        "domain/pricing.py",
        "infra/_internal.py",
        "constants.py",
    ],
    axis_line_style=Styles.Gray4Thin,
    axis_text_style=Styles.Dark.patch(text_size=9.2),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral,
    title="モジュール別 静的品質・実測カバレッジ・保守健全度マトリクス (%)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.5,
    cell_r=0.4,
    value_format="{:.1f}%",
)
hm.set_data(
    [
        [0.0, 0.0, 50.0, 0.0, 10.0],
        [25.0, 0.0, 50.0, 0.0, 30.0],
        [50.0, 0.0, 0.0, 0.0, 25.0],
        [40.0, 0.0, 100.0, 0.0, 40.0],
        [100.0, 50.0, 100.0, 0.0, 45.0],
        [100.0, 50.0, 100.0, 0.0, 60.0],
        [100.0, 100.0, 100.0, 100.0, 100.0],
    ]
)
hm.draw((2, 2), width=116, height=66)
hm.draw_colorbar(
    (124, 12),
    text_style=Styles.Dark.patch(text_size=9.2),
    length=44.0,
    thickness=2.4,
    orientation="vertical",
    num_ticks=5,
    value_format="{:.0f}%",
    label="達成率",
)

save()
```

## コンテナ動的検証ステージとカバレッジ 0.0% モジュール内訳

`tests/test_orders.py` が `order_app.constants` しかインポートしていないため、`pytest` 実行時には `handlers.py` や `schemas.py` が一度も読み込まれず、`smoke_check`（`importlib.import_module("order_app.api.handlers")`）および `web_pentest`（`uvicorn` コンテナ起動 → `http://127.0.0.1:54305` ポーリング）を実行した瞬間に初めて Pydantic v2 の未注釈フィールド検査例外（`legacy_flag = True`）が顕在化しました。

```drawlib file=05_runtime_verification_summary.png caption="図5-2: コンテナ動的検証 (run_check & web_pentest) KPI（左）とステージ・最低カバレッジ内訳（右）"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Panel, Table
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

Panel(
    "コンテナ動的検証KPI",
    style=Styles.Neutral,
    header_style=Styles.Danger,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
).draw((2, 2), width=52, height=66)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.DangerBold.patch(text_size=15.0),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=8.8),
    accent_style=Styles.Danger,
)
kpis.add("PASS (1.00s)", "Dockerfile ビルド", "ハーネス構築も 0.96s で成功", accent_style=Styles.Success, metric_style=Styles.SuccessBold.patch(text_size=14.5))
kpis.add("1 / 1 (2.13s)", "オフライン pytest", "assert無し・constantsのみ通過", accent_style=Styles.Warning, metric_style=Styles.WarningBold.patch(text_size=14.5))
kpis.add("6.6% / 0.0%", "実測 行 / 分岐網羅率", "106文中7文のみ実行 (99文未通過)")
kpis.add("CRASH (exit 1)", "起動Smoke & DAST", "server_booted=false (schemas:L9)")
kpis.draw((4, 4), width=48, height=53, columns=1)

tbl = Table(
    cell_style=Styles.WhiteBordered,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (57, 68),
    column_widths=[36.0, 16.0, 35.0],
    row_heights=[8.5, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2],
    data=[
        ["モジュール (lowest_covered)", "行 / 分岐", "実行文数・未実行理由"],
        ["services/processor.py", "0.0% / 0%", "0 / 45 文 (中核バッチ処理が完全未テスト)"],
        ["api/handlers.py", "0.0% / —", "0 / 17 文 (import時にschemasで例外停止)"],
        ["schemas.py", "0.0% / —", "0 / 12 文 (legacy_flag未注釈クラッシュ)"],
        ["infra/gateway.py", "0.0% / —", "0 / 10 文 (未宣言boto3でImportError潜在)"],
        ["domain/pricing.py", "0.0% / 0%", "0 / 9 文 (割引・手数料・税計算が未検証)"],
        ["infra/_internal.py", "0.0% / 0%", "0 / 6 文 (/tmp/order_spool分岐が未検証)"],
        ["constants.py", "100% / —", "7 / 7 文 (唯一テストから呼出、assert無し)"],
    ],
)

save()
```

## 動的検証・`pytest-cov` 実測結果と起動障害の詳細診断

| 検証項目 / モジュール | ステータス / 計測値 | 詳細証跡 (`RuntimeFacts` / `PentestFacts`) と技術的原因 |
| :--- | :---: | :--- |
| **`project_dockerfile_build`** | `passed` (`1.00s`) | `Dockerfile`（`FROM python:latest`）のビルド自体は成功（ただし `uvicorn` は `fastapi` 推移的依存頼み）。 |
| **`harness_build`** | `passed` (`0.96s`) | `python/pip.dockerfile`（Python 3.12）テストハーネスのビルド成功。 |
| **`test_execution` (`--network=none`)** | `passed` (`1/1`, `2.13s`) | `tests/test_orders.py::test_currency_smoke` 1件のみ実行。`assert` 無しのため戻り値を一切検証せず終了。 |
| **`smoke_check` (`web_api`)** | **`failed` (`exit=1`, `1.92s`)** | `order_app.api.handlers` インポート時に `order_app/schemas.py:9` で `pydantic.errors.PydanticUserError: A non-annotated attribute was detected: legacy_flag = True` が送出され起動不能。 |
| **`web_pentest` (`http://127.0.0.1:54305`)** | **`error` (`server_booted=false`, `3.52s`)** | 実コンテナ HTTP 起動時も同一の `For further information visit https://errors.pydantic.dev/2.14/u/model-field-missing-annotation` で即座に終了し、ライブ DAST プローブ実行数 `0/0`。 |
| `order_app/services/processor.py` | **行 `0.0%` / 分岐 `0.0%`** | `0 / 45` 文（未通過行: `1-3, 5, 7-8, 11, 22, 24-25...`）。16分岐すべて未通電。 |
| `order_app/api/handlers.py` | **行 `0.0%`** | `0 / 17` 文（未通過行: `1-2, 4-5, 7-9, 12-14...`）。`POST /orders`・起動イベントともに未検証。 |
| `order_app/schemas.py` | **行 `0.0%`** | `0 / 12` 文（未通過行: `1-2, 5-9, 11-12, 14...`）。Pydantic v2 非互換コードが潜在。 |
| `order_app/infra/gateway.py` | **行 `0.0%`** | `0 / 10` 文（未通過行: `1-4, 7, 9-13`）。インポートすると `ModuleNotFoundError: No module named 'boto3'` が発生。 |
| `order_app/domain/pricing.py` | **行 `0.0%` / 分岐 `0.0%`** | `0 / 9` 文（未通過行: `3-5, 8, 18-22`）。クーポン割引や税率丸め計算が未検証。 |
| `order_app/infra/_internal.py` | **行 `0.0%` / 分岐 `0.0%`** | `0 / 6` 文（未通過行: `1, 4-8`）。`/tmp/order_spool/fees.dat` 分岐が未検証。 |
| `order_app/constants.py` + `__init__.py` | **行 `100.0%`** | `7 / 7` 文（`missing_lines=[]`）。唯一の実行済モジュール。 |
