# 1. Migration Strategy Summary & Multi-Axis Gap Matrix

This phased PR execution plan modernizes `legacy-billing` (Baseline Audit `wf-8177454c`: **Grade C, 66/100**) from a broken Java 1.8 / unpinned Spring Boot / cyclic monolith into a deterministic **Java 21 LTS + Spring Boot 3.4.x + PostgreSQL 16 (JPA + Flyway) + Redis 7** service organized under **Clean Architecture** (`domain` / `port` / `usecase` / `adapter`).

```drawlib align=center code=fold file=multi_axis_gap_matrix.png caption="Multi-Axis As-Is Baseline vs. To-Be Target Transformation Gap Matrix (7 Axes)"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=88, dpi=150)

text(
    (78.0, 83.2),
    "Multi-Axis As-Is -> To-Be Transformation Gap Matrix (7 Axes)",
    style=Styles.DarkBold.patch(text_size=12.5),
)

table = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.0),
    border_style=Styles.MutedThin,
)

table.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)
table.set_style_cell_header(
    background_color=Colors.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2, 3, 4, 5, 6, 7],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.DangerNeutral.shape_fill_color,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    rows=[1, 2, 6, 7],
    columns=[3],
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[3, 4, 5],
    columns=[3],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Axis", "As-Is Baseline (66/100)", "To-Be Target State", "Risk", "Execution Approach"],
    [
        "1. Runtime\n(language)",
        "Java 1.8 vs java.net.http &\nBoot 4.2.0; Date/Vector",
        "Java 21 LTS + mvnw, records,\njava.time Clock & List",
        "CRITICAL",
        "P0 toolchain, W1 domain,\nP2 UpgradeToJava21",
    ],
    [
        "2. Framework\n(Spring/Test)",
        "Boot LATEST, javax.servlet,\nJUnit 4, @Autowired fields",
        "Spring Boot 3.4 BOM, Jakarta,\nJUnit 5 + Mockito + JaCoCo",
        "CRITICAL",
        "P0 BOM pin + Golden Master,\nP2 OpenRewrite Boot 3.4",
    ],
    [
        "3. Architecture\n(Clean Arch)",
        "Controller <-> Manager cycle,\ncognitive=56 god method",
        "Inward Clean Arch: domain,\nport, usecase, adapter",
        "HIGH",
        "Leaf-first Waves 1->4,\nP1 cycle cut (PR-04)",
    ],
    [
        "4. Database\n(Persistence)",
        "Private @Transactional stub\n(no spring-tx), System.out",
        "PostgreSQL 16 JPA + Flyway\nV1 DDL & public @Transactional",
        "HIGH",
        "P1 RepositoryPort shim,\nP2 JPA + Testcontainers",
    ],
    [
        "5. Cache/State\n(Concurrency)",
        "Static raw INVOICE_CACHE &\nmutable singleton channel",
        "Stateless beans + Redis 7\nStringRedisTemplate w/ TTL",
        "HIGH",
        "W3 delete channel field,\nP2 Redis adapter (PR-06)",
    ],
    [
        "6. Security\n(Auth/Boundary)",
        "Hardcoded <REDACTED_SECRET>,\nunbounded HTTP, ANY /charge",
        "@ConfigurationProperties,\nRestClient timeouts, @Valid",
        "CRITICAL",
        "P0 clear CVE range, P2\nRestClient, P3 DTO/secrets",
    ],
    [
        "7. Container\n& CI/CD",
        "Root openjdk:latest, no probe,\npull_request_target @main",
        "Multi-stage Temurin 21 Alpine\nnon-root + SHA-pinned CI",
        "CRITICAL",
        "P4 hardened Docker/CI +\nPNI audit, Trivy & DAST",
    ],
]

table.draw_flexible(
    xy=(4.0, 78.5),
    column_widths=[24.0, 40.0, 40.0, 14.0, 30.0],
    row_heights=[8.0, 9.2, 9.2, 9.2, 9.2, 9.2, 9.2, 9.2],
    data=data,
    align="top_left",
)
save()
```

## Executive Modernization Rationale

Baseline audit `wf-8177454c` (`java_api_spring_messy`) established that `legacy-billing` cannot currently compile inside a clean Maven/Docker harness because `pom.xml` pins Java 1.8 while `GatewayClient.java` imports Java 11's `java.net.http` API and `spring-boot-starter-web:LATEST` resolves Spring Boot 4.2.0 bytecode (`class file version 61.0`). Beyond the broken build, `BillingController` and `BillingManager` form a bidirectional runtime dependency cycle (`circularController`), share unsynchronized mutable singleton/static state (`channel`, `INVOICE_CACHE`), swallow exceptions silently, and expose an unvalidated catch-all `@RequestMapping("/charge")` endpoint.

To eliminate regressions under Hyrum's Law, the migration follows a strict **5-Phase Gated Phased-PR** strategy (`phased_pr`) instead of a big-bang rewrite:

- **Phase 0 (`PR-01`, `PR-02`)**: Restore a deterministic green build on Java 21 LTS + Spring Boot 3.4.x BOM and lock the external `POST /charge` JSON contract (`customerId`, `amountCents`, `billedCents`) with JUnit 5 + MockMvc Golden Master characterization tests.
- **Phase 1 (`PR-03`, `PR-04`)**: Execute leaf-first Domain extraction (Wave 1) and sever the `BillingManager -> BillingController` back-edge (Wave 3) behind explicit inbound/outbound Ports and temporary in-memory shims with zero behavioral drift.
- **Phase 2 (`PR-05`, `PR-06`)**: Isolate mechanical OpenRewrite codemod diffs in `PR-05`, then swap in production PostgreSQL 16 (JPA + Flyway), Redis 7 (TTL), and timeout-bounded Spring `RestClient` adapters verified via Testcontainers and WireMock in `PR-06`.
- **Phase 3 (`PR-07`)**: Enforce `@PostMapping("/charge")` with `@Valid` Java 21 record DTOs, delete hardcoded `GATEWAY_SECRET` (`<REDACTED_SECRET>`), enforce SLF4J structured logging, and apply stakeholder-approved resolutions for `DEC-JAVA-01`..`DEC-JAVA-04`.
- **Phase 4 (`PR-08`)**: Replace the broken root `openjdk:latest` Dockerfile and privileged `pull_request_target` CI workflow with a multi-stage non-root `eclipse-temurin:21-jre-alpine` image, Actuator `/actuator/health` probe, and SHA-pinned GitHub Actions, concluding with a full PNI v2 verification audit, Trivy scan, and live DAST run.

```drawlib align=center code=fold file=pr_effort_risk_distribution.png caption="Phased PR Effort, Count, and Multi-Axis Risk Distribution (Phase 0..Phase 4)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=150, height=70, dpi=150)

# Left: Grouped BarChart comparing PR Count vs Relative Effort Units per Phase
chart = BarChart(
    axis_line_style=Styles.Dark.patch(line_width=1.0),
    categories=["Phase 0\nBuild/Test", "Phase 1\nCycle/Ports", "Phase 2\nCodemod/IO", "Phase 3\nDTO/Sec", "Phase 4\nDocker/CI"],
    width=80.0,
    height=44.0,
    bar_mode="group",
    bar_width_ratio=0.68,
    bar_r=0.8,
    title="Phased PR Volume & Relative Effort (S=1, M=2, L=3)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
chart.add_series("PR Count", [2.0, 2.0, 2.0, 1.0, 1.0], style=Styles.SecondaryNeutral)
chart.add_series("Effort Units (S=1,M=2,L=3)", [3.0, 3.0, 4.0, 2.0, 2.0], style=Styles.PrimaryFlat)
chart.configure_y_axis(min_value=0.0, max_value=5.0, tick_step=1.0, label="Count / Units")
chart.draw(xy=(10.0, 11.0))
chart.draw_legend(xy=(14.0, 63.0), text_style=Styles.Dark.patch(text_size=9.5), orientation="horizontal")

# Right: Risk & Scope Summary KPI Stack
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.34,
    spacing=2.6,
)
kpis.add(
    "4 CRIT",
    "Critical Risk Axes",
    "Runtime, Framework, Sec, CI",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=12.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "3 HIGH",
    "High Risk Axes",
    "Clean Arch, PostgreSQL, Redis",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=12.5),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "8 PRs",
    "Total Effort: 14 Units",
    "3 Small | 4 Medium | 1 Large",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.add(
    ">= 85",
    "Exit Quality Gate",
    "From 66 (C) to Grade A/S",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.SuccessBold.patch(text_size=12.5),
    accent_style=Styles.SuccessFlat,
)
kpis.draw(xy=(96.0, 8.0), width=50.0, height=56.0, columns=1)

save()
```

## Confirmed Assumptions vs. Explicit Non-Goals

All scope boundaries were locked prior to PR decomposition so implementation teams do not drift into unapproved platform rewrites.

| Scope Type | Confirmed Decision / Guardrail |
| :--- | :--- |
| **Confirmed Assumption** | Target runtime and framework are pinned to **Java 21 LTS + Spring Boot 3.4.x BOM** (Jakarta EE 10, JUnit 5 Jupiter, Mockito, JaCoCo). |
| **Confirmed Assumption** | Persistence is externalized to **PostgreSQL 16** via Spring Data JPA + Flyway versioned DDL migrations (`V1__create_billing_audit.sql`). |
| **Confirmed Assumption** | Process-local `BillingManager.INVOICE_CACHE` is externalized to **Redis 7** (`StringRedisTemplate` / Spring Data Redis) with explicit key TTL. |
| **Confirmed Assumption** | **Strict** external HTTP JSON contract compatibility is preserved on `POST /charge` (`customerId`, `amountCents`, `billedCents`). |
| **Confirmed Assumption** | Ambiguous legacy quirks (`controllerPing`, `String ==` comparisons, fixed `100L` retry charge, silent `catch`) are quarantined in the Stakeholder Decision Log under `ask_human` prior to Phase 3. |
| **Explicit Non-Goal** | **No microservice decomposition** or multi-artifact repository split — retain a single deployable Maven artifact (`com.example:legacy-billing`). |
| **Explicit Non-Goal** | **No Kafka or RabbitMQ** event bus introduction in this migration wave. |
| **Explicit Non-Goal** | **No breaking URL path changes** or `/v2/charge` API versioning on `/charge`. |

## Detailed 7-Axis Modernization Matrix

| Axis (`category`) | Risk | Affected Files | As-Is Baseline | To-Be Target State |
| :--- | :--- | :--- | :--- | :--- |
| `language_runtime` | **CRITICAL** | `pom.xml`, `GatewayClient.java`, `LegacyDateHelper.java` | `pom.xml` targets Java 1.8 (colliding with Java 11 `java.net.http` and Boot 4.2.0 bytecode `61.0`); `LegacyDateHelper` uses non-thread-safe `SimpleDateFormat`, `Date`, and `Vector`. | Java 21 LTS toolchain + Maven Wrapper (`mvnw`), immutable Java 21 `record` types, `java.time.Instant` / `DateTimeFormatter` / `Clock`, and `List`/`ArrayList`. |
| `framework` | **CRITICAL** | `pom.xml`, `BillingApp.java`, `BillingController.java`, `BillingManager.java`, `BillingManagerTest.java` | `spring-boot-starter-web:LATEST` without BOM, `javax.servlet:4.0.1`, JUnit 4.13.2 assertion-free test, `@Autowired` field injection, catch-all `@RequestMapping`, missing `spring-tx`. | Pinned Spring Boot 3.4.x BOM, `jakarta.servlet` / `jakarta.validation`, Spring `RestClient`, constructor DI, `@PostMapping("/charge")`, JUnit 5 Jupiter + Mockito + JaCoCo. |
| `architecture_pattern` | **HIGH** | `InvoiceRecord.java`, `BillingController.java`, `BillingManager.java`, `GatewayClient.java` | Runtime circular dependency `BillingController <-> BillingManager` (`circularController`), `cognitive=56` god method (8 params), raw `Map`/`List` payloads. | Strict inward-only Clean Architecture: framework-free `domain` records & `TaxPolicy`, inbound/outbound `port` interfaces, pure `usecase` orchestrators, isolated `adapter` packages. |
| `database_persistence` | **HIGH** | `pom.xml`, `BillingManager.java` | `BillingManager.saveAuditTrail()` uses `private @Transactional` (bypassed by Spring AOP self-invocation and missing `spring-tx`) and logs to `System.out`. | Outbound `BillingAuditRepositoryPort` implemented by `JpaBillingAuditAdapter` backed by PostgreSQL 16 + Flyway `V1__create_billing_audit.sql` with public `@Transactional`. |
| `cache_state` | **HIGH** | `BillingController.java`, `BillingManager.java` | Unsynchronized static raw `Map` (`BillingManager.INVOICE_CACHE`) and mutable singleton field (`BillingController.channel`) cause cross-request data races. | Stateless controllers and use cases with `InvoiceCachePort` implemented by `RedisInvoiceCacheAdapter` (Redis 7 `StringRedisTemplate` with explicit TTL). |
| `auth_security` | **CRITICAL** | `GatewayClient.java`, `BillingController.java`, `pom.xml` | Hardcoded `GATEWAY_SECRET` (`<REDACTED_SECRET>`) at `GatewayClient.java:13`, untyped `System.getenv`, unbounded `HttpClient.newHttpClient()`, unauthenticated `ANY /charge`, unpinned CVE-2022-22965 range. | `@ConfigurationProperties` secret & endpoint binding, timeout-bounded `RestClient`, `@PostMapping("/charge")` with `@Valid ChargeRequest`, auth filter, SLF4J structured logging. |
| `container_cicd` | **CRITICAL** | `Dockerfile`, `.github/workflows/build.yml` | `FROM openjdk:latest` (removed on Docker Hub, root user, no `.dockerignore`, no `HEALTHCHECK`); CI uses `pull_request_target` + `actions/checkout@main` with no `permissions`. | Multi-stage `eclipse-temurin:21-jdk` / `21-jre-alpine` non-root image + `.dockerignore` + Actuator `HEALTHCHECK`; `pull_request` workflow with `contents: read` and commit-SHA pinning. |
