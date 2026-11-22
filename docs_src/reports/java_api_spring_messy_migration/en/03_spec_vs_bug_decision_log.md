# 3. Stakeholder Decision Log (Spec vs. Bug)

Under **Hyrum's Law** and this workflow's `bug_handling_policy: ask_human`, legacy behavioral quirks discovered in `BillingManager.java` MUST NOT be altered silently during Phase 0–2 toolchain, Clean Architecture, or persistence upgrades. Instead, all four high-impact ambiguities (`DEC-JAVA-01`..`DEC-JAVA-04`) are locked by Phase 0 Golden Master tests and escalated for explicit Product Owner sign-off prior to Phase 3 (`PR-07`).

```drawlib align=center code=fold file=decision_log_matrix.png caption="Stakeholder Decision Matrix (DEC-JAVA-01..DEC-JAVA-04): Legacy Behavior, Risk, and Recommended Resolution"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=78, dpi=150)

text(
    (78.0, 73.5),
    "Stakeholder Decision Matrix (Spec vs. Bug — ask_human Governance Gate)",
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
    rows=[1, 2, 3, 4],
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
    ["Decision ID", "Source Location", "Observed Legacy Behavior", "Impact if Changed Silently", "Recommended Resolution (P3)"],
    [
        "DEC-JAVA-01",
        "BillingManager\n.java:52,55,57",
        "Uses == for status==\"PAID\",\ncurrency==\"USD\"/\"JPY\"; skips\ntax/PAID on HTTP strings.",
        "Deserialized inputs begin\nincurring 8%/10% tax and\nchanging billedCents.",
        "Fix to Currency/InvoiceStatus\nenums (.equals()) after caller\naudit + release note.",
    ],
    [
        "DEC-JAVA-02",
        "BillingManager\n.java:65-71",
        "When amountCents <= 0 and\nforceRetry=true, sends fixed\n100L charge up to maxRetries.",
        "Alters retry fee revenue or\nledger reconciliation for\nzero-amount payloads.",
        "Confirm if 100L is auth hold;\nkeep configurable property\nor enforce @Positive.",
    ],
    [
        "DEC-JAVA-03",
        "BillingManager\n.java:80-82",
        "Conditionally emits diagnostic\nkey 'controllerPing' from\nmutable lastChannel() field.",
        "Dropping key may break\ndownstream monitor scripts\nunder strict compatibility.",
        "Pass request.getMethod() as\nstateless param if needed;\ndeprecate & remove later.",
    ],
    [
        "DEC-JAVA-04",
        "BillingManager\n.java:83-84",
        "Empty catch (Exception e) {}\nswallows audit & cache errors\nand returns HTTP 200.",
        "Propagating failures shifts\nHTTP 200 responses to\nHTTP 500/503 on DB fault.",
        "SLF4J + correlation ID; fail-\nfast on PostgreSQL audit,\ngraceful warn on Redis miss.",
    ],
]

table.draw_flexible(
    xy=(4.0, 69.5),
    column_widths=[19.0, 22.0, 38.0, 33.0, 36.0],
    row_heights=[8.0, 14.0, 14.0, 14.0, 14.0],
    data=data,
    align="top_left",
)
save()
```

## Decision Governance Lifecycle (Phase 0 -> Phase 3)

Every candidate ambiguity follows a four-stage lifecycle so infrastructure upgrades remain behaviorally transparent while business-logic bugs are resolved intentionally with auditability.

```drawlib align=center code=fold file=decision_governance_workflow.png caption="Four-Stage Spec vs. Bug Governance Workflow Across Phase 0 Characterization to Phase 3 Sign-Off"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=150, height=58, dpi=150)

frame = Panel(
    "ask_human Decision Governance Flow (Hyrum's Law Safeguard)",
    "Zero silent behavioral drift during Phases 0-2",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    header_variant="filled",
    header_height=8.5,
)
frame.draw((4.0, 4.0), width=142.0, height=50.0)
inner_xy, inner_w, inner_h = frame.get_content_box((4.0, 4.0), width=142.0, height=50.0, padding=(3.5, 3.0))

steps = CardList(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    badge_shape="circle",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.5),
    icon_style=Styles.PrimaryBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.DarkBold,
    spacing=4.0,
)
steps.add(
    "1. Characterize",
    "Phase 0 (PR-02)\nLock current quirks\nin MockMvc tests",
    icon=phosphor.flask,
)
steps.add(
    "2. Quarantine",
    "Phases 1-2 (PR-03..06)\nRefactor ports/DB/Redis\nwith zero semantic drift",
    icon=phosphor.shield_check,
)
steps.add(
    "3. PO Sign-Off",
    "Pre-Phase 3 Gate\nResolve DEC-JAVA-01..04\nOption A vs. Option B",
    icon=phosphor.users_three,
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
    icon_style=Styles.WhiteBold,
)
steps.add(
    "4. Execute PR-07",
    "Phase 3 Cutover\nApply approved fixes +\nupdate test contracts",
    icon=phosphor.check_circle,
    badge_style=Styles.PrimaryFlat,
    icon_style=Styles.WhiteBold,
)
steps.draw(xy=inner_xy, width=inner_w, height=inner_h)

save()
```

## Detailed Decision Records & Stakeholder Options

### `DEC-JAVA-01` — Reference Equality (`==`) on `status` and `currency`
- **Location**: `src/main/java/com/example/billing/service/BillingManager.java:52,55,57` (consolidates deterministic candidates `DEC-03`, `DEC-04`, `DEC-05`).
- **Observed Behavior**: Compares `status == "PAID"`, `currency == "USD"`, and `currency == "JPY"` using Java reference identity (`==`). Currently `BillingController.chargeCustomer()` passes interned string literals `"USD"` and `"PENDING"`, so HTTP `/charge` happens to match `"USD"` (1.08x tax), whereas any non-interned deserialized string silently skips both the `PAID` duplicate guard and tax calculation.
- **Stakeholder Options**:
  - **Option A (Recommended)**: Replace with typed `Currency` and `InvoiceStatus` enums (value equality `.equals()`) in Phase 3 (`PR-07`) with an explicit release note and updated characterization test expectations.
  - **Option B**: Preserve legacy reference-equality quirk behind a feature flag during canary rollout.

### `DEC-JAVA-02` — Hardcoded `100L` Cent Retry Charge on Non-Positive Amounts
- **Location**: `src/main/java/com/example/billing/service/BillingManager.java:65-71` (consolidates deterministic candidate `DEC-08`).
- **Observed Behavior**: When `rec.getAmountCents() <= 0` and `forceRetry == true`, `BillingManager` loops up to `maxRetries` (`2`) calling `gatewayClient.sendCharge(customerId, 100L)` and adds `100L` to `total` on the first successful response.
- **Stakeholder Options**:
  - **Option A (Recommended)**: Keep the `100L` retry authorization amount configurable via `BillingProperties` (default `100L`) until Billing Product Owners confirm whether it is an intentional minimum authorization probe or a defect; if confirmed as a defect, enforce `@Positive` validation on `ChargeRequest.amountCents`.
  - **Option B**: Reject `amountCents <= 0` immediately with HTTP `400 Bad Request` in Phase 3.

### `DEC-JAVA-03` — Conditional Diagnostic Key `controllerPing` from Cyclic Singleton State
- **Location**: `src/main/java/com/example/billing/service/BillingManager.java:80-82` and `BillingController.java:20,41-43` (consolidates deterministic candidate `DEC-09`).
- **Observed Behavior**: When `circularController != null && extraContext != null`, `BillingManager` inserts `"controllerPing": circularController.lastChannel()` into the response map, reading a mutable unsynchronized field on the singleton controller bean.
- **Stakeholder Options**:
  - **Option A (Recommended)**: Pass `servletRequest.getMethod()` as a stateless request-scoped scalar parameter inside `BillingCommand` when `traceHint` is present (severing the cycle and data race immediately in Phase 1), and deprecate `controllerPing` via response header.
  - **Option B**: Remove `controllerPing` entirely in Phase 3 after consumer log auditing confirms zero external readers.

### `DEC-JAVA-04` — Empty `catch (Exception e) {}` Swallowing Audit & Cache Failures
- **Location**: `src/main/java/com/example/billing/service/BillingManager.java:83-84` (consolidates deterministic candidate `DEC-02`, alongside console-logging candidates `DEC-01`, `DEC-06`, `DEC-07`).
- **Observed Behavior**: Wraps `saveAuditTrail(...)`, `INVOICE_CACHE.put(...)`, and `controllerPing` inside a bare `catch (Exception e) {}` block, returning HTTP `200 OK` even when audit persistence or cache updates fail.
- **Stakeholder Options**:
  - **Option A (Recommended)**: Log all exceptions via SLF4J with correlation ID; **fail-fast** (propagate error -> HTTP `500`/`503`) on PostgreSQL audit write failures while **degrading gracefully** (warn log + counter metric) on Redis cache failures.
  - **Option B**: Log via SLF4J while retaining best-effort HTTP `200` during Phase 2 shadow testing before enabling fail-fast enforcement.

## Strict `POST /charge` Contract Preservation Reference

| Contract Element | Baseline (`ANY /charge`) | Phase 0–2 Behavior | Phase 3 Target (`POST /charge`) | Governing Decision |
| :--- | :--- | :--- | :--- | :--- |
| **HTTP Method** | Catch-all `@RequestMapping("/charge")` | Preserved while Golden Master locks `POST` | Restricted to `@PostMapping("/charge")` (`405` on non-POST) | Strict API compatibility |
| **Request `customerId`** | Raw `Map` key, default `"anon"` | Preserved verbatim | `ChargeRequest.customerId` (`@Size`, fallback `"anon"` if optional) | Strict API compatibility |
| **Request `amountCents`** | Raw `Map` parsed via `Long.parseLong`, default `500` | Preserved verbatim | `ChargeRequest.amountCents` (`Long`, default `500L`, validation per sign-off) | `DEC-JAVA-02` |
| **Response `customerId`** | `String` in raw `Map` | Locked by Golden Master | `ChargeResponse.customerId` | Strict API compatibility |
| **Response `billedCents`** | `long` (`Math.round(cents * 1.08)` for interned `"USD"`) | Locked by Golden Master | `ChargeResponse.billedCents` (`TaxPolicy` enum evaluation) | `DEC-JAVA-01` |
| **Response `controllerPing`** | Conditional `String` from mutable singleton field | Stateless `requestMethod` passthrough (Wave 3) | Optional `@JsonInclude(NON_NULL)` or deprecated/removed | `DEC-JAVA-03` |
| **Error Status on Audit/Cache Fault** | Silent HTTP `200` via empty `catch` | Preserved during shim/adapter wiring | Fail-fast `5xx` on PostgreSQL audit fault; warn on Redis miss | `DEC-JAVA-04` |
