# 2. Architecture & Source Code Structure

`legacy-billing` is a **Cyclic Legacy Spring Boot Layered Monolith with Shared Mutable Global/Singleton State** comprising 6 Java production files (`187 LOC`) and 1 JUnit 4 smoke test. While the repository contains a clean immutable DTO pattern in `InvoiceRecord.java`, core business logic and HTTP routing collapse into a runtime circular dependency (`BillingController <-> BillingManager`) combined with thread-unsafe global caches and singleton request fields.

```drawlib align=center code=hide file=arch_module_tree.png caption="Physical Repository Directory Tree (Left) and 5-Layer Monolith Architecture Assessment (Right)"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, Panel, TreeNode
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

# Left Panel: Source & Config Tree
p_tree = Panel(
    "Repository & Source Module Tree (187 Production LOC)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=7.5,
)
p_tree.draw((4.0, 4.0), width=68.0, height=66.0)

tree_style = Styles.Dark.patch(text_size=9.5)
tree_bold = Styles.DarkBold.patch(text_size=9.5)
tree_danger = Styles.DangerBold.patch(text_size=9.5)
tree_ok = Styles.SuccessBold.patch(text_size=9.5)
line_st = Styles.Muted

root = TreeNode(
    "examples/java/api_spring_messy/",
    text_style=tree_bold,
    line_style=line_st,
    line_horizontal_margin=1.5,
    line_horizontal_length=3.0,
    line_vertical_margin=4.2,
)
root.add("pom.xml  [RISK 1.00 | LATEST, Java 1.8]", text_style=tree_danger)
root.add("Dockerfile  [RISK 0.58 | openjdk:latest]", text_style=tree_danger)
root.add(".github/workflows/build.yml  [RISK 0.45]", text_style=tree_danger)
root.add("README.md  [2 lines]", text_style=tree_style)
src_pkg = root.add("src/main/java/com/example/billing/", text_style=tree_bold)
src_pkg.add("BillingApp.java (9 LOC)", text_style=tree_style)
src_pkg.add("controller/BillingController.java (38 LOC)", text_style=tree_danger)
src_pkg.add("service/BillingManager.java (78 LOC)", text_style=tree_danger)
src_pkg.add("client/GatewayClient.java (32 LOC)", text_style=tree_danger)
src_pkg.add("model/InvoiceRecord.java (15 LOC, CLEAN)", text_style=tree_ok)
src_pkg.add("util/LegacyDateHelper.java (15 LOC)", text_style=tree_style)
root.add("src/test/.../BillingManagerTest.java (0 asserts)", text_style=tree_style)
root.draw((8.0, 58.5))

# Right Panel: 5-Layer Architecture Profile
p_layers = Panel(
    "Discovered 5-Layer Profile & Boundary Violations",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=7.5,
)
p_layers.draw((76.0, 4.0), width=66.0, height=66.0)

layers = CardList(
    style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.5),
    direction="vertical",
    spacing=2.2,
)
layers.add(
    "Bootstrap Layer (BillingApp)",
    "Spring Boot entrypoint; clean 9 LOC bootstrap.",
    badge_text="L1",
)
layers.add(
    "Controller Layer (BillingController)",
    "ANY /charge, raw Map, @Autowired, mutable 'channel'.",
    badge_text="L2",
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
)
layers.add(
    "Service Layer (BillingManager)",
    "God method (cog=56), static cache, UPWARD cycle to L2.",
    badge_text="L3",
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
)
layers.add(
    "External Client (GatewayClient)",
    "Java 11 HttpClient (no timeout) + hardcoded secret.",
    badge_text="L4",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
)
layers.add(
    "Model & Utility (InvoiceRecord, DateHelper)",
    "Immutable DTO (0 issues) vs legacy Date/Vector.",
    badge_text="L5",
    style=Styles.SuccessNeutral.patch(shape_r=1.8),
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
)
layers.draw((79.0, 7.0), width=60.0, height=52.5)

save()
```

---

## System Profile & Source Module Inventory

- **Runtime Archetype & Stack**: `web_api` declaring Java `1.8` in `pom.xml` (colliding with Java 11 `java.net.http` in `GatewayClient.java`), unpinned `spring-boot-starter-web:LATEST`, `javax.servlet-api:4.0.1`, `junit:4.13.2`, and Maven without a committed wrapper (`mvnw`).
- **External Integrations**: Outbound HTTP `POST` payment gateway resolved at runtime via `System.getenv("LEGACY_PAYMENT_URL")` (fallback `https://billing.example.invalid/charge`).
- **Entry Points**: `src/main/java/com/example/billing/BillingApp.java:main` and `src/main/java/com/example/billing/controller/BillingController.java:chargeCustomer`.

| Source File | LOC | Layer | Public Types | Public Callables | Health Assessment |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `src/main/java/com/example/billing/BillingApp.java` | 9 | Bootstrap | `BillingApp` | `main` | Clean Spring Boot entrypoint; missing class Javadoc |
| `src/main/java/com/example/billing/controller/BillingController.java` | 38 | Controller | `BillingController` | `chargeCustomer`, `lastChannel` | Cyclic dependency, mutable singleton `channel`, raw `Map`, unauthenticated `ANY /charge` |
| `src/main/java/com/example/billing/service/BillingManager.java` | 78 | Service | `BillingManager` | `processBatchBilling` | Primary code hotspot: upward cycle, `cognitive=56`, 8 params, static `INVOICE_CACHE`, `String ==`, empty catch |
| `src/main/java/com/example/billing/client/GatewayClient.java` | 32 | External Client | `GatewayClient` | `sendCharge` | Hardcoded `<REDACTED_SECRET>`, Java 11 `HttpClient` on Java 1.8 target, missing timeouts, `System.getenv` |
| `src/main/java/com/example/billing/model/InvoiceRecord.java` | 15 | Model & Utility | `InvoiceRecord` | `InvoiceRecord`, `getAmountCents`, `getInvoiceId` | **Cleanest module in repository**: immutable DTO, complete Javadocs, 0 AST issues |
| `src/main/java/com/example/billing/util/LegacyDateHelper.java` | 15 | Model & Utility | `LegacyDateHelper` | `collectAuditTags`, `formatTimestamp` | Legacy `SimpleDateFormat`, `java.util.Date`, and raw `Vector`; missing Javadocs |

---

## Cyclic Dependency & Thermal Hotspot Analysis

The class dependency and thermal risk overlay below contrasts the concentrated risk hotspots (`GatewayClient` `0.70`, `BillingManager` `0.56`, `BillingController` `0.56`) against the clean immutable baseline (`InvoiceRecord` `0.06`). Notice the upward injection arrow (`circularController`) from `BillingManager` back to `BillingController`, which creates a runtime Spring DI cycle prohibited by default in Spring Boot 2.6+ and 3.x.

```drawlib align=center code=hide file=arch_class_heatmap.png caption="UML Class Dependency Structure with Thermal Risk Overlay (Hotspot BillingManager/Controller/GatewayClient vs. Clean InvoiceRecord)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=92, dpi=150)

text(
    (73.0, 88.0),
    "Java Component Dependency Graph & Thermal Risk Overlay (show_contour_lines=False)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# 1. Define ClassDiagram using Styles.Neutral (dark readable text on light fill)
diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryNeutral,
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
    width=136.0,
    height=74.0,
)

n_app = ClassNode(
    "BillingApp",
    stereotype="bootstrap",
    width=27.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.PrimaryNeutral,
)
n_app.add_method("main", params="args", return_type="void", visibility="+", is_static=True)

n_ctrl = ClassNode(
    "BillingController",
    stereotype="RestController",
    width=36.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.DangerNeutral,
)
n_ctrl.add_attribute("billingManager", type="BillingManager", visibility="-")
n_ctrl.add_attribute("channel", type="String [MUTABLE]", visibility="-")
n_ctrl.add_method("chargeCustomer", params="Map", return_type="Map", visibility="+")
n_ctrl.add_method("lastChannel", params="", return_type="String", visibility="+")

n_mgr = ClassNode(
    "BillingManager",
    stereotype="Service",
    width=38.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.DangerNeutral,
)
n_mgr.add_attribute("INVOICE_CACHE", type="Map [STATIC]", visibility="+", is_static=True)
n_mgr.add_attribute("circularController", type="BillingController", visibility="-")
n_mgr.add_method("processBatchBilling", params="8 args", return_type="Map", visibility="+")
n_mgr.add_method("saveAuditTrail", params="id, total", return_type="void", visibility="-")

n_gw = ClassNode(
    "GatewayClient",
    stereotype="Component",
    width=35.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.DangerNeutral,
)
n_gw.add_attribute("GATEWAY_SECRET", type="String [REDACTED]", visibility="-", is_static=True)
n_gw.add_method("sendCharge", params="id, cents", return_type="boolean", visibility="+")

n_inv = ClassNode(
    "InvoiceRecord",
    stereotype="CLEAN DTO",
    width=29.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.SuccessNeutral,
)
n_inv.add_attribute("invoiceId", type="final String", visibility="-")
n_inv.add_attribute("amountCents", type="final long", visibility="-")
n_inv.add_method("getAmountCents", params="", return_type="long", visibility="+")

n_date = ClassNode(
    "LegacyDateHelper",
    stereotype="util",
    width=33.0,
    row_height=3.4,
    style=Styles.Neutral,
    header_style=Styles.WarningNeutral,
)
n_date.add_method("formatTimestamp", params="Date", return_type="String", visibility="+", is_static=True)
n_date.add_method("collectAuditTags", params="str", return_type="Vector", visibility="+", is_static=True)

# Position nodes cleanly with generous routing corridors
diag.add(n_app, (16.0, 62.0))
diag.add(n_ctrl, (65.0, 58.0))
diag.add(n_gw, (117.0, 58.0))
diag.add(n_inv, (17.0, 18.0))
diag.add(n_mgr, (65.0, 18.0))
diag.add(n_date, (117.0, 18.0))

# Valid & cyclic relationships (zero crossing behind class boxes)
diag.connect(
    n_app,
    n_ctrl,
    relationship_type="dependency",
    label="boots",
    start_side="right",
    end_side="left",
    padding=1.2,
)
diag.connect(
    n_ctrl,
    n_mgr,
    relationship_type="association",
    directed=True,
    label="@Autowired",
    start_side="bottom",
    end_side="top",
    padding=1.2,
)
diag.connect(
    n_mgr,
    n_ctrl,
    relationship_type="association",
    directed=True,
    label="CYCLE",
    start_side="right",
    end_side="right",
    routing="orthogonal",
    style=Styles.DangerBold,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    padding=1.2,
)
diag.connect(
    n_ctrl,
    n_inv,
    relationship_type="dependency",
    label="creates",
    start_side="left",
    end_side="top",
    routing="direct",
    padding=1.2,
)
diag.connect(
    n_mgr,
    n_inv,
    relationship_type="dependency",
    label="uses",
    start_side="left",
    end_side="right",
    padding=1.2,
)
diag.connect(
    n_mgr,
    n_gw,
    relationship_type="association",
    directed=True,
    label="sendCharge",
    start_side="right",
    end_side="bottom",
    routing="direct",
    padding=1.2,
)
diag.connect(
    n_mgr,
    n_date,
    relationship_type="composition",
    label="dateHelper",
    start_side="right",
    end_side="left",
    padding=1.2,
)

# 2. Draw UML diagram first, then translucent Thermal Risk Overlay on top (show_contour_lines=False)
diag.draw(xy=(5.0, 10.0))

overlay = HeatmapOverlay(
    styles=[Styles.SuccessFlat, Styles.WarningFlat, Styles.DangerFlat],
    width=136.0,
    height=74.0,
    mode="smooth",
    blend_mode="max",
    min_value=0.0,
    max_value=0.72,
    default_radius=20.0,
    max_alpha=0.32,
    show_contour_lines=False,
)
overlay.add_spot((117.0, 58.0), value=0.70, radius=22.0)  # GatewayClient.java
overlay.add_spot((65.0, 18.0), value=0.56, radius=23.0)   # BillingManager.java
overlay.add_spot((65.0, 58.0), value=0.56, radius=21.0)   # BillingController.java
overlay.add_spot((117.0, 18.0), value=0.06, radius=14.0)  # LegacyDateHelper.java
overlay.add_spot((16.0, 62.0), value=0.06, radius=14.0)   # BillingApp.java
overlay.add_spot((17.0, 18.0), value=0.06, radius=14.0)   # InvoiceRecord.java (clean baseline)

overlay.draw(xy=(5.0, 10.0))

overlay.draw_legend(
    xy=(6.0, 3.2),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    orientation="horizontal",
    num_steps=4,
    labels=["0.06 Clean", "0.35 Med", "0.56 High", "0.70+ Crit"],
)
text(
    (140.0, 3.8),
    "Build/CI Hotspots: pom.xml (1.00) | Dockerfile (0.58) | build.yml (0.45)",
    style=Styles.MutedBold.patch(text_size=9.5, halign="right"),
)

save()
```

### Pre-Sorted Module Risk Hotspots

| File Path | LOC | Risk Score | Findings by Severity | Triggered Rules |
| :--- | :---: | :---: | :--- | :--- |
| `pom.xml` | — | **`1.00`** | `2 CRIT`, `1 HIGH` | `common/security_vulnerability`, `common/runtime_verification`, `java/dependencies` |
| `examples/java/api_spring_messy/src/main/java/com/example/billing/client/GatewayClient.java` | 32 | **`0.70`** | `1 CRIT` | `common/security` |
| `src/main/java/com/example/billing/client/GatewayClient.java` | — | **`0.60`** | `1 CRIT`, `1 MED` | `common/security`, `java/modern_stack` |
| `Dockerfile` | — | **`0.58`** | `1 HIGH` | `common/supply_chain` |
| `src/main/java/com/example/billing/controller/BillingController.java` | — | **`0.56`** | `2 HIGH` | `common/security_vulnerability`, `java/frameworks/spring_boot` |
| `src/main/java/com/example/billing/service/BillingManager.java` | — | **`0.56`** | `2 HIGH` | `common/architecture`, `java/code_quality` |
| `.github/workflows/build.yml` | — | **`0.45`** | `1 CRIT` | `common/supply_chain` |
| `examples/java/api_spring_messy/src/main/java/com/example/billing/service/BillingManager.java` | 78 | **`0.41`** | `1 MED` | `common/maintainability` |

---

## Customer Charge Execution Flow & Concurrency Model

Every incoming HTTP request to `/charge` traverses four tightly coupled stages with shared mutable state and silent error handling:

```drawlib align=center code=hide file=arch_charge_flow.png caption="Customer Charge & Batch Billing Runtime Execution Flow (Trigger: Unrestricted HTTP ANY /charge)"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=54, dpi=150)

text(
    (73.0, 49.0),
    "Execution Flow: Customer Charge & Batch Billing (Trigger: HTTP ANY /charge)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

flow_cards = CardList(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=3.5,
    show_arrows=True,
    arrow_style=Styles.DarkBold,
)
flow_cards.add(
    "ANY /charge Intake",
    "BillingController:\nmutates singleton\n'channel'; parses\nraw Map payload.",
    badge_text="01",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    badge_style=Styles.DangerFlat,
)
flow_cards.add(
    "8-Arg Raw Handoff",
    "Wraps 1 record in\nraw ArrayList and\ncalls 8-parameter\nprocessBatchBilling.",
    badge_text="02",
    style=Styles.Neutral.patch(shape_r=2.0),
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.5),
)
flow_cards.add(
    "Tax == & Retry IO",
    "String == checks\n(PAID/USD/JPY);\nGatewayClient POST\nwith zero timeout.",
    badge_text="03",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
)
flow_cards.add(
    "Silent Cache & Cycle",
    "Private @Transactional\nbypassed; static Map\nINVOICE_CACHE;\nempty catch {}.",
    badge_text="04",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    badge_style=Styles.DangerFlat,
)
flow_cards.draw((4.0, 6.0), width=138.0, height=38.0)

save()
```

### State Storage, Boundary & Concurrency Assessment

- **Boundary Violation**: `BillingManager` imports and `@Autowired`-injects `BillingController` (`circularController`, line 23), creating a runtime cycle (`BillingController -> BillingManager -> BillingController`) solely to read `lastChannel()`.
- **Shared Mutable State**:
  - `BillingManager.INVOICE_CACHE` (`src/main/java/com/example/billing/service/BillingManager.java:17`): unsynchronized process-local static raw `HashMap` mutated without bounds or eviction.
  - `BillingController.channel` (`src/main/java/com/example/billing/controller/BillingController.java:20`): mutable singleton instance field overwritten with `servletRequest.getMethod()` on every incoming HTTP request.
- **Error & Concurrency Model**: Under concurrent Servlet execution, threads race on `BillingController.channel` and corrupt `INVOICE_CACHE`. `BillingManager` swallows all audit/cache exceptions in an empty `catch (Exception e) {}` block (line 83), while `GatewayClient` invokes `e.printStackTrace()` and blocks Servlet worker threads indefinitely because `HttpClient.newHttpClient()` configures no connect or read timeout.
