# 2. Architecture & Source Code Structure

`order-dispatch` is an asynchronous FastAPI and Pydantic v2 microservice (`web_api` + `library`) organized as a **Strict 4-Layer Acyclic Clean/Hexagonal Microservice** (`api -> services -> domain + infra`) wired by a thin Composition & Config Root (`main.py`, `settings.py`). Static AST analysis across all 14 Python source files (435 LOC) confirms **0 circular dependencies** and **0 architectural boundary violations**, with the `domain` package completely isolated from FastAPI, Pydantic, and `httpx`.

```drawlib align=center code=fold file=source_module_tree.png caption="Source Directory Tree (14 Modules / 435 LOC) and 5-Layer Dependency Boundaries"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, Panel, TreeNode
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

left_panel = Panel(
    "Source Layout (14 Files / 435 LOC)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    header_height=8.5,
)
left_panel.draw((2.0, 2.0), width=66.0, height=66.0)

dir_style = Styles.PrimaryBold.patch(text_size=10.0)
file_style = Styles.Dark.patch(text_size=9.5)
line_style = Styles.MutedThin

root = TreeNode(
    "src/order_dispatch/",
    text_style=dir_style,
    line_style=line_style,
    line_horizontal_margin=1.8,
    line_horizontal_length=3.5,
    line_vertical_margin=3.75,
)
root.add("main.py (48 LOC) — create_app, lifespan", text_style=file_style)
root.add("settings.py (18 LOC) — ServiceSettings", text_style=file_style)

api_dir = TreeNode("api/", text_style=dir_style)
api_dir.add("routes.py (74 LOC) — /healthz, /v1/orders", text_style=file_style)
api_dir.add("schemas.py (67 LOC) — Pydantic v2 DTOs", text_style=file_style)
root.children.append(api_dir)

svc_dir = TreeNode("services/", text_style=dir_style)
svc_dir.add("dispatcher.py (74 LOC) — OrderDispatcherService", text_style=file_style)
root.children.append(svc_dir)

dom_dir = TreeNode("domain/", text_style=dir_style)
dom_dir.add("models.py (29 LOC) — OrderRecord, OrderLine", text_style=file_style)
dom_dir.add("pricing.py (41 LOC) — integer-cents pricing", text_style=file_style)
root.children.append(dom_dir)

inf_dir = TreeNode("infra/", text_style=dir_style)
inf_dir.add("repository.py (39 LOC) — OrderRepository Port", text_style=file_style)
inf_dir.add("webhook_client.py (35 LOC) — AsyncWebhookClient", text_style=file_style)
root.children.append(inf_dir)

root.draw((5.5, 57.8))

right_panel = Panel(
    "Architectural Layers & Allowed Dependencies",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    header_height=8.5,
)
right_panel.draw((71.0, 2.0), width=73.0, height=66.0)

layers = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    spacing=1.8,
)
layers.add(
    "Composition & Config Root (main.py, settings.py)",
    "Deps: API, Service, Infra | Lifespan & env config",
    badge_text="L0",
    badge_style=Styles.PrimaryFlat,
)
layers.add(
    "API Layer (api/routes.py, api/schemas.py)",
    "Deps: Service, Domain, Config | HTTP & DTOs",
    badge_text="L1",
    badge_style=Styles.WarningFlat,
)
layers.add(
    "Application Service (services/dispatcher.py)",
    "Deps: Domain, Infra | Pricing, webhook & save",
    badge_text="L2",
    badge_style=Styles.SecondaryFlat,
)
layers.add(
    "Infrastructure Layer (infra/repository, webhook)",
    "Deps: Domain | OrderRepository & httpx client",
    badge_text="L3",
    badge_style=Styles.SecondaryFlat,
)
layers.add(
    "Pure Domain Layer (domain/models, pricing)",
    "Deps: NONE | Immutable models & cents pricing",
    badge_text="L4",
    badge_style=Styles.SuccessFlat,
)
layers.draw((74.0, 4.5), width=67.0, height=53.0)

save()
```

## Acyclic Dependency Graph & Thermal Risk Overlay

The diagram below pairs the grounded component dependency graph (`ClassDiagram`) with exact `module_hotspots.risk_score` values (`HeatmapOverlay`). Risk concentrates strictly at the perimeter — `api/routes.py` (`0.36`, unauthenticated `/v1/orders` + `56.0%` line coverage), `Dockerfile` (`0.30`, aged Debian 12.7 base + `pip@24.2` + missing `HEALTHCHECK`), and `main.py` (`0.12`, in-memory default repository + missing security headers/OpenAPI gate) — while the inner service, domain, and adapter core remains uniformly low-risk (`0.06`).

```drawlib align=center code=fold file=architecture_risk_heatmap.png caption="4-Layer Acyclic Class & Component Dependencies with Thermal Risk Overlay (module_hotspots)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=92, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryNeutral,
    edge_style=Styles.Dark,
    edge_text_style=Styles.Dark.patch(text_size=9.5),
    title="order-dispatch — 4-Layer Acyclic Dependencies & Risk Hotspots",
    title_style=Styles.DarkBold.patch(text_size=12.0),
    width=140.0,
    height=74.0,
    margin=4.0,
)

n_main = ClassNode(
    "main.py / settings.py",
    stereotype="Composition Root",
    width=36.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.PrimaryNeutral,
)
n_main.add_method("create_app", "settings", "FastAPI")
n_main.add_method("lifespan", "app", "AsyncGen")

n_routes = ClassNode(
    "api/routes.py + schemas",
    stereotype="API Layer [Risk 0.36]",
    width=38.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.WarningNeutral,
)
n_routes.add_method("create_order", "req", "OrderResp")
n_routes.add_method("get_order", "id", "OrderResp")

n_docker = ClassNode(
    "Dockerfile",
    stereotype="Runtime [Risk 0.30]",
    width=32.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.WarningNeutral,
)
n_docker.add_attribute("base", "py:3.12.6-slim")
n_docker.add_attribute("user", "appuser:10001")

n_svc = ClassNode(
    "OrderDispatcherService",
    stereotype="Application Service",
    width=40.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.SecondaryNeutral,
)
n_svc.add_method("place_order", "cust, tier, lines", "OrderRecord")
n_svc.add_method("find_order", "order_id", "OrderRecord|None")

n_dom = ClassNode(
    "domain/models + pricing",
    stereotype="Pure Domain (0 Deps)",
    width=38.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.SuccessNeutral,
)
n_dom.add_attribute("types", "OrderLine, OrderRecord")
n_dom.add_method("compute_order_total_cents", "", "tuple")

n_repo = ClassNode(
    "infra/repository.py",
    stereotype="Port + Adapter",
    width=36.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.PrimaryNeutral,
)
n_repo.add_method("save", "record", "None")
n_repo.add_method("get", "order_id", "OrderRecord|None")

n_hook = ClassNode(
    "AsyncWebhookClient",
    stereotype="Infra Adapter",
    width=36.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.PrimaryNeutral,
)
n_hook.add_attribute("timeout_sec", "float = 5.0")
n_hook.add_method("notify_order_accepted", "rec", "bool")

diag.add(n_main, xy=(22.0, 62.0))
diag.add(n_routes, xy=(70.0, 62.0))
diag.add(n_docker, xy=(118.0, 62.0))
diag.add(n_svc, xy=(70.0, 38.0))
diag.add(n_dom, xy=(23.0, 14.0))
diag.add(n_repo, xy=(70.0, 14.0))
diag.add(n_hook, xy=(117.0, 14.0))

diag.connect(n_main, n_routes, relationship_type="dependency", start_side="right", end_side="left", label="mounts")
diag.connect(n_main, n_svc, relationship_type="dependency", start_side="bottom", end_side="left", label="wires")
diag.connect(n_routes, n_svc, relationship_type="dependency", start_side="bottom", end_side="top", label="Depends()")
diag.connect(n_svc, n_dom, relationship_type="dependency", start_side="bottom", end_side="top", label="prices")
diag.connect(n_svc, n_repo, relationship_type="dependency", start_side="bottom", end_side="top", label="persists")
diag.connect(n_svc, n_hook, relationship_type="dependency", start_side="right", end_side="top", label="notifies")
diag.connect(n_repo, n_dom, relationship_type="dependency", start_side="left", end_side="right")

overlay = HeatmapOverlay(
    styles=[Styles.SuccessNeutral, Styles.WarningNeutral, Styles.DangerFlat],
    width=140.0,
    height=74.0,
    min_value=0.0,
    max_value=0.40,
    default_radius=17.0,
    max_alpha=0.46,
    show_contour_lines=False,
)
overlay.add_spot(n_routes, value=0.36, radius=19.0)
overlay.add_spot(n_docker, value=0.30, radius=17.0)
overlay.add_spot(n_main, value=0.12, radius=15.0)
overlay.add_spot(n_svc, value=0.06, radius=13.0)
overlay.add_spot(n_dom, value=0.06, radius=13.0)
overlay.add_spot(n_repo, value=0.06, radius=13.0)
overlay.add_spot(n_hook, value=0.06, radius=13.0)

diag.draw((3.0, 13.0))
overlay.draw((3.0, 13.0))
overlay.draw_colorbar(
    (46.0, 4.0),
    text_style=Styles.Dark.patch(text_size=9.5),
    length=54.0,
    thickness=2.4,
    orientation="horizontal",
    num_ticks=5,
    value_format="{:.2f}",
    label="Thermal Risk Score (module_hotspots)",
)

save()
```

## Runtime Execution Flows & Concurrency Model

`order-dispatch` runs on Uvicorn's asyncio event loop with non-blocking `httpx.AsyncClient` outbound calls. Application-scoped dependencies (`ServiceSettings`, `InMemoryOrderRepository`, `AsyncWebhookClient`, and `OrderDispatcherService`) are bound once onto `app.state` during FastAPI's `asynccontextmanager` lifespan. Domain invariant failures raise `PricingError`, missing order lookups return HTTP 404, and outbound webhook `httpx.HTTPError` failures degrade gracefully to `OrderStatus.WEBHOOK_DEFERRED` with structured warning logs.

```drawlib align=center code=fold file=order_execution_flow.png caption="Order Creation, Async Webhook Fallback & Lookup Execution Sequence"
from drawlib.canvas import save, setup
from drawlib.diagrams.sequence import Participant, SequenceDiagram
from drawlib.styles import Styles
from drawlib.text import text

setup(width=156, height=78, dpi=150)

text(
    (78.0, 73.5),
    "POST /v1/orders Async Dispatch & GET /healthz | /v1/orders/{id} Flow",
    style=Styles.DarkBold.patch(text_size=11.5),
)

seq = SequenceDiagram(
    node_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    node_text_style=Styles.DarkBold.patch(text_size=9.5),
    edge_style=Styles.Dark,
    edge_text_style=Styles.Dark.patch(text_size=9.2),
    autonumber=True,
    col_width=23.5,
    step_y=6.0,
    margin=4.0,
)

p_client = seq.add(Participant("HTTP Client", width=21.0, height=8.0, style=Styles.Neutral))
p_api = seq.add(Participant("api/routes.py", width=21.5, height=8.0, style=Styles.WarningNeutral))
p_svc = seq.add(Participant("DispatcherSvc", width=22.0, height=8.0, style=Styles.PrimaryNeutral))
p_dom = seq.add(Participant("domain/pricing", width=22.0, height=8.0, style=Styles.SuccessNeutral))
p_hook = seq.add(Participant("WebhookClient", width=22.0, height=8.0, style=Styles.SecondaryNeutral))
p_repo = seq.add(Participant("OrderRepository", width=22.5, height=8.0, style=Styles.Neutral))

seq.request(p_client, p_api, "POST /v1/orders (DTO)")
seq.request(p_api, p_svc, "place_order(cust, tier, lines)")
seq.request(p_svc, p_dom, "compute_order_total_cents()")
seq.reply(p_dom, p_svc, "(subtotal, total_cents)")
seq.request(p_svc, p_hook, "notify_order_accepted (5.0s)", is_async=True)
seq.reply(p_hook, p_svc, "2xx -> DISPATCHED | Err -> DEFERRED")
seq.request(p_svc, p_repo, "save(final_record)")
seq.reply(p_api, p_client, "201 OrderResp | /healthz -> 200")

seq.draw((78.0, 36.5), align="center")

save()
```

## Source Module Inventory (`14` Files, `435` LOC)

| Module Path (`examples/python/api_fastapi_clean/...`) | Layer | LOC | Public Types | Public Callables | Hotspot Risk |
| :--- | :--- | :---: | :--- | :--- | :---: |
| `src/order_dispatch/main.py` | Composition Root | 48 | — | `lifespan`, `create_app` | `0.12` |
| `src/order_dispatch/settings.py` | Composition Root | 18 | `ServiceSettings` | `load_settings` | `0.06` |
| `src/order_dispatch/api/routes.py` | API Layer | 74 | — | `get_dispatcher`, `get_settings`, `health_check`, `create_order`, `get_order` | `0.36` |
| `src/order_dispatch/api/schemas.py` | API Layer | 67 | `CreateOrderRequest`, `HealthResponse`, `OrderLineInput`, `OrderResponse` | `to_domain_lines`, `to_order_response` | `0.06` |
| `src/order_dispatch/services/dispatcher.py` | Application Service | 74 | `OrderDispatcherService` | — | `0.06` |
| `src/order_dispatch/domain/models.py` | Domain Layer | 29 | `CustomerTier`, `OrderLine`, `OrderRecord`, `OrderStatus` | — | `0.06` |
| `src/order_dispatch/domain/pricing.py` | Domain Layer | 41 | `PricingError` | `calculate_subtotal_cents`, `compute_order_total_cents` | `0.06` |
| `src/order_dispatch/infra/repository.py` | Infrastructure | 39 | `InMemoryOrderRepository`, `OrderRepository` | — | `0.06` |
| `src/order_dispatch/infra/webhook_client.py` | Infrastructure | 35 | `AsyncWebhookClient` | — | `0.06` |
| `src/order_dispatch/__init__.py` (+ 4 package `__init__.py`) | Package Exports | 10 (2 × 5) | — | — | `0.06` |
| `Dockerfile` | Container Build | — | — | Non-root `appuser` (`uid 10001`), `python:3.12.6-slim-bookworm` | `0.30` |
