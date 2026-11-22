# 4. 5-Phase Gated Execution Roadmap

Migration execution is organized into **five strictly gated phases (`Phase 0`..`Phase 4`)**. Each phase defines deterministic verification exit criteria and an explicit rollback or coexistence mechanism so the service remains buildable, testable, and reversible after every individual Pull Request.

```drawlib align=center code=fold file=five_phase_gate_roadmap.png caption="5-Phase Gated Migration Execution Roadmap (Phase 0 Build Recovery through Phase 4 Final PNI Audit)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles
from drawlib.text import text

setup(width=150, height=86, dpi=150)

text(
    (75.0, 81.5),
    "5-Phase Gated Migration Execution Timeline (legacy-billing -> Java 21 + Clean Architecture)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.DarkBold,
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    curve_bend=0.0,
    card_shape="rounded_rect",
    spacing=2.4,
)
rm.add(
    "Phase 0 — Green Build Recovery & Golden Master Harness  [PR-01, PR-02]",
    "Pin Java 21 + Spring Boot 3.4 BOM + mvnw; fix jakarta.servlet; lock POST /charge with >=80% JaCoCo.",
    badge_text="P0",
    icon=phosphor.wrench,
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WarningBold,
)
rm.add(
    "Phase 1 — Cycle Cut & Clean Architecture Domain / Port Extraction  [PR-03, PR-04]",
    "Wave 1 domain records & Clock; sever circularController; extract Ports/UseCases & constructor DI.",
    badge_text="P1",
    icon=phosphor.code,
)
rm.add(
    "Phase 2 — OpenRewrite Codemods & PG 16 / Redis 7 / RestClient Adapters  [PR-05, PR-06]",
    "Run isolated OpenRewrite recipes; wire JPA+Flyway, Redis TTL, RestClient timeouts (Testcontainers/WireMock).",
    badge_text="P2",
    icon=phosphor.database,
)
rm.add(
    "Phase 3 — Typed @Valid DTOs, Security Hardening & DEC-JAVA-01..04  [PR-07]",
    "Enforce @PostMapping + @Valid records; delete <REDACTED_SECRET>; apply PO-approved decision log fixes.",
    badge_text="P3",
    icon=phosphor.lock_key,
)
rm.add(
    "Phase 4 — Container / CI Hardening & Final PNI Acceptance Audit  [PR-08]",
    "Non-root Temurin 21 Alpine + Actuator HEALTHCHECK; SHA-pinned CI; PNI audit + Trivy + live DAST >= 85.",
    badge_text="P4",
    icon=phosphor.rocket_launch,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
)
rm.draw(xy=(4.0, 4.0), width=142.0, height=74.0)

save()
```

## Phase Gate Exit Criteria & Rollback / Coexistence Matrix

No phase may advance until its automated verification gates pass cleanly in CI.

```drawlib align=center code=fold file=phase_gate_exit_rollback_matrix.png caption="Phase 0..Phase 4 Exit Gate Criteria, Verification Commands, and Rollback / Coexistence Strategy"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=80, dpi=150)

text(
    (78.0, 75.5),
    "Phase Gate Exit Criteria, Verification Commands & Rollback Matrix",
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
    rows=[1],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[2, 3, 4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.SuccessNeutral.shape_fill_color,
    text_style=Styles.SuccessBold.patch(text_size=9.5),
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
    ["Phase", "PRs", "Mandatory Exit Criteria", "Gate Command", "Rollback / Coexistence"],
    [
        "Phase 0\nBuild/Test",
        "PR-01\nPR-02",
        "Offline Docker build passes; >=80% JaCoCo;\nPOST /charge Golden Master keys locked.",
        "./mvnw test\njacoco:report",
        "Single reversible build PR;\nzero runtime schema change.",
    ],
    [
        "Phase 1\nCycle/Ports",
        "PR-03\nPR-04",
        "0 circular dependencies; 0 @Autowired fields;\nPhase 0 Golden Master tests pass unchanged.",
        "./mvnw test\n+ AST cycle=0",
        "In-memory adapter shims;\nsafe to revert per PR.",
    ],
    [
        "Phase 2\nCodemod/IO",
        "PR-05\nPR-06",
        "Flyway PG16, Redis TTL & RestClient timeout\nTestcontainers/WireMock pass; 0 static state.",
        "./mvnw rewrite:run\n&& ./mvnw verify",
        "Spring profile feature-toggle\nduring staging soak test.",
    ],
    [
        "Phase 3\nDTO/Sec",
        "PR-07",
        "0 secrets, 0 raw generics, 0 unchecked;\nDEC-JAVA-01..04 signed off & tested.",
        "./mvnw verify\n(MockMvc + sec)",
        "Canary metrics guarding\nDEC-JAVA-01/02 behavior.",
    ],
    [
        "Phase 4\nDocker/CI",
        "PR-08",
        "0 HIGH/CRIT Docker IaC & app CVEs; live\nDAST 0 CRIT/HIGH; PNI score >= 85 (A/S).",
        "docker build &\nPNI audit + DAST",
        "Blue/green deploy w/ Actuator\n/actuator/health rollback.",
    ],
]

table.draw_flexible(
    xy=(4.0, 71.5),
    column_widths=[18.0, 14.0, 50.0, 28.0, 38.0],
    row_heights=[8.0, 11.8, 11.8, 11.8, 11.8, 11.8],
    data=data,
    align="top_left",
)
save()
```

## Detailed Phase Execution Playbook

### Phase 0 — Green Build Recovery & Golden Master Characterization Harness (`PR-01`, `PR-02`)
- **Objective**: Unblock broken Maven/Docker compilation (Java 1.8 vs. Spring Boot 4.2.0 bytecode `61.0` crash) with minimal behavioral edits and lock `POST /charge` contracts with JUnit 5 + MockMvc tests.
- **Key Tasks**:
  1. Pin Spring Boot 3.4.x BOM and Java 21 compiler target in `pom.xml` and commit the Maven Wrapper (`mvnw`).
  2. Update `javax.servlet.http.HttpServletRequest` -> `jakarta.servlet.http.HttpServletRequest` in `BillingController.java` so the service compiles cleanly under Spring Boot 3.4.
  3. Replace the assertion-free `BillingManagerTest.testSmokeRun` with JUnit 5 + MockMvc Golden Master tests pinning `POST /charge` (`customerId`, `amountCents`, `billedCents`), tax branches, and retry behavior.
- **Exit Criteria**:
  - `./mvnw test` succeeds offline inside Docker with `>= 80%` JaCoCo line coverage on existing billing flows.
  - Golden Master tests lock all implicit `POST /charge` input and output keys prior to structural refactoring.
- **Rollback**: Single reversible build PR; zero runtime schema or endpoint contract changes.

### Phase 1 — Cycle Cut & Clean Architecture Domain / Port Extraction (`PR-03`, `PR-04`)
- **Objective**: Execute Wave 1 (leaf models and time utilities) and the Wave 3 cycle cut to sever `BillingController <-> BillingManager` and establish framework-free `domain`, `port`, and `usecase` packages.
- **Key Tasks**:
  1. Migrate `InvoiceRecord` and `LegacyDateHelper` to pure Java 21 domain records (`Invoice`, `Money`, `BillingSummary`) and `BillingPeriodFormatter` (`DateTimeFormatter` + `Clock`).
  2. Define inbound (`ChargeCustomerUseCase`, `ProcessBatchBillingUseCase`) and outbound (`PaymentGatewayPort`, `InvoiceCachePort`, `BillingAuditRepositoryPort`) Port interfaces.
  3. Sever `@Autowired circularController` in `BillingManager`, delete the mutable `BillingController.channel` singleton field, decompose `processBatchBilling` (`cognitive <= 15`, `params <= 6`), switch to constructor DI, and wrap existing in-memory cache/audit behind temporary adapter shims.
- **Exit Criteria**:
  - Zero circular dependencies (`AstFacts.circular_dependencies == 0`) and zero `@Autowired` field injections.
  - All Phase 0 Golden Master characterization tests pass unchanged.
- **Rollback**: Behavior-preserving refactor backed by in-memory adapter shims; cleanly revertible per PR.

### Phase 2 — OpenRewrite Codemods & PostgreSQL 16 / Redis 7 / RestClient Adapters (`PR-05`, `PR-06`)
- **Objective**: Execute deterministic OpenRewrite upgrades in an isolated mechanical diff, then replace temporary shims with production PostgreSQL 16 (JPA + Flyway), Redis 7 (TTL), and timeout-bounded Spring `RestClient` adapters.
- **Key Tasks**:
  1. Run OpenRewrite `UpgradeToJava21`, `UpgradeSpringBoot_3_4`, and `JUnit4to5Migration` in dedicated mechanical `PR-05`.
  2. Implement `JpaBillingAuditAdapter` with Flyway `V1__create_billing_audit.sql` and a public `@Transactional` boundary (replacing the broken `private @Transactional` stub).
  3. Implement `RedisInvoiceCacheAdapter` (explicit TTL) and `RestClientPaymentGatewayAdapter` (explicit connect/read timeouts + `@ConfigurationProperties`) verified via Testcontainers and WireMock.
- **Exit Criteria**:
  - All PostgreSQL Flyway migration tests, Redis TTL integration tests, and `RestClient` timeout tests pass via Testcontainers/WireMock.
  - Zero missing I/O timeouts and zero static mutable state (`INVOICE_CACHE` removed).
- **Rollback**: Feature-toggle persistence and cache adapter beans via Spring profiles during staging soak testing.

### Phase 3 — Typed `@Valid` DTOs, Security Hardening & Approved Decision Log Fixes (`PR-07`)
- **Objective**: Harden the HTTP boundary, eliminate hardcoded secrets, and execute stakeholder-approved Decision Log resolutions (`DEC-JAVA-01`..`04`).
- **Key Tasks**:
  1. Replace raw `Map` payload and catch-all `@RequestMapping("/charge")` with `@PostMapping("/charge")` and `@Valid ChargeRequest` / `ChargeResponse` Java 21 records preserving strict JSON keys.
  2. Delete the hardcoded `GATEWAY_SECRET` literal (`<REDACTED_SECRET>`) in `GatewayClient`, rotate gateway credentials, and bind exclusively via `@ConfigurationProperties`.
  3. Apply stakeholder-approved `DEC-JAVA-01`..`04` fixes (enum/`.equals()` comparisons, configurable retry amount, `controllerPing` disposition, SLF4J structured logging + PostgreSQL fail-fast / Redis graceful fallback).
- **Exit Criteria**:
  - Zero hardcoded secrets, zero raw `Map`/`List` generics, zero `@SuppressWarnings("unchecked")`, and passing auth/validation MockMvc tests.
  - All four Stakeholder Decision Log items signed off and covered by automated unit and integration tests.
- **Rollback**: Guard behavioral `DEC-JAVA-01` / `DEC-JAVA-02` changes with explicit canary ledger metrics prior to 100% rollout.

### Phase 4 — Container / CI Hardening & Final PNI Acceptance Audit (`PR-08`)
- **Objective**: Replace the broken root `openjdk:latest` Dockerfile and privileged `pull_request_target` CI workflow, then pass full PNI v2 audit + Trivy + live HTTP DAST acceptance gates.
- **Key Tasks**:
  1. Author a multi-stage `eclipse-temurin:21-jdk` / `eclipse-temurin:21-jre-alpine` non-root `Dockerfile` with `.dockerignore` and Spring Boot Actuator `/actuator/health` `HEALTHCHECK`.
  2. Harden `.github/workflows/build.yml` (`pull_request` trigger, explicit `permissions: { contents: read }`, full commit-SHA-pinned actions) and add `LICENSE`, `SECURITY.md`, `.gitignore`, and Dependabot configuration.
  3. Re-run the full `java_api_spring_messy` PNI v2 audit including containerized Maven/Docker verification, Trivy SCA/IaC scanning, and live HTTP DAST penetration tests.
- **Exit Criteria**:
  - Docker image builds cleanly with `0` HIGH/CRITICAL Dockerfile misconfigurations and `0` unpinned application CVEs.
  - Live DAST pentest (`.pni/pentests/examples/java/api_spring_messy`) boots cleanly and passes with `0` CRITICAL/HIGH findings; overall PNI score **`>= 85` (Grade A/S)**.
- **Rollback**: Blue/green container deployment with `/actuator/health` readiness-probe automated rollback trigger.
