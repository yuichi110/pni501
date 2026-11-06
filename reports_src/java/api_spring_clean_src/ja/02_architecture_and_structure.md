# 2. アーキテクチャとソースコード構成

`inventory-service` は **Layered Spring Boot Microservice Architecture（Bootstrap 層 -> API プレゼンテーション層 -> アプリケーションサービス層 -> 純粋ドメイン層 + 外部 HTTP クライアントアダプタ層 + 構成層）** を採用しており、全7ソースファイル（計 `180` LOC・7型・16メソッド/コンストラクタ）が単方向の非循環グラフを形成している。

```drawlib file=arch_tree_and_inventory.png caption="リポジトリディレクトリ構造ツリーとASTモジュールインベントリ (全7ファイル・180 LOC)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=80, dpi=150)

left_panel = Panel(
    "リポジトリ構成ツリー",
    "",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    icon=phosphor.git_branch,
    icon_style=Styles.White,
    header_height=9.5,
)
left_panel.draw(xy=(2, 3), width=48, height=74)

t_style = Styles.Dark.patch(text_size=9.2)
b_style = Styles.PrimaryBold.patch(text_size=9.2)
root = TreeNode(
    "api_spring_clean/",
    text_style=b_style,
    line_style=Styles.Neutral,
    line_horizontal_margin=0.9,
    line_horizontal_length=2.0,
    line_vertical_margin=3.6,
)
root.add("pom.xml / Dockerfile / mvnw", text_style=Styles.DangerBold.patch(text_size=9.2))
root.add(".github/ (ci.yml, dependabot)", text_style=t_style)
root.add("README.md / SECURITY.md", text_style=t_style)
src_node = root.add("src/main/.../inventory/", text_style=b_style)
src_node.add("InventoryApplication (12 LOC)", text_style=t_style)
src_node.add("api/InventoryController (33)", text_style=Styles.DangerBold.patch(text_size=9.2))
src_node.add("service/InventoryService (43)", text_style=Styles.WarningBold.patch(text_size=9.2))
src_node.add("client/SupplierRestClient (43)", text_style=Styles.WarningBold.patch(text_size=9.2))
src_node.add("domain/StockItem, Policy (37)", text_style=t_style)
src_node.add("config/SupplierProperties (12)", text_style=t_style)
tst_node = root.add("src/test/.../inventory/", text_style=b_style)
tst_node.add("ServiceTest / PolicyTest (2)", text_style=t_style)
root.draw(xy=(4.2, 65.5))

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.2),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.3),
    border_style=Styles.NeutralThin,
)
rows = [
    ["モジュール (相対パス要約)", "LOC", "公開型・メソッドと主要責務"],
    ["InventoryApplication.java", "12", "InventoryApplication.main\nSpring起動・SupplierProperties有効化"],
    ["api/\nInventoryController.java", "33", "getItem, reserveItem\nGET /{sku}・POST /{sku}/reserve 公開"],
    ["service/\nInventoryService.java", "43", "upsertItem, findBySku, reserveStock\n在庫引当更新と補充判定オーケストレーション"],
    ["client/\nSupplierRestClient.java", "43", "requestRestock (HttpClient)\nタイムアウト付 POST /v1/restock 送信"],
    ["domain/\nStockItem.java", "22", "availableUnits, withAdditionalReservation\nJava 21 record による不変在庫スナップショット"],
    ["domain/\nReorderPolicy.java", "15", "requiresRestock, recommendedOrderQuantity\n発注点判定および推奨補充数量の純粋計算"],
    ["config/\nSupplierProperties.java", "12", "SupplierProperties, defaults\ninventory.supplier.* 外部設定バインド"],
]
tbl.draw_flexible(
    xy=(52, 77),
    column_widths=[30, 9, 53],
    row_heights=[7.5, 9.2, 9.5, 9.8, 9.5, 9.5, 9.5, 9.2],
    data=rows,
)

save()
```

## Spring レイヤー依存グラフとモジュールリスク密度（`HeatmapOverlay`）

AST 内部 import グラフ解析により、循環依存（`circular_dependencies = 0`）および上位層への逆依存（`boundary_violations = 0`）はゼロであることが検証された。`StockItem` と `ReorderPolicy` は外部ライブラリへの依存を持たない純粋ドメインモデルとして隔離されている。一方、指摘密度に基づくホットスポット（`module_hotspots`）では、無認証・例外変換・セキュリティヘッダ指摘（DAST 含む）が重なる `InventoryController.java`（`risk_score=0.64`）を筆頭に、推移 CVE を抱える `pom.xml`（`0.45`）、JSON 文字列連結と低カバレッジが重なる `SupplierRestClient.java`（`0.40`）、および未知 SKU `HTTP 500`（`CWE-755`）・競合更新課題を持つ `InventoryService.java`（`0.36`）にリスクが集中している。

```drawlib file=arch_layer_hotspot_diagram.png caption="Spring Boot レイヤー依存関係グラフとモジュールホットスポット (HeatmapOverlay)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=8.8),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=124,
    height=66,
    title="inventory-service クラス依存グラフ × リスクホットスポット",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)

n_app = ClassNode("InventoryApplication", stereotype="Bootstrap (12 LOC)", width=35, row_height=3.2)
n_app.add_method("main", "args", "void")

n_ctrl = ClassNode("InventoryController", stereotype="API Layer (33 LOC)", width=41, row_height=3.2, header_style=Styles.Danger)
n_ctrl.add_method("getItem", "sku", "ResponseEntity")
n_ctrl.add_method("reserveItem", "sku, qty", "ResponseEntity")

n_svc = ClassNode("InventoryService", stereotype="Service Layer (43 LOC)", width=39, row_height=3.2, header_style=Styles.Warning)
n_svc.add_attribute("inventoryStore", "ConcurrentMap")
n_svc.add_method("reserveStock", "sku, qty", "StockItem")

n_cli = ClassNode("SupplierRestClient", stereotype="Client Adapter (43 LOC)", width=36, row_height=3.2, header_style=Styles.Danger)
n_cli.add_attribute("httpClient", "HttpClient")
n_cli.add_method("requestRestock", "sku, qty", "boolean")

n_pol = ClassNode("ReorderPolicy", stereotype="Domain Policy (15 LOC)", width=35, row_height=3.2, header_style=Styles.Success)
n_pol.add_method("requiresRestock", "item", "boolean")
n_pol.add_method("recommendedOrderQty", "item, min", "int")

n_item = ClassNode("StockItem", stereotype="Domain Record (22 LOC)", width=40, row_height=3.2, header_style=Styles.Success)
n_item.add_attribute("sku / onHand / reserved", "record")
n_item.add_method("withAdditionalResv", "qty, now", "StockItem")

n_cfg = ClassNode("SupplierProperties", stereotype="Config Record (12 LOC)", width=38, row_height=3.2)
n_cfg.add_attribute("baseUrl / timeoutSec", "record")

diag.add(n_app, xy=(22, 51))
diag.add(n_ctrl, xy=(70, 51))
diag.add(n_pol, xy=(22, 31))
diag.add(n_svc, xy=(63, 31))
diag.add(n_cli, xy=(103, 31))
diag.add(n_item, xy=(36, 11))
diag.add(n_cfg, xy=(90, 11))

diag.connect(n_app, n_cfg, directed=True)
diag.connect(n_ctrl, n_svc, directed=True)
diag.connect(n_ctrl, n_item, directed=True)
diag.connect(n_svc, n_pol, directed=True)
diag.connect(n_svc, n_item, directed=True)
diag.connect(n_svc, n_cli, directed=True)
diag.connect(n_svc, n_cfg, directed=True)
diag.connect(n_pol, n_item, directed=True)
diag.connect(n_cli, n_cfg, directed=True)
diag.draw(xy=(3, 4))

ov = HeatmapOverlay(
    min_style=Styles.Success,
    max_style=Styles.Danger,
    width=124,
    height=66,
    min_value=0.0,
    max_value=0.70,
    default_radius=13.0,
    max_alpha=0.28,
    show_contour_lines=True,
)
ov.add_spot(xy=(70, 51), value=0.64, radius=15.0)
ov.add_spot(xy=(103, 31), value=0.40, radius=14.0)
ov.add_spot(xy=(63, 31), value=0.36, radius=13.0)
ov.add_spot(xy=(90, 11), value=0.15, radius=11.0)
ov.add_spot(xy=(36, 11), value=0.06, radius=10.0)
ov.add_spot(xy=(22, 31), value=0.06, radius=10.0)
ov.draw(xy=(3, 4))
ov.draw_colorbar(
    xy=(131, 13),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=44.0,
    thickness=2.6,
    orientation="vertical",
    label="Risk",
)

save()
```

## リクエスト実行フローと状態・並行制御モデル

本サービスは `GET /api/v1/items/{sku}`（在庫照会フロー）と `POST /api/v1/items/{sku}/reserve?quantity={n}`（在庫引当・条件付きサプライヤー補充フロー）の2系統の HTTP エントリポイントを持つ。状態は `InventoryService` 内のインメモリ `ConcurrentHashMap<String, StockItem>` に保持され、外部サプライヤー通信では `IOException` や `InterruptedException`（割り込みフラグ復元付き）を捕捉して `false` へグレースフルに縮退する設計となっている。

```drawlib file=arch_request_execution_flow.png caption="POST /api/v1/items/{sku}/reserve 在庫引当・サプライヤー補充実行フロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

flow = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=9.2),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=2.5,
)
flow.add(
    "1. HTTP受付・検証",
    "InventoryController\n@Min(1) 数量引数を受付",
    badge_text="S1",
    style=Styles.PrimaryNeutral,
    icon=phosphor.terminal_window,
    icon_style=Styles.Primary,
)
flow.add(
    "2. 不変ドメイン引当",
    "StockItem.withAdditional\n在庫不足時は例外送出",
    badge_text="S2",
    style=Styles.Neutral,
    icon=phosphor.file_text,
    icon_style=Styles.Primary,
)
flow.add(
    "3. 発注点ポリシー判定",
    "ReorderPolicy計算\n残数<=reorderPoint判定",
    badge_text="S3",
    style=Styles.PrimaryNeutral,
    icon=phosphor.chart_bar,
    icon_style=Styles.Primary,
)
flow.add(
    "4. 外部補充POST・応答",
    "SupplierRestClient送信\nSLF4J記録後 200 OK返却",
    badge_text="S4",
    style=Styles.Neutral,
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
    badge_style=Styles.Success,
)
flow.draw(xy=(3, 5), width=140, height=48)

save()
```
