# 6. Deep Dive: Security, Supply Chain & API Surface

`legacy-billing` fails all core security and supply-chain gates (`security=50/100`, `security_vulnerability_audit=18/100`, `supply_chain_audit=15/100`, `web_penetration_audit=20/100`). Risk spans every layer of the software delivery lifecycle: an unpinned Spring Boot dependency triggering a CRITICAL CVE range alert, a privileged GitHub Actions workflow, a deprecated root Dockerfile, a hardcoded gateway credential (`<REDACTED_SECRET>`), and an unauthenticated catch-all HTTP endpoint whose live DAST verification is blocked by the Maven compilation failure.

```drawlib align=center code=hide file=sec_supply_chain_breakdown.png caption="Security Findings by Surface & Severity (Left) and Reconciliation of Static Trivy SCA vs. Live Maven Resolution (Right)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

# Left: Multi-series stacked BarChart with explicit legend
bar = BarChart(
    axis_line_style=Styles.Dark,
    width=70.0,
    height=46.0,
    categories=["SCA\nCVEs", "Docker\nIaC", "CI\nActions", "AST\nSecrets", "API\nSurface"],
    orientation="vertical",
    bar_mode="stack",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.WhiteBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="Security & Supply-Chain Defects by Surface",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
bar.configure_y_axis(min_value=0, max_value=4, tick_step=1, show_grid=True)
bar.add_series("CRITICAL", [1, 0, 1, 1, 0], style=Styles.DangerFlat)
bar.add_series("HIGH", [0, 1, 1, 0, 1], style=Styles.WarningFlat)
bar.add_series("MED / LOW", [0, 2, 1, 0, 0], style=Styles.PrimaryFlat)
bar.draw(xy=(6.0, 13.0))
bar.draw_legend(
    xy=(11.0, 4.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    orientation="horizontal",
    item_gap=6.0,
)

# Right: Reconciling Trivy Static Range vs Live Maven Resolution
p_rec = Panel(
    "Reconciling Trivy SCA vs. Live Maven (LATEST)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    header_variant="filled",
    header_height=7.5,
)
p_rec.draw((80.0, 5.0), width=62.0, height=58.0)

cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.0),
    direction="vertical",
    spacing=2.4,
)
cards.add(
    "Static Trivy FS Scan",
    "is_unpinned_specifier=True:\nfull CVE range -> CVE-2022-22965.",
    badge_text="SCA",
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    badge_style=Styles.DangerFlat,
)
cards.add(
    "Live Maven Harness",
    "Pulls Spring Boot 4.2.0 -> 61.0\ncrash on Java 1.8 (52.0).",
    badge_text="BUILD",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
)
cards.add(
    "Unified P0 Resolution",
    "Pin Java 21 + Boot 3.4.x BOM +\nmvnw: fixes CVE & build crash.",
    badge_text="FIX",
    style=Styles.SuccessNeutral.patch(shape_r=1.8),
    badge_style=Styles.SuccessFlat,
)
cards.draw((83.0, 8.0), width=56.0, height=44.5)

save()
```

---

## Supply-Chain, SCA & Container Hardening Audit

### Governance & Supply-Chain Baseline

- **Lockfiles & Dependency Hygiene**: `has_lockfile=False` (no `mvnw` or dependency verification), `dependencies_count=2`, `unpinned_dependencies_count=1` (`org.springframework.boot:spring-boot-starter-web:LATEST`).
- **Governance & Automation**: `has_license=False`, `has_security_policy=False`, `has_dependency_automation=False` (no Dependabot/Renovate), `has_gitignore=False`.
- **Trivy Scanner Configuration**: `ghcr.io/aquasecurity/trivy:0.69.3` (`docker`), `scanned_filesystem=True`, `scanned_resolved_image=False` (project container failed to build due to `openjdk:latest not found`, so OS base-image CVEs are `0` / unverified until buildability is restored).

### Application CVEs & Dockerfile IaC Misconfigurations

| Category | ID | Severity | Target | Observed State / Details | Recommended Fix |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **App CVE (`runtime_core`)** | **`CVE-2022-22965`** | **`CRITICAL`** *(CVSS 9.8)* | `pom.xml` (`spring-boot-starter-web@LATEST`) | `spring-framework: RCE via Data Binding on JDK 9+` (`is_unpinned_specifier=True` — static SCA evaluates full historical CVE range until locked; live Maven attempted `4.2.0` and crashed) | Pin explicit patched BOM release (`>= 2.5.12 / 2.6.6`; migrate to Spring Boot `3.4.x` BOM + Java 21 LTS) |
| **Container OS CVEs** | `—` | `INFO` | Project Docker Image | `0` reported (`scanned_resolved_image=False` because `openjdk:latest` failed to pull) | Migrate to `eclipse-temurin:21-jre-alpine` and re-scan built image |
| **Dockerfile IaC** | **`DS-0002`** | **`HIGH`** | `Dockerfile` | Image user should not be `root` (missing non-root `USER` instruction) | Create dedicated non-root user and add `USER appuser` |
| **Dockerfile IaC** | **`DS-0001`** | **`MEDIUM`** | `Dockerfile:1` | `FROM openjdk:latest` uses mutable `:latest` tag (and image is deprecated) | Pin digest or explicit tag (`eclipse-temurin:21-jre-alpine`) |
| **Dockerfile IaC** | **`DS-0026`** | **`LOW`** | `Dockerfile` | No `HEALTHCHECK` defined; `.dockerignore` is also missing | Add `HEALTHCHECK` probing Spring Actuator `/actuator/health` and add `.dockerignore` |

### CI/CD Supply-Chain Exposure (`.github/workflows/build.yml`)

1. **Privileged `pull_request_target` Trigger**: Executes `mvn package` in the context of the base repository with privileged secrets/write scope on untrusted PRs. Replace with `pull_request`.
2. **Missing Explicit `permissions:` Block**: Violates OpenSSF Token-Permissions least-privilege guidance. Add `permissions: { contents: read }`.
3. **Mutable Branch Reference (`actions/checkout@main`)**: Tracks a moving branch tip instead of an immutable commit SHA. Pin `actions/checkout` to a verified full 40-character SHA.

---

## Secret Hygiene, API Attack Surface & Blocked DAST Status

```drawlib align=center code=hide file=sec_attack_surface_map.png caption="End-to-End Security Boundary & Attack Surface Map: CI/Build Supply Chain, Unauthenticated ANY /charge Ingress, and Redacted Outbound Secret"
from drawlib.canvas import save, setup
from drawlib.lines import line
from drawlib.shapes import rectangle
from drawlib.smartarts import Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=66, dpi=150)

text(
    (73.0, 62.0),
    "Security Boundary & Attack Surface Map (0 AST CWE Sinks | 1 Unauth Endpoint | 1 Hardcoded Secret)",
    style=Styles.DarkBold.patch(text_size=11.0),
)

# Zone 1: Delivery & Supply Chain
p1 = Panel(
    "1. Build & CI Supply Chain",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=7.0,
)
p1.draw((4.0, 6.0), width=42.0, height=51.0)
rectangle(
    (25.0, 41.0),
    width=36.0,
    height=11.0,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    text="GitHub Actions CI\npull_request_target + @main",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (25.0, 27.0),
    width=36.0,
    height=11.0,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    text="pom.xml (LATEST)\nCVE-2022-22965 range",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (25.0, 13.0),
    width=36.0,
    height=11.0,
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    text="Dockerfile (root)\nDS-0002 / DS-0001 / DS-0026",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)

# Zone 2: HTTP Ingress & Blocked DAST
p2 = Panel(
    "2. HTTP Ingress & DAST",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=7.0,
)
p2.draw((52.0, 6.0), width=42.0, height=51.0)
rectangle(
    (73.0, 41.0),
    width=36.0,
    height=12.0,
    style=Styles.DangerFlat.patch(shape_r=1.5),
    text="ANY /charge (Line 22)\nNo Auth | Raw Map | No @Valid",
    text_style=Styles.WhiteBold.patch(text_size=9.2),
)
rectangle(
    (73.0, 26.5),
    width=36.0,
    height=11.0,
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    text="web_pentest (SEC-06)\nBLOCKED: 0/0 probes executed",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (73.0, 13.0),
    width=36.0,
    height=10.5,
    style=Styles.SuccessNeutral.patch(shape_r=1.5),
    text="AST CWE Sinks (SAST)\n0 dangerous sinks detected",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)

# Zone 3: Secret Hygiene & External Egress
p3 = Panel(
    "3. Secret & Outbound Egress",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=7.0,
)
p3.draw((100.0, 6.0), width=42.0, height=51.0)
rectangle(
    (121.0, 40.5),
    width=36.0,
    height=13.0,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    text="GatewayClient.java:13\nGATEWAY_SECRET =\n<REDACTED_SECRET>",
    text_style=Styles.DangerBold.patch(text_size=9.2),
)
rectangle(
    (121.0, 25.0),
    width=36.0,
    height=11.0,
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    text="HttpClient (No Timeout)\nSystem.getenv + printStackTrace",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (121.0, 12.0),
    width=36.0,
    height=9.5,
    style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    text="External Gateway POST\nbilling.example.invalid/charge",
    text_style=Styles.DarkBold.patch(text_size=9.0),
)

# Connectors between zones
line((46.5, 31.5), (51.5, 31.5), arrow_head="->", style=Styles.DarkBold)
line((94.5, 31.5), (99.5, 31.5), arrow_head="->", style=Styles.DarkBold)

save()
```

### Secret Detection, AST CWE Sinks & HTTP Attack Surface Matrix

| Security Surface | Target / Symbol | Status | Detailed Audit Evidence |
| :--- | :--- | :---: | :--- |
| **Hardcoded Secret (`SEC-03`)** | `GatewayClient.GATEWAY_SECRET` (`GatewayClient.java:13`) | **`CRITICAL`** | AST OWASP ASVS heuristic flagged hardcoded live-style secret token literal (`<REDACTED_SECRET>`). Trivy's generic regex secret scanner returned `0` (as the synthetic token prefix did not match vendor-specific signatures), proving the value of combined AST + SCA defense. Delete, rotate, and inject via `@ConfigurationProperties`. |
| **AST Dangerous Sinks (CWE)** | Production source (`187 LOC`) | **`PASS (0)`** | `0` CWE-tagged SQL injection, command execution, deserialization, or XXE sinks detected in Java source. |
| **Extracted HTTP API Surface (`SEC-05`)** | `ANY /charge` -> `BillingController.chargeCustomer` (`BillingController.java:22`) | **`HIGH`** | Unrestricted `@RequestMapping("/charge")` accepts `GET`, `POST`, `PUT`, `DELETE`, etc. with `auth_hint=NONE`, raw untyped `@RequestBody Map`, and zero Bean Validation (`@Valid`). |
| **Dynamic Web Pentest (`SEC-06`)** | `.pni/pentests/examples/java/api_spring_messy` | **`ERROR` (Blocked)** | 4 pytest/httpx probe modules materialized (`conftest.py`, `test_app_probes.py`, `test_baseline_http.py`, `test_target_surface.py`), `0/0` probes executed (`server_booted=False`) because the Maven container failed compiling `spring-boot-4.2.0.jar` under Java 8. Re-execute immediately after `P0` build restoration. |
