# PNI Software Health Diagnostic Report: `legacy-billing`

**Target Repository**: `examples/java/api_spring_messy` (`java_api_spring_messy`)  
**Language & Stack**: Java 1.8 (declared) / Spring Boot Web Starter (`LATEST`) / `javax.servlet-api` 4.0.1 / JUnit 4.13.2 / Maven

```drawlib align=center code=hide file=cover_scorecard.png caption="PNI501 Software Health Diagnostic Scorecard for legacy-billing (Grade C, 66/100)"
from drawlib.canvas import save, setup
from drawlib.shapes import rectangle
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text
from drawlib.utils import draw_pni_logo

setup(width=146, height=72, dpi=150)

# Outer report cover frame with Google-styled dark blue header band
frame = Panel(
    "",
    style=Styles.Neutral.patch(shape_r=2.5),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=13.5),
    header_variant="filled",
    header_height=15.0,
)
frame.draw((4, 4), width=138, height=64)

# Left-aligned cover title & subtitle inside dark header, leaving right side clear for emblem
text(
    (8.5, 63.2),
    "PNI501 Software Health Diagnostic Report",
    style=Styles.WhiteBold.patch(text_size=13.5, halign="left"),
)
text(
    (8.5, 57.2),
    "legacy-billing  |  examples/java/api_spring_messy  |  Workflow: java_api_spring_messy (wf-8177454c)",
    style=Styles.White.patch(text_size=9.5, halign="left"),
)

# Official PNI501 emblem centered vertically in the right side of the dark header
draw_pni_logo((134.5, 60.5), width=9.0, dark=True)

# Left Hero Score & Grade card
hero_style = Styles.WarningNeutral.patch(
    shape_r=2.5,
    shape_line_color=Colors.GoogleOrange,
    shape_line_width=2.0,
)
rectangle((25.5, 29.0), width=35.0, height=40.0, style=hero_style)
rectangle(
    (25.5, 44.0),
    width=27.0,
    height=5.2,
    style=Styles.WarningFlat.patch(shape_r=2.0),
    text="OVERALL SCORE",
    text_style=Styles.WhiteBold.patch(text_size=9.5),
)
text((25.5, 32.5), "66 / 100", style=Styles.DarkBold.patch(text_size=18.0))
text((25.5, 22.5), "Grade C", style=Styles.WarningBold.patch(text_size=14.0))
text(
    (25.5, 14.0),
    "Baseline 76 (-10 AI Adj.)\n15 FAIL | 1 WARN | 0 PASS",
    style=Styles.Dark.patch(text_size=9.5),
)

# Right 2x2 executive headline KPIs
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="top_stack",
    spacing=2.8,
)
kpis.add(
    "0 / 16",
    "Rule Pass Rate",
    "15 FAIL, 1 WARN (0 PASS)",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=13.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "19 Findings",
    "14 Consolidated Locations",
    "6 CRIT | 8 HIGH | 4 MED | 1 LOW",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.0),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "BUILD FAIL",
    "Docker Maven Runtime",
    "Boot 4.2.0 (61.0) vs JDK 8 (52.0)",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=12.5),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "1 CRIT CVE",
    "Trivy SCA & IaC Posture",
    "CVE-2022-22965 + 3 Docker IaC",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.draw((46.5, 9.0), width=91.5, height=40.0, columns=2)

save()
```

---

## Audit Identification & Provenance

| Attribute | Value |
| :--- | :--- |
| **Project Name** | `legacy-billing` (`com.example:legacy-billing:0.0.1-SNAPSHOT`) |
| **Target Root** | `examples/java/api_spring_messy` |
| **Primary Language** | `java` (Maven, 6 production files / 187 LOC, 1 test file) |
| **Workflow ID & Scope** | `java_api_spring_messy` (`category=audit`, `scope=repo`) |
| **Workflow Run ID** | `wf-8177454c` |
| **Evaluated At (UTC)** | `2026-11-22T11:29:02.337544+00:00` |
| **Git Provenance** | `main@d1e02277 (dirty)` |
| **Overall Score & Grade** | **66 / 100 (Grade C)** *(Deterministic Baseline: 76, AI Qualitative Adjustment: -10)* |
| **Rule Compliance** | `0 / 16` rules passed (`15 FAIL`, `1 WARN`, `0 PASS`) |
| **Findings Summary** | `19` total (`7` deterministic, `12` AI qualitative) across `14` unique locations (`6 CRITICAL`, `8 HIGH`, `4 MEDIUM`, `1 LOW`) |
| **Downstream Linkage** | Feeds directly into the `java_api_spring_messy_migration` Clean Architecture modernization plan |

> **Scope & Audit Notice**: This report synthesizes deterministic AST parsing (`tree-sitter`), project manifest inspection, containerized Maven/Docker build and runtime verification, Trivy filesystem SCA/IaC scanning, and dynamic HTTP penetration readiness checks executed under PNI501 Workflow v2. All credentials referenced from source analysis are redacted (`<REDACTED_SECRET>`).
