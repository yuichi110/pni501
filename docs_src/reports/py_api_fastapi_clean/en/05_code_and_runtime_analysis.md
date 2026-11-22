# 5. Deep Dive: Code Quality, Testing & Runtime

Static AST analysis confirms uniform **100.0%** compliance across import hygiene, type safety, and Google-style docstrings with **0** complexity hotspots, **0** circular dependencies, and **0** missing I/O timeouts across all 14 modules (435 LOC). Isolated Docker verification passed all four runtime gates — building cleanly, passing `4/4` offline tests (`--network=none`), achieving **85.2% line coverage** (`178/209` statements), and booting ASGI cleanly (`/healthz -> 200`) — while exposing localized branch-coverage gaps (`62.5%` overall) at the HTTP and outbound webhook boundaries (`webhook_client.py` `55.6%`, `routes.py` `56.0%`, `main.py` `67.9%`).

```drawlib align=center code=fold file=module_quality_heatmap.png caption="Module × Quality Dimension Fitness Matrix (0-100%, Highlighting Boundary Coverage & Auth Gaps)"
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

## Container Runtime Verification & Module Coverage Breakdown

Unit tests isolate `OrderDispatcherService` with an explicit `_StubWebhookClient`, ensuring deterministic offline execution (`--network=none`, `5.05s`) and **100.0% line coverage** across `services/dispatcher.py`, `domain/models.py`, `infra/repository.py`, and `settings.py`. However, because `tests/test_routes.py` does not invoke FastAPI `TestClient` routes or `httpx.MockTransport` failure branches, `webhook_client.py` (`55.6%`), `routes.py` (`56.0%`, `0.0%` branch), and `main.py` lifespan (`67.9%`, `0.0%` branch) pull overall branch coverage down to `62.5%`. Note that the ASGI smoke check (`/healthz -> 200`, `2.25s`) succeeded cleanly with one minor `StarletteDeprecationWarning` regarding `httpx` in `starlette.testclient`.

```drawlib align=center code=fold file=runtime_coverage_breakdown.png caption="Container Runtime Gate Outcomes and Measured Line Coverage by Module (Lowest-First)"
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

## Static AST, Maintainability & Operational Readiness Metrics

| Metric Group | Indicator | Measured Value | Target / Status |
| :--- | :--- | :---: | :---: |
| **Codebase Footprint** | Source files / LOC / Classes / Functions | `14` / `435` / `14` / `23` | Clean microservice scale |
| **Static Quality Coverage** | Import hygiene / Type safety / Docstrings / Static module test cov | `100.0%` / `100.0%` / `100.0%` / `100.0%` | **PASS** (100% across all four) |
| **SIG Maintainability** | Complex funcs / Excessive params / Global state / Circular deps | `0` / `0` / `0` / `0` | **PASS** |
| **Hygiene & Typing** | Bug-risk idioms / Undeclared deps / Weak `Any` / Version mismatches | `0` / `0` / `0` / `0` | **PASS** (`py.typed` present) |
| **12-Factor / SRE PRR** | Missing I/O timeouts / Scattered env reads / Unstructured `print` | `0` / `0` / `0` | **PASS** (`5.0s` timeout, `pydantic-settings`) |
| **Container Runtime** | Build / Offline pytest (`--network=none`) / ASGI smoke (`/healthz`) | `passed` / `4/4` (`5.05s`) / `200` (`2.25s`) | **PASS** (1 minor Starlette deprecation note) |

## Per-Module Measured Coverage Details (`pytest-cov`)

| Module Path | Line Cov | Branch Cov | Covered / Total Stmts | Uncovered Lines (`missing_lines_preview`) | Recommended Test Addition |
| :--- | :---: | :---: | :---: | :--- | :--- |
| `src/order_dispatch/infra/webhook_client.py` | **55.6%** | `n/a` | `10 / 18` | `36, 41-47` | `httpx.MockTransport` 2xx success & `httpx.HTTPError` fallback |
| `src/order_dispatch/api/routes.py` | **56.0%** | **0.0%** | `14 / 25` | `29-30, 42-43, 56, 74, 79, 96-98` | FastAPI `TestClient` for `/healthz`, `POST /v1/orders`, `GET` 200 & 404 |
| `src/order_dispatch/main.py` | **67.9%** | **0.0%** | `19 / 28` | `30-34, 38, 43-45` | `with TestClient(create_app())` exercising `lifespan` startup/shutdown |
| `src/order_dispatch/api/schemas.py` | `94.6%` | `50.0%` | `35 / 37` | `32, 90` | Blank-SKU whitespace validation error & `to_order_response()` |
| `src/order_dispatch/domain/pricing.py` | `95.2%` | `90.0%` | `20 / 21` | `49` | Out-of-range `vip_discount_rate` (`<0.0` or `>0.5`) `PricingError` |
| `src/order_dispatch/services/dispatcher.py` | `100.0%` | `n/a` | `26 / 26` | `[]` | Fully covered (`_StubWebhookClient`) |
| `src/order_dispatch/domain/models.py` | `100.0%` | `n/a` | `24 / 24` | `[]` | Fully covered |
| `src/order_dispatch/infra/repository.py` | `100.0%` | `n/a` | `13 / 13` | `[]` | Fully covered |
| `src/order_dispatch/settings.py` + 5 `__init__.py` | `100.0%` | `n/a` | `17 / 17` | `[]` | Fully covered |
