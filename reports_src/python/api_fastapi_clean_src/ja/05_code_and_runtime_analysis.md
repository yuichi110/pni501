# 5. 詳細分析：コード品質・テスト・動的検証

静的 AST 解析（全14ファイル・435 LOC・23関数・14クラス）では、**型安全性 `100.0%`・Docstring網羅率 `100.0%`・Import衛生 `100.0%`**、SIG 保守性リスク（複雑関数・過剰引数・循環依存・グローバル可変状態）すべて **`0件`** を確認しました。さらに Docker 隔離環境での動的検証（`run_check`）では、ビルド・オフライン単体テスト（`4/4` 成功）・ASGI `/healthz` スモーク（HTTP `200`）がすべて正常通過し、実測カバレッジは **行 `85.2%`（`178/209` 文）・分岐 `62.5%`** を記録しました。

```drawlib file=05_module_quality_heatmap.png caption="図5-1: 主要9モジュール × 5品質軸の健全性ヒートマップ（静的AST完全性 vs 実測行・分岐カバレッジ）"
from drawlib.canvas import setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    styles=[Styles.Danger, Styles.Warning, Styles.Success],
    x_categories=["型安全性", "Docstring", "Import衛生", "実測行Cov", "分岐・実行健全度"],
    y_categories=[
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
    axis_line_style=Styles.Gray4Thin,
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral,
    title="モジュール別 静的品質・実測カバレッジ適合マトリクス (%)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.5,
    cell_r=0.4,
    value_format="{:.1f}%",
)
hm.set_data(
    [
        [100.0, 100.0, 100.0, 55.6, 55.6],
        [100.0, 100.0, 100.0, 56.0, 0.0],
        [100.0, 100.0, 100.0, 67.9, 0.0],
        [100.0, 100.0, 100.0, 94.6, 50.0],
        [100.0, 100.0, 100.0, 95.2, 90.0],
        [100.0, 100.0, 100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0, 100.0, 100.0],
    ]
)
hm.draw((2, 2), width=116, height=66)
hm.draw_colorbar(
    (124, 12),
    text_style=Styles.Dark.patch(text_size=9.5),
    length=44.0,
    thickness=2.4,
    orientation="vertical",
    num_ticks=5,
    value_format="{:.0f}%",
    label="達成率",
)
```

## コンテナ動的検証ステージとモジュール別カバレッジ詳細

ドメイン層（`models.py` `100%`, `pricing.py` `95.2%`）およびサービス層（`dispatcher.py` `100%`）は単体テストで緻密に検証されている一方、リポジトリ内の `pytest` スイート単体では ASGI トランスポート層（`routes.py` `56.0%`, `main.py` `67.9%`）と外部 HTTP 通信アダプタ（`webhook_client.py` `55.6%`）が未実行行を残しています。なお、別工程の動的 Web ペネトレーションテスト（`web_pentest`、`.pni/pentests/examples/python/api_fastapi_clean/`、`5.24s`）では稼働中の Uvicorn コンテナに対して計19件のライブ HTTP プローブを実行し、`/healthz`・`POST /v1/orders`（201 / 422）・`GET /v1/orders/1`（404）の実通信動作も補完確認しています。

```drawlib file=05_runtime_and_coverage_bars.png caption="図5-2: モジュール別実測行カバレッジ比較（左）とコンテナ動的検証パイプライン結果（右）"
from drawlib.canvas import setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

bar = BarChart(
    axis_line_style=Styles.Gray5Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral,
    title="モジュール別 実測行カバレッジ (昇順 %)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    categories=[
        "webhook.py",
        "routes.py",
        "main.py",
        "schemas.py",
        "pricing.py",
        "dispatcher",
        "models.py",
        "repository",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    value_format="{:.1f}%",
)
bar.value_axis.min_value = 0
bar.value_axis.max_value = 112
bar.add_series(
    "行カバレッジ",
    [55.6, 56.0, 67.9, 94.6, 95.2, 100.0, 100.0, 100.0],
    style=Styles.Primary,
)
bar.draw((2, 2), width=82, height=64)

Panel(
    "コンテナ動的検証 (run_check & pentest)",
    style=Styles.Neutral,
    header_style=Styles.Success,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
).draw((87, 2), width=57, height=64)

stages = CardList(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.5),
)
stages.add("Dockerfile ビルド検証", "python:3.12.6-slim 28.40秒で完了", badge_text="PASS")
stages.add("オフライン pytest 実行", "--network=none 4/4成功 (5.40秒)", badge_text="PASS")
stages.add("ASGI /healthz スモーク", "uvicorn起動・HTTP 200応答 (2.49秒)", badge_text="PASS")
stages.add("動的 HTTP 侵入プローブ", "15/19合格・重大脆弱性0件 (5.24秒)", badge_text="WARN")
stages.draw((89, 4), width=53, height=51)
```

## 静的品質指標・12-Factor 準備度と `pytest-cov` 実測内訳

| モジュール相対パス | 実行文 / 総文数 | 実測行カバレッジ | 実測分岐カバレッジ | 未通過行番号 (`missing_lines`) と補完テスト方針 |
| :--- | :---: | :---: | :---: | :--- |
| `src/order_dispatch/infra/webhook_client.py` | `10 / 18` | **55.6%** | `100.0%` (0分岐) | `36, 41-47` — `httpx.MockTransport` で 200 OK / 503 / `ConnectTimeout` を検証 |
| `src/order_dispatch/api/routes.py` | `14 / 25` | **56.0%** | **0.0%** | `29-30, 42-43, 56, 74, 79, 96-98` — `TestClient` で `/healthz`, `POST`/`GET /v1/orders` (201/200/404) を通電 |
| `src/order_dispatch/main.py` | `19 / 28` | **67.9%** | **0.0%** | `30-34, 38, 43-45` — `with TestClient(create_app()) as client:` で Lifespan 起動・終了を通電 |
| `src/order_dispatch/api/schemas.py` | `35 / 37` | **94.6%** | `50.0%` | `32, 90` — 空白 SKU バリデーション失敗（HTTP 422）と `to_order_response` 射影を検証 |
| `src/order_dispatch/domain/pricing.py` | `20 / 21` | **95.2%** | `90.0%` | `49` — 不正 `vip_discount_rate` 境界値に対する `PricingError` 例外テストを1件追加 |
| `src/order_dispatch/services/dispatcher.py` | `26 / 26` | **100.0%** | `100.0%` | なし（正常配送 `DISPATCHED`・失敗縮退 `WEBHOOK_DEFERRED` とも検証済） |
| `src/order_dispatch/domain/models.py` | `24 / 24` | **100.0%** | `100.0%` | なし（全 `dataclass(frozen=True)`・`StrEnum` 網羅） |
| `src/order_dispatch/infra/repository.py` | `13 / 13` | **100.0%** | `100.0%` | なし（保存・ID検索・未存在 `None` 応答とも網羅） |
| `src/order_dispatch/settings.py` + `__init__.py` (5件) | `17 / 17` | **100.0%** | `100.0%` | なし（全設定フィールド・パッケージ初期化を通過） |
| **合計 / 全体集計 (`pytest-cov`)** | **`178 / 209`** | **85.2%** | **62.5%** | `TestClient` + `MockTransport` 約40行の追加で行・分岐とも `95%+` 到達可能 |
