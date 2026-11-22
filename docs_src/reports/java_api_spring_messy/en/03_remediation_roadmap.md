# 3. Recommended Remediation Roadmap

Remediation of `legacy-billing` is sequenced into **11 prioritized actions (`5 P0`, `5 P1`, `1 P2`)** designed to restore deterministic Java 21 / Spring Boot 3.4 buildability and eliminate critical security exposure first, before establishing a JUnit 5 characterization harness and refactoring the cyclic monolith into a clean, thread-safe architecture.

```drawlib align=center code=hide file=remediation_roadmap.png caption="Phased Remediation Roadmap (P0 -> P1 -> P2) Feeding Directly into the java_api_spring_messy_migration Execution Plan"
from drawlib.canvas import save, setup
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=82, dpi=150)

text(
    (73.0, 78.0),
    "Phased Remediation Timeline (P0 Urgent -> P1 Hardening -> P2 Governance -> Migration Plan)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.3),
    description_style=Styles.Dark.patch(text_size=9.3),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.3),
    direction="vertical",
    card_shape="rounded_rect",
    spacing=2.6,
)
rm.add(
    "P0 — Unblock Build, Secrets, CI & DI Cycle (5 Actions)",
    "Pin Java 21 LTS + Spring Boot 3.4.x BOM + eclipse-temurin:21 non-root Dockerfile;\nfix pull_request_target CI, delete GATEWAY_SECRET, break BillingController<->BillingManager cycle.",
    badge_text="P0 | NOW",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    badge_style=Styles.DangerFlat,
)
rm.add(
    "P1 — Characterization Tests, Refactoring & DAST (5 Actions)",
    "JUnit 5 + MockMvc tests (>=80% cov); RestClient timeouts, @ConfigurationProperties & SLF4J;\ndecompose processBatchBilling (cog <=15), adopt java.time, and re-run web_pentest.",
    badge_text="P1 | NEXT",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
)
rm.add(
    "P2 — Documentation & Repository Governance (1 Action)",
    "Expand README.md with architecture, environment config, API contract, and test commands;\ncommit LICENSE, SECURITY.md, .gitignore, and Dependabot configuration.",
    badge_text="P2 | POLISH",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.3),
)
rm.add(
    "Chained Execution: java_api_spring_messy_migration",
    "Operationalizes P0-P2 as a staged Clean Architecture plan with Stakeholder Decision Log\n(String == tax semantics), verified offline Maven/JaCoCo gates, and live DAST probes.",
    badge_text="MIGRATION",
    style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=Styles.WhiteBold.patch(text_size=10.3),
    description_style=Styles.White.patch(text_size=9.3),
    badge_style=Styles.DarkFlat,
)
rm.draw((6.0, 5.0), width=134.0, height=69.0)

save()
```

---

## Remediation Effort & Domain Distribution

Security and dependency stabilization account for **55% (6 of 11)** of the backlog, with every `P0` action directly unblocking either Maven/Docker compilation (`RV-01`), critical SCA/secret findings (`SEC-01..03`), or Spring Boot 3.x startup (which prohibits bean cycles by default).

```drawlib align=center code=hide file=remediation_priority_breakdown.png caption="Remediation Action Distribution by Engineering Domain (Left) and Phase Gate Targets (Right)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

# Left: Action counts by category (single series)
bar = BarChart(
    axis_line_style=Styles.Dark,
    width=76.0,
    height=46.0,
    categories=["Security", "Code Quality", "Dependencies", "Architecture", "Testing", "Docs"],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.8),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    value_format="{:.0f}",
    title="11 Remediation Actions by Target Domain",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
bar.configure_x_axis(min_value=0, max_value=5, tick_step=1, show_grid=True)
bar.add_series("Actions", [4, 2, 2, 1, 1, 1], style=Styles.PrimaryFlat)
bar.draw(xy=(6.0, 7.0))

# Right: Phase exit criteria KPI cards
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.28,
    spacing=2.6,
)
kpis.add(
    "5 P0",
    "Phase 0: Unblock & Secure",
    "0 CRIT CVEs/secrets; clean Java 21 build",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=12.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "5 P1",
    "Phase 1: Test & Refactor",
    "JUnit 5 >=80% cov; cog <=15; DAST green",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=12.5),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "1 P2",
    "Phase 2: Governance",
    "README, LICENSE, SECURITY, .gitignore",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.draw((86.0, 8.0), width=56.0, height=45.0, columns=1)

save()
```

---

## Action Plan Traceability Matrix (`P0 -> P1 -> P2`)

Every action below preserves the exact pre-sorted priority sequence from `java_api_spring_messy_score.json` and maps directly to concrete target files, measurable engineering impact, and audited rule/CVE identifiers:

| # | Priority | Category | Action Title & Concrete Work | Target Files | Expected Impact | Related Rules / CVEs |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **`P0`** | `architecture` | **Break `BillingController<->BillingManager` cycle and eliminate mutable singleton/static state**: Remove `circularController` and `BillingController.channel`, switch to constructor injection, and externalize `INVOICE_CACHE`. | `src/main/java/com/example/billing/controller/BillingController.java`, `src/main/java/com/example/billing/service/BillingManager.java` | Eliminates Spring DI circularity and concurrent cross-request data races. | `common/architecture`, `java/frameworks/spring_boot` |
| 2 | **`P0`** | `dependencies` | **Fix broken Maven & Docker build by pinning Java 21 LTS + Spring Boot 3.4 BOM + `eclipse-temurin:21`**: Replace Java 1.8 + `spring-boot-starter-web:LATEST` with Java 21 + pinned Spring Boot 3.4.x parent/BOM and replace deprecated `openjdk:latest` with `eclipse-temurin:21-jdk/jre`. | `pom.xml`, `Dockerfile` | Restores deterministic compilation, JaCoCo test coverage, and runtime boot verification. | `common/runtime_verification`, `java/dependencies` |
| 3 | **`P0`** | `security` | **Harden GitHub Actions CI trigger and root Dockerfile**: Replace `pull_request_target` with `pull_request` + minimal permissions + SHA-pinned actions, and migrate `Dockerfile` to pinned non-root `eclipse-temurin:21-jre` with `.dockerignore`. | `.github/workflows/build.yml`, `Dockerfile` | Eliminates CI token hijacking and mutable root container exposure. | `common/supply_chain`, `common/security` |
| 4 | **`P0`** | `security` | **Pin Spring Boot 3.4.x BOM and eliminate Dockerfile root/`:latest` misconfigurations**: Lock Spring Boot 3.4.x via parent/BOM (resolving static `CVE-2022-22965` unpinned range matching) and harden `Dockerfile` to resolve `DS-0001`, `DS-0002`, and `DS-0026`. | `pom.xml`, `Dockerfile` | Eliminates CRITICAL unpinned SCA exposure and HIGH root-container misconfiguration. | `common/security_vulnerability`, `SEC-01`, `SEC-02`, `CVE-2022-22965` |
| 5 | **`P0`** | `security` | **Remove hardcoded `GATEWAY_SECRET` and inject via `@ConfigurationProperties`**: Delete the `GATEWAY_SECRET` string constant at line 13, rotate credentials, and bind secrets via Spring `@ConfigurationProperties` from externalized environment/vault config. | `src/main/java/com/example/billing/client/GatewayClient.java` | Eliminates CRITICAL credential exposure in source control. | `common/security`, `common/supply_chain` |
| 6 | **`P1`** | `code_quality` | **Configure `RestClient` timeouts, `@ConfigurationProperties`, SLF4J logging, and Actuator `/healthz`**: Replace `System.getenv` and `HttpClient.newHttpClient()` with `@ConfigurationProperties` + timeout-bounded `RestClient`, replace `System.out`/`printStackTrace` and empty catch with SLF4J error logging, and enable Spring Boot Actuator health probes. | `src/main/java/com/example/billing/client/GatewayClient.java`, `src/main/java/com/example/billing/service/BillingManager.java` | Prevents thread exhaustion from hung gateway calls and restores 12-Factor observability. | `common/twelve_factor`, `common/production_readiness` |
| 7 | **`P1`** | `code_quality` | **Refactor `processBatchBilling`, fix `String ==` / empty catch / private `@Transactional`, and replace legacy `Date`/`Vector`**: Replace raw `Map`/`List` with typed DTO records, decompose `processBatchBilling` (`cognitive <=15`, `params <=6`), use `.equals()` + SLF4J, and replace `SimpleDateFormat`/`Date`/`Vector` with `java.time` and `List`. | `src/main/java/com/example/billing/service/BillingManager.java`, `src/main/java/com/example/billing/util/LegacyDateHelper.java` | Drastically reduces defect risk and restores type safety and readability. | `common/maintainability`, `java/code_quality`, `java/typing`, `java/modern_stack` |
| 8 | **`P1`** | `dependencies` | **Upgrade Maven build to Java 21 LTS, Spring Boot 3.4 BOM, and `mvnw`**: Migrate `pom.xml` from Java 1.8 / `LATEST` / `javax` / JUnit 4 to Java 21 LTS + Spring Boot 3.4 BOM + JUnit 5 and commit `mvnw`. | `pom.xml` | Restores deterministic reproducible builds and supported LTS security updates. | `java/dependencies`, `common/supply_chain` |
| 9 | **`P1`** | `security` | **Re-run `web_pentest` after restoring Java 21 + Spring Boot 3.4 container build**: After fixing `pom.xml` and `Dockerfile` buildability, execute `.pni/pentests/examples/java/api_spring_messy` to verify POST-only enforcement, validation, and security headers. | `pom.xml`, `src/main/java/com/example/billing/controller/BillingController.java` | Restores continuous dynamic security verification (`SEC-06`). | `common/security_vulnerability`, `SEC-06` |
| 10 | **`P1`** | `testing` | **Replace assertion-free JUnit 4 smoke test with JUnit 5 + `MockMvc` characterization suite**: Migrate to JUnit 5 Jupiter and add characterization tests with real assertions for `BillingController`, `BillingManager`, and `GatewayClient` before refactoring. | `src/test/java/com/example/billing/BillingManagerTest.java` | Creates a safety harness for Java 21 / Clean Architecture migration and lifts coverage to `>=80%`. | `java/testing` |
| 11 | **`P2`** | `documentation` | **Expand README and add core repository governance files**: Expand `README.md` with setup, environment config, API endpoints, and test commands, and add `LICENSE`, `SECURITY.md`, and `.gitignore`. | `README.md` | Improves onboarding and repository governance compliance. | `common/documentation`, `common/git_workflow` |

---

## Handoff to Chained Migration Plan (`java_api_spring_messy_migration`)

This diagnostic roadmap links directly into the chained **`java_api_spring_messy_migration`** execution workflow, which operationalizes the 11 items above into verified migration waves:

1. **Wave 1 (Stabilize & Lock — Actions #2, #3, #4, #5)**: Pin Java 21 LTS + Spring Boot 3.4.x BOM + `mvnw`, harden `.github/workflows/build.yml` and `Dockerfile`, and externalize `GATEWAY_SECRET`.
2. **Wave 2 (Safety Harness & Behavioral Contract — Actions #10, #7)**: Establish JUnit 5 + `MockMvc` characterization tests and log stakeholder confirmation on `String ==` tax-branch behavior (`PAID`, `USD`, `JPY`) before altering business semantics.
3. **Wave 3 (Clean Architecture & PRR — Actions #1, #6, #7, #8, #9, #11)**: Eliminate the `BillingController <-> BillingManager` cycle, extract typed Java `record` DTOs and repository/gateway ports, enforce `@PostMapping("/charge")` with `@Valid` and auth, re-run `web_pentest` + JaCoCo (`>=80%`), and finalize governance documentation.
