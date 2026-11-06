# 2. アーキテクチャとソースコード構成

`acme/order-fulfillment-api` は **5層単方向サービス・リポジトリアーキテクチャ（HTTP Entry & Routing 層 -> Thin Controller 層 -> Readonly Domain Service 層 -> Parameterized PDO Repository 層 -> Immutable Entity & Input DTO 層）** を採用しており、全7ソースファイル（計 `252` LOC・5クラス・16関数/メソッド）が完全な有向非巡回グラフ（`circular_dependencies = 0`・`boundary_violations = 0`）を構成している。

```drawlib file=arch_tree_and_inventory.png caption="図2-1: リポジトリディレクトリ構造ツリーとASTモジュールインベントリ (全7ソースファイル・252 LOC)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=82, dpi=150)

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
left_panel.draw(xy=(2, 3), width=48, height=76)

t_style = Styles.Dark.patch(text_size=9.0)
b_style = Styles.PrimaryBold.patch(text_size=9.2)
root = TreeNode(
    "api_laravel_clean/",
    text_style=b_style,
    line_style=Styles.Neutral,
    line_horizontal_margin=0.9,
    line_horizontal_length=2.0,
    line_vertical_margin=3.5,
)
root.add("composer.json / composer.lock", text_style=t_style)
root.add("Dockerfile / .dockerignore", text_style=Styles.WarningBold.patch(text_size=9.0))
root.add(".github/workflows/ci.yml", text_style=t_style)
root.add("config/fulfillment.php / artisan", text_style=t_style)
app_node = root.add("app/ (PSR-4: App\\)", text_style=b_style)
app_node.add("Http/Controllers/OrderController (32)", text_style=Styles.SuccessBold.patch(text_size=9.0))
app_node.add("Services/OrderFulfillmentService (50)", text_style=Styles.SuccessBold.patch(text_size=9.0))
app_node.add("Repositories/OrderRepository (63)", text_style=Styles.SuccessBold.patch(text_size=9.0))
app_node.add("Models/OrderRecord (38 LOC)", text_style=t_style)
app_node.add("DTO/OrderPayload (33 LOC)", text_style=t_style)
web_node = root.add("routes/ & public/ & tests/", text_style=b_style)
web_node.add("routes/api.php (8) / index.php (28)", text_style=t_style)
web_node.add("OrderFulfillmentServiceTest (8 tests)", text_style=t_style)
root.draw(xy=(4.2, 68.0))

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.0),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.3),
    border_style=Styles.NeutralThin,
)
rows = [
    ["モジュール相対パス", "LOC", "公開クラス・メソッドと主要責務"],
    ["public/index.php", "28", "buildHealthResponse\n/up・/healthz Liveness/Readiness JSON応答"],
    ["routes/api.php", "8", "Route::middleware('auth:sanctum')\nGET /orders・POST /orders 認証ルート定義"],
    ["app/Http/Controllers/\nOrderController.php", "32", "OrderController::store, listRecent\nfinal readonly 薄型HTTPコントローラ"],
    ["app/Services/\nOrderFulfillmentService.php", "50", "createOrder, listRecentOrders, verifyWebhookSignature\n10%割引計算・CSPRNG採番・hash_equals検証"],
    ["app/Repositories/\nOrderRepository.php", "63", "OrderRepository::save, findRecent\nPDOプリペアドINSERT・上限100件SELECT"],
    ["app/Models/\nOrderRecord.php", "38", "OrderRecord::toArray, fillableColumns\nreadonly属性エンティティ・$fillable明示許可"],
    ["app/DTO/\nOrderPayload.php", "33", "OrderPayload::__construct, fromArray\nSKU正規表現・数量1..1000検証のreadonly DTO"],
]
tbl.draw_flexible(
    xy=(52, 79),
    column_widths=[32, 9, 51],
    row_heights=[7.5, 9.5, 9.5, 9.8, 10.2, 9.8, 9.8, 9.8],
    data=rows,
)

save()
```

## 観点1：5層レイヤード構造・単方向依存グラフとリスク密度（`HeatmapOverlay`）

AST 内部 Import グラフ解析により、`routes/api.php` -> `OrderController` -> `OrderFulfillmentService` -> `OrderRepository` -> `OrderRecord`（および末端 DTO `OrderPayload`）の完全な下向き単方向依存が確認された。`module_hotspots` の実測リスクスコアもアプリケーション各モジュールで `0.02〜0.06` と極めて低く、相対的なホットスポットは Debian 12 OS ベースイメージ更新および開発用 `php -S` エントリポイント（`TRACE` 応答）を持つ `Dockerfile`（`risk_score = 0.27`）のみに局在している。

```drawlib file=arch_layer_hotspot_diagram.png caption="図2-2 [観点1]: 5層単方向クラス依存グラフとモジュール別リスクホットスポット (HeatmapOverlay)"
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
    title="order-fulfillment-api 5層単方向依存グラフ × ホットスポット (0.00 - 0.30)",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)

n_pub = ClassNode("public/index.php", stereotype="Probe Entry (28 LOC)", width=35, row_height=3.2, header_style=Styles.PrimaryFlat)
n_pub.add_method("buildHealthResponse", "uriPath", "array")

n_rte = ClassNode("routes/api.php", stereotype="Sanctum Route (8 LOC)", width=36, row_height=3.2, header_style=Styles.PrimaryFlat)
n_rte.add_attribute("auth:sanctum", "GET/POST /orders")

n_dkr = ClassNode("Dockerfile", stereotype="Container IaC (21 L)", width=33, row_height=3.2, header_style=Styles.Warning)
n_dkr.add_attribute("php:8.3.12-bookworm", "UID 10001")

n_ctl = ClassNode("OrderController", stereotype="Controller (32 LOC)", width=39, row_height=3.2, header_style=Styles.Success)
n_ctl.add_method("store", "payload, price", "array")
n_ctl.add_method("listRecent", "limit", "array")

n_svc = ClassNode("OrderFulfillmentService", stereotype="Domain Service (50 LOC)", width=43, row_height=3.2, header_style=Styles.Success)
n_svc.add_method("createOrder", "payload, price", "OrderRecord")
n_svc.add_method("verifyWebhookSignature", "body, sig, key", "bool")

n_dto = ClassNode("OrderPayload", stereotype="Readonly DTO (33 LOC)", width=36, row_height=3.2, header_style=Styles.Success)
n_dto.add_attribute("customerId / sku / qty", "readonly")

n_rep = ClassNode("OrderRepository", stereotype="PDO Repo (63 LOC)", width=39, row_height=3.2, header_style=Styles.Success)
n_rep.add_method("save / findRecent", "PDO prepared", "list")

n_rec = ClassNode("OrderRecord", stereotype="Entity (38 LOC)", width=37, row_height=3.2, header_style=Styles.Success)
n_rec.add_attribute("$fillable (6 cols)", "readonly props")

diag.add(n_dkr, xy=(22, 54))
diag.add(n_pub, xy=(63, 54))
diag.add(n_rte, xy=(105, 54))
diag.add(n_dto, xy=(23, 33))
diag.add(n_svc, xy=(66, 31))
diag.add(n_ctl, xy=(106, 34))
diag.add(n_rec, xy=(38, 11))
diag.add(n_rep, xy=(88, 11))

diag.connect(n_dkr, n_pub, directed=True)
diag.connect(n_rte, n_ctl, directed=True)
diag.connect(n_ctl, n_svc, directed=True)
diag.connect(n_ctl, n_dto, directed=True)
diag.connect(n_svc, n_dto, directed=True)
diag.connect(n_svc, n_rep, directed=True)
diag.connect(n_svc, n_rec, directed=True)
diag.connect(n_rep, n_rec, directed=True)
diag.draw(xy=(3, 4))

ov = HeatmapOverlay(
    min_style=Styles.Success,
    max_style=Styles.Warning,
    width=124,
    height=66,
    min_value=0.0,
    max_value=0.30,
    default_radius=12.0,
    max_alpha=0.25,
    show_contour_lines=True,
)
ov.add_spot(xy=(22, 54), value=0.27, radius=14.0)
ov.add_spot(xy=(63, 54), value=0.06, radius=11.0)
ov.add_spot(xy=(105, 54), value=0.06, radius=11.0)
ov.add_spot(xy=(106, 34), value=0.06, radius=11.0)
ov.add_spot(xy=(66, 31), value=0.06, radius=11.0)
ov.add_spot(xy=(23, 33), value=0.06, radius=11.0)
ov.add_spot(xy=(88, 11), value=0.02, radius=10.0)
ov.add_spot(xy=(38, 11), value=0.02, radius=10.0)
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

## 観点2：`POST /api/orders` 実行・PDO 永続化・Webhook HMAC データフロー

注文作成リクエストは、(1) `auth:sanctum` ミドルウェア境界通過後、(2) `OrderPayload` での SKU 正規表現 `/^[A-Z0-9-]{3,32}$/`・数量 `1..1000` の不変 DTO 検証、(3) `OrderFulfillmentService::createOrder` における整数セント金額計算（10個以上で10%割引）と `random_bytes(8)` による CSPRNG 注文 ID 採番、(4) `OrderRepository::save` の PDO プリペアド `INSERT` 永続化と HTTP `201` 応答の4段階で完結する。また配送キャリア Webhook 検証では `verifyWebhookSignature` が `hash_hmac('sha256', ...)` を `hash_equals()` で定数時間比較する。

```drawlib file=arch_request_execution_flow.png caption="図2-3 [観点2]: POST /api/orders 注文作成・割引算出・PDO SQLite 永続化パイプライン"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=56, dpi=150)

flow = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=9.1),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    direction="horizontal",
    spacing=2.5,
)
flow.add(
    "1. Sanctum & DTO検証",
    "OrderPayload::fromArray\nSKU正規表現・数量1..1000",
    badge_text="Boundary",
    style=Styles.PrimaryNeutral,
    icon=phosphor.shield_check,
    icon_style=Styles.Primary,
)
flow.add(
    "2. 薄型Controller委譲",
    "OrderController::store\n単価・DTOをServiceへ渡す",
    badge_text="HTTP",
    style=Styles.Neutral,
    icon=phosphor.arrows_left_right,
    icon_style=Styles.Primary,
)
flow.add(
    "3. 10%割引・CSPRNG採番",
    "qty>=10で10%割引(cents)\nrandom_bytes(8) ord_生成",
    badge_text="Domain",
    style=Styles.PrimaryNeutral,
    icon=phosphor.calculator,
    icon_style=Styles.Primary,
)
flow.add(
    "4. PDO保存・201応答",
    "prepare/execute INSERT\nOrderRecord::toArray返却",
    badge_text="SQLite",
    style=Styles.SuccessNeutral,
    icon=phosphor.database,
    icon_style=Styles.Success,
    badge_style=Styles.Success,
)
flow.draw(xy=(3, 4), width=140, height=48)

save()
```

## 観点3：コンテナ実行基盤（非 root UID 10001）と GitHub Actions CI/CD トポロジ

デプロイ・検証環境は、最小権限（`permissions: contents: read`）かつ 40文字 SHA ピン留め（`actions/checkout@11bd7190...`）された GitHub Actions CI パイプラインと、`php:8.3.12-cli-bookworm` 上で非特権ユーザ `appuser`（`UID 10001`, `/usr/sbin/nologin`）として稼働するコンテナランタイムで構成される。環境変数（`APP_NAME`, `DB_DSN`）は `config/fulfillment.php` のみに集約されている。

```drawlib file=arch_container_cicd_topology.png caption="図2-4 [観点3]: 非root Dockerコンテナ実行環境 (:8080 / PDO SQLite) と SHA固定 GitHub Actions CI トポロジ"
from drawlib.canvas import save, setup
from drawlib.smartarts import Panel
from drawlib.styles import Styles
from drawlib.utils import connect, service_card

setup(width=146, height=58, dpi=150)

Panel(
    "コンテナ実行境界 (UID 10001 appuser) & 最小権限 CI/CD パイプライン構成",
    "Dockerfile + .github/workflows/ci.yml",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.2),
    header_height=9.5,
).draw(xy=(2, 3), width=142, height=52)

service_card((22, 34), "GitHub Actions CI", "SHA固定 / contents:read", width=32, height=13, style=Styles.PrimaryFlat)
service_card((22, 14), "HTTP Client / Carrier", "Bearer + HMAC-SHA256", width=32, height=13, style=Styles.Dark)
service_card((74, 34), "PHP 8.3 Container", "UID 10001 / :8080", width=34, height=13, style=Styles.Success)
service_card((74, 14), "HealthCHECK Probe", "GET /up & /healthz (3s)", width=34, height=13, style=Styles.PrimaryFlat)
service_card((124, 34), "PDO SQLite Engine", "DB_DSN / ERRMODE_EXC", width=31, height=13, style=Styles.Primary)
service_card((124, 14), "config/fulfillment", "APP_NAME / Timeout 5s", width=31, height=13, style=Styles.Warning)

connect((38, 34), (57, 34), label="phpunit")
connect((38, 14), (57, 29), label="Sanctum")
connect((74, 20.5), (74, 27.5), label="200 OK")
connect((91, 34), (108.5, 34), label="Prepared")
connect((108.5, 19), (91, 29), label="getenv集約")

save()
```
