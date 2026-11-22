# 6. PR Work Breakdown Structure (WBS) & Verification Gates

This chapter provides the issue-tracker-ready Pull Request Work Breakdown Structure (`PR-01`..`PR-08`), deterministic per-PR verification commands, the executed PNI Workflow v2 Migration Planning DAG, and a reference index of all machine-readable evidence artifacts.

```drawlib align=center code=fold file=pr_wbs_dependency_chain.png caption="Topologically Ordered PR-01..PR-08 Execution Dependency Chain Grouped by Migration Phase"
from drawlib.canvas import save, setup
from drawlib.diagrams.flow import FlowDiagram, Process
from drawlib.shapes import rectangle
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=162, height=84, dpi=150)

text(
    (81.0, 79.8),
    "Phased PR Dependency Chain (PR-01 .. PR-08 across Phases 0 -> 4)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

# Subtle Phase group containers (Row 1: y=44..72; Corridor: y=38; Row 2: y=5..33)
phase_boxes = [
    (46.0, 58.0, 72.0, 28.0, "Phase 0: Green Build & Golden Master", Styles.WarningNeutral.patch(shape_fill_color=Colors.Light)),
    (122.0, 58.0, 72.0, 28.0, "Phase 1: Clean Arch & Cycle Cut", Styles.PrimaryNeutral.patch(shape_fill_color=Colors.Light)),
    (46.0, 19.0, 72.0, 28.0, "Phase 2: Codemod & PG16/Redis7 Adapters", Styles.SecondaryNeutral.patch(shape_fill_color=Colors.Light)),
    (103.5, 19.0, 36.0, 28.0, "Phase 3: DTO & Sec", Styles.DangerNeutral.patch(shape_fill_color=Colors.Light)),
    (142.0, 19.0, 36.0, 28.0, "Phase 4: Docker/CI", Styles.SuccessNeutral.patch(shape_fill_color=Colors.Light)),
]
for cx, cy, bw, bh, label, st in phase_boxes:
    rectangle(
        (cx, cy),
        width=bw,
        height=bh,
        style=st.patch(shape_r=2.0, shape_line_style="dashed", shape_line_width=1.0),
    )
    text((cx, cy + bh / 2.0 - 3.2), label, style=Styles.DarkBold.patch(text_size=9.5))

txt_dark = Styles.DarkBold.patch(text_size=9.5)
txt_white = Styles.WhiteBold.patch(text_size=9.5)

flow = FlowDiagram(
    node_style=Styles.Neutral.patch(text_size=9.5),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.Dark.patch(text_size=9.5),
)

# Top Row (y=54.5): PR-01 -> PR-02 -> PR-03 -> PR-04
pr1 = flow.add(
    Process("PR-01 [S | hybrid]\nJava 21 + Boot 3.4\nBOM & jakarta", width=31.0, height=15.0, style=Styles.WarningNeutral, text_style=txt_dark),
    xy=(28.0, 54.5),
)
pr2 = flow.add(
    Process("PR-02 [M | manual]\nJUnit 5 + MockMvc\nGolden Master", width=31.0, height=15.0, style=Styles.Neutral, text_style=txt_dark),
    xy=(64.0, 54.5),
)
pr3 = flow.add(
    Process("PR-03 [S | manual]\nWave 1 Domain\nRecords & Clock", width=31.0, height=15.0, style=Styles.Neutral, text_style=txt_dark),
    xy=(104.0, 54.5),
)
pr4 = flow.add(
    Process("PR-04 [M | manual]\nSever Cycle, Ports,\nUseCase & DI", width=31.0, height=15.0, style=Styles.PrimaryNeutral, text_style=txt_dark),
    xy=(140.0, 54.5),
)

# Bottom Row (y=15.5): PR-05 -> PR-06 -> PR-07 -> PR-08
pr5 = flow.add(
    Process("PR-05 [S | codemod]\nOpenRewrite Java21\nBoot 3.4 & JUnit5", width=31.0, height=15.0, style=Styles.PrimaryNeutral, text_style=txt_dark),
    xy=(28.0, 15.5),
)
pr6 = flow.add(
    Process("PR-06 [L | manual]\nPG16 JPA+Flyway,\nRedis7 & RestClient", width=31.0, height=15.0, style=Styles.Neutral, text_style=txt_dark),
    xy=(64.0, 15.5),
)
pr7 = flow.add(
    Process("PR-07 [M | manual]\n@Valid DTO, Secrets\n& DEC-JAVA-01..04", width=31.0, height=15.0, style=Styles.DangerNeutral, text_style=txt_dark),
    xy=(103.5, 15.5),
)
pr8 = flow.add(
    Process("PR-08 [M | manual]\nTemurin 21, SHA CI\n& Final PNI >= 85", width=31.0, height=15.0, style=Styles.PrimaryFlat, text_style=txt_white),
    xy=(142.0, 15.5),
)

flow.connect(pr1, pr2, start_side="right", end_side="left", padding=0.8)
flow.connect(pr2, pr3, start_side="right", end_side="left", padding=0.8)
flow.connect(pr3, pr4, start_side="right", end_side="left", padding=0.8)
# Route PR-04 -> PR-05 cleanly through central corridor (y=38.5) and left margin (x=5.0) without crossing Phase 2 title
flow.connect(pr4, pr5, start_side="bottom", end_side="left", padding=0.8).via((140.0, 38.5), (5.0, 38.5), (5.0, 15.5))
flow.connect(pr5, pr6, start_side="right", end_side="left", padding=0.8)
flow.connect(pr6, pr7, start_side="right", end_side="left", padding=0.8)
flow.connect(pr7, pr8, start_side="right", end_side="left", padding=0.8)

flow.draw(xy=(0.0, 0.0))
save()
```

## Topologically Ordered PR Work Breakdown Structure (`PR-01`..`PR-08`)

Each PR is independently reviewable, targets an explicit set of repository files, and must pass its deterministic verification command before merging.

```drawlib align=center code=fold file=pr_wbs_verification_table.png caption="Issue-Tracker-Ready PR Work Breakdown Structure (PR-01..PR-08) with Files, Size, Mode, and Verification Gates"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=162, height=96, dpi=150)

text(
    (81.0, 91.5),
    "Topologically Ordered PR Work Breakdown Structure (PR-01 .. PR-08)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

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
    rows=[1, 2, 3, 4, 5, 6, 7, 8],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.SuccessNeutral.shape_fill_color,
    text_style=Styles.SuccessBold.patch(text_size=9.5),
    rows=[5],
    columns=[5],
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[6],
    columns=[5],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["PR ID", "Phase/W", "PR Scope & Deliverable", "Primary Target Files", "Verification Gate", "Size/Mode"],
    [
        "PR-01",
        "P0 / W1",
        "Pin Java 21 + Boot 3.4 BOM, add\nmvnw, fix jakarta.servlet import",
        "pom.xml,\nBillingController.java",
        "./mvnw clean\ntest-compile",
        "S\nhybrid",
    ],
    [
        "PR-02",
        "P0 / W1",
        "JUnit 5 + MockMvc Golden Master\nlocking POST /charge + JaCoCo",
        "BillingManagerTest.java",
        "./mvnw test\njacoco:report",
        "M\nmanual",
    ],
    [
        "PR-03",
        "P1 / W1",
        "Extract pure domain records\n(Invoice/Money) & Clock formatter",
        "InvoiceRecord.java,\nLegacyDateHelper.java",
        "./mvnw test",
        "S\nmanual",
    ],
    [
        "PR-04",
        "P1 / W3",
        "Sever Controller<->Manager cycle,\nextract Ports/UseCases & DI",
        "BillingController.java,\nBillingManager.java",
        "./mvnw test",
        "M\nmanual",
    ],
    [
        "PR-05",
        "P2 / W2",
        "Run OpenRewrite UpgradeToJava21,\nBoot 3.4 & JUnit4to5Migration",
        "pom.xml,\nBillingApp.java",
        "./mvnw rewrite:run\n&& ./mvnw test",
        "S\ncodemod",
    ],
    [
        "PR-06",
        "P2 / W2",
        "Implement PG16 JPA+Flyway, Redis7\nTTL & RestClient timeout adapters",
        "pom.xml, GatewayClient,\nBillingManager.java",
        "./mvnw verify",
        "L\nmanual",
    ],
    [
        "PR-07",
        "P3 / W3",
        "@PostMapping @Valid DTOs, delete\n<REDACTED_SECRET> & DEC-01..04",
        "BillingController, Gateway,\nBillingManager.java",
        "./mvnw verify",
        "M\nmanual",
    ],
    [
        "PR-08",
        "P4 / W4",
        "Non-root Temurin 21 Docker, SHA\nCI, docs & final PNI audit/DAST",
        "Dockerfile, build.yml,\nREADME.md",
        "docker build &\n./mvnw verify",
        "M\nmanual",
    ],
]

table.draw_flexible(
    xy=(4.0, 87.5),
    column_widths=[14.0, 15.0, 48.0, 35.0, 27.0, 15.0],
    row_heights=[8.0, 9.3, 9.3, 9.3, 9.3, 9.3, 9.3, 9.3, 9.3],
    data=data,
    align="top_left",
)
save()
```

### Detailed PR Ticket Specifications

| PR ID | Deps | Phase / Wave | Axis | Size / Mode | Target Files | Verification Command |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`PR-01`** | *(root)* | Phase 0 / Wave 1 | `framework` | `S` / `hybrid` | `pom.xml`, `src/main/java/com/example/billing/controller/BillingController.java` | `./mvnw clean test-compile` |
| **`PR-02`** | `PR-01` | Phase 0 / Wave 1 | `framework` | `M` / `manual` | `src/test/java/com/example/billing/BillingManagerTest.java` | `./mvnw test jacoco:report` |
| **`PR-03`** | `PR-02` | Phase 1 / Wave 1 | `language_runtime` | `S` / `manual` | `src/main/java/com/example/billing/model/InvoiceRecord.java`, `src/main/java/com/example/billing/util/LegacyDateHelper.java` | `./mvnw test` |
| **`PR-04`** | `PR-03` | Phase 1 / Wave 3 | `architecture_pattern` | `M` / `manual` | `src/main/java/com/example/billing/controller/BillingController.java`, `src/main/java/com/example/billing/service/BillingManager.java` | `./mvnw test` |
| **`PR-05`** | `PR-04` | Phase 2 / Wave 2 | `framework` | `S` / `codemod` | `pom.xml`, `src/main/java/com/example/billing/BillingApp.java` | `./mvnw rewrite:run && ./mvnw test` |
| **`PR-06`** | `PR-05` | Phase 2 / Wave 2 | `database_persistence` | `L` / `manual` | `pom.xml`, `src/main/java/com/example/billing/client/GatewayClient.java`, `src/main/java/com/example/billing/service/BillingManager.java` | `./mvnw verify` |
| **`PR-07`** | `PR-06` | Phase 3 / Wave 3 | `auth_security` | `M` / `manual` | `src/main/java/com/example/billing/controller/BillingController.java`, `src/main/java/com/example/billing/client/GatewayClient.java`, `src/main/java/com/example/billing/service/BillingManager.java` | `./mvnw verify` |
| **`PR-08`** | `PR-07` | Phase 4 / Wave 4 | `container_cicd` | `M` / `manual` | `Dockerfile`, `.github/workflows/build.yml`, `README.md` | `docker build -t legacy-billing:21 . && ./mvnw verify` |

## Executed Migration Planning Pipeline DAG & Evidence Provenance

This migration plan was generated by PNI501 Workflow v2 (`java_api_spring_messy_migration`, run `wf-b1c19b56`), chained directly from the baseline audit run `wf-8177454c` (`java_api_spring_messy`).

```drawlib align=center code=fold file=executed_migration_pipeline_dag.png caption="Executed PNI Workflow v2 Migration Planning Pipeline DAG (wf-b1c19b56, chained from wf-8177454c)"
from drawlib.canvas import save, setup
from drawlib.diagrams.flow import End, FlowDiagram, Process, Start
from drawlib.graph import LayerGraph
from drawlib.shapes import rectangle
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=184, height=64, dpi=150)

text(
    (92.0, 59.5),
    "Executed Migration Planning Workflow DAG (java_api_spring_messy_migration | wf-b1c19b56)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Compute Sugiyama layered layout for the 6-node workflow chain (6*23.5 + 5*5.5 = 168.5 <= 184)
g = LayerGraph(direction="LR", rank_sep=5.5, default_node_width=23.5, default_node_height=18.0)
for nid in ["base", "act01", "act02", "act03", "act04", "act05"]:
    g.node(nid)
g.cluster("stage2", ["act02", "act03", "act04"], padding=3.2, header_height=4.8)

g.edge("base", "act01")
g.edge("act01", "act02")
g.edge("act02", "act03")
g.edge("act03", "act04")
g.edge("act04", "act05")

layout = g.get_layout(width=184.0, height=46.0, margin=7.5)
ox, oy = 0.0, 4.0

# Draw Stage 2 HYBRID cluster enclosing act-02..act-04
s2 = layout["stage2"]
rectangle(
    (s2.xy[0] + ox, s2.xy[1] + oy),
    width=s2.width,
    height=s2.height,
    style=Styles.PrimaryNeutral.patch(shape_fill_color=Colors.Light, shape_r=2.0, shape_line_style="dashed", shape_line_width=1.0),
)
text(
    (s2.xy[0] + ox, s2.top + oy - 2.6),
    "migration_intelligence_and_plan  [HYBRID | COMPLETED]",
    style=Styles.PrimaryBold.patch(text_size=9.5),
)

txt_dark = Styles.DarkBold.patch(text_size=9.5)
txt_white = Styles.WhiteBold.patch(text_size=9.5)

flow = FlowDiagram(
    node_style=Styles.Neutral.patch(text_size=9.5),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.Dark.patch(text_size=9.5),
)

def pos(nid: str) -> tuple[float, float]:
    n = layout[nid]
    return (n.xy[0] + ox, n.xy[1] + oy)

n_base = flow.add(
    Start("[INPUT | DONE]\nBaseline Audit\n66/100 Grade C", width=23.5, height=18.0, style=Styles.Neutral, text_style=txt_dark),
    xy=pos("base"),
)
n_a1 = flow.add(
    Process("[ASK | DONE]\nact-01\nconfirm_plan", width=23.5, height=18.0, style=Styles.SuccessNeutral, text_style=txt_dark),
    xy=pos("act01"),
)
n_a2 = flow.add(
    Process("[AUTO | DONE]\nact-02\nmigration_analyze", width=23.5, height=18.0, style=Styles.PrimaryNeutral, text_style=txt_dark),
    xy=pos("act02"),
)
n_a3 = flow.add(
    Process("[AI | DONE]\nact-03\nai_interpret", width=23.5, height=18.0, style=Styles.SecondaryNeutral, text_style=txt_dark),
    xy=pos("act03"),
)
n_a4 = flow.add(
    Process("[AI | DONE]\nact-04\nemit_plan JSON", width=23.5, height=18.0, style=Styles.SecondaryNeutral, text_style=txt_dark),
    xy=pos("act04"),
)
n_a5 = flow.add(
    End("[AI | ACTIVE]\nact-05\nDrawlib Report", width=23.5, height=18.0, style=Styles.PrimaryFlat, text_style=txt_white),
    xy=pos("act05"),
)

flow.connect(n_base, n_a1, start_side="right", end_side="left", padding=0.6)
flow.connect(n_a1, n_a2, start_side="right", end_side="left", padding=0.6)
flow.connect(n_a2, n_a3, start_side="right", end_side="left", padding=0.6)
flow.connect(n_a3, n_a4, start_side="right", end_side="left", padding=0.6)
flow.connect(n_a4, n_a5, start_side="right", end_side="left", padding=0.6)

flow.draw(xy=(0.0, 0.0))
save()
```

### Inspection Scope & Deterministic Tooling Provenance

| Provenance Field | Recorded Value |
| :--- | :--- |
| **Target Root & Paths** | `examples/java/api_spring_messy` | `source=['src/main/java']`, `tests=['src/test/java']`, `docs=['README.md']`, `exclude=['none']` |
| **Language & Detected Frameworks** | Primary: `java` (companions: `none`); Frameworks: `spring-boot`, `spring-framework`, `javax-ee`, `junit4` |
| **Git Revision** | `main@d1e02277 (dirty)` |
| **Deterministic Tools Executed** | `project_inspect (java)`, `tree-sitter AST (java)`, `container runtime harness (docker: java/maven.dockerfile)`, `Trivy (docker: fs)`, `web_pentest (httpx, 0 probes)`, `migration_analyze (import DAG + boundary AST + codemods)` |
| **Logical Stage Summary** | `confirm_plan` (**ASK \| COMPLETED**), `migration_intelligence_and_plan` (**HYBRID \| COMPLETED** — 7 axes, 8 PRs, 4 decisions), `compile_migration_report` (**AI \| ACTIVE** — EN/JA A4 Drawlib PDF & HTML synthesis) |

### Machine-Readable Evidence Artifacts

All raw JSON payloads and structured migration outputs remain stored as versioned workspace files rather than pasted inline into the PDF:

| Artifact Workspace Path | Schema / Content Purpose |
| :--- | :--- |
| `docs/reports/java_api_spring_messy_migration/java_api_spring_messy_migration_plan.json` | Validated Migration Plan (`MigrationPlanResult`: 7 axes, target architecture, 4 decisions, 5 phase gates, 8 PR WBS items) |
| `docs_src/reports/java_api_spring_messy_migration/_facts/migration_facts.json` | Deterministic Migration Facts (topological Waves 1..4, cycle-cut edge, implicit contracts, boundary touchpoints, OpenRewrite recipes) |
| `docs_src/reports/java_api_spring_messy_migration/_facts/plan.json` | Pre-Flight Recon Plan, action-level DAG (`act-01`..`act-05`), and validated Mermaid workflow definition |
| `pni_report/java_api_spring_messy_score.json` | Prerequisite Baseline Audit Score JSON (`based_on: java_api_spring_messy`, `wf-8177454c`, 66/100 Grade C) |
