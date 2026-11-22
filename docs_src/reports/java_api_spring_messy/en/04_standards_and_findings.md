# 4. Audit Pipeline (DAG), Standards & Findings

This chapter establishes end-to-end audit provenance and reproducibility: the action-level **Executed Audit Pipeline DAG**, inspection targets and deterministic tools, the **7-Axis Deterministic Baseline vs. AI Adjustment (`±10pt`)** audit trail, weakest-first audit step scores, the complete `FAIL -> WARN` rule compliance matrix, consolidated findings by unique location, and a compact machine-readable artifact reference index.

```drawlib align=center code=hide file=audit_pipeline_dag.png caption="Executed PNI Workflow v2 Audit Pipeline DAG (9 Logical Stages with ASK/HYBRID/AI Mode Badges and Live Failure Highlights)"
from drawlib.canvas import save, setup
from drawlib.graph import LayerGraph
from drawlib.lines import line, lines
from drawlib.shapes import rectangle
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=96, dpi=150)

text(
    (73.0, 92.2),
    "Executed Audit Pipeline DAG — java_api_spring_messy (wf-8177454c)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Step 1: Solve 5-rank DAG coordinates via LayerGraph (no skip-layer node crossings)
g = LayerGraph(
    direction="LR",
    rank_sep=5.5,
    node_sep=2.2,
    edge_routing="orthogonal",
    default_node_width=24.0,
    default_node_height=11.6,
)
g.node("confirm_plan", layer=0, width=20.5, height=12.0)
g.node("repo_and_deps", layer=1, width=22.5, height=12.0)
g.node("ast_and_quality", layer=2, width=24.5, height=11.6)
g.node("runtime_verification", layer=2, width=24.5, height=11.6)
g.node("security_audit", layer=2, width=24.5, height=11.6)
g.node("web_pentest", layer=2, width=24.5, height=11.6)
g.node("supply_chain", layer=2, width=24.5, height=11.6)
g.node("ast_ai_eval", layer=3, width=23.5, height=11.6)
g.node("output_score", layer=4, width=22.5, height=14.5)

g.edge("confirm_plan", "repo_and_deps")
g.edge("repo_and_deps", "ast_and_quality")
g.edge("repo_and_deps", "runtime_verification")
g.edge("repo_and_deps", "security_audit")
g.edge("repo_and_deps", "web_pentest")
g.edge("repo_and_deps", "supply_chain")
g.edge("ast_and_quality", "ast_ai_eval")

layout = g.get_layout(width=140.0, height=69.0, margin=1.5)

# Align ast_ai_eval with top ast_and_quality row
ast_top_y = layout["ast_and_quality"].y
layout.offset("ast_ai_eval", dy=ast_top_y - layout["ast_ai_eval"].y)

# Place DAG cleanly in y=13..85 band (clear of legend y=4.8 and title y=92.2)
dx, dy = 3.0, 14.0

# Step 2: Render solved edges (re-route ast_and_quality -> ast_ai_eval straight horizontally)
edge_st = Styles.Dark.patch(line_width=1.3)
for e in layout.edges:
    if e.src == "ast_and_quality" and e.dst == "ast_ai_eval":
        continue
    pts = [(px + dx, py + dy) for px, py in e.points]
    lines(pts, arrow_head="->", style=edge_st)

n_ast = layout["ast_and_quality"]
n_ai = layout["ast_ai_eval"]
line(
    (n_ast.right + dx, ast_top_y + dy),
    (n_ai.left + dx, ast_top_y + dy),
    arrow_head="->",
    style=edge_st,
)

# Clean collector bus from ast_ai_eval + lower 4 parallel branches into output_score (zero card crossings)
score_n = layout["output_score"]
bus_x = score_n.left + dx - 4.2
score_in = (score_n.left + dx, score_n.y + dy)
for src_id in ("ast_ai_eval", "runtime_verification", "security_audit", "web_pentest", "supply_chain"):
    sn = layout[src_id]
    sx = sn.right + dx
    sy = sn.y + dy
    lines([(sx, sy), (bus_x, sy), (bus_x, score_in[1]), score_in], arrow_head="->", style=edge_st)

# Step 3: Render stage cards with ASK / HYBRID / AI badges
specs = {
    "confirm_plan": (
        "ASK",
        "Confirm Plan",
        "Auto-approved",
        Styles.Neutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.MutedFlat,
    ),
    "repo_and_deps": (
        "HYBRID",
        "Repo & Deps",
        "6 src / 1 test\n2 deps (LATEST)",
        Styles.PrimaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.PrimaryFlat,
    ),
    "ast_and_quality": (
        "HYBRID",
        "Java AST Audit",
        "187 LOC, 1 cycle\n0 CWE sinks",
        Styles.PrimaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.PrimaryFlat,
    ),
    "runtime_verification": (
        "HYBRID",
        "Container Runtime",
        "build=failed\n(61.0 vs 52.0)",
        Styles.DangerNeutral,
        Styles.DangerBold,
        Styles.Dark,
        Styles.DangerFlat,
    ),
    "security_audit": (
        "HYBRID",
        "Trivy SCA & IaC",
        "Trivy 1 CRIT\nunpinned + 3 IaC",
        Styles.DangerNeutral,
        Styles.DangerBold,
        Styles.Dark,
        Styles.DangerFlat,
    ),
    "web_pentest": (
        "HYBRID",
        "Web Pentest",
        "DAST blocked\n(0/0 probes)",
        Styles.WarningNeutral,
        Styles.WarningBold,
        Styles.Dark,
        Styles.WarningFlat,
    ),
    "supply_chain": (
        "AI",
        "Supply Chain & CI",
        "PR_target, @main\nroot Docker",
        Styles.SecondaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.SecondaryFlat,
    ),
    "ast_ai_eval": (
        "AI",
        "Arch / PRR / Test",
        "5 layers, 12F\n1 JUnit4 test",
        Styles.SecondaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.SecondaryFlat,
    ),
    "output_score": (
        "AI",
        "Score & Report",
        "66/100 (Grade C)\n16 rules, 19 find.",
        Styles.PrimaryFlat,
        Styles.WhiteBold,
        Styles.White,
        Styles.DarkFlat,
    ),
}

for nid, (mode, title, detail, box_st, title_st, body_st, badge_st) in specs.items():
    n = layout[nid]
    cx, cy = n.x + dx, n.y + dy
    rectangle((cx, cy), width=n.width, height=n.height, style=box_st.patch(shape_r=1.8))
    badge_w = 9.8 if mode == "HYBRID" else 6.4
    bx = cx - n.width / 2.0 + badge_w / 2.0 + 1.0
    by = cy + n.height / 2.0 - 2.0
    rectangle(
        (bx, by),
        width=badge_w,
        height=3.0,
        style=badge_st.patch(shape_r=0.9),
        text=mode,
        text_style=Styles.WhiteBold.patch(text_size=7.6),
    )
    text((cx, cy + 1.2), title, style=title_st.patch(text_size=9.2))
    text((cx, cy - 3.1), detail, style=body_st.patch(text_size=8.1))

# Legend strip at bottom with generous horizontal spacing
legend_items = [
    (15.0, 21.0, "ASK: Plan Gate", Styles.Neutral),
    (44.5, 31.0, "HYBRID: Deterministic + AI", Styles.PrimaryNeutral),
    (77.5, 27.0, "AI: Qualitative Eval", Styles.SecondaryNeutral),
    (106.5, 25.0, "Failed / Blocked", Styles.DangerNeutral),
    (132.5, 21.0, "Score Synthesis", Styles.PrimaryFlat),
]
for lx, lw, lbl, st in legend_items:
    t_st = Styles.WhiteBold.patch(text_size=8.8) if st is Styles.PrimaryFlat else Styles.DarkBold.patch(text_size=8.8)
    rectangle((lx, 4.5), width=lw, height=5.0, style=st.patch(shape_r=1.2), text=lbl, text_style=t_st)

save()
```

---

## Inspection Scope & Deterministic Tools Executed

| Scope Dimension | Recorded Audit Configuration & Executed Evidence |
| :--- | :--- |
| **Target Root & Paths** | Root: `examples/java/api_spring_messy` \| Source: `['src/main/java']` \| Tests: `['src/test/java']` \| Docs: `['README.md']` \| Exclusions: `['none']` |
| **Languages & Frameworks** | Primary: `java` \| Companions: `['none']` \| Detected Frameworks: `spring-boot`, `spring-framework`, `javax-ee`, `junit4` |
| **Repository Provenance** | Git branch & commit: `main@d1e02277 (dirty)` \| Run ID: `wf-8177454c` |
| **Deterministic Tools Executed** | `project_inspect (java)`, `tree-sitter AST (java)`, `container runtime harness (docker: java/maven.dockerfile)`, `Trivy (docker: fs, ghcr.io/aquasecurity/trivy:0.69.3)`, `web_pentest (httpx, 0 probes — blocked by build failure)` |

---

## 7-Axis Deterministic Baseline vs. AI Adjustment (`±10pt`)

PNI Workflow v2 anchors all seven engineering scores to deterministic static/runtime baselines before applying bounded `±10pt` qualitative AI adjustments. Across `legacy-billing`, every axis incurred the maximum `-10pt` qualitative penalty—moving the overall score from **76** to **66 (Grade C)**—because critical runtime, architectural, and security defects compound beyond raw static AST ratios.

```drawlib align=center code=hide file=baseline_vs_final_comparison.png caption="7-Axis Deterministic Baseline vs. Final Audited Score After Bounded -10pt AI Qualitative Adjustments"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Dark,
    width=132.0,
    height=44.0,
    categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Documentation",
    ],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.8),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="7-Axis Deterministic Baseline (Avg 76) vs. Final Audited Score (Avg 66)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
chart.configure_y_axis(min_value=0, max_value=105, tick_step=20, show_grid=True)
chart.add_series("Deterministic AST Baseline", [90, 96, 87, 61, 82, 60, 54], style=Styles.SecondaryNeutral)
chart.add_series("Final Audited Score (-10pt AI Adj.)", [80, 86, 77, 51, 72, 50, 44], style=Styles.PrimaryFlat)
chart.draw(xy=(8.0, 12.0))
chart.draw_legend(
    xy=(36.0, 4.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    orientation="horizontal",
    item_gap=10.0,
)

save()
```

| Engineering Axis | Deterministic Baseline | AI Δ (`±10pt`) | Final Score | Qualitative Adjustment Rationale |
| :--- | :---: | :---: | :---: | :--- |
| **Architecture** | `90` | **`-10`** | **`80`** | Runtime `BillingController <-> BillingManager` circular dependency, `@Autowired` field injection, mutable singleton field `BillingController.channel`, and process-local static `HashMap INVOICE_CACHE`. |
| **Code Quality** | `96` | **`-10`** | **`86`** | `BillingManager.processBatchBilling` god method (`cognitive=56`, 8 params, 57 LOC), 3 `String ==` reference-equality bugs, empty `catch` block, broken private `@Transactional` self-invocation, and 4 `System.out`/`printStackTrace` calls. |
| **Typing** | `87` | **`-10`** | **`77`** | Raw `Map`/`List` generics in `BillingController` and `BillingManager`, untyped `Object` parameters (`traceHint`, `extraContext`), `@SuppressWarnings("unchecked")`, and Java 11 `java.net.http` import colliding with Java 1.8 target. |
| **Testing** | `61` | **`-10`** | **`51`** | Sole JUnit 4 test (`BillingManagerTest.testSmokeRun`) is assertion-free, static module coverage is `33.3%`, and live Maven/JaCoCo execution is completely blocked by the Java 8 vs. Spring Boot 4.2.0 build crash. |
| **Dependencies** | `82` | **`-10`** | **`72`** | Unpinned `spring-boot-starter-web:LATEST` (dynamically pulling Spring Boot 4.2.0 bytecode `61.0` and breaking Java 1.8 builds), EOL `javax.servlet`/JUnit 4, missing `mvnw`, and missing Dependabot. |
| **Security** | `60` | **`-10`** | **`50`** | Hardcoded `GATEWAY_SECRET` (`<REDACTED_SECRET>`), privileged `pull_request_target` + `actions/checkout@main` CI, root `openjdk:latest` Dockerfile (`DS-0001`/`DS-0002`/`DS-0026`), unpinned CRITICAL `CVE-2022-22965` static exposure, unauthenticated catch-all `ANY /charge`, and blocked DAST. |
| **Documentation** | `54` | **`-10`** | **`44`** | Minimal 2-line `README.md`, `33.3%` Javadoc coverage (10 missing public Javadocs), stale `@param obsoleteToken` mismatch, and missing `LICENSE`/`SECURITY.md`. |
| **Overall Composite** | **`76`** | **`-10`** | **`66 (C)`** | **Compounding build, security, and architectural failures reduce overall health to Grade C.** |

---

## Executed Audit Step Scores & Finding Source Split

All eight executed audit steps scored **Grade D (`10` to `25 / 100`)**, led downward by `container_runtime_audit (10)`, `supply_chain_audit (15)`, and `java_test_audit (15)`.

```drawlib align=center code=hide file=audit_step_scores_bar.png caption="Executed Audit Step Scores Sorted Weakest-First (Left) and Finding Source & Triage Provenance (Right)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

# Left: Horizontal BarChart of all 8 audit steps (weakest-first bottom to top -> weakest visually prominent)
bar = BarChart(
    axis_line_style=Styles.Dark,
    width=70.0,
    height=52.0,
    categories=[
        "Java AST",
        "Repo Structure",
        "Web Pentest",
        "Security SCA",
        "Service PRR",
        "Java Testing",
        "Supply Chain",
        "Container Runtime",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="Audit Step Scores (0-100, All Grade D)",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
bar.configure_x_axis(min_value=0, max_value=100, tick_step=20, show_grid=True)
bar.add_series("Step Score", [25, 24, 20, 18, 16, 15, 15, 10], style=Styles.DangerFlat)
bar.draw(xy=(22.0, 7.0))

# Right: Provenance & Triage KPIs
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.30,
    spacing=2.4,
)
kpis.add(
    "7 Det.",
    "Deterministic Analyzers",
    "AST, manifest, Docker, Trivy",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
    accent_style=Styles.PrimaryFlat,
)
kpis.add(
    "12 AI",
    "AI Qualitative Findings",
    "Cross-file architecture & PRR",
    style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    accent_style=Styles.SecondaryFlat,
)
kpis.add(
    "14 Locs",
    "Consolidated Index",
    "Deduplicated from 19 raw items",
    style=Styles.Neutral.patch(shape_r=2.0),
    accent_style=Styles.DarkFlat,
)
kpis.add(
    "0 / 0",
    "FP Triage & Waivers",
    "0 waived FPs; 0 [[opt_out]]",
    style=Styles.Neutral.patch(shape_r=2.0),
    accent_style=Styles.MutedFlat,
)
kpis.draw((96.0, 8.0), width=46.0, height=50.0, columns=1)

save()
```

### Finding Source Split, Triage & Waiver Log

- **Finding Source Split**: `deterministic_analyzers = 7`, `ai_qualitative = 12`, `total = 19` (consolidated to `14` unique locations).
- **AI False-Positive Triage Log**: `0` deterministic pre-findings waived or reclassified.
- **Configured Design Waivers (`pni.toml [[opt_out]]`)**: `0` active waivers.

---

## Rule Compliance Matrix (`FAIL -> WARN`, 16 Rules)

| Status | Rule ID | Source Action | Concise Compliance Evidence |
| :---: | :--- | :--- | :--- |
| **`FAIL`** | `common/architecture` | `java_ast_audit` | 1 runtime circular dependency (`BillingController -> BillingManager -> BillingController`), upward service->controller coupling via `@Autowired circularController`, and mutable static `INVOICE_CACHE`. |
| **`FAIL`** | `common/documentation` | `repo_structure_audit` | `README.md` is only 2 lines (`# Legacy Billing` / `Run mvn spring-boot:run`) with no architecture overview, environment configuration, API spec, or test instructions. |
| **`FAIL`** | `common/maintainability` | `java_ast_audit` | `BillingManager.processBatchBilling` violates SIG unit size (57 lines), complexity (`branches=13`, `cognitive=56`), interfacing (8 params > 6), and holds mutable static `INVOICE_CACHE` plus empty catch at line 83. |
| **`FAIL`** | `common/production_readiness` | `container_runtime_audit` | Service cannot build or boot; `GatewayClient.java:22` lacks HTTP `connectTimeout`; `BillingManager.java:83` swallows exceptions in empty catch; 4 `System.out`/`printStackTrace` calls bypass structured logging; no Actuator `/healthz`; unauthenticated `ANY /charge`. |
| **`FAIL`** | `common/runtime_verification` | `deterministic_baseline` | `harness_build=failed`; `RV-01` failed (`docker.io/library/openjdk:latest not found` and Java 8 Maven harness failed compiling `spring-boot-4.2.0.jar` bytecode `61.0` vs `52.0`); `RV-02`/`RV-03`/`RV-04` blocked. |
| **`FAIL`** | `common/security` | `repo_structure_audit` | Hardcoded `GATEWAY_SECRET` (`<REDACTED_SECRET>`) at `GatewayClient.java:13`, privileged `pull_request_target` CI workflow, root `openjdk:latest` container, raw unvalidated `Map` payload, and unauthenticated catch-all `ANY /charge`. |
| **`FAIL`** | `common/security_vulnerability` | `java_ast_audit` | `SEC-01`: CRITICAL `CVE-2022-22965` (CVSS 9.8) on unpinned `spring-boot-starter-web:LATEST`; `SEC-02`: Dockerfile `DS-0002` HIGH root + `DS-0001` MED `:latest` + `DS-0026` LOW; `SEC-03`: hardcoded `GATEWAY_SECRET`; `SEC-05`: unauthenticated `ANY /charge`; `SEC-06`: DAST `error` (`0` probes, container build failed). |
| **`FAIL`** | `common/supply_chain` | `repo_structure_audit` | Missing `LICENSE`, `SECURITY.md`, Dependabot, and `mvnw`/lockfile; unpinned `spring-boot-starter-web:LATEST`; `.github/workflows/build.yml` uses `pull_request_target` + `actions/checkout@main` without `permissions:`; `Dockerfile` uses mutable root `openjdk:latest` without `.dockerignore`. |
| **`FAIL`** | `common/twelve_factor` | `service_readiness_audit` | Factor III FAIL: direct `System.getenv("LEGACY_PAYMENT_URL")` in `GatewayClient.java:16`; Factor VI FAIL: mutable static `INVOICE_CACHE` and singleton field `BillingController.channel`; Factor XI FAIL: 4 `System.out.println`/`printStackTrace` calls. |
| **`FAIL`** | `java/code_quality` | `java_ast_audit` | `33.3%` Javadoc coverage (10 missing Javadocs, 1 `@param` mismatch with stale `obsoleteToken`), 3 `String ==` literal bugs (`status=="PAID"`, `currency=="USD"/"JPY"`), empty catch block, 4 `System.out`/`printStackTrace` calls. |
| **`FAIL`** | `java/dependencies` | `repo_structure_audit` | `pom.xml` pins `maven.compiler.source/target` to EOL `1.8`, uses dynamic version `LATEST` for `spring-boot-starter-web`, depends on legacy `javax.servlet:4.0.1` and JUnit 4 (`4.13.2`), and lacks `mvnw`. |
| **`FAIL`** | `java/frameworks/spring_boot` | `java_ast_audit` | 3 `@Autowired` field injections (`BillingController`, `BillingManager`), mutable singleton field `BillingController.channel` mutated per request, catch-all `@RequestMapping("/charge")`, private `@Transactional` without `spring-tx`, and legacy `javax.servlet`. |
| **`FAIL`** | `java/modern_stack` | `java_ast_audit` | Java `1.8` target collides with Java 11 `java.net.http.HttpClient` import in `GatewayClient.java:4`; `LegacyDateHelper` uses non-thread-safe `SimpleDateFormat`, `java.util.Date`, and synchronized `Vector`; 4 unsorted imports and 1 wildcard import. |
| **`FAIL`** | `java/testing` | `java_test_audit` | Legacy JUnit 4 (`junit:4.13.2`), only 1 test method (`BillingManagerTest.testSmokeRun`) with zero assertions (`assertion_free_tests=1`), `33.3%` static module coverage, and runtime JUnit/JaCoCo execution blocked by build failure. |
| **`FAIL`** | `java/typing` | `java_ast_audit` | `81.8%` type safety coverage: raw `Map`/`List` in `BillingController.chargeCustomer` and `BillingManager.processBatchBilling`, untyped `Object` params (`traceHint`, `extraContext`), and `@SuppressWarnings("unchecked")`. |
| **`WARN`** | `common/git_workflow` | `repo_structure_audit` | `.gitignore` is missing and `.github/workflows/build.yml` runs `mvn package` on `pull_request_target` instead of safe `pull_request` verification. |

---

## Consolidated Location Findings Index (14 Unique Locations)

| # | Severity | Location | Rules | Evidence & Recommended Fix |
| :---: | :---: | :--- | :--- | :--- |
| 1 | **`CRITICAL`** | `.github/workflows/build.yml` | `common/supply_chain` | Triggers on `pull_request_target` without `permissions:` and uses mutable `actions/checkout@main`. **Fix**: Switch to `pull_request`, add `permissions: { contents: read }`, and SHA-pin actions. |
| 2 | **`CRITICAL`** | `examples/java/api_spring_messy/src/main/java/com/example/billing/client/GatewayClient.java:13` | `common/security` | Hardcoded secret literal assigned to `GATEWAY_SECRET` (`<REDACTED_SECRET>`, OWASP ASVS). **Fix**: Move secrets to environment variables or a secret manager and rotate exposed keys. |
| 3 | **`CRITICAL`** | `pom.xml` | `common/security_vulnerability`, `common/runtime_verification`, `java/dependencies` | Unpinned `spring-boot-starter-web@LATEST` triggers Trivy `CVE-2022-22965` range match AND breaks Maven build (`spring-boot-4.2.0.jar` bytecode `61.0` vs Java `1.8` `52.0`), alongside legacy `javax.servlet`/JUnit 4 and missing `mvnw`. **Fix**: Pin Java 21 LTS + Spring Boot 3.4.x BOM + JUnit 5 and commit `mvnw`. |
| 4 | **`CRITICAL`** | `src/main/java/com/example/billing/client/GatewayClient.java` | `common/security`, `java/modern_stack` | Embeds hardcoded `GATEWAY_SECRET` (`<REDACTED_SECRET>`), imports Java 11 `java.net.http` on Java 1.8 target, lacks connect/read timeouts, calls `System.getenv`, and prints stack traces. **Fix**: Rotate/externalize secret, upgrade to Java 21 + timeout-bounded `RestClient`, `@ConfigurationProperties`, SLF4J, and sorted imports. |
| 5 | **`CRITICAL`** | `—` *(Dependency SCA)* | `CVE-2022-22965` | `org.springframework.boot:spring-boot-starter-web@LATEST (pom)` matched full historical Spring4Shell range. **Fix**: Lock to a patched release (`2.5.12, 2.6.6` minimum; target Spring Boot 3.4.x BOM). |
| 6 | **`HIGH`** | `Dockerfile` | `common/supply_chain` | Builds from deprecated/mutable `openjdk:latest`, copies workspace without `.dockerignore`, and runs as `root`. **Fix**: Multi-stage `eclipse-temurin:21-jdk` / `21-jre-alpine` with non-root `USER` and `.dockerignore`. |
| 7 | **`HIGH`** | `src/main/java/com/example/billing/controller/BillingController.java` | `common/security_vulnerability`, `java/frameworks/spring_boot` | Blocked `web_pentest` (`ANY /charge`), mutates singleton field `channel` per request, and binds raw `Map` without Bean Validation or auth. **Fix**: Remove `channel`, enforce `@PostMapping("/charge")` + `@Valid` Java `record` + auth, and re-run `web_pentest`. |
| 8 | **`HIGH`** | `src/main/java/com/example/billing/service/BillingManager.java` | `common/architecture`, `java/code_quality` | Circular `@Autowired BillingController`, static raw `INVOICE_CACHE`, `processBatchBilling` (`cognitive=56`, 8 params, stale `@param obsoleteToken`, `String ==` lines 52/55/57, empty catch line 83, broken private `@Transactional`). **Fix**: Constructor injection, externalize cache, decompose method, `.equals()`, SLF4J, repository bean. |
| 9 | **`HIGH`** | `src/test/java/com/example/billing/BillingManagerTest.java` | `java/testing` | `testSmokeRun` only instantiates `InvoiceRecord` without assertions or coverage of core classes. **Fix**: JUnit 5 + Mockito + `MockMvc` characterization suite reaching `>=80%` JaCoCo line coverage. |
| 10 | **`HIGH`** | `—` *(Import Graph)* | `common/architecture` | Circular import cycle: `BillingController -> BillingManager -> BillingController`. **Fix**: Remove upward dependency and extract shared models/interfaces into a lower layer. |
| 11 | **`MEDIUM`** | `examples/java/api_spring_messy/src/main/java/com/example/billing/service/BillingManager.java:33` | `common/maintainability` | `processBatchBilling`: `length=57 lines`, `branches=13`, `cognitive=56`. **Fix**: Decompose into cohesive single-responsibility helpers (`cognitive <= 15`). |
| 12 | **`MEDIUM`** | `—` *(Repository Docs)* | `common/documentation` | `has_readme=True`, `lines=2`. **Fix**: Document architecture, environment setup, API usage, and test commands in `README.md`. |
| 13 | **`MEDIUM`** | `—` *(Lockfile)* | `common/supply_chain` | `manifests=['pom.xml']`, `lockfiles=[]`. **Fix**: Pin BOM coordinates and commit Maven Wrapper (`mvnw`) / dependency verification metadata. |
| 14 | **`LOW`** | `—` *(Version Bounds)* | `common/supply_chain` | `unpinned=['org.springframework.boot:spring-boot-starter-web:LATEST']`. **Fix**: Pin explicit dependency versions to ensure reproducible builds. |

---

## Machine-Readable Evidence Artifacts

All structured metrics, findings, DAG metadata, and deterministic scanner outputs are persisted as machine-readable artifacts for CI gates and IDE integration:

| Artifact Path | Format / Schema | Purpose |
| :--- | :--- | :--- |
| `docs/reports/java_api_spring_messy/java_api_spring_messy_score.json` | `ScoreResult` v2.0 (JSON) | Full structured 7-axis score, compliance matrix, findings, and action plan |
| `docs/reports/java_api_spring_messy/java_api_spring_messy_summary.json` | `ScoreSummary` (JSON) | Lightweight CI / portal summary badge metrics |
| `docs/reports/java_api_spring_messy/java_api_spring_messy_findings.sarif` | `SARIF 2.1.0` | GitHub Code Scanning & IDE inline diagnostic findings |
| `docs_src/reports/java_api_spring_messy/_facts/plan.json` | PNI Plan v2.0 (JSON) | Pre-flight reconnaissance plan & validated workflow DAG |
| `docs_src/reports/java_api_spring_messy/_facts/facts.json` | Deterministic Bundle (JSON) | Raw AST, Maven/Docker runtime, Trivy SCA, and pentest facts |
| `docs_src/reports/java_api_spring_messy/_facts/architecture.json` | `ArchitectureRecord` (JSON) | Grounded 5-layer architecture, symbol map, and execution flows |
