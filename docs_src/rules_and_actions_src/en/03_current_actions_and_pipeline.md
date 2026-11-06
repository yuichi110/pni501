# 3. Implemented Actions Catalog & Deterministic Map-Reduce Pipeline

While **Rules** define declarative evaluation criteria, **Actions** (`src/pni/_actions/`) define executable audit units. `pni501` currently provides **8 canonical `PrimitiveType`s** and **13 built-in Composite Action YAMLs** (`7` universal `common/` actions, `3` `python/` actions, and `3` `java/` actions), orchestrated through a deterministic Map-Reduce-Blueprint pipeline.

```drawlib file=ra_actions_catalog_table.png caption="Complete Catalog of All 13 Implemented Built-In Composite Actions (common/*, python/*, and java/*)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=98, dpi=150)

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.4),
    border_style=Styles.MutedThin,
    has_header=True,
)
tbl.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=8.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=8.5),
)

rows = [
    ["Scope / Action ID", "Primitive Sequence", "Bound Rules", "Validated Push Output"],
    ["common/architecture_analysis", "3x record_architecture", "common/architecture", "SystemProfile + StructureMap + Flows"],
    ["common/supply_chain_audit", "ai_interpret", "supply_chain, security, git_workflow", "InterpretationInput (rule_checks[])"],
    ["common/service_readiness_audit", "ai_interpret", "twelve_factor, prod_readiness, security", "InterpretationInput (12F / PRR)"],
    ["common/cli_guidelines_audit", "ai_interpret", "cli_guidelines, documentation", "InterpretationInput (CLI UX)"],
    ["common/library_hygiene_audit", "ai_interpret", "library_guidelines, docs, maintainability", "InterpretationInput (SDK API)"],
    ["common/emit_score", "emit_score", "(Consumes CompiledAuditDigest)", "ScoreResult (<target>_score.json)"],
    ["common/write_drawlib_report", "write_drawlib_report", "(Consumes 5-Chapter Blueprint)", "ReportPushInput + HTML/PDF/PNG"],
    ["python/repo_structure_audit", "project_inspect -> ai_interpret", "supply_chain, docs, git, sec, py/deps", "ProjectFacts + InterpretationInput"],
    ["python/python_ast_audit", "ast_analyze -> ai_interpret", "arch, maint, sec, py/{quality,typing,stack}", "AstFacts (py) + InterpretationInput"],
    ["python/python_test_audit", "ai_interpret", "python/testing", "InterpretationInput (pytest audit)"],
    ["java/repo_structure_audit", "project_inspect -> ai_interpret", "supply_chain, docs, git, sec, java/deps", "ProjectFacts + InterpretationInput"],
    ["java/java_ast_audit", "ast_analyze -> ai_interpret", "arch, maint, sec, java/{quality,typing,sb}", "AstFacts (java) + InterpretationInput"],
    ["java/java_test_audit", "ai_interpret", "java/testing", "InterpretationInput (JUnit 5 audit)"],
]
tbl.draw_flexible(
    xy=(4.0, 94.5),
    column_widths=[36.0, 31.0, 37.0, 34.0],
    row_heights=[7.0] + [6.4] * 13,
    data=rows,
)
save()
```

---

## 3.1 The 8 Canonical `PrimitiveType`s (`base_model.py`)

Every workflow step—whether declared inline via `action:` or expanded from a composite YAML via `uses:`—executes as one of **8 canonical primitives**:

1. **`project_inspect`** *(Deterministic Python)*: Scans manifests (`pyproject.toml`, `pom.xml`, `build.gradle`), lockfiles, CI workflows, Dockerfiles, secrets, README headings, and `docs/` trees into `.pni/cache/<target>_facts.json`.
2. **`ast_analyze`** *(Deterministic Python)*: Runs the 8-dimension `LanguageAnalyzerSuite` (`python` or `java`) to measure exact import hygiene, type coverage, docstring/Javadoc sync, cognitive complexity, coupling cycles, operational timeouts, and test smells.
3. **`run_check`** *(Deterministic Subprocess)*: Executes whitelisted read-only verification commands and captures exit codes and output summaries into `WorkflowFactsBundle.checks`.
4. **`load_rules`** *(Context Injection)*: Injects cascaded rule Markdown documents directly into the step context when standalone rule priming is needed.
5. **`record_architecture`** *(Schema-Grounded AI)*: Records repository-verified `SystemProfile`, `StructureMap` (layers, modules, internal edges), and `ExecutionFlowMap` into `.pni/cache/<target>_architecture.json`, verifying every referenced `path` exists on disk.
6. **`ai_interpret`** *(Schema-Grounded AI Map Step)*: Evaluates active rules against extracted facts and source files. Enforces submission of a numeric `step_score` (`0–100`), explicit `rule_checks` (`pass` / `warn` / `fail` / `not_applicable`) covering **100% of active step rules**, file-verified `findings`, and concrete `action_items`.
7. **`emit_score`** *(Deterministic Reduce + Synthesis)*: Presents the pre-sorted `CompiledAuditDigest` to synthesize `overall_score`, `grade`, and executive rationales, then deterministically merges all sorted `audit_dimensions`, `rule_compliance`, `module_hotspots`, `findings`, `action_plan`, and `metrics_snapshot` into `<target>_score.json`.
8. **`write_drawlib_report`** *(Blueprint-Driven Visual Compiler)*: Generates `.pni/cache/<target>_report_blueprint.json` specifying exact sorted tables, heatmaps, and diagrams for Chapters `00`–`04`, then verifies compiled deliverables (`report.pdf` / `report_html/index.html`) at push time.

---

## 3.2 Action-Driven Map-Reduce & 5-Chapter Blueprint Pipeline

Earlier audit pipelines asked the LLM to remember dozens of rules at the end of a run, causing newly added checks to be omitted from prose reports. `pni501` solves this via **deterministic Python aggregation** (`aggregator.py` and `blueprint.py`):

```drawlib file=ra_mapreduce_blueprint_flow.png caption="Map-Reduce-Blueprint Loop: Per-Action Structured Push -> Python Deterministic Sort -> 5-Chapter Drawlib Spec"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=9.4),
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.0),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.6),
)

map_grp = diag.add(
    NodeGroup(
        title="1. Map Phase (Push Validation)",
        width=42.0,
        height=50.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=9.5, halign="left", valign="top"),
    ),
    xy=(3.0, 4.0),
)
n_arch = map_grp.add(
    Node("record_architecture\n(Paths Verified)", width=34.5, height=14.5, icon=PhosphorIcon.BLUEPRINT, icon_size=5.0),
    xy=(21.0, 33.5),
)
n_interp = map_grp.add(
    Node("ai_interpret (xN)\n(step_score + 100%\nrule_checks[])", width=34.5, height=16.5, icon=PhosphorIcon.LIST_CHECKS, icon_size=5.0),
    xy=(21.0, 12.5),
)

reduce_node = diag.add(
    Node(
        "2. Python Reduce\n(aggregator.py)\n- FAIL->WARN->PASS\n- CRITICAL->INFO\n- Module Hotspots",
        width=33.0,
        height=31.0,
        icon=PhosphorIcon.SORT_ASCENDING,
        icon_size=5.6,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.4),
        card_style=Styles.SecondaryFlat.patch(shape_r=1.8),
    ),
    xy=(73.0, 29.0),
)

out_grp = diag.add(
    NodeGroup(
        title="3. Blueprint & Report",
        width=42.0,
        height=50.0,
        style=Styles.PrimaryNeutral.patch(shape_r=2.0),
        text_style=Styles.SuccessBold.patch(text_size=9.5, halign="left", valign="top"),
    ),
    xy=(101.0, 4.0),
)
n_score = out_grp.add(
    Node("<target>_score.json\n(Enriched ScoreResult)", width=34.5, height=14.5, icon=PhosphorIcon.MEDAL, icon_size=5.0),
    xy=(21.0, 33.5),
)
n_bp = out_grp.add(
    Node("ReportBlueprint\n(00_cover .. 04_roadmap)\n-> HTML & A4 PDF", width=34.5, height=16.5, icon=PhosphorIcon.FILE_PDF, icon_size=5.0, style=Styles.SuccessBold, card_style=Styles.SuccessNeutral.patch(shape_r=1.5)),
    xy=(21.0, 12.5),
)

diag.connect(map_grp, reduce_node, routing="direct")
diag.connect(reduce_node, out_grp, routing="direct", style=Styles.SuccessBold)
diag.connect(n_score, n_bp, routing="direct", style=Styles.PrimaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

### Standard Workflow Archetype Recipes

Workflows in `.pni/workflows/*.yaml` compose these 13 actions by project archetype:

- **Library / SDK**: `architecture_analysis` → `repo_structure_audit` → `<lang>_ast_audit` → `library_hygiene_audit` → `<lang>_test_audit` → `emit_score` → `write_drawlib_report`.
- **CLI Application**: `architecture_analysis` → `repo_structure_audit` → `<lang>_ast_audit` → `cli_guidelines_audit` → `<lang>_test_audit` → `emit_score` → `write_drawlib_report`.
- **Service / Web API**: `architecture_analysis` → `repo_structure_audit` → `<lang>_ast_audit` → `service_readiness_audit` → `supply_chain_audit` → `<lang>_test_audit` → `emit_score` → `write_drawlib_report`.
