# 5. Deep Dive: Code Quality, Testing & Runtime

Static tree-sitter AST analysis across the 6 Java source modules (`187 LOC`, `11` functions) and live Docker container verification reveal a sharp divide between clean isolated value objects (`InvoiceRecord.java`) and severely degraded core orchestration (`BillingManager.java`, `BillingController.java`, `GatewayClient.java`), compounded by a total Maven/Docker compilation crash that blocked runtime testing and JaCoCo coverage measurement.

```drawlib align=center code=hide file=code_module_fitness_heatmap.png caption="Module × Quality Dimension Fitness Matrix (0–100 Scale Grounded in Per-File AST Findings; InvoiceRecord Clean Baseline vs. BillingManager Hotspot)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    styles=[Styles.DangerFlat, Styles.WarningNeutral, Styles.SuccessNeutral],
    x_categories=[
        "Maintainability",
        "Typing",
        "Javadoc",
        "DI / Arch",
        "Modernity",
        "Ops / Sec",
    ],
    y_categories=[
        "InvoiceRecord.java",
        "BillingApp.java",
        "LegacyDateHelper.java",
        "GatewayClient.java",
        "BillingController.java",
        "BillingManager.java",
    ],
    width=126.0,
    height=46.0,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.9,
    cell_r=0.8,
    value_format="{:.0f}",
    auto_contrast_text=True,
    x_label_position="top",
    y_origin="top",
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    title="Per-Module Engineering Fitness Matrix (0 = Severe Defects, 100 = Zero AST Issues)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
hm.set_data(
    [
        [100, 100, 100, 100, 100, 100],  # InvoiceRecord.java: 0 AST defects
        [100, 100, 50, 100, 100, 100],   # BillingApp.java: missing class Javadoc
        [85, 70, 0, 100, 20, 60],        # LegacyDateHelper.java: Date/SDF/Vector, 0 Javadocs
        [55, 70, 0, 85, 15, 5],          # GatewayClient.java: Java 11 API, secret, no timeout
        [60, 30, 0, 15, 40, 20],         # BillingController.java: cycle, mutable channel, raw Map
        [5, 25, 20, 10, 45, 15],         # BillingManager.java: cog=56, 8 params, ==, empty catch
    ]
)
hm.draw(xy=(12.0, 13.0))
hm.draw_legend(
    xy=(28.0, 4.0),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    orientation="horizontal",
    num_steps=5,
    labels=["0 Critical", "25 Poor", "50 Fair", "75 Good", "100 Clean"],
)

save()
```

---

## Static AST Quality, SIG Maintainability & 12-Factor Telemetry

| Metric Category | Metric Name | Measured Value | Diagnostic Interpretation |
| :--- | :--- | :---: | :--- |
| **Codebase Scale** | `total_files` / `total_loc` / `total_functions` | `6` / `187` / `11` | Compact service where defects concentrate heavily in 3 core files |
| **Static Coverage** | `import_hygiene_coverage_pct` | `83.3%` | 4 unsorted imports + 1 wildcard `import java.util.*;` in `GatewayClient.java` |
| **Static Coverage** | `type_safety_coverage_pct` | `81.8%` | 2 raw generic signatures (`Map`/`List`), 2 untyped `Object` params, 2 `@SuppressWarnings("unchecked")` |
| **Static Coverage** | `docstring_coverage_pct` | `33.3%` | 10 missing public Javadocs + 1 stale `@param obsoleteToken` mismatch on `processBatchBilling` |
| **Static Coverage** | `module_test_coverage_pct` | `33.3%` | Only `InvoiceRecord` touched by 1 assertion-free JUnit 4 smoke test |
| **SIG Maintainability** | `complex_functions` / `excessive_parameters` | `1` / `1` | `BillingManager.processBatchBilling`: `57 lines`, `branches=13`, `cognitive=56`, `8 params (> 6)` |
| **Coupling & Correctness** | `circular_dependencies` / `global_state` / `bug_risk_idioms` | `1` / `1` / `7` | `BillingController <-> BillingManager`, static `INVOICE_CACHE`, 3 `String ==`, empty catch, 3 `System.out` |
| **Compatibility** | `undeclared_dependencies` / `language_version_mismatches` | `1` / `1` | `@Transactional` without `spring-tx`; Java 11 `java.net.http.HttpResponse` on Java 1.8 target |
| **12-Factor / SRE PRR** | `missing_io_timeouts` / `scattered_env` / `unstructured_logging` | `1` / `1` / `4` | `HttpClient.newHttpClient()` without timeout; `System.getenv()`; 3 `System.out` + 1 `printStackTrace()` |

### Primary Code Defect Breakdown

1. **`BillingManager.processBatchBilling` (`src/main/java/com/example/billing/service/BillingManager.java:33`)**:
   - **SIG Unit Size, Complexity & Interfacing**: `57` lines, `13` branches, cognitive complexity **`56`** (threshold `<= 15`), and **`8` parameters** (threshold `<= 6`) mixing raw `List items`, booleans (`forceRetry`, `applyTax`), and untyped `Object extraContext`.
   - **Reference-Equality Bugs (`String ==`)**: Lines `52` (`status == "PAID"`), `55` (`currency == "USD"`), and `57` (`currency == "JPY"`) compare non-interned HTTP payload strings by reference identity rather than `.equals()`, causing tax rules to silently fall through for runtime-deserialized JSON values.
   - **Silent Failure & Ineffective Transaction Proxy**: Line `83` contains an empty `catch (Exception e) {}` block that swallows audit, cache, and controller exceptions (including a latent invocation of nonexistent `dateHelper.currentPeriodLabel()` at line 79). Line `91` annotates `private void saveAuditTrail(...)` with `@Transactional`—which is both bypassed by Spring AOP self-invocation on a `private` method and backed by an undeclared `org.springframework.transaction` dependency missing from `pom.xml`.
   - **Stale Documentation**: Javadoc declares `@param obsoleteToken` (absent from signature) while omitting 7 actual parameters.
2. **`GatewayClient.java` (`src/main/java/com/example/billing/client/GatewayClient.java`)**:
   - **Language-Version API Mismatch**: Imports Java 11+ `java.net.http.{HttpResponse, HttpRequest, HttpClient}` (line 4–6) while `pom.xml` pins `maven.compiler.source/target=1.8`.
   - **Operational & Logging Defects**: Creates `HttpClient.newHttpClient()` at line 22 with zero connect/request timeout, calls `System.getenv("LEGACY_PAYMENT_URL")` inline at line 16, emits `System.out.println` (line 20) and `e.printStackTrace()` (line 32), and contains 4 unsorted imports plus `import java.util.*;`.
3. **`LegacyDateHelper.java` (`src/main/java/com/example/billing/util/LegacyDateHelper.java`)**:
   - Relies on non-thread-safe `SimpleDateFormat`, legacy `java.util.Date`, and legacy synchronized raw `Vector` instead of `java.time.Instant`/`DateTimeFormatter` and typed `List<String>`.

---

## Container Runtime Verification & Build Failure Diagnosis

Both containerized build paths failed at gate **`RV-01` (Buildability)**, cascading directly into blocked unit tests (`RV-02`), unmeasured JaCoCo coverage (`RV-03`), and blocked web startup smoke checks (`RV-04`).

```drawlib align=center code=hide file=runtime_build_failure_diag.png caption="Dual Container Build Failures (RV-01) Cascading into Blocked JUnit, JaCoCo Coverage, and Startup Smoke Verification"
from drawlib.canvas import save, setup
from drawlib.lines import line, lines
from drawlib.shapes import rectangle
from drawlib.smartarts import Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=74, dpi=150)

text(
    (73.0, 70.0),
    "Container Runtime Diagnostic: Dual RV-01 Build Crashes Blocking RV-02..RV-04",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Top-left Track A: Project Dockerfile Failure
p_a = Panel(
    "Track A: Project Dockerfile — FAILED (1.21s)",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=9.8),
    header_variant="filled",
    header_height=7.0,
)
p_a.draw((4.0, 38.0), width=66.0, height=28.0)
text(
    (37.0, 52.5),
    "examples/java/api_spring_messy/Dockerfile:1\nFROM openjdk:latest",
    style=Styles.DarkBold.patch(text_size=9.8),
)
text(
    (37.0, 43.0),
    "ERROR: docker.io/library/openjdk:latest: not found\nDeprecated base image removed from Docker Hub",
    style=Styles.DangerBold.patch(text_size=9.3),
)

# Top-right Track B: Java 8 Maven Harness Failure
p_b = Panel(
    "Track B: Maven Harness (JDK 8) — FAILED (23.98s)",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=9.8),
    header_variant="filled",
    header_height=7.0,
)
p_b.draw((76.0, 38.0), width=66.0, height=28.0)
text(
    (109.0, 52.5),
    "pom.xml: Java 1.8 + spring-boot-starter-web:LATEST\nResolves spring-boot-4.2.0.jar (SpringApplication.class)",
    style=Styles.DarkBold.patch(text_size=9.5),
)
text(
    (109.0, 43.0),
    "ERROR: bad class file — wrong version 61.0, should be 52.0\nJDK 17+ bytecode cannot compile under Java 8 javac",
    style=Styles.DangerBold.patch(text_size=9.3),
)

# Convergence bus from both failed tracks down to RV-02, RV-03, RV-04 blocked gates
line((37.0, 38.0), (37.0, 31.5), style=Styles.DangerBold)
line((109.0, 38.0), (109.0, 31.5), style=Styles.DangerBold)
line((26.0, 31.5), (120.0, 31.5), style=Styles.DangerBold)
line((26.0, 31.5), (26.0, 26.2), arrow_head="->", style=Styles.DangerBold)
line((73.0, 31.5), (73.0, 26.2), arrow_head="->", style=Styles.DangerBold)
line((120.0, 31.5), (120.0, 26.2), arrow_head="->", style=Styles.DangerBold)

# Bottom 3 blocked downstream verification gates
gates = [
    (26.0, "RV-02: Offline JUnit Tests", "BLOCKED (0 / 0)\nBillingManagerTest.testSmokeRun\n(JUnit 4, 0 assertions) never ran"),
    (73.0, "RV-03: JaCoCo Coverage", "BLOCKED (N/A)\nLine/Branch coverage unmeasured\nStatic module coverage: 33.3%"),
    (120.0, "RV-04: Web API Smoke", "BLOCKED (web_api)\nSpring Boot never started\nBlocks DAST on ANY /charge"),
]
for gx, title, body in gates:
    rectangle((gx, 15.0), width=42.0, height=21.0, style=Styles.WarningNeutral.patch(shape_r=2.0))
    rectangle(
        (gx, 22.5),
        width=38.0,
        height=4.8,
        style=Styles.WarningFlat.patch(shape_r=1.2),
        text=title,
        text_style=Styles.WhiteBold.patch(text_size=9.5),
    )
    text((gx, 12.2), body, style=Styles.Dark.patch(text_size=9.2))

save()
```

### Verbatim Compiler & Docker Failure Excerpts

**1. Project Dockerfile Build Failure (`examples/java/api_spring_messy/Dockerfile`, `1.21s`, exit code `1`)**:

```text
#2 ERROR: docker.io/library/openjdk:latest: not found
Dockerfile:1
   1 | >>> FROM openjdk:latest
ERROR: failed to build: failed to solve: openjdk:latest: failed to resolve source metadata
for docker.io/library/openjdk:latest: docker.io/library/openjdk:latest: not found
```

**2. Java 8 Maven Harness Compiler Failure (`.pni/dockerfiles/examples/java/api_spring_messy/Dockerfile`, `23.98s`, exit code `1`)**:

```text
9.861 [ERROR]   bad class file: /m2repo/org/springframework/boot/spring-boot/4.2.0/spring-boot-4.2.0.jar(org/springframework/boot/SpringApplication.class)
9.861 [ERROR]     class file has wrong version 61.0, should be 52.0
9.861 [ERROR]     Please remove or make sure it appears in the correct subdirectory of the classpath.
ERROR: failed to build: failed to solve: process "/bin/sh -c mvn -B -Dmaven.repo.local=/m2repo
  org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:prepare-agent test ...
  org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:report ..." did not complete successfully: exit code: 1
```

---

## Test Suite Health Analysis (`java/testing`)

| Test Metric | Observed Value | Assessment |
| :--- | :---: | :--- |
| **Framework & Version** | JUnit 4 (`junit:4.13.2`, `<scope>test</scope>`) | Legacy JUnit 4; needs migration to JUnit 5 (`junit-jupiter`) |
| **Test Files / Test Methods** | `1` file (`BillingManagerTest.java`) / `1` method (`testSmokeRun`) | Critically under-tested across 6 production classes |
| **Assertion-Free Tests** | `1 / 1` (`100%`) | `testSmokeRun` instantiates `InvoiceRecord` and calls `getAmountCents()` without any `assert*` or verification call |
| **Static / Measured Coverage** | `33.3%` static / `N/A` measured | `BillingManager`, `BillingController`, `GatewayClient`, and `LegacyDateHelper` have zero direct test assertions; JaCoCo blocked by `RV-01` |
