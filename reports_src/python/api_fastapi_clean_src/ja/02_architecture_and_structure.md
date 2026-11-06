# 2. アーキテクチャとソースコード構成

`order-dispatch` は **FastAPI Lifespan 依存性注入（DI）と Repository Protocol ポートを備えた4層クリーンアーキテクチャ** を採用する非同期 Web API マイクロサービス（`runtime=web_api`、全14ファイル・435 LOC）です。内部 Import グラフは完全な有向非巡回グラフ（循環依存 `0件`・レイヤ境界違反 `0件`）であり、`domain/` パッケージは FastAPI・Pydantic・httpx への依存を一切持ちません。

```drawlib file=02_source_tree_and_inventory.png caption="図2-1: 物理ソースディレクトリ構造 (TreeNode) とレイヤ別責務・規模サマリー (Table)"
from drawlib.canvas import setup
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

Panel(
    "src/order_dispatch/ 構造 (435 LOC)",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((2, 2), width=52, height=64)

root = TreeNode(
    "order_dispatch/ (14 files)",
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    line_style=Styles.Gray5Thin,
    line_horizontal_margin=1.0,
    line_horizontal_length=2.8,
    line_vertical_margin=5.6,
)
root.add("main.py (48) / settings.py (18)")
root.add("api/ -> routes (74), schemas (67)")
root.add("services/ -> dispatcher.py (74)")
root.add("domain/ -> models (29), pricing (41)")
root.add("infra/ -> repository (39)")
root.add("infra/ -> webhook_client (35)")
root.draw((5, 53))

tbl = Table(
    cell_style=Styles.WhiteBordered,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (57, 65),
    column_widths=[25.0, 11.0, 51.0],
    row_heights=[9.5, 10.5, 10.5, 10.5, 10.5, 10.5],
    data=[
        ["アーキテクチャ層", "LOC", "主要コンポーネントと許可された依存方向"],
        ["Composition Root", "68", "main.py, settings.py — Lifespan DI配線・設定検証"],
        ["API Transport", "143", "routes.py, schemas.py -> Services / Domain"],
        ["Application Svc", "76", "OrderDispatcherService -> Domain / Repository"],
        ["Infra Adapters", "76", "OrderRepository, AsyncWebhookClient -> Domain"],
        ["Domain Core", "72", "OrderRecord, OrderLine, pricing -> 外部依存ゼロ"],
    ],
)
```

## レイヤ依存関係とリスクホットスポット・実行フロー

以下のクラス／コンポーネント依存図では、`module_hotspots` の実測リスクスコアをサーマルオーバーレイ（`HeatmapOverlay`）として重畳しています。アプリケーション内部コードの複雑度リスクは極めて低い一方、リスクはコンテナ基盤 `Dockerfile`（`0.70`）、認証境界の未実装が動的検証でも確認された `api/routes.py`（`0.60`）、および HTTP ヘッダ／OpenAPI 公開制御を担う `main.py`（`0.18`）に局在しています。

```drawlib file=02_layer_dependency_hotspot.png caption="図2-2: レイヤ間コンポーネント依存関係とモジュール別リスクホットスポット (HeatmapOverlay)"
from drawlib.canvas import setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.smartarts import Panel
from drawlib.styles import Colors, Styles

setup(width=146, height=74, dpi=150)

Panel(
    "4層クリーンアーキテクチャ依存グラフ × リスクホットスポット重畳 (0.00〜0.75)",
    style=Styles.Neutral,
    header_style=Styles.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((2, 2), width=142, height=70)

card_body = Styles.Neutral.patch(shape_fill_color=Colors.White, text_size=9.5)
diag = ClassDiagram(
    node_style=card_body,
    header_style=Styles.PrimaryNeutral,
    edge_style=Styles.Gray6Thin,
    edge_text_style=Styles.Dark.patch(text_size=9.5),
    margin=2.0,
)

n_docker = ClassNode("Dockerfile / uv.lock", stereotype="build & image", width=34.0, header_style=Styles.DangerNeutral)
n_docker.add_attribute("python:3.12.6-slim", "risk=0.70")

n_main = ClassNode("main.py / settings.py", stereotype="composition", width=34.0, header_style=Styles.PrimaryNeutral)
n_main.add_method("create_app", return_type="risk=0.18")

n_routes = ClassNode("api/routes & schemas", stereotype="transport", width=34.0, header_style=Styles.WarningNeutral)
n_routes.add_method("create_order", return_type="risk=0.60")

n_infra = ClassNode("AsyncWebhookClient", stereotype="infra", width=34.0, header_style=Styles.Neutral)
n_infra.add_method("notify_order", return_type="bool")

n_disp = ClassNode("OrderDispatcherService", stereotype="service", width=34.0, header_style=Styles.PrimaryNeutral)
n_disp.add_method("place_order", return_type="OrderRecord")

n_domain = ClassNode("domain/pricing & models", stereotype="domain", width=34.0, header_style=Styles.SuccessNeutral)
n_domain.add_method("compute_total", return_type="int")

diag.add(n_docker, xy=(25, 50))
diag.add(n_main, xy=(73, 50))
diag.add(n_routes, xy=(121, 50))
diag.add(n_infra, xy=(25, 24))
diag.add(n_disp, xy=(73, 24))
diag.add(n_domain, xy=(121, 24))

diag.connect(n_docker, n_main, relationship_type="dependency", directed=True, label="boots")
diag.connect(n_main, n_routes, relationship_type="dependency", directed=True, label="mounts")
diag.connect(n_main, n_disp, relationship_type="composition", directed=True, label="lifespan")
diag.connect(n_routes, n_domain, relationship_type="dependency", directed=True, label="DTO投影")
diag.connect(n_disp, n_infra, relationship_type="association", directed=True, label="POST 5s")
diag.connect(n_disp, n_domain, relationship_type="dependency", directed=True, label="cents")

overlay = HeatmapOverlay(
    styles=[Styles.Success, Styles.Warning, Styles.Danger],
    min_value=0.0,
    max_value=0.75,
    default_radius=16.0,
    max_alpha=0.40,
    mode="smooth",
)
overlay.add_spot(n_docker, value=0.70, radius=18.0)
overlay.add_spot(n_routes, value=0.60, radius=17.5)
overlay.add_spot(n_infra, value=0.18, radius=14.0)
overlay.add_spot(n_disp, value=0.06, radius=12.0)
overlay.add_spot(n_main, value=0.18, radius=14.0)

overlay.draw((0, 0))
diag.draw((0, 0))
overlay.draw_colorbar(
    (8, 7.0),
    text_style=Styles.Dark.patch(text_size=9.5),
    length=44.0,
    thickness=2.0,
    num_ticks=4,
    label="ホットスポット risk_score",
)
```

注文作成リクエスト（`POST /v1/orders`）の実行時ライフサイクルは、DTO 検証・整数セント価格計算・5秒タイムアウト付き非同期 Webhook 通知・状態遷移（`DISPATCHED` または `WEBHOOK_DEFERRED`）の5段階で完結します。

```drawlib file=02_execution_flow_roadmap.png caption="図2-3: 注文作成・価格計算・非同期Webhook配送の5段階実行フロー"
from drawlib.canvas import setup
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=56, dpi=150)

flow = Roadmap(
    style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
)
flow.add("1. DTO検証", "extra禁止検証・\nSKU正規化", badge_text="API")
flow.add("2. ドメイン変換", "不変OrderLine\nタプルへ射影", badge_text="DTO")
flow.add("3. 価格計算", "整数セント小計・\nVIP割引算出", badge_text="Domain")
flow.add("4. 非同期通知", "AsyncClient(5s)\nWebhook POST", badge_text="Infra")
flow.add("5. 永続化・応答", "状態保存後に\nHTTP 201返却", badge_text="Repo")
flow.draw((3, 4), width=140, height=48)
```

## 全ソースモジュール一覧（14ファイル・435 LOC）

| モジュール相対パス | LOC | 公開クラス / 型 | 公開関数・エンドポイント / 役割 |
| :--- | :---: | :--- | :--- |
| `src/order_dispatch/main.py` | 48 | — | `lifespan`, `create_app` — ASGI アプリ生成と Lifespan DI 初期化 |
| `src/order_dispatch/settings.py` | 18 | `ServiceSettings` | `load_settings` — `ORDER_DISPATCH_*` 環境変数の型検証 |
| `src/order_dispatch/api/routes.py` | 74 | — | `health_check`, `create_order`, `get_order`, `get_dispatcher`, `get_settings` |
| `src/order_dispatch/api/schemas.py` | 67 | `OrderLineInput`, `CreateOrderRequest`, `OrderResponse`, `HealthResponse` | `to_domain_lines`, `to_order_response` (`extra="forbid"` DTO変換) |
| `src/order_dispatch/services/dispatcher.py` | 74 | `OrderDispatcherService` | `place_order`, `find_order` — 価格算出・Webhook通知・保存の調停 |
| `src/order_dispatch/domain/models.py` | 29 | `CustomerTier`, `OrderStatus`, `OrderLine`, `OrderRecord` | 不変 `frozen=True` エンティティとライフサイクル `StrEnum` |
| `src/order_dispatch/domain/pricing.py` | 41 | `PricingError` | `calculate_subtotal_cents`, `compute_order_total_cents`（整数セント演算） |
| `src/order_dispatch/infra/repository.py` | 39 | `OrderRepository`, `InMemoryOrderRepository` | `Protocol` 永続化ポートとインメモリ辞書アダプタ |
| `src/order_dispatch/infra/webhook_client.py` | 35 | `AsyncWebhookClient` | `notify_order_accepted`（5秒タイムアウト・例外時 `False` 縮退） |
| `src/order_dispatch/**/__init__.py` (計5件) | 10 | — | パッケージ境界初期化モジュール（各2 LOC × 5ファイル） |
