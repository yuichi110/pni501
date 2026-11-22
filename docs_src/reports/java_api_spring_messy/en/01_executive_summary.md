# 1. Executive Summary

`legacy-billing` (`examples/java/api_spring_messy`) scores **66/100 (Grade C)** with **`0/16` rules passing** (`15 FAIL`, `1 WARN`), reflecting a `-10pt` qualitative deduction across all seven engineering dimensions relative to its deterministic AST baseline of **76/100**. Live Docker verification, tree-sitter AST analysis, and Trivy SCA proved a single compounding causal chain: unpinned `spring-boot-starter-web:LATEST` in `pom.xml` simultaneously breaks Maven compilation on Java 1.8, triggers a CRITICAL static Spring4Shell range alert, and blocks both JaCoCo coverage and dynamic HTTP penetration testing.

```drawlib align=center code=hide file=exec_7axis_radar.png caption="7-Axis Engineering Health Radar (Deterministic Baseline vs. Final Audited Score) and Executive KPIs"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

# Left: 7-Axis RadarChart comparing Deterministic Baseline vs Final Score
radar = RadarChart(
    categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Docs",
    ],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=9.8),
    grid_style=Styles.MutedThin,
    scale_text_style=Styles.Muted.patch(text_size=8.5),
    radius=20.0,
    width=72.0,
    height=56.0,
    min_value=0.0,
    max_value=100.0,
    levels=5,
    grid_shape="polygon",
    title="7-Axis Health: Baseline (76) vs. Final (66)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
radar.add_series(
    "AST Baseline",
    [90, 96, 87, 61, 82, 60, 54],
    style=Styles.SecondaryNeutral,
    fill_alpha=0.22,
    line_style="dashed",
    line_width=1.8,
)
radar.add_series(
    "Final Audited",
    [80, 86, 77, 51, 72, 50, 44],
    style=Styles.PrimaryFlat,
    fill_alpha=0.28,
    line_width=2.2,
)
radar.draw(xy=(4.0, 11.0))
radar.draw_legend(
    xy=(14.0, 4.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    orientation="horizontal",
    item_gap=6.0,
)

# Right: Executive headline KPI stack
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.31,
    spacing=2.6,
)
kpis.add(
    "66/100",
    "Overall Health (Grade C)",
    "Baseline 76 with -10pt qualitative deduction",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=13.0),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "0 / 16",
    "Rules Passed (15 FAIL)",
    "1 WARN (git_workflow); all 8 steps Grade D",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "FAILED",
    "Container Runtime & DAST",
    "Maven build 61.0 vs 52.0; 0 tests, 0 probes",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    accent_style=Styles.DarkFlat,
)
kpis.add(
    "6 CRIT",
    "19 Findings / 14 Locations",
    "CVE-2022-22965, secret, CI, Docker",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.draw((80.0, 7.0), width=62.0, height=58.0, columns=1)

save()
```

---

## Live AST × Docker × Trivy Causal Chain & Key Findings

The central operational insight of this audit is that build instability, unverified runtime behavior, and critical supply-chain exposure all originate from the same unpinned dependency and deprecated container baseline:

1. **Unpinned Manifest (`pom.xml`)**: `org.springframework.boot:spring-boot-starter-web` specifies `<version>LATEST</version>` alongside an end-of-life Java `1.8` compiler target (`52.0` bytecode) and no Maven Wrapper (`mvnw`).
2. **Live Compiler Crash (`harness_build`)**: During containerized build verification (`java/maven.dockerfile`, `JAVA_VERSION=8`), Maven resolved `spring-boot-4.2.0.jar` (`SpringApplication.class`, bytecode `61.0` / JDK 17+), aborting compilation immediately with `class file has wrong version 61.0, should be 52.0`. Meanwhile, the project `Dockerfile` failed in `1.21s` because `docker.io/library/openjdk:latest` is no longer published on Docker Hub.
3. **Compounding Verification Blindness & Static SCA Risk**: Because neither the project image nor the Maven harness could compile, offline JUnit execution (`0/0` tests), JaCoCo line coverage (`N/A`), Spring Boot startup smoke checks (`blocked`), and live HTTP penetration testing (`web_pentest`, `0/0` probes) were all blocked. Simultaneously, Trivy filesystem SCA evaluated the unpinned `LATEST` specifier against the full historical CVE range (`is_unpinned_specifier=True`), raising **CRITICAL `CVE-2022-22965`** (Spring4Shell, CVSS 9.8).
4. **Concentrated Source Hotspots**: Inside the 187-LOC codebase, architectural and security debt concentrates in three classes—`BillingManager.java` (circular `BillingController` dependency, `cognitive=56`, 8 parameters, static `INVOICE_CACHE`, `String ==` bugs, empty `catch`, broken private `@Transactional`), `GatewayClient.java` (hardcoded `GATEWAY_SECRET` redacted as `<REDACTED_SECRET>`, Java 11 `java.net.http` mismatch on Java 1.8 target, missing HTTP timeout), and `BillingController.java` (mutable singleton `channel` race condition, unauthenticated catch-all `ANY /charge`).

```drawlib align=center code=hide file=exec_causal_chain_risks.png caption="AST × Docker × Trivy Failure Causal Chain (Top) and Strengths vs. Top Critical Risks (Bottom)"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, ChevronProcess, Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=84, dpi=150)

# Section title for causal chain
text(
    (73.0, 80.0),
    "Root-Cause Chain: Unpinned Manifest -> Bytecode Crash -> Blocked Verification & SCA Exposure",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Top half: 4-stage ChevronProcess causal chain
chain = ChevronProcess(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    corner_angle=62.0,
    spacing=1.5,
    flat_left_end=True,
)
chain.add(
    "1. Unpinned Manifest",
    description="pom.xml: LATEST\nJava 1.8 + no mvnw",
    style=Styles.Neutral,
)
chain.add(
    "2. Live Resolution",
    description="Spring Boot 4.2.0\nBytecode 61.0 pulled",
    style=Styles.PrimaryNeutral,
)
chain.add(
    "3. Container Crash",
    description="61.0 vs 52.0 error\nopenjdk:latest 404",
    style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.5),
)
chain.add(
    "4. Blocked Gates",
    description="JaCoCo & DAST blocked\nCVE-2022-22965 range",
    style=Styles.WarningNeutral,
)
chain.draw(xy=(4.0, 58.0), width=138.0, height=18.0)

# Bottom-left: Verified Strengths Panel
p_str = Panel(
    "Verified Baseline Strengths (2)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.SuccessNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.8),
    header_variant="filled",
    header_height=7.5,
)
p_str.draw((4.0, 4.0), width=66.0, height=49.0)

strengths = CardList(
    style=Styles.SuccessNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.3),
    badge_shape="rounded_rect",
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.3),
    direction="vertical",
    spacing=3.0,
)
strengths.add(
    "Test Scope Isolation",
    "junit:4.13.2 cleanly scoped to\n<scope>test</scope> in pom.xml.",
    badge_text="OK",
)
strengths.add(
    "Clean Immutable DTO Baseline",
    "InvoiceRecord.java has full Javadocs\nand 0 AST violations.",
    badge_text="OK",
)
strengths.draw((7.0, 7.5), width=60.0, height=34.5)

# Bottom-right: Top Critical Risks Panel
p_risk = Panel(
    "Top Critical Risks Requiring P0 Action (3)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.8),
    header_variant="filled",
    header_height=7.5,
)
p_risk.draw((76.0, 4.0), width=66.0, height=49.0)

risks = CardList(
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    direction="vertical",
    spacing=2.2,
)
risks.add(
    "CRITICAL CVE-2022-22965 (CVSS 9.8)",
    "Unpinned starter-web@LATEST\nstatic full-range exposure.",
    badge_text="CRIT",
)
risks.add(
    "Hardcoded GATEWAY_SECRET",
    "GatewayClient.java:13 embeds\n<REDACTED_SECRET> in source.",
    badge_text="CRIT",
)
risks.add(
    "CI Token & Root Container Risk",
    "pull_request_target + @main;\nroot openjdk:latest Dockerfile.",
    badge_text="CRIT",
)
risks.draw((79.0, 6.5), width=60.0, height=37.0)

save()
```

---

## Executive Scorecard Summary

| Verification Gate | Status | Key Observed Evidence |
| :--- | :--- | :--- |
| **Overall Health Score** | **66 / 100 (Grade C)** | 7-axis scores: `architecture=80`, `code_quality=86`, `typing=77`, `testing=51`, `dependencies=72`, `security=50`, `documentation=44` |
| **Lowest-Scoring Audit Steps** | **10 – 15 / 100 (Grade D)** | `container_runtime_audit=10 (D)`, `supply_chain_audit=15 (D)`, `java_test_audit=15 (D)` |
| **Container Runtime (`RV-01..04`)** | **`failed`** | `build=failed`, `tests=0/0 (blocked)`, `line_cov=N/A`, `smoke=blocked (web_api)` |
| **Trivy SCA & IaC (`SEC-01..03`)** | **`failed`** | `app_cves=1` (`CRITICAL=1`, `HIGH=0`), Dockerfile misconfigs=`3` (`HIGH=1`, `MED=1`, `LOW=1`), Trivy secrets=`0` (AST hardcoded secret=`1`) |
| **Dynamic Web Pentest (`SEC-06`)** | **`error` (blocked)** | `probes=0/0` passed, `findings=0`; suite materialized at `.pni/pentests/examples/java/api_spring_messy` but target container failed to build |
| **Approved Audit Plan & Scope** | **Full Repository** | Auto-approved via `--auto-approve` (`plan_gate=false`); 6 source files (`src/main/java`), 1 test file (`src/test/java`), `README.md` |
