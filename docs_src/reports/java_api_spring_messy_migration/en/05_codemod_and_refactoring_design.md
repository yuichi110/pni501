# 5. Automated Codemods & Boundary Adapter Design

To keep code review noise low and guarantee deterministic AST transformations, this plan strictly separates **automated OpenRewrite codemod recipes** (3 recipes isolated in `PR-05`) from **manual architectural extractions** addressing three hard migration blockers (`BLK-01`..`BLK-03`) and four stateful/I/O boundary touchpoints.

```drawlib align=center code=fold file=codemod_vs_manual_breakdown.png caption="Automated OpenRewrite Codemod Recipes vs. Manual Architectural Refactoring Split"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=78, dpi=150)

text(
    (78.0, 73.8),
    "Mechanical OpenRewrite Codemods vs. Manual Port/Adapter Refactoring Scope",
    style=Styles.DarkBold.patch(text_size=12.0),
)

# Left: Grouped BarChart of Automated vs Manual file touches across Phases 0..4
chart = BarChart(
    axis_line_style=Styles.Dark.patch(line_width=1.0),
    categories=["P0", "P1", "P2", "P3", "P4"],
    width=54.0,
    height=44.0,
    bar_mode="group",
    bar_width_ratio=0.70,
    bar_r=0.8,
    title="File Touches by Execution Mode",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
chart.add_series("OpenRewrite / Auto", [1.0, 0.0, 7.0, 0.0, 0.0], style=Styles.PrimaryFlat)
chart.add_series("Manual Design", [2.0, 4.0, 3.0, 3.0, 3.0], style=Styles.SecondaryNeutral)
chart.configure_y_axis(min_value=0.0, max_value=8.0, tick_step=2.0, label="Files")
chart.draw(xy=(9.0, 11.0))
chart.draw_legend(xy=(6.0, 63.0), text_style=Styles.Dark.patch(text_size=9.5), orientation="horizontal")

# Right: OpenRewrite Recipe Catalog & Blocker Summary Table
text((111.0, 65.5), "OpenRewrite Recipes (PR-05) & Pre-Requisite Blockers", style=Styles.DarkBold.patch(text_size=10.5))

table = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
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
    text_style=Styles.WhiteBold.patch(text_size=9.8),
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[1, 2, 3],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.DangerNeutral.shape_fill_color,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    rows=[4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[5, 6],
    columns=[0],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Type / ID", "Recipe or Blocker", "Scope", "Resolution"],
    ["Codemod\n(OR-1)", "UpgradeToJava21", "6 files", "POM props, diamond,\ndeprecated JDK APIs"],
    ["Codemod\n(OR-2)", "UpgradeSpringBoot_3_4", "6 files", "javax.* -> jakarta.*,\nBoot 3.4 starters"],
    ["Codemod\n(OR-3)", "JUnit4to5Migration", "1 file", "JUnit 4 @Test/Assert\n-> Jupiter api.*"],
    ["BLK-01\nCRIT", "Java 1.8 vs java.net.http\n(GatewayClient.java:4)", "Phase 0", "Pin Java 21 + Boot\n3.4 BOM (PR-01)"],
    ["BLK-02\nHIGH", "Controller <-> Manager\ncircular dependency", "Phase 1", "Sever back-edge via\nPorts/DTO (PR-04)"],
    ["BLK-03\nMED", "@Transactional without\nspring-tx (Manager:12)", "Phase 2", "Add spring-boot-data\nJPA + Flyway (PR-06)"],
]

table.draw_flexible(
    xy=(70.0, 62.5),
    column_widths=[17.0, 29.0, 12.0, 25.0],
    row_heights=[7.5, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2],
    data=data,
    align="top_left",
)
save()
```

## Pre-Codemod Manual Blockers (`BLK-01`..`BLK-03`)

OpenRewrite requires a compilable Maven project AST before running Lossless Semantic Tree (LST) recipes. Three deterministic blockers must be resolved in order before `PR-05`:

| Blocker ID | Severity | Source Location | Deterministic Finding | Resolution Gate |
| :--- | :--- | :--- | :--- | :--- |
| **`BLK-01`** | **CRITICAL** | `examples/java/api_spring_messy/src/main/java/com/example/billing/client/GatewayClient.java:4` | Java 11+ `java.net.http` API imported while `pom.xml` declares Java `1.8` (also colliding with resolved Spring Boot 4.2.0 bytecode `61.0`). | Align `pom.xml` to Java 21 LTS + Spring Boot 3.4.x BOM and commit `mvnw` in **Phase 0 (`PR-01`)**. |
| **`BLK-02`** | **HIGH** | `com.example.billing.controller.BillingController` <-> `com.example.billing.service.BillingManager` | Bidirectional runtime circular dependency via `@Autowired private BillingController circularController`. | Sever upward back-edge via explicit scalar/DTO input and `ChargeCustomerUseCase` Port in **Phase 1 (`PR-04`)**. |
| **`BLK-03`** | **MEDIUM** | `examples/java/api_spring_messy/src/main/java/com/example/billing/service/BillingManager.java:12` | `org.springframework.transaction.annotation.Transactional` imported without `spring-tx` or a data/JDBC starter declared in `pom.xml`, and placed on a `private` method bypassed by Spring AOP. | Remove stray private annotation in `PR-04`, then declare `spring-boot-starter-data-jpa` + Flyway + public `@Transactional` on `JpaBillingAuditAdapter` in **Phase 2 (`PR-06`)**. |

## OpenRewrite Automated Recipe Catalog (`PR-05`)

All three recipes execute in one isolated mechanical PR (`./mvnw rewrite:run && ./mvnw test`) with zero manual business-logic changes mixed into the diff:

| Tool | OpenRewrite Recipe ID | Files | Automated Transformation Scope |
| :--- | :--- | :--- | :--- |
| `openrewrite` | `org.openrewrite.java.migrate.UpgradeToJava21` | `6` | Updates Maven compiler properties to Java 21, modernizes diamond operators, and replaces deprecated JDK 8 API idioms. |
| `openrewrite` | `org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_4` | `6` | Rewrites remaining `javax.servlet` / `javax.persistence` / `javax.validation` namespaces to `jakarta.*`, updates Spring Boot 3.4 starters, and enforces constructor-injection patterns. |
| `openrewrite` | `org.openrewrite.java.testing.junit5.JUnit4to5Migration` | `1` | Deterministically converts any lingering JUnit 4 `@Test` and `Assert.*` imports to `org.junit.jupiter.api.*`. |

## Boundary Touchpoints -> Outbound Port & Adapter Design

Four deterministic boundary touchpoints (plus the hardcoded gateway credential at `GatewayClient.java:13`) drive the Clean Architecture Port & Adapter extractions across `PR-04`, `PR-06`, and `PR-07`.

```drawlib align=center code=fold file=boundary_touchpoints_adapter_design.png caption="Stateful, Persistence, and External HTTP Boundary Touchpoints Mapped to Clean Architecture Ports & Adapters"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=76, dpi=150)

text(
    (78.0, 71.8),
    "Boundary Touchpoints (State / DB / HTTP / Secret) -> Target Port & Adapter Design",
    style=Styles.DarkBold.patch(text_size=12.0),
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
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[1, 2],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[3, 4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.DangerNeutral.shape_fill_color,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    rows=[5],
    columns=[0],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Boundary Kind", "Legacy Source & Symbol", "Current Coupling / Hazard", "Target Port Interface", "Target Adapter"],
    [
        "in_memory_state",
        "BillingController.java:20\nchannel (instance field)",
        "Mutable field on singleton\nSpring bean -> request race.",
        "ChargeCustomerUseCase\n(stateless BillingCommand)",
        "Stateless BillingController\npassing request.getMethod().",
    ],
    [
        "in_memory_state",
        "BillingManager.java:17\nstatic Map INVOICE_CACHE",
        "Unsynchronized static raw\nHashMap -> OOM & data race.",
        "InvoiceCachePort\nputSummary(id, val, ttl)",
        "RedisInvoiceCacheAdapter\n(Redis 7 + explicit TTL).",
    ],
    [
        "persistence_db",
        "BillingManager.java:91\nprivate @Transactional",
        "Self-invoked private AOP\nbypass + System.out stub.",
        "BillingAuditRepositoryPort\nsaveAudit(id, Money)",
        "JpaBillingAuditAdapter\n(PG 16 + Flyway V1 DDL).",
    ],
    [
        "external_http_rpc",
        "GatewayClient.java:22\nHttpClient.newHttpClient",
        "No connect/read timeouts;\nper-call client allocation.",
        "PaymentGatewayPort\nsendCharge(id, Money)",
        "RestClientPaymentGateway\nAdapter (bounded timeouts).",
    ],
    [
        "secret_config",
        "GatewayClient.java:13,16\nGATEWAY_SECRET / env",
        "Literal <REDACTED_SECRET>\n& untyped System.getenv().",
        "GatewayProperties\n(@ConfigurationProperties)",
        "External env/secret mount\n+ SLF4J (never log secrets).",
    ],
]

table.draw_flexible(
    xy=(4.0, 67.8),
    column_widths=[22.0, 30.0, 34.0, 30.0, 32.0],
    row_heights=[8.0, 10.6, 10.6, 10.6, 10.6, 10.6],
    data=data,
    align="top_left",
)
save()
```

### Adapter Implementation Guardrails

1. **`JpaBillingAuditAdapter` (PostgreSQL 16 + Flyway)**:
   - Schema versioned via `src/main/resources/db/migration/V1__create_billing_audit.sql` (`billing_audit` table with `id`, `customer_id`, `billed_cents`, `currency`, `created_at`).
   - Public `@Transactional` boundary on the adapter class (never `private`), verified against a real PostgreSQL 16 container via Testcontainers in `PR-06`.
2. **`RedisInvoiceCacheAdapter` (Redis 7)**:
   - Uses `StringRedisTemplate` with namespaced keys (`billing:invoice:{customerId}`) and explicit configurable TTL (e.g., `Duration.ofMinutes(15)`), eliminating unbounded heap growth and cross-thread corruption.
3. **`RestClientPaymentGatewayAdapter` (Spring Boot 3.4 `RestClient`)**:
   - Configures explicit `connectTimeout` and `readTimeout` on a shared `ClientHttpRequestFactory`, binds `LEGACY_PAYMENT_URL` and gateway credentials (`<REDACTED_SECRET>` rotated and removed from source) through validated `@ConfigurationProperties`, and verifies timeout/5xx handling with WireMock.
