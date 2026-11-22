# 6. Deep Dive: Security, Supply Chain & API Surface

Security verification combines Trivy filesystem + container image SCA, static AST sink/secret inspection, and live HTTP DAST penetration testing (`19` probes against the running Docker container). Crucially, `order-dispatch` carries **zero CVEs in its five declared application dependencies** (`fastapi`, `pydantic`, `pydantic-settings`, `uvicorn`, `httpx`), **zero hardcoded or committed secrets**, and **zero dangerous AST code sinks**; all container vulnerability debt originates from the aged `python:3.12.6-slim-bookworm` base image (`6` build-time `pip@24.2` CVEs + `612` Debian 12.7 OS CVEs), while live HTTP DAST verified three defense-in-depth findings (`CWE-306`, `CWE-200`, `CWE-693`) with zero critical or high exploitable flaws.

```drawlib align=center code=fold file=supply_chain_vuln_breakdown.png caption="Supply-Chain & Container Vulnerability Breakdown: 0 Declared App CVEs vs. Build-Time pip@24.2 vs. Debian 12.7 OS"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=68, dpi=150)

# Left Chart: Python App vs Build-Time Tool (pip@24.2) — Multi-series with mandatory horizontal legend
app_chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=58.0,
    height=38.0,
    categories=["Declared App\n(5 runtime deps)", "Build Tool\n(pip@24.2)"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.6,
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="Python Packages: App vs. Build-Time pip",
    title_style=Styles.DarkBold.patch(text_size=10.8),
)
app_chart.configure_y_axis(
    min_value=0.0,
    max_value=7.0,
    ticks=[0, 1, 2, 3, 4, 5, 6],
    show_grid=True,
    label="CVE Count",
)
app_chart.add_series("CRITICAL", [0, 0], style=Styles.DangerFlat)
app_chart.add_series("HIGH", [0, 0], style=Styles.WarningFlat)
app_chart.add_series("MEDIUM", [0, 5], style=Styles.WarningNeutral)
app_chart.add_series("LOW", [0, 1], style=Styles.SecondaryNeutral)
app_chart.draw((10.0, 17.0))
app_chart.draw_legend(
    (6.0, 4.0),
    text_style=Styles.Dark.patch(text_size=9.2),
    orientation="horizontal",
    item_gap=4.5,
)

# Right Chart: Debian 12.7 Base-Image OS CVEs (612 Total)
os_chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=56.0,
    height=38.0,
    categories=["CRIT", "HIGH", "MED", "LOW"],
    orientation="vertical",
    bar_width_ratio=0.58,
    bar_r=0.7,
    axis_text_style=Styles.Dark.patch(text_size=9.6),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    value_format="{:.0f}",
    title="Debian 12.7 Base Image OS CVEs (612 Total)",
    title_style=Styles.DarkBold.patch(text_size=10.8),
)
os_chart.configure_y_axis(
    min_value=0.0,
    max_value=290.0,
    ticks=[0, 50, 100, 150, 200, 250],
    show_grid=True,
    label="OS CVE Count",
)
os_chart.add_series("Debian 12.7 OS", [9, 158, 253, 173], style=Styles.PrimaryNeutral)
os_chart.draw((84.0, 17.0))

text(
    (112.0, 5.2),
    "Trivy IaC: 1 LOW (DS-0026 No HEALTHCHECK) | Secrets: 0",
    style=Styles.Muted.patch(text_size=9.2),
)

save()
```

## Live HTTP DAST (`15/19` Probes) & Extracted API Attack Surface

All 19 live HTTP probes executed against the isolated Docker container (`http://127.0.0.1:55857`, `28.04s`) confirmed strong resilience against XSS, SQL injection, path traversal, and secret disclosure (`15` passed, `3` failed, `1` skipped). Strict Pydantic v2 `ConfigDict(extra="forbid")` schemas rejected malformed payloads cleanly, while the three failed probes directly surfaced missing route-level authentication (`CWE-306`), default OpenAPI schema exposure (`CWE-200`), and missing `X-Content-Type-Options: nosniff` (`CWE-693`).

```drawlib align=center code=fold file=dast_api_attack_surface.png caption="Live HTTP DAST Summary, Extracted API Endpoints & Verified CWE Findings"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Muted.patch(text_size=9.0),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add("0 / 0", "Secrets & Sinks", "0 Hardcoded, 0 AST CWEs", accent_style=Styles.SuccessFlat)
kpis.add("1 LOW", "IaC Misconfig", "DS-0026 No HEALTHCHECK", accent_style=Styles.WarningFlat)
kpis.add("15 / 19", "Live DAST Probes", "3 Failed, 1 Skipped (28s)", accent_style=Styles.PrimaryFlat)
kpis.add("0 / 3", "Auth-Guarded APIs", "/v1/orders Needs Depends()", accent_style=Styles.WarningFlat)
kpis.draw((3.0, 56.5), width=140.0, height=15.0, columns=4)

left_panel = Panel(
    "Extracted API Attack Surface (routes.py)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_height=8.0,
)
left_panel.draw((3.0, 3.0), width=68.0, height=50.5)

ep_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    spacing=2.4,
)
ep_cards.add(
    "GET /healthz -> health_check",
    "routes.py:47 | Public readiness probe (auth_hint=NONE)",
    badge_text="GET",
    badge_style=Styles.SuccessFlat,
)
ep_cards.add(
    "POST /v1/orders -> create_order",
    "routes.py:60 | Mutating, NO auth guard (TODO line 73)",
    badge_text="POST",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    badge_style=Styles.WarningFlat,
)
ep_cards.add(
    "GET /v1/orders/{order_id} -> get_order",
    "routes.py:83 | Order lookup, NO auth/tenant guard",
    badge_text="GET",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    badge_style=Styles.WarningFlat,
)
ep_cards.draw((6.0, 5.5), width=62.0, height=38.0)

right_panel = Panel(
    "Verified Live HTTP DAST Findings (3)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.WarningNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_height=8.0,
)
right_panel.draw((75.0, 3.0), width=68.0, height=50.5)

dast_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    spacing=2.4,
)
dast_cards.add(
    "CWE-306: Unauth POST /v1/orders",
    "HTTP 201 returned with order_id (ord-94b1ebabb3)",
    badge_text="MED",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    badge_style=Styles.WarningFlat,
)
dast_cards.add(
    "CWE-200: Public /openapi.json",
    "GET /openapi.json returned HTTP 200 (4,753 bytes)",
    badge_text="LOW",
    badge_style=Styles.SecondaryFlat,
)
dast_cards.add(
    "CWE-693: Missing Security Header",
    "GET /healthz omitted X-Content-Type-Options: nosniff",
    badge_text="LOW",
    badge_style=Styles.SecondaryFlat,
)
dast_cards.draw((78.0, 5.5), width=62.0, height=38.0)

save()
```

## Supply-Chain Governance & Build-Time `pip@24.2` CVEs

`order-dispatch` passes every repository governance gate (`uv.lock` committed, `5` pinned runtime dependencies, `0` unpinned dependencies, `SECURITY.md`, `.github/dependabot.yml`, `Apache-2.0 LICENSE`, SHA-pinned GitHub Actions with `permissions: contents: read`, non-root `appuser` `uid 10001`, `.dockerignore`, `0` secrets, and `0` AST dangerous sinks). The only Python-layer Trivy CVEs stem from build-time `pip@24.2` bundled inside `python:3.12.6-slim-bookworm`:

| CVE ID | Scanner Severity | Triaged Severity | Package (`python-pkg`) | Installed -> Fixed | CVSS | Summary |
| :--- | :---: | :---: | :--- | :--- | :---: | :--- |
| `CVE-2026-8643` | MEDIUM | LOW (build-only) | `pip` | `24.2` -> `26.1.2` | `8.0` | Path traversal via malicious entry point name in wheel install |
| `CVE-2026-13346` | MEDIUM | LOW (build-only) | `pip` | `24.2` -> `26.2.0` | `6.5` | Arbitrary file installation via malicious package indexes |
| `CVE-2026-6357` | MEDIUM | LOW (build-only) | `pip` | `24.2` -> `26.1` | `5.8` | Code execution / info disclosure via malicious wheel install |
| `CVE-2025-8869` | MEDIUM | LOW (build-only) | `pip` | `24.2` -> `25.3` | `5.3` | Missing checks on symbolic link extraction |
| `CVE-2026-3219` | MEDIUM | LOW (build-only) | `pip` | `24.2` -> `26.1` | `5.0` | Incorrect file installation via improper archive handling |
| `CVE-2026-1703` | LOW | LOW | `pip` | `24.2` -> `26.0` | `3.9` | Info disclosure via path traversal in crafted wheel archives |

## Top Container Base-Image OS CVEs (`python:3.12.6-slim-bookworm` / Debian 12.7)

Trivy (`ghcr.io/aquasecurity/trivy:0.69.3`) scanned the built project `Dockerfile` image and reported `612` Debian 12.7 OS package CVEs (`9` CRITICAL, `158` HIGH, `253` MEDIUM, `173` LOW) plus `1` LOW IaC misconfiguration (`DS-0026`: missing `HEALTHCHECK`). Refreshing to the latest patched `python:3.12.x-slim-bookworm` digest resolves the patchable CRITICAL items below:

| CVE ID | Severity | Debian Package | Installed -> Fixed Version | CVSS | Summary |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `CVE-2026-42010` | **CRITICAL** | `libgnutls30` | `3.7.9-2+deb12u3` -> `3.7.9-2+deb12u7` | `9.8` | GnuTLS authentication bypass via NUL character in username |
| `CVE-2026-31789` | **CRITICAL** | `libssl3`, `openssl` | `3.0.14-1~deb12u2` -> `3.0.19-1~deb12u2` | `9.8` | OpenSSL heap buffer overflow on 32-bit systems (X.509) |
| `CVE-2026-8376` | **CRITICAL** | `perl-base` | `5.36.0-7+deb12u1` -> `5.36.0-7+deb12u4` | `9.8` | Perl heap buffer overflow compiling regexes on 32-bit builds |
| `CVE-2023-45853` | **CRITICAL** | `zlib1g` | `1:1.2.13.dfsg-1` -> *(no upstream fix)* | `9.8` | zlib integer overflow in `zipOpenNewFileInZip4_6` |
| `CVE-2026-33845` | **CRITICAL** | `libgnutls30` | `3.7.9-2+deb12u3` -> `3.7.9-2+deb12u7` | `9.1` | GnuTLS Denial of Service via DTLS zero-length fragment |
| `CVE-2025-7458` | **CRITICAL** | `libsqlite3-0` | `3.40.1-2` -> *(no upstream fix)* | `9.1` | SQLite integer overflow |
| `CVE-2026-13221` | **CRITICAL** | `perl-base` | `5.36.0-7+deb12u1` -> `5.36.0-7+deb12u4` | `9.1` | Perl incorrect regex processing via large regular expressions |
| `CVE-2026-42496` | **CRITICAL** | `perl-base` | `5.36.0-7+deb12u1` -> `5.36.0-7+deb12u4` | `9.1` | `perl-archive-tar` path traversal via crafted symlinks |
| `CVE-2025-6965` | **HIGH** | `libsqlite3-0` | `3.40.1-2` -> `3.40.1-2+deb12u2` | `9.8` | SQLite integer truncation |

## Live HTTP DAST Findings & API Endpoint Surface

**AST Dangerous Code Sinks**: `0` sinks detected.  
**Pentest Suite**: `.pni/pentests/examples/python/api_fastapi_clean` (`15/19` passed, `3` failed, `1` skipped).

| Endpoint / Surface | Handler / Probe Test ID | Auth / CWE | Severity | Live Evidence & Boundary Assessment |
| :--- | :--- | :---: | :---: | :--- |
| `GET /healthz` | `health_check` (`routes.py:47`) / `test_baseline_http::test_x_content_type_options_nosniff` | `auth_hint=NONE` · `CWE-693` | **LOW** | Intentionally public readiness probe; `GET /healthz -> 200`, `X-Content-Type-Options=<absent>`. |
| `POST /v1/orders` | `create_order` (`routes.py:60`) / `test_app_probes::test_create_order_enforces_authentication_guard` | `auth_hint=NONE` · `CWE-306` | **MEDIUM** | State-mutating endpoint accepted unauthenticated request and returned HTTP `201` with created `order_id` (`ord-94b1ebabb3`), matching line 73 `TODO(security)`. |
| `GET /v1/orders/{order_id}` | `get_order` (`routes.py:83`) | `auth_hint=NONE` · `CWE-306` | **MEDIUM** | Order lookup lacks caller authentication and tenant ownership check; guard alongside `POST /v1/orders`. |
| `GET /openapi.json` | `test_app_probes::test_openapi_schema_not_publicly_exposed_without_auth` | `CWE-200` | **LOW** | Unauthenticated OpenAPI schema exposed by default (`GET /openapi.json -> 200`, `4,753` bytes); disable via `openapi_url=None` in `prod`. |
