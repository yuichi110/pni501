# PNI Software Health Diagnostic Report

**Target Repository**: `order-dispatch` (`examples/python/api_fastapi_clean`) — Python 3.11+ Async FastAPI + Pydantic v2 Order Fulfillment Microservice

```drawlib align=center code=fold file=cover_scorecard.png caption="PNI501 Executive Health Scorecard — order-dispatch (Grade S, 94/100)"
from drawlib.canvas import save, setup
from drawlib.shapes import rectangle
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles
from drawlib.text import text
from drawlib.utils import draw_pni_logo

setup(width=146, height=64, dpi=150)

panel = Panel(
    "",
    "",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=Styles.WhiteBold.patch(text_size=13.5),
    header_height=16.0,
    header_align="left",
)
panel.draw((2.0, 2.0), width=142.0, height=60.0)

text(
    (6.5, 56.8),
    "PNI501 Software Health Audit — order-dispatch",
    style=Styles.WhiteBold.patch(text_size=13.5, halign="left"),
)
text(
    (6.5, 50.8),
    "examples/python/api_fastapi_clean  |  FastAPI + Pydantic v2  |  Run wf-f819234f",
    style=Styles.White.patch(text_size=9.8, halign="left"),
)

# Official PNI501 emblem positioned on the right of the dark primary header
draw_pni_logo((135.5, 54.0), width=8.5, dark=True)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.DarkBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
cards.add(
    "94 / 100",
    "Grade S",
    "7-Axis Composite Score",
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=15.0),
    accent_style=Styles.PrimaryFlat,
)
cards.add(
    "12 / 16",
    "Rule Pass Rate",
    "0 FAIL | 4 WARN | 12 PASS",
    accent_style=Styles.SuccessFlat,
)
cards.add(
    "4 / 4",
    "Docker Tests",
    "85.2% Line | 62.5% Branch",
    accent_style=Styles.SecondaryFlat,
)
cards.add(
    "0 CRIT/HIGH",
    "Declared App CVEs",
    "3 Med / 9 Low Total Findings",
    accent_style=Styles.WarningFlat,
)
cards.draw((6.0, 15.0), width=134.0, height=28.0, columns=4)

rectangle(
    (73.0, 8.0),
    width=134.0,
    height=7.5,
    style=Styles.PrimaryNeutral.patch(shape_r=1.2),
)
text(
    (73.0, 8.0),
    "Python >=3.11 (uv)  |  4-Layer Clean Architecture  |  Trivy SCA + Live HTTP DAST (15/19 Probes)  |  2026-11-22 UTC",
    style=Styles.Dark.patch(text_size=9.8),
)

save()
```

| Audit Attribute | Verified Value |
| :--- | :--- |
| **Project / Target Path** | `order-dispatch` (`examples/python/api_fastapi_clean`) |
| **Primary Language & Stack** | `python` (`>=3.11`, `uv_build` + `uv.lock`, FastAPI `>=0.115.0`, Pydantic v2, `httpx`, Uvicorn) |
| **Runtime Archetype** | `web_api`, `library` (14 source modules, 435 LOC, 3 test files) |
| **Workflow ID / Run ID** | `py_api_fastapi_clean` / `wf-f819234f` (PNI Workflow v2, scope=`repo`) |
| **Evaluated At (UTC)** | `2026-11-22T11:29:00.803894+00:00` (`main@d1e02277`, dirty) |
| **Overall Score & Grade** | **94 / 100 (Grade S)** — `12/16` rules passed (`0 FAIL`, `4 WARN`, `12 PASS`) |
| **Container Runtime Verification** | `passed` — Dockerfile & `uv` harness built, `4/4` offline tests (`--network=none`), `85.2%` line cov, `/healthz -> 200` |
| **Security & Penetration Posture** | Trivy `passed` (`0` declared app CRIT/HIGH, `0` secrets, `0` AST sinks) · Live DAST `15/19` probes (`3` findings) |
