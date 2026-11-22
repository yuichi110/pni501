# 4. Audit Pipeline (DAG), Standards & Findings

This chapter establishes full reproducibility and evidence provenance for workflow run `wf-f819234f` (`py_api_fastapi_clean`): the executed action-level pipeline DAG, exact inspection scope and deterministic analyzers, 7-axis deterministic baseline anchoring (`±10pt` cap), audit step scores, `WARN -> PASS` rule compliance matrix, consolidated findings, AI false-positive triage log, and machine-readable artifact manifest.

```drawlib align=center code=fold file=executed_audit_dag.png caption="Executed PNI Workflow v2 Audit Pipeline DAG (9 Logical Stages: ASK, HYBRID & AI Badges)"
from drawlib.canvas import save, setup
from drawlib.graph import LayerGraph
from drawlib.lines import lines
from drawlib.shapes import rectangle
from drawlib.styles import Styles
from drawlib.text import text

setup(width=156, height=84, dpi=150)

text(
    (78.0, 79.5),
    "Executed Audit Pipeline DAG — py_api_fastapi_clean (wf-f819234f | 0 Skipped)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

g = LayerGraph(
    direction="LR",
    rank_sep=5.5,
    node_sep=2.8,
    default_node_width=23.0,
    default_node_height=9.2,
    edge_routing="orthogonal",
)

g.node("plan", width=22.0, height=9.5, layer=0)
g.node("repo", width=23.5, height=9.5, layer=1)
g.node("supply", width=25.5, height=8.8, layer=2)
g.node("ast", width=25.5, height=8.8, layer=2)
g.node("runtime", width=25.5, height=8.8, layer=2)
g.node("trivy", width=25.5, height=8.8, layer=2)
g.node("dast", width=25.5, height=8.8, layer=2)
g.node("synth", width=24.0, height=9.5, layer=3)
g.node("score", width=24.5, height=11.0, layer=4)

g.edge("plan", "repo")
g.edge("repo", "supply")
g.edge("repo", "ast")
g.edge("repo", "runtime")
g.edge("repo", "trivy")
g.edge("repo", "dast")
g.edge("ast", "synth")
g.edge("supply", "score")
g.edge("synth", "score")
g.edge("runtime", "score")
g.edge("trivy", "score")
g.edge("dast", "score")

layout = g.get_layout(width=156.0, height=84.0, margin=4.0)

# Compute exact bounding box of solved nodes and center cleanly inside x=[4, 152], y=[13, 73]
min_x = min(n.x - n.width / 2.0 for n in layout.nodes.values())
max_x = max(n.x + n.width / 2.0 for n in layout.nodes.values())
min_y = min(n.y - n.height / 2.0 for n in layout.nodes.values())
max_y = max(n.y + n.height / 2.0 for n in layout.nodes.values())
dx = 78.0 - (min_x + max_x) / 2.0
dy = 43.0 - (min_y + max_y) / 2.0

for edge in layout.edges:
    pts = [(px + dx, py + dy) for px, py in edge.points]
    lines(pts, arrow_head="->", style=Styles.Muted)

specs = [
    ("plan", "[ASK] Confirm Plan", "Auto-approved DAG", Styles.Neutral, Styles.DarkBold, Styles.Muted),
    ("repo", "[HYBRID] Repo & Deps", "14 src / 3 tests, 5 deps", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("supply", "[AI] Supply Chain", "SHA-pin CI, non-root", Styles.SecondaryNeutral, Styles.DarkBold, Styles.Muted),
    ("ast", "[HYBRID] Python AST", "14 files, 435 LOC, 0 sinks", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("runtime", "[HYBRID] Docker Run", "4/4 tests, 85.2% cov", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("trivy", "[HYBRID] Trivy SCA", "Trivy 0 CRIT/HIGH app", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("dast", "[HYBRID] Live DAST", "DAST 15/19 probes", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("synth", "[AI] Arch / PRR / Test", "5 layers, 12F, cov audit", Styles.SecondaryNeutral, Styles.DarkBold, Styles.Muted),
    ("score", "[AI] Score & Report", "94/100 (S) | 16 rules", Styles.PrimaryFlat, Styles.WhiteBold, Styles.White),
]

for nid, title_lbl, sub_lbl, box_style, t_style, s_style in specs:
    n = layout[nid]
    cx, cy = n.x + dx, n.y + dy
    rectangle((cx, cy), width=n.width, height=n.height, style=box_style.patch(shape_r=1.5))
    text((cx, cy + 1.6), title_lbl, style=t_style.patch(text_size=9.2))
    text((cx, cy - 2.0), sub_lbl, style=s_style.patch(text_size=8.6))

# Legend bar cleanly separated below DAG
legend_items = [
    (22.0, "[ASK] Human Plan Gate", Styles.Neutral, Styles.Dark),
    (59.0, "[HYBRID] Deterministic + AI", Styles.PrimaryNeutral, Styles.Dark),
    (97.0, "[AI] Qualitative Audit", Styles.SecondaryNeutral, Styles.Dark),
    (134.0, "Final Score (94/100 S)", Styles.PrimaryFlat, Styles.WhiteBold),
]
for lx, ltxt, lbox, lts in legend_items:
    rectangle((lx, 4.8), width=33.0, height=5.4, style=lbox.patch(shape_r=1.2))
    text((lx, 4.8), ltxt, style=lts.patch(text_size=9.2))

save()
```

## Inspection Scope & Deterministic Tools Executed

| Scope Dimension | Recorded Ground Truth (`audit_scope`) |
| :--- | :--- |
| **Target Root & Paths** | `examples/python/api_fastapi_clean` · source=`['src']`, tests=`['tests']`, docs=`['README.md']`, exclude=`['none']` |
| **Languages & Frameworks** | Primary=`python`, companions=`['none']`, detected frameworks=`fastapi`, `pydantic`, `pytest`, `httpx` |
| **Git Provenance** | `main@d1e02277 (dirty)` |
| **Deterministic Analyzers Run** | `project_inspect (python)`, `tree-sitter AST (python)`, `container runtime harness (docker: python/uv.dockerfile)`, `Trivy (docker: fs+image)`, `web_pentest (httpx, 19 probes)` |
| **Stage Count & Execution** | 12 workflow stages (`1` ASK, `5` HYBRID, `6` AI — 11 completed + `create_report` in progress, `0` skipped) |

## 7-Axis Deterministic Baseline vs. AI Adjustment (`±10pt` Anchoring)

Every category score starts from a deterministic analyzer baseline and is bounded to a maximum `±10pt` AI qualitative adjustment grounded in explicit evidence.

| Health Axis | Deterministic Baseline | AI Adjustment (`Δ`) | Final Score | Grounded Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **Architecture** | `100` | `-4` | **96** | Strict 4-layer acyclic Clean/Hexagonal layout (`api -> services -> domain + infra`) with zero circular dependencies and pure domain core; `-4pt` reflects default process-local `InMemoryOrderRepository` under 12-Factor VI. |
| **Code Quality** | `100` | `-2` | **98** | 100% import hygiene, 0 complexity hotspots, 0 bug-risk idioms, structured logging, and modern FastAPI lifespan/Pydantic v2 idioms; `-2pt` reflects minor `StarletteDeprecationWarning` on `TestClient`. |
| **Typing** | `100` | `0` | **100** | 100% type safety coverage with `py.typed` marker, `from __future__ import annotations`, zero `Any` usages, and zero unscoped type ignores. |
| **Testing** | `100` | `-10` | **90** | `4/4` offline Docker pytest tests pass with `85.2%` line coverage and 100% core domain/service coverage; `-10pt` reflects `62.5%` branch coverage with untested `routes.py` (`56.0%`) and `webhook_client.py` (`55.6%`) branches. |
| **Dependencies** | `100` | `-5` | **95** | PEP 621 `pyproject.toml` + `uv.lock` with 0 unpinned deps, 0 declared app CVEs, Dependabot, and SHA-pinned CI; `-5pt` reflects aged `python:3.12.6-slim-bookworm` base image bundling `pip@24.2`. |
| **Security** | `85` | `-1` | **84** | 0 declared app CVEs, 0 secrets, 0 dangerous sinks, non-root Dockerfile, and `15/19` live DAST probes passed; deducted for live DAST `CWE-306` unauthenticated `POST /v1/orders`, `CWE-200` `/openapi.json`, `CWE-693` header gap, and Debian 12.7 OS CVEs (`5` build-time `pip` CVEs reclassified to `low`). |
| **Documentation** | `100` | `-2` | **98** | Diataxis-structured `README.md` (Quickstart, How-To, API Reference, Architecture) and 100% Google-style docstrings across all public symbols. |

## Audit Step Scores (Weakest to Strongest)

```drawlib align=center code=fold file=audit_step_scores.png caption="Executed Audit Step Scores Sorted Weakest-First (82/100 to 96/100)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=96.0,
    height=44.0,
    categories=[
        "security_vulnerability_audit (A)",
        "web_penetration_audit (A)",
        "python_test_audit (A)",
        "container_runtime_audit (S)",
        "service_readiness_audit (S)",
        "supply_chain_audit (S)",
        "python_ast_audit (S)",
        "repo_structure_audit (S)",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.Dark.patch(text_size=9.6),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    value_format="{:.0f}",
    title="Audit Step Scores (Weakest -> Strongest | Grade S >= 90)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
chart.configure_x_axis(
    min_value=0.0,
    max_value=105.0,
    ticks=[0, 20, 40, 60, 80, 90, 100],
    show_grid=True,
    label="Audit Score (0-100)",
)
chart.add_series(
    "Step Score",
    [82, 86, 88, 90, 91, 92, 95, 96],
    style=Styles.PrimaryNeutral,
)
chart.draw((40.0, 9.0))

save()
```

## Rule Compliance Matrix (`WARN -> PASS`, 16 Rules)

```drawlib align=center code=fold file=rule_compliance_summary.png caption="Visual Rule Compliance Matrix (4 WARN, 12 PASS, 0 FAIL — Pre-Sorted)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=146, height=96, dpi=150)

text(
    (73.0, 92.5),
    "PNI Rule Compliance Matrix — 12/16 PASS, 4 WARN, 0 FAIL",
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
    rows=[1, 2, 3, 4],
    columns=[0],
)
tbl.set_style_cell(
    Styles.SuccessNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=list(range(5, 17)),
    columns=[0],
)

rows = [
    ["Status", "Rule ID", "Source Action", "Primary Evidence Summary"],
    ["WARN", "common/security", "service_readiness", "0 secrets/sinks; /v1/orders lacks caller auth"],
    ["WARN", "common/security_vulnerability", "python_ast_audit", "0 app CRIT/HIGH; CWE-306/200/693 DAST; 612 OS"],
    ["WARN", "common/supply_chain", "security_vuln_audit", "SHA-pinned CI & uv.lock; aged Debian 12.7 base"],
    ["WARN", "common/twelve_factor", "service_readiness", "III/IV/IX/XI PASS; VI WARN (InMemoryRepo)"],
    ["PASS", "common/architecture", "python_ast_audit", "Strict 4-layer acyclic DAG; 0 cycles/violations"],
    ["PASS", "common/documentation", "repo_structure", "Diataxis README (23 lines) & 100% docstrings"],
    ["PASS", "common/git_workflow", "repo_structure", ".gitignore + CI ruff check & pytest on main"],
    ["PASS", "common/maintainability", "python_ast_audit", "0 complex funcs, 0 global state, 0 bug idioms"],
    ["PASS", "common/production_readiness", "container_runtime", "5.0s httpx timeout, /healthz 200, WEBHOOK_DEFERRED"],
    ["PASS", "common/runtime_verification", "deterministic", "Docker build PASS, 4/4 tests, 85.2% cov, smoke OK"],
    ["PASS", "python/code_quality", "python_ast_audit", "100% Google docstrings, 0 print logs, clean style"],
    ["PASS", "python/dependencies", "repo_structure", "PEP 621 uv_build, 5 bounded deps, uv.lock"],
    ["PASS", "python/frameworks/fastapi", "python_ast_audit", "Async lifespan, response_model, Depends() DI"],
    ["PASS", "python/modern_stack", "python_ast_audit", "100% import hygiene, Pydantic v2, Py 3.11+"],
    ["PASS", "python/testing", "python_test_audit", "4/4 offline tests, 100% core cov (62.5% branch)"],
    ["PASS", "python/typing", "python_ast_audit", "100% typing, py.typed, 0 Any, 0 type ignores"],
]

tbl.draw_flexible(
    (2.0, 89.5),
    column_widths=[14.0, 42.0, 28.0, 58.0],
    row_heights=[6.0] + [4.95] * 16,
    data=rows,
    align="top_left",
)

save()
```

| Status | Rule ID | Source Action | Verified Evidence |
| :---: | :--- | :--- | :--- |
| **WARN** | `common/security` | `service_readiness_audit` | 0 committed/hardcoded secrets, 0 dangerous sinks, strict Pydantic v2 `ConfigDict(extra='forbid')`, non-root `uid 10001`, least-privilege CI; `/v1/orders` endpoints omit caller authentication (`TODO` in `routes.py:73`). |
| **WARN** | `common/security_vulnerability` | `python_ast_audit` | `SEC-01`: 0 CRIT/HIGH in declared app packages, 6 `pip@24.2` CVEs + 612 Debian 12.7 OS CVEs; `SEC-02`: `DS-0026` (no `HEALTHCHECK`); `SEC-03/04`: 0 secrets/sinks; `SEC-05/06`: live DAST verified `CWE-306` (`POST /v1/orders -> 201`), `CWE-200` (`/openapi.json`), `CWE-693` (missing `X-Content-Type-Options`). |
| **WARN** | `common/supply_chain` | `security_vulnerability_audit` | `uv.lock`, 0 unpinned deps, `LICENSE`, `SECURITY.md`, Dependabot, SHA-pinned CI with `contents: read`, non-root `appuser` + `.dockerignore`; `Dockerfile` pins aged `python:3.12.6-slim-bookworm` (Debian 12.7, `pip@24.2`) and omits `HEALTHCHECK`. |
| **WARN** | `common/twelve_factor` | `service_readiness_audit` | Factors III (`pydantic-settings`), IV (`OrderRepository` Protocol), IX (lifespan), XI (`logging.getLogger`) PASS; Factor VI WARN due to default `InMemoryOrderRepository` in `main.py:33`. |
| **PASS** | `common/architecture` | `python_ast_audit` | Strict acyclic layered DAG (`api -> services -> domain + infra`); zero framework/network imports in `domain/`; 0 cycles and 0 boundary violations. |
| **PASS** | `common/documentation` | `repo_structure_audit` | `README.md` (23 lines, 6 headings) covers Quickstart Tutorial, Operations How-To, HTTP API Reference, and Layered Architecture aligned with Diataxis. |
| **PASS** | `common/git_workflow` | `repo_structure_audit` | `.gitignore` committed; `.github/workflows/ci.yml` gates push and pull requests on `main` with `ruff check` and `pytest`. |
| **PASS** | `common/maintainability` | `python_ast_audit` | 0 complex functions, 0 excessive parameter lists, 0 global mutable state usages, and 0 bug-risk idioms across 14 files (435 LOC). |
| **PASS** | `common/production_readiness` | `container_runtime_audit` | 0 missing I/O timeouts (`timeout_sec=5.0`), `/healthz -> 200`, structured logging via `logging.getLogger`, graceful `httpx.HTTPError` fallback to `WEBHOOK_DEFERRED`. |
| **PASS** | `common/runtime_verification` | `deterministic_baseline` | `RV-01` Dockerfile + harness build passed; `RV-02` `4/4` offline tests passed (`--network=none`); `RV-03` `85.2%` line (`178/209` stmts) / `62.5%` branch; `RV-04` ASGI smoke `/healthz -> 200`. |
| **PASS** | `python/code_quality` | `python_ast_audit` | 100.0% Google-style docstring coverage, 0 signature mismatches, 0 unstructured `print` calls, consistent naming. |
| **PASS** | `python/dependencies` | `repo_structure_audit` | PEP 621 `pyproject.toml` (`uv_build`, `requires-python >=3.11`), 5 bounded runtime dependencies, separate `[dependency-groups].dev`, committed `uv.lock`. |
| **PASS** | `python/frameworks/fastapi` | `python_ast_audit` | Modern `asynccontextmanager` lifespan in `main.py`, explicit `response_model` on all routes, `Depends()` DI in `routes.py`, non-blocking `httpx.AsyncClient` with explicit timeout. |
| **PASS** | `python/modern_stack` | `python_ast_audit` | 100.0% import hygiene, PEP 621 + `uv.lock`, Pydantic v2 `ConfigDict`/`@field_validator`, Python 3.11+ `StrEnum` and `X \| None` unions, 0 unused/undeclared deps. |
| **PASS** | `python/testing` | `python_test_audit` | `pytest` + `pytest-cov` configured; `4/4` offline deterministic tests, 0 assertion-free tests, 100% static module coverage, 100% core line coverage (`62.5%` branch). |
| **PASS** | `python/typing` | `python_ast_audit` | 100.0% type safety coverage, `py.typed` marker present, 0 weak `Any` usages, 0 unscoped type ignores, `from __future__ import annotations` consistently applied. |

## Consolidated Location Findings Index (`9` Locations from `12` Raw Findings)

**Source Split**: `6` deterministic analyzer findings + `6` AI qualitative findings = `12` total raw findings (`3` Medium, `9` Low), consolidated to `9` unique locations below.

| # | Severity | Location | Rule IDs | Consolidated Evidence | Recommended Fix |
| :-: | :---: | :--- | :--- | :--- | :--- |
| 1 | **MEDIUM** | `Dockerfile` | `common/security_vulnerability` | Trivy image scan on `python:3.12.6-slim-bookworm` (Debian 12.7) reports 9 CRITICAL / 158 HIGH Debian OS CVEs (e.g., `CVE-2026-42010` in `libgnutls30`, `CVE-2026-31789` in `openssl`/`libssl3`), 6 `pip@24.2` CVEs, and `DS-0026` missing `HEALTHCHECK`. | Refresh base image to latest patched `python:3.12.x-slim-bookworm` (or multi-stage `uv` venv copy without `pip`), upgrade/remove `pip`, and add `HEALTHCHECK` for `/healthz`. |
| 2 | **MEDIUM** | `src/order_dispatch/api/routes.py` | `common/security_vulnerability`, `common/runtime_verification` | `POST /v1/orders` and `GET /v1/orders/{order_id}` omit OAuth2/JWT/API-key `Depends()` guard (`TODO(security)` line 73); live probe received HTTP 201 with created `order_id`; branch coverage is `62.5%` (`routes.py` 56.0% line / 0.0% branch). | Add FastAPI `Security`/`Depends()` caller authentication and per-tenant authZ on `/v1/orders`; add `TestClient` 200/404 and `MockTransport` tests. |
| 3 | **LOW** | `src/order_dispatch/main.py` | `common/twelve_factor`, `common/security_vulnerability` | Defaults to process-local `InMemoryOrderRepository` during lifespan startup; live probes confirmed `GET /openapi.json` returns 200 (4,753 bytes) without auth and `/healthz` omits `X-Content-Type-Options: nosniff`. | Wire durable external `OrderRepository` (PostgreSQL/Redis) for `env == "prod"`; gate `openapi_url`/`docs_url` in prod and register security headers middleware. |
| 4 | **LOW** | `-` | `CVE-2025-8869` | `pip@24.2` (`python-pkg`) — AI reclassified to `low` (wheel symlink extraction unreachable at ASGI runtime). | Upgrade `pip` to `>=25.3` or omit `pip` in multi-stage runtime image. |
| 5 | **LOW** | `-` | `CVE-2026-13346` | `pip@24.2` (`python-pkg`) — AI reclassified to `low` (package index install build-time only). | Upgrade `pip` to `>=26.2.0` or refresh multi-stage base image. |
| 6 | **LOW** | `-` | `CVE-2026-1703` | `pip@24.2` (`python-pkg`) — information disclosure via crafted wheel path traversal. | Upgrade `pip` to `>=26.0` or remove `pip` from runtime stage. |
| 7 | **LOW** | `-` | `CVE-2026-3219` | `pip@24.2` (`python-pkg`) — AI reclassified to `low` (confined to Dockerfile line 9 build install). | Upgrade `pip` to `>=26.1` or adopt multi-stage build. |
| 8 | **LOW** | `-` | `CVE-2026-6357` | `pip@24.2` (`python-pkg`) — AI reclassified to `low` (wheel extraction never invoked dynamically at runtime). | Upgrade `pip` to `>=26.1` or strip `pip` from runtime image. |
| 9 | **LOW** | `-` | `CVE-2026-8643` | `pip@24.2` (`python-pkg`) — AI reclassified to `low` (build-time packaging tool bundled in base image). | Upgrade `pip` to `>=26.1.2` (or `>=26.2.0`) via multi-stage image. |

## AI False-Positive Triage Log & Configured Waivers

**Configured Design Waivers (`pni.toml [[opt_out]]`)**: `0` active waivers.  
**AI Finding Adjustments (`finding_adjustments`)**: `5` deterministic build-tool CVEs on `pip@24.2` were reclassified from `medium` to `low` because `pip` is strictly a build-stage packaging tool bundled in `python:3.12.6-slim-bookworm` and is never imported or invoked during Uvicorn ASGI request handling.

| Finding ID | CVE ID | Action | Triage Rationale |
| :--- | :--- | :---: | :--- |
| `det-13c60704` | `CVE-2026-8643` | `reclassify -> low` | `pip@24.2` is a build-time packaging tool bundled in `python:3.12.6-slim-bookworm`, not imported or invoked by `order-dispatch` at runtime; resolve via multi-stage Docker build or `pip>=26.2`. |
| `det-f749f183` | `CVE-2026-13346` | `reclassify -> low` | `pip@24.2` package index install vulnerability is build-time only and unreachable by `order-dispatch` runtime HTTP requests; mitigate by refreshing base image. |
| `det-88839930` | `CVE-2026-6357` | `reclassify -> low` | `pip@24.2` wheel extraction CVE is not reachable at runtime because `order-dispatch` never invokes `pip` dynamically; fix via multi-stage runtime image. |
| `det-dac9a878` | `CVE-2025-8869` | `reclassify -> low` | `pip@24.2` symlink extraction CVE applies only during wheel installs, not during Uvicorn ASGI request handling. |
| `det-dbf87858` | `CVE-2026-3219` | `reclassify -> low` | `pip@24.2` archive handling CVE is confined to build-stage installation in `Dockerfile` line 9 and not exposed at runtime. |

## Machine-Readable Evidence Artifacts

All structured telemetry, findings, and architectural records are preserved as machine-readable artifacts alongside this report:

| Artifact Path | Schema / Format | Purpose |
| :--- | :--- | :--- |
| `docs/reports/py_api_fastapi_clean/py_api_fastapi_clean_score.json` | `ScoreResult` v2.0 (JSON) | Complete 7-axis scores, rationales, runtime/Trivy/DAST facts, and findings |
| `docs/reports/py_api_fastapi_clean/py_api_fastapi_clean_summary.json` | `ScoreSummary` (JSON) | Lightweight CI gate and executive portal summary |
| `docs/reports/py_api_fastapi_clean/py_api_fastapi_clean_findings.sarif` | `SARIF 2.1.0` | GitHub Code Scanning and IDE findings import |
| `docs_src/reports/py_api_fastapi_clean/_facts/plan.json` | PNI Plan (JSON) | Pre-flight recon plan and validated Mermaid execution DAG |
| `docs_src/reports/py_api_fastapi_clean/_facts/facts.json` | Deterministic Bundle (JSON) | Raw AST, container runtime, Trivy SCA, and DAST telemetry |
| `docs_src/reports/py_api_fastapi_clean/_facts/architecture.json` | `ArchitectureRecord` (JSON) | Grounded 5-layer structure map and execution flow metadata |
