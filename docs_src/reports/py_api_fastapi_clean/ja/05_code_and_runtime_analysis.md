# 5. 詳細分析：コード品質・テスト・ランタイム検証

静的 AST 解析の結果、全 14 モジュール（435 LOC）にわたってインポート衛生・型安全性・Google スタイル docstring のすべてが **100.0%** に達しており、複雑度ホットスポット `0` 件・循環依存 `0` 件・タイムアウト未指定 I/O `0` 件と極めて健全なコード品質を維持しています。隔離 Docker 環境でのランタイム検証でも全 4 ゲートを通過し、ビルド成功・オフラインテスト `4/4` 合格（`--network=none`）・**行カバレッジ 85.2%**（`178/209` 文）・ASGI 起動成功（`/healthz -> 200`）を実証しました。一方、HTTP 境界および外部 Webhook 境界（`webhook_client.py` `55.6%`、`routes.py` `56.0%`、`main.py` `67.9%`）の未通過分岐により、全体の分岐カバレッジは `62.5%` に留まっています。

```drawlib align=center code=fold file=module_quality_heatmap.png caption="モジュール × 品質軸 適合度マトリクス（50%〜100%：境界カバレッジと認証ギャップを可視化）"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    styles=[Styles.WarningFlat, Styles.WarningNeutral, Styles.PrimaryNeutral, Styles.SuccessFlat],
    x_categories=["Typing", "Imports", "Docstrings", "Line Cov", "Boundary Sec"],
    width=88.0,
    height=46.0,
    min_value=50.0,
    max_value=100.0,
    cell_gap=0.7,
    cell_r=0.6,
    value_format="{:.0f}%",
    auto_contrast_text=True,
    x_label_position="top",
    y_origin="top",
    axis_text_style=Styles.Dark.patch(text_size=9.8),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    title="Substantive Modules × Quality Fitness Matrix (50% - 100%)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)

# Ordered lowest-fitness-first (top to bottom)
hm.add_row("api/routes.py", [100, 100, 100, 56, 70])
hm.add_row("infra/webhook_client.py", [100, 100, 100, 56, 100])
hm.add_row("main.py", [100, 100, 100, 68, 85])
hm.add_row("api/schemas.py", [100, 100, 100, 95, 100])
hm.add_row("domain/pricing.py", [100, 100, 100, 95, 100])
hm.add_row("services/dispatcher.py", [100, 100, 100, 100, 100])
hm.add_row("domain/models.py", [100, 100, 100, 100, 100])
hm.add_row("infra/repository.py", [100, 100, 100, 100, 100])
hm.add_row("settings.py", [100, 100, 100, 100, 100])

hm.draw((36.0, 11.0))
hm.draw_colorbar(
    (51.0, 3.5),
    text_style=Styles.Dark.patch(text_size=9.5),
    length=58.0,
    thickness=2.2,
    orientation="horizontal",
    num_ticks=6,
    value_format="{:.0f}%",
    label="Module Fitness Score (%)",
)

save()
```

## コンテナランタイム検証とモジュール別カバレッジ内訳

単体テストでは明示的な `_StubWebhookClient` により `OrderDispatcherService` を外部ネットワークから切り離しており、決定論的オフライン実行（`--network=none`, `5.05s`）のもと `services/dispatcher.py`・`domain/models.py`・`infra/repository.py`・`settings.py` のすべてで **行カバレッジ 100.0%** を達成しています。ただし `tests/test_routes.py` が FastAPI `TestClient` の HTTP ルート呼び出しや `httpx.MockTransport` のエラー分岐を実行していないため、`webhook_client.py`（`55.6%`）・`routes.py`（`56.0%`、分岐 `0.0%`）・`main.py` lifespan（`67.9%`、分岐 `0.0%`）が全体分岐カバレッジを `62.5%` に押し下げています。なお ASGI スモーク検証（`/healthz -> 200`, `2.25s`）自体は正常完了しましたが、`starlette.testclient` の `httpx` 非推奨警告（`StarletteDeprecationWarning`）が 1 件観測されました。

```drawlib align=center code=fold file=runtime_coverage_breakdown.png caption="コンテナランタイム検証ゲート結果とモジュール別実測行カバレッジ（低い順）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=72, dpi=150)

gates = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5),
    metric_style=Styles.DarkBold.patch(text_size=11.5),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Muted.patch(text_size=9.0),
    accent_style=Styles.SuccessFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
gates.add("PASS (31.3s)", "Dockerfile Build", "uv Harness: 0.48s", accent_style=Styles.SuccessFlat)
gates.add("4 / 4 PASS", "Offline Pytest", "--network=none (5.05s)", accent_style=Styles.SuccessFlat)
gates.add("85.2% / 62.5%", "Line / Branch Cov", "178 / 209 Statements", accent_style=Styles.WarningFlat)
gates.add("HTTP 200", "ASGI Smoke Boot", "/healthz (2.25s)", accent_style=Styles.PrimaryFlat)
gates.draw((4.0, 55.0), width=138.0, height=15.0, columns=4)

chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=102.0,
    height=41.0,
    categories=[
        "infra/webhook_client.py",
        "api/routes.py",
        "main.py",
        "api/schemas.py",
        "domain/pricing.py",
        "services/dispatcher.py",
        "domain/models.py",
        "infra/repository.py",
        "settings.py",
    ],
    orientation="horizontal",
    bar_width_ratio=0.64,
    bar_r=0.7,
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.1f}%",
    title="Measured Line Coverage by Module (pytest-cov | Avg 85.2%)",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
chart.configure_x_axis(
    min_value=0.0,
    max_value=112.0,
    ticks=[0, 20, 40, 60, 80, 100],
    show_grid=True,
    label="Line Coverage (%)",
)
chart.add_series(
    "Line Coverage %",
    [55.6, 56.0, 67.9, 94.6, 95.2, 100.0, 100.0, 100.0, 100.0],
    style=Styles.PrimaryNeutral,
)
chart.draw((36.0, 7.5))

save()
```

## 静的 AST・保守性・運用準備度（12-Factor / PRR）指標

| 指標カテゴリ | 測定項目 | 実測値 | 判定・補足 |
| :--- | :--- | :---: | :---: |
| **コードベース規模** | ソースファイル数 / LOC / クラス数 / 関数数 | `14` / `435` / `14` / `23` | 簡潔なマイクロサービス粒度 |
| **静的品質カバレッジ** | インポート衛生 / 型安全性 / docstring / 静的モジュールテスト網羅 | `100.0%` / `100.0%` / `100.0%` / `100.0%` | **PASS**（4 指標すべて 100%） |
| **SIG 保守性・結合度** | 複雑関数 / 過多引数 / グローバル状態 / 循環依存 | `0` / `0` / `0` / `0` | **PASS** |
| **衛生・型規律** | バグ懸念 / 未宣言依存 / 弱い `Any` / 言語版不整合 | `0` / `0` / `0` / `0` | **PASS**（`py.typed` 完備） |
| **12-Factor / SRE PRR** | タイムアウト欠落 / 散在環境変数読取 / 非構造化 `print` | `0` / `0` / `0` | **PASS**（`5.0s` タイムアウト・`pydantic-settings`） |
| **コンテナランタイム** | ビルド / オフライン pytest（`--network=none`） / ASGI スモーク | `passed` / `4/4`（`5.05s`） / `200`（`2.25s`） | **PASS**（軽微な Starlette 非推奨警告 1 件） |

## モジュール別実測カバレッジ詳細（`pytest-cov`）

| モジュールパス | 行カバレッジ | 分岐カバレッジ | カバー文 / 総文数 | 未カバー行（`missing_lines_preview`） | 推奨追加テスト |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `src/order_dispatch/infra/webhook_client.py` | **55.6%** | `n/a` | `10 / 18` | `36, 41-47` | `httpx.MockTransport` による 2xx 成功および `httpx.HTTPError` フォールバック検証 |
| `src/order_dispatch/api/routes.py` | **56.0%** | **0.0%** | `14 / 25` | `29-30, 42-43, 56, 74, 79, 96-98` | FastAPI `TestClient` での `/healthz`・`POST /v1/orders`・`GET` 200 & 404 検証 |
| `src/order_dispatch/main.py` | **67.9%** | **0.0%** | `19 / 28` | `30-34, 38, 43-45` | `with TestClient(create_app())` による `lifespan` 起動・終了経路の検証 |
| `src/order_dispatch/api/schemas.py` | `94.6%` | `50.0%` | `35 / 37` | `32, 90` | 空白のみ SKU のバリデーションエラーおよび `to_order_response()` 検証 |
| `src/order_dispatch/domain/pricing.py` | `95.2%` | `90.0%` | `20 / 21` | `49` | 範囲外 `vip_discount_rate`（`<0.0` / `>0.5`）時の `PricingError` 送出検証 |
| `src/order_dispatch/services/dispatcher.py` | `100.0%` | `n/a` | `26 / 26` | `[]` | 完全カバー済み（`_StubWebhookClient`） |
| `src/order_dispatch/domain/models.py` | `100.0%` | `n/a` | `24 / 24` | `[]` | 完全カバー済み |
| `src/order_dispatch/infra/repository.py` | `100.0%` | `n/a` | `13 / 13` | `[]` | 完全カバー済み |
| `src/order_dispatch/settings.py` + 5 `__init__.py` | `100.0%` | `n/a` | `17 / 17` | `[]` | 完全カバー済み |
