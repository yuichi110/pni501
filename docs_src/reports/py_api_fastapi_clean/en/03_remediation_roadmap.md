# 3. Recommended Remediation Roadmap

Because `order-dispatch` already achieves **Grade S (94/100)** with zero critical or high application vulnerabilities (`0` `P0` blockers), remediation follows a focused two-wave sequence: two **P1** production security actions that close the live `CWE-306` authentication gap and base-image OS/pip CVE debt, followed by three **P2** hardening and test-coverage improvements that unlock multi-replica stateless scaling and lift branch coverage above 80%.

```drawlib align=center code=fold file=remediation_roadmap.png caption="Phased Remediation Roadmap (P1 Security Hardening -> P2 Production Polish)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=74, dpi=150)

text(
    (73.0, 69.5),
    "order-dispatch — Phased Production Hardening Roadmap (0 P0 | 2 P1 | 3 P2)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    direction="vertical",
    card_shape="rounded_rect",
    spacing=2.4,
)
rm.add(
    "Enforce OAuth2/JWT or mTLS Auth & Tenant AuthZ on /v1/orders",
    "routes.py | Add FastAPI Security/Depends() guard to resolve live DAST CWE-306 & line 73 TODO",
    badge_text="P1-1",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
)
rm.add(
    "Refresh Base Image, Multi-Stage Build (No pip) & Add HEALTHCHECK",
    "Dockerfile | Patch python:3.12.x-slim, strip pip@24.2 from runtime venv, clear DS-0026",
    badge_text="P1-2",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
)
rm.add(
    "Add Durable OrderRepository Adapter for Multi-Replica Prod",
    "main.py, repository.py | Wire PostgreSQL/Redis adapter via ServiceSettings (12-Factor VI)",
    badge_text="P2-3",
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    badge_style=Styles.PrimaryFlat,
)
rm.add(
    "Add HTTP Security Headers & Gate /openapi.json in Production",
    "main.py | Set X-Content-Type-Options: nosniff, X-Frame-Options: DENY; openapi_url=None in prod",
    badge_text="P2-4",
    style=Styles.Neutral.patch(shape_r=1.8),
    badge_style=Styles.SecondaryFlat,
)
rm.add(
    "Expand FastAPI TestClient & httpx MockTransport Branch Tests",
    "test_routes.py, routes.py, webhook_client.py | Cover 200/404, lifespan, HTTPError (branch >=80%)",
    badge_text="P2-5",
    style=Styles.Neutral.patch(shape_r=1.8),
    badge_style=Styles.SecondaryFlat,
)
rm.draw((4.0, 3.0), width=138.0, height=62.5)

save()
```

## Action Plan Traceability Matrix

Each action item below maps directly to verified source files, PNI rules, CWE/CVE identifiers, and concrete production outcomes.

```drawlib align=center code=fold file=remediation_traceability_table.png caption="Action Plan Traceability Matrix — Priority, Target Files, Rules/CVEs & Expected Impact"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=146, height=64, dpi=150)

text(
    (73.0, 60.0),
    "Remediation Action Plan — File & Rule/CVE Traceability",
    style=Styles.DarkBold.patch(text_size=11.5),
)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
    border_style=Styles.MutedThin,
    has_header=True,
)
tbl.set_style_cell_evenodd(
    Colors.White,
    Styles.Dark.patch(text_size=9.5),
    Colors.Neutral,
    Styles.Dark.patch(text_size=9.5),
)
tbl.set_style_cell_header(Colors.Primary, Styles.WhiteBold.patch(text_size=9.8))
tbl.set_style_cell(
    Styles.WarningNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2],
    columns=[0],
)
tbl.set_style_cell(
    Styles.PrimaryNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=[3, 4, 5],
    columns=[0],
)

data = [
    ["Prio", "Action", "Target Files", "Related Rules / IDs", "Expected Impact"],
    [
        "P1",
        "Auth & tenant authZ\non /v1/orders",
        "api/routes.py",
        "common/\nsecurity_vulnerability,\nCWE-306",
        "Blocks unauth order\nwrites & enumeration",
    ],
    [
        "P1",
        "Refresh base image,\nno pip, HEALTHCHECK",
        "Dockerfile",
        "SEC-01/02, CVE-2026-\n42010 / 31789 / 8643",
        "Drops 6 pip CVEs, OS\nCRITs & DS-0026",
    ],
    [
        "P2",
        "Durable prod\nOrderRepository",
        "main.py,\ninfra/repository.py",
        "common/\ntwelve_factor",
        "Stateless multi-replica\nscale-out (12F VI)",
    ],
    [
        "P2",
        "Security headers &\nprod OpenAPI gate",
        "main.py",
        "SEC-06, CWE-693,\nCWE-200",
        "Closes live DAST\nheader/schema gaps",
    ],
    [
        "P2",
        "TestClient & httpx\nMockTransport tests",
        "test_routes.py,\nroutes.py, webhook",
        "common/\nruntime_verification",
        "Lifts branch cov from\n62.5% to >=80%",
    ],
]

tbl.draw_flexible(
    (2.0, 56.5),
    column_widths=[10.0, 32.0, 28.0, 40.0, 32.0],
    row_heights=[7.0, 9.2, 9.2, 9.2, 9.2, 9.2],
    data=data,
    align="top_left",
)

save()
```

### Detailed Engineering Specifications (`P1 -> P2`)

| Priority | Category | Action & Engineering Specification | Target Files | Related Rules & IDs | Expected Impact |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **P1** | `security` | **Enforce authentication and tenant authorization on `/v1/orders` endpoints**: Introduce an OAuth2/JWT or mTLS caller principal `Depends()` dependency on `POST /v1/orders` and `GET /v1/orders/{order_id}` to resolve `CWE-306` and the `TODO(security)` marker at line 73. | `src/order_dispatch/api/routes.py` | `common/security_vulnerability`, `CWE-306` | Prevents unauthorized order creation and cross-tenant order enumeration. |
| **P1** | `security` | **Refresh Dockerfile base image, adopt multi-stage build without `pip`, and add `HEALTHCHECK`**: Update `python:3.12.6-slim-bookworm` to the latest patched 3.12 slim digest, copy only the built virtual environment into a clean runtime stage (eliminating `pip@24.2` CVEs), and add a `HEALTHCHECK` probing `/healthz`. | `Dockerfile` | `common/security_vulnerability`, `SEC-01`, `SEC-02`, `CVE-2026-42010`, `CVE-2026-31789`, `CVE-2026-8643` | Eliminates all 6 `pip` CVEs, resolves patchable Debian OS CRITICAL CVEs, and clears Trivy `DS-0026`. |
| **P2** | `architecture` | **Add durable `OrderRepository` adapter for multi-replica production deployments**: Implement a persistent `OrderRepository` adapter (PostgreSQL/Redis) wired via `ServiceSettings` when `env == "prod"` so container processes remain strictly stateless. | `src/order_dispatch/main.py`, `src/order_dispatch/infra/repository.py` | `common/twelve_factor` | Enables zero-data-loss restarts and horizontal replica scaling under 12-Factor VI. |
| **P2** | `security` | **Add HTTP security headers middleware and gate `/openapi.json` in production**: Register lightweight Starlette HTTP middleware emitting `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY`, and set `openapi_url=None` when `settings.env == "prod"`. | `src/order_dispatch/main.py` | `common/security_vulnerability`, `SEC-06`, `CWE-693`, `CWE-200` | Resolves live DAST `CWE-693` and `CWE-200` baseline hardening findings. |
| **P2** | `testing` | **Add FastAPI `TestClient` and `httpx` `MockTransport` tests for HTTP/lifespan branches**: Exercise `/healthz`, `POST /v1/orders`, `GET /v1/orders/{id}` (200 and 404), lifespan startup/shutdown, and `httpx.HTTPError` fallback via `MockTransport`. | `tests/test_routes.py`, `src/order_dispatch/api/routes.py`, `src/order_dispatch/infra/webhook_client.py` | `common/runtime_verification` | Raises measured branch coverage from `62.5%` to `>=80%` and closes HTTP boundary gaps. |
