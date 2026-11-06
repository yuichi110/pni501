# 2. アーキテクチャとソースコード構成

`legacy-order-hub` はディレクトリ上こそ `api/`・`services/`・`domain/`・`infra/` の4層パッケージ構成を採っていますが、実態は **循環依存・レイヤ逆転・2種類の Web フレームワーク同居・サイドバンド Bash スクリプトが絡み合う劣化した階層型サービス**（Python 12ファイル計 `149 LOC` + `scripts/legacy_sync.sh` `106 LOC`）です。とりわけ `order_app/domain/pricing.py` が上位 `order_app/api/handlers.py` の `ACTIVE_PROMO_CODES` を逆参照して3ノードの循環 Import を形成し、同時に `order_app/infra/_internal.py`（`/tmp/order_spool/fees.dat` 参照）へ直接結合しています。

```drawlib file=02_source_tree_and_inventory.png caption="図2-1: リポジトリ物理ディレクトリ構造 (TreeNode) とレイヤ別責務・規模一覧 (Table)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

Panel(
    "api_legacy_messy 物理構造",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((2, 2), width=52, height=66)

root = TreeNode(
    "api_legacy_messy/",
    text_style=Styles.PrimaryBold.patch(text_size=9.2),
    line_style=Styles.Gray5Thin,
    line_horizontal_margin=0.8,
    line_horizontal_length=2.0,
    line_vertical_margin=1.25,
)
app_node = root.add("order_app/ (149 LOC)")
app_node.add("constants.py (14 LOC)")
app_node.add("schemas.py (12 LOC)")
api_node = app_node.add("api/")
api_node.add("handlers.py (25 LOC)")
svc_node = app_node.add("services/")
svc_node.add("processor.py (59 LOC)")
dom_node = app_node.add("domain/")
dom_node.add("pricing.py (17 LOC)")
inf_node = app_node.add("infra/")
inf_node.add("_internal.py (6) / gateway.py (11)")
root.add("scripts/legacy_sync.sh (106 LOC)")
root.add("tests/test_orders.py (4 LOC)")
root.add("Dockerfile / deploy.yml / config/")
root.draw((4, 57))

tbl = Table(
    cell_style=Styles.WhiteBordered,
    text_style=Styles.Dark.patch(text_size=9.2),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (57, 67),
    column_widths=[25.0, 12.0, 50.0],
    row_heights=[9.5, 11.0, 11.0, 11.0, 11.0, 11.0],
    data=[
        ["アーキテクチャ層", "LOC", "対象パスと境界健全性メモ"],
        ["API / Presentation", "38", "handlers.py, schemas.py (FastAPI+Flask同居・起動失敗)"],
        ["Application Svc", "60", "services/processor.py (複雑度44・CWEシンク・Global辞書)"],
        ["Domain Layer", "18", "domain/pricing.py (handlers逆参照で循環依存・float演算)"],
        ["Infra & Scripts", "124", "gateway.py, _internal.py, legacy_sync.sh (/tmp・boto3未宣言)"],
        ["Shared Core", "15", "constants.py, __init__.py (Final型完備・唯一の健全層)"],
    ],
)

save()
```

## レイヤ間循環依存グラフとリスクホットスポット重畳

以下のコンポーネント依存図では、`module_hotspots` の実測リスクスコアを `HeatmapOverlay` として重畳しています。`Dockerfile`・`order_app/services/processor.py`・`order_app/schemas.py`・`order_app/api/handlers.py`（いずれも `risk_score=1.00`）を筆頭に、`tests/test_orders.py`（`0.90`）、`requirements.txt`（`0.84`）、`order_app/infra/gateway.py`（`0.72`）、`order_app/domain/pricing.py`（`0.50`）と、ほぼ全層が高リスク帯（赤〜橙）に染まっています。

```drawlib file=02_layer_dependency_hotspot.png caption="図2-2: レイヤ間循環依存・境界違反グラフとモジュール別リスクホットスポット (HeatmapOverlay)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.smartarts import Panel
from drawlib.styles import Colors, Styles

setup(width=146, height=76, dpi=150)

Panel(
    "モジュール依存関係・循環Import経路 × リスクホットスポット重畳 (0.00〜1.00)",
    style=Styles.Neutral,
    header_style=Styles.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((2, 2), width=142, height=72)

card_body = Styles.Neutral.patch(shape_fill_color=Colors.White, text_size=9.0)
diag = ClassDiagram(
    node_style=card_body,
    header_style=Styles.PrimaryNeutral,
    edge_style=Styles.Gray6Thin,
    edge_text_style=Styles.Dark.patch(text_size=8.8),
    margin=2.0,
)

n_docker = ClassNode("Dockerfile & reqs.txt", stereotype="supply chain", width=36.0, header_style=Styles.DangerNeutral)
n_docker.add_attribute("python:latest (root)", "risk=1.00/0.84")

n_handlers = ClassNode("api/handlers.py", stereotype="FastAPI + Flask", width=36.0, header_style=Styles.DangerNeutral)
n_handlers.add_method("submit_orders", return_type="risk=1.00")

n_schemas = ClassNode("schemas.py", stereotype="Pydantic v1", width=36.0, header_style=Styles.DangerNeutral)
n_schemas.add_attribute("legacy_flag=True", "risk=1.00")

n_proc = ClassNode("services/processor.py", stereotype="hotspot (59 LOC)", width=36.0, header_style=Styles.DangerNeutral)
n_proc.add_method("process_order_batch", return_type="risk=1.00")

n_pricing = ClassNode("domain/pricing.py", stereotype="cycle & bypass", width=36.0, header_style=Styles.WarningNeutral)
n_pricing.add_method("calculate_legacy_total", return_type="float")

n_infra = ClassNode("infra/ (_internal & gw)", stereotype="infra &constants", width=36.0, header_style=Styles.PrimaryNeutral)
n_infra.add_method("_compute_handling_fee", return_type="risk=0.72")

diag.add(n_docker, xy=(25, 51))
diag.add(n_handlers, xy=(73, 51))
diag.add(n_schemas, xy=(121, 51))
diag.add(n_proc, xy=(25, 24))
diag.add(n_pricing, xy=(73, 24))
diag.add(n_infra, xy=(121, 24))

diag.connect(n_docker, n_handlers, relationship_type="dependency", directed=True, label="uvicorn CMD")
diag.connect(n_handlers, n_schemas, relationship_type="dependency", directed=True, label="import crash")
diag.connect(n_handlers, n_proc, relationship_type="dependency", directed=True, label="calls")
diag.connect(n_proc, n_pricing, relationship_type="dependency", directed=True, label="calls")
diag.connect(n_pricing, n_handlers, relationship_type="dependency", directed=True, label="逆参照(循環!)")
diag.connect(n_pricing, n_infra, relationship_type="dependency", directed=True, label="private侵食")

overlay = HeatmapOverlay(
    styles=[Styles.Success, Styles.Warning, Styles.Danger],
    min_value=0.0,
    max_value=1.0,
    default_radius=16.0,
    max_alpha=0.42,
    mode="smooth",
)
overlay.add_spot(n_docker, value=1.00, radius=18.5)
overlay.add_spot(n_proc, value=1.00, radius=18.5)
overlay.add_spot(n_schemas, value=1.00, radius=18.0)
overlay.add_spot(n_handlers, value=1.00, radius=18.0)
overlay.add_spot(n_infra, value=0.72, radius=15.5)
overlay.add_spot(n_pricing, value=0.50, radius=14.0)

overlay.draw((0, 0))
diag.draw((0, 0))
overlay.draw_colorbar(
    (8, 6.8),
    text_style=Styles.Dark.patch(text_size=9.2),
    length=46.0,
    thickness=2.0,
    num_ticks=5,
    label="ホットスポット risk_score",
)

save()
```

## 実行フローと状態汚染・危険シンク経路

注文バッチ送信（`POST /orders`）から価格算出・インメモリキャッシュ記録に至る実行経路と、GitHub Actions `pull_request_target` から起動される `scripts/legacy_sync.sh` の流れは以下の5段階に整理されます。

```drawlib file=02_execution_flow_roadmap.png caption="図2-3: 注文バッチ処理リクエスト経路に潜む状態汚染・循環参照・危険シンクの5段階フロー"
from drawlib.canvas import save, setup
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=56, dpi=150)

flow = Roadmap(
    style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.0),
    spine_style=Styles.DangerBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.0),
    direction="horizontal",
)
flow.add("1. 境界スキーマ", "LegacyOrderPayload: Pydantic v2で起動時例外、itemsはAny辞書", badge_text="API")
flow.add("2. ハンドラ呼出", "POST /ordersが無認証で同期processor呼出、customer_id破棄", badge_text="Route")
flow.add("3. バッチ前処理", "yaml.load(CWE-502)とtags=[]可変デフォルトへ状態蓄積", badge_text="Svc")
flow.add("4. 価格・手数料", "handlers逆参照(循環)と/tmp/order_spool/fees.dat同期参照", badge_text="Domain")
flow.add("5. 通知・保存", "shell=True(CWE-78)実行とglobal ORDER_STATE_CACHE書込", badge_text="Sink")
flow.draw((3, 4), width=140, height=48)

save()
```

## 全ソースモジュール・スクリプト一覧

| モジュール相対パス | LOC | 公開クラス / 型 | 公開関数・主要シンボル / 健全性診断 |
| :--- | :---: | :--- | :--- |
| `order_app/services/processor.py` | 59 | — | `process_order_batch`, `ORDER_STATE_CACHE`, `WEBHOOK_SIGNING_SECRET`（複雑度44・CWE-502/78） |
| `order_app/api/handlers.py` | 25 | — | `app`, `legacy_flask`, `init_cache`, `submit_orders`, `legacy_health`, `ACTIVE_PROMO_CODES` |
| `order_app/domain/pricing.py` | 17 | — | `calculate_legacy_total`（`api.handlers` 循環参照・`infra._internal` 直参照・Docstring不一致） |
| `order_app/constants.py` | 14 | — | `is_supported_currency`, `SUPPORTED_CURRENCIES`, `DEFAULT_TAX_RATE`（`Final` 型・テスト100%） |
| `order_app/schemas.py` | 12 | `LegacyOrderPayload`, `Config` | `check_customer`（Pydantic v1 `@validator`・未注釈 `legacy_flag` で起動クラッシュ） |
| `order_app/infra/gateway.py` | 11 | — | `notify_partner_webhook`（`from math import *`・未宣言 `boto3`・`async` 内同期 `sleep`/`post`） |
| `order_app/infra/_internal.py` | 6 | — | `_compute_handling_fee`（`/tmp/order_spool/fees.dat` 存在有無で手数料分岐） |
| `order_app/**/__init__.py` (計5件) | 5 | — | ルートおよび `api`/`services`/`domain`/`infra` 各パッケージ初期化（各1 LOC） |
| `scripts/legacy_sync.sh` | 106 | — | `check_stage`, `rotate_archives`, `emit_metrics` 等（`/var/tmp` 操作・未使用関数残存） |
