# 15 Actions & 12 Primitives: Two-Tier Action Pipeline

To eliminate LLM guesswork over code metrics, dependency versions, runtime test pass rates, CVE counts, and refactoring blast radius, `pni501` decouples **declarative workflow authoring** from **execution mechanics**. For each of the 6 supported languages (**Python, Java, PHP, Go, TypeScript, and JavaScript**), workflows compose **15 core composite YAML actions** (`12` universal `common/` actions + `3` language-specific `<lang>/` actions) that flatten into **12 canonical `PrimitiveType` steps**—pairing `6` auto-executed Python analyzers with `6` schema-enforced, repository-grounded AI and gate primitives.

```drawlib align=center code=fold file=two_tier_action_expansion.png caption="Two-Tier Action Expansion: 15 Per-Language Composite Actions Flatten into 6 Deterministic Python Analyzers and 6 Grounded AI/Gate Primitives"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=164, height=96, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=10.0),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.6),
)

wf_node = diag.add(
    Node(
        "Workflow YAML\n15 Composite Actions\n(12 common + 3 <lang>)",
        width=35.0,
        height=20.0,
        icon=PhosphorIcon.FILE_CODE,
        icon_size=6.0,
    ),
    xy=(20.0, 69.0),
)

mgr_node = diag.add(
    Node(
        "Action Manager\n(Cascade & Flatten)",
        width=35.0,
        height=19.0,
        icon=PhosphorIcon.STACK,
        icon_size=6.0,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.2),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.6),
    ),
    xy=(20.0, 27.0),
)

det_group = diag.add(
    NodeGroup(
        title="6 Deterministic Auto-Executed Python Primitives",
        width=114.0,
        height=43.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(46.0, 50.0),
)

d1 = det_group.add(
    Node("project_inspect", width=24.5, height=13.5, icon=PhosphorIcon.FILE_MAGNIFYING_GLASS, icon_size=5.2),
    xy=(15.0, 26.5),
)
d2 = det_group.add(
    Node("ast_analyze", width=24.5, height=13.5, icon=PhosphorIcon.TREE_STRUCTURE, icon_size=5.2),
    xy=(43.5, 26.5),
)
d3 = det_group.add(
    Node("run_check", width=24.5, height=13.5, icon=PhosphorIcon.TERMINAL_WINDOW, icon_size=5.2),
    xy=(72.0, 26.5),
)
d4 = det_group.add(
    Node("security_scan", width=24.5, height=13.5, icon=PhosphorIcon.SHIELD_WARNING, icon_size=5.2),
    xy=(15.0, 10.0),
)
d5 = det_group.add(
    Node("web_pentest", width=24.5, height=13.5, icon=PhosphorIcon.BUG, icon_size=5.2),
    xy=(43.5, 10.0),
)
d6 = det_group.add(
    Node("migration_analyze", width=24.5, height=13.5, icon=PhosphorIcon.GIT_DIFF, icon_size=5.2),
    xy=(72.0, 10.0),
)
facts_node = det_group.add(
    Node(
        ".pni/cache/<wf>/\nfacts.json",
        width=22.5,
        height=29.0,
        icon=PhosphorIcon.DATABASE,
        icon_size=5.8,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.6),
    ),
    xy=(100.0, 18.2),
)

ai_group = diag.add(
    NodeGroup(
        title="6 Schema-Guided & Grounded AI / Gate Primitives",
        width=114.0,
        height=43.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.SecondaryBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(46.0, 3.0),
)

a1 = ai_group.add(
    Node("load_rules", width=33.0, height=13.5, icon=PhosphorIcon.BOOK_OPEN_TEXT, icon_size=5.2),
    xy=(20.0, 26.5),
)
a2 = ai_group.add(
    Node("record_architecture", width=33.0, height=13.5, icon=PhosphorIcon.BLUEPRINT, icon_size=5.2),
    xy=(57.0, 26.5),
)
a3 = ai_group.add(
    Node("ai_interpret", width=33.0, height=13.5, icon=PhosphorIcon.BRAIN, icon_size=5.2),
    xy=(94.0, 26.5),
)
a4 = ai_group.add(
    Node(
        "emit_score",
        width=33.0,
        height=13.5,
        icon=PhosphorIcon.MEDAL,
        icon_size=5.2,
        style=Styles.PrimaryBold,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.6),
    ),
    xy=(20.0, 10.0),
)
a5 = ai_group.add(
    Node(
        "emit_migration_plan",
        width=33.0,
        height=13.5,
        icon=PhosphorIcon.PATH,
        icon_size=5.2,
        style=Styles.PrimaryBold,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.6),
    ),
    xy=(57.0, 10.0),
)
a6 = ai_group.add(
    Node(
        "write_drawlib_report",
        width=33.0,
        height=13.5,
        icon=PhosphorIcon.CHART_POLAR,
        icon_size=5.2,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=1.6),
    ),
    xy=(94.0, 10.0),
)

diag.connect(wf_node, mgr_node, label="normalize", routing="orthogonal")
mgr_node.fork([det_group, ai_group], at_x=41.5, style=Styles.PrimaryBold)
diag.connect(d3, facts_node, routing="orthogonal", style=Styles.SecondaryBold)
diag.connect(d6, facts_node, routing="orthogonal", style=Styles.SecondaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

---

## 1. Two-Tier Action Expansion (`15` Composite Actions -> `12` Primitives)

Workflow definitions in `.pni/workflows/*.yaml` (`WorkflowDefinition`) stay concise because `src/pni/_actions/base_model.py` separates reusable domain audit bundles from low-level execution steps:

1. **Tier 1 — Composite Actions (`CompositeActionDefinition`)**: Domain-focused YAML specifications invoked via `uses: <action_id>`. Each composite action bundles default engineering `rules`, ordered `CompositePrimitiveSpec` entries, default `with` parameters, and domain-specific prompt instructions.
2. **Tier 2 — Canonical Primitives (`PrimitiveStep` & `PrimitiveType`)**: The `12` core execution primitives referenced inside composite YAMLs or directly in a workflow step via `action: <primitive_type>`. Every stateful workflow run and ad-hoc `run-action` call operates over flattened `PrimitiveStep` instances.

### 1.1 Catalog of the 15 Per-Language Composite Actions (`01` through `15`)

For any target language (`python`, `java`, `php`, `go`, `typescript`, or `javascript`), `src/pni/_actions/` provides **15 core composite YAML actions** (`12` universal actions in `common/` + `3` language-scoped actions in `<lang>/`):

| Stage | Composite `uses:` ID | Scope | Expanded `PrimitiveType` Sequence | Default Attached Rules & Purpose |
| :---: | :--- | :--- | :--- | :--- |
| **`01`** | **`repo_structure_audit`**<br>*(01_project_inspect)* | `<lang>/` | `project_inspect` -> `ai_interpret` | `<lang>/dependencies`, `common/supply_chain`, `common/documentation`, `common/git_hygiene`, `common/security` |
| **`02`** | **`architecture_analysis`**<br>*(02_architecture)* | `common/` | `record_architecture` (`×3`: `purpose_and_stack`, `layers_and_modules`, `flows_and_state`) | `common/architecture` — Grounded 3-aspect system comprehension saved to `architecture.json` |
| **`03`** | **`<lang>_ast_audit`**<br>*(03_ast_quality)* | `<lang>/` | `ast_analyze` -> `ai_interpret` | `<lang>/code_quality`, `<lang>/typing`, `<lang>/modernization`, and detected framework rules |
| **`04`** | **`<lang>_test_audit`**<br>*(04_test_suite)* | `<lang>/` | `ai_interpret` (consumes `AstFacts`) | `<lang>/testing` — Evaluates test isolation, mirror layout, and assertion density |
| **`05`** | **`supply_chain_audit`**<br>*(05_supply_chain)* | `common/` | `ai_interpret` (consumes `ProjectFacts`) | `common/supply_chain`, `common/git_hygiene`, `common/security` — OpenSSF & CI/CD governance |
| **`06`** | **`library_hygiene_audit`**<br>*(06_library_hygiene)* | `common/` | `ai_interpret` | `common/library_hygiene`, `common/documentation` — SemVer API surface & minimal dependencies |
| **`07`** | **`cli_guidelines_audit`**<br>*(07_cli_guidelines)* | `common/` | `ai_interpret` | `common/cli_guidelines`, `common/error_handling` — Clig.dev ergonomics, `--help`, exit codes |
| **`08`** | **`service_readiness_audit`**<br>*(08_service_readiness)* | `common/` | `ai_interpret` | `common/twelve_factor`, `common/production_readiness`, `common/observability`, `common/resilience` |
| **`09`** | **`container_runtime_audit`**<br>*(09_runtime_check)* | `common/` | `run_check` -> `ai_interpret` | `common/container_hygiene`, `common/production_readiness` — Offline `--network=none` tests & smoke probe |
| **`10`** | **`security_vulnerability_audit`**<br>*(10_security_scan)* | `common/` | `security_scan` -> `ai_interpret` | `common/security`, `common/supply_chain`, `common/container_hygiene` — Socketless Trivy FS + image tar scan |
| **`11`** | **`web_penetration_audit`**<br>*(11_web_pentest)* | `common/` | `web_pentest` -> `ai_interpret` | `common/security`, `common/resilience` — Loopback container boot + live `httpx` security probes |
| **`12`** | **`emit_score`**<br>*(12_emit_score)* | `common/` | `emit_score` | Aggregates findings, hotspots, rule compliance & stamps `reports/<target>_score.json` |
| **`13`** | **`write_drawlib_report`**<br>*(13_audit_report)* | `common/` | `write_drawlib_report` (`report_kind: audit`) | `common/reporting` — Emits `blueprint.json` and verifies 7-chapter A4 PDF audit deliverable |
| **`14`** | **`migration_proposal`**<br>*(14_migration_plan)* | `common/` | `migration_analyze` -> `ai_interpret` -> `emit_migration_plan` | `common/migration_planning`, `common/architecture` — Waves 1..4, Tarjan SCC cuts & `*_migration_plan.json` |
| **`15`** | **`write_migration_report`**<br>*(15_migration_report)* | `common/` | `write_drawlib_report` (`report_kind: migration`) | `common/reporting`, `common/migration_planning` — Compiles 7-chapter Migration A4 PDF report |

> **Progress Tracking Extension (`category: progress`)**: In addition to the 15 core audit and migration actions, `common/` also includes `progress_assessment` (`progress_analyze` -> `ai_interpret` -> `emit_progress`) and `write_progress_report` (`report_kind: progress`) to measure multi-sprint remediation delta against a baseline audit and migration plan.

### 1.2 Three-Layer Cascade & Parameter Merging (`_actions/manager.py`)

When `normalize_workflow_steps()` expands a workflow, `expand_composite_action()` resolves `uses:` via `local (.pni/actions/) > <active_lang>/ > common/` and merges three configuration layers:

- **Parameters (`params`)**: Workflow-level target/output paths (`workflow_id`, `target_root`, `source_targets`, `test_targets`, `doc_targets`, `facts_path`, `score_path`, `output_dir`) merge with the workflow step's `with:` block, overriding primitive-level `with:` defaults (`{**prim.with_params, **override_params}`).
- **Rules (`rules`)**: Composite rules, workflow-step `rules:` additions, and primitive-level rules are concatenated and deduplicated in declaration order (`dict.fromkeys`).
- **Provenance IDs**: Workflow-step `prompt:` overrides append cleanly below base prompts, producing compound step IDs (`{step_id}__{idx}_{prim.type.value}`) with `source_action=comp.id` before SQLite assigns sequential action IDs (`act-01`, `act-02`, ...).

```yaml
id: web_penetration_audit
name: Live Web Application Penetration Testing Audit
description: Starts the target web service in an isolated loopback container and executes Python + httpx security probes.
rules:
  - common/security
  - common/resilience
primitives:
  - type: web_pentest
    name: Execute Live Web Penetration Test Suite
    with:
      pentest_timeout_sec: 180
  - type: ai_interpret
    name: Evaluate Live Penetration Test Findings & Attack Surface
    prompt: |
      Review PentestFacts (discovered endpoints, failed security probes, CWE tags, and HTTP evidence).
      Cross-reference with AST dangerous_sinks and api_endpoints to prioritize P0-P2 remediations.
```

---

## 2. Complete Catalog of the 12 Canonical Primitives

In `src/pni/_actions/ai_actions.py` and `src/pni/_workflows/engine.py`, every `get-action` prompt injects `get_expected_input_schema_json()`, and every `push-action` call validates both **Pydantic v2 structure** and **repository path grounding** (`_verify_grounded_paths()` rejects any file or module path absent from disk and `AstFacts.module_inventory`):

```drawlib align=center code=fold file=primitive_catalog_table.png caption="Complete Catalog of the 12 Canonical PrimitiveType Actions, Execution Modes, Push Schemas, and Grounding / Side Effects"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=162, height=118, dpi=150)

headers_and_rows = [
    ["Primitive", "Mode", "Validated Push Schema", "Grounding & Side Effects"],
    [
        "project_inspect",
        "Deterministic",
        "DeterministicAckInput",
        "Parses manifests, lockfiles & governance\n-> .pni/cache/<wf>/facts.json",
    ],
    [
        "ast_analyze",
        "Deterministic",
        "DeterministicAckInput",
        "Runs 9 Tree-sitter AST checkers (6 langs)\n-> .pni/cache/<wf>/facts.json",
    ],
    [
        "run_check",
        "Deterministic",
        "DeterministicAckInput",
        "Materializes .pni/dockerfiles/, runs\n--network=none unit tests & coverage",
    ],
    [
        "security_scan",
        "Deterministic",
        "DeterministicAckInput",
        "Runs socketless Trivy FS + image tar scan\n-> security_facts.json & facts.json",
    ],
    [
        "web_pentest",
        "Deterministic",
        "DeterministicAckInput",
        "Boots 127.0.0.1 loopback container & runs\n.pni/pentests/<target>/ httpx probes",
    ],
    [
        "migration_analyze",
        "Deterministic",
        "DeterministicAckInput",
        "Computes Waves 1..4, Tarjan SCC cuts,\ncontracts & DEC-XX -> migration_facts.json",
    ],
    [
        "load_rules",
        "AI / Gate",
        "DeterministicAckInput",
        "Resolves & injects cascaded Markdown\nengineering rules into prompt context",
    ],
    [
        "record_architecture",
        "AI / Grounded",
        "SystemProfile | StructureMap |\nExecutionFlowMap",
        "Verifies paths against module_inventory\n-> .pni/cache/<wf>/architecture.json",
    ],
    [
        "ai_interpret",
        "AI / Grounded",
        "InterpretationInput",
        "Grounds findings/action_items & runs\nnormalize_step_rule_checks() per rule",
    ],
    [
        "emit_score",
        "AI + Aggregator",
        "ScoreResult",
        "Runs aggregator.py digest + metric stamp\n-> reports/<target>_score.json",
    ],
    [
        "emit_migration_plan",
        "AI + Grounded",
        "MigrationPlanResult",
        "Grounds As-Is paths + attaches MigrationFacts\n-> reports/<target>_migration_plan.json",
    ],
    [
        "write_drawlib_report",
        "AI + Compiler",
        "ReportCompletionInput",
        "Emits blueprint.json & verifies non-empty\ncompiled PDF deliverable on disk",
    ],
]

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=10.0),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.5),
    border_style=Styles.MutedThin,
    has_header=True,
)

tbl.set_style_cell_evenodd(
    even_color=Styles.Neutral.shape_fill_color,
    even_text_style=Styles.Dark.patch(text_size=10.0),
    odd_color=Styles.White.shape_fill_color,
    odd_text_style=Styles.Dark.patch(text_size=10.0),
)
tbl.set_style_cell(
    background_color=Styles.PrimaryFlat.shape_fill_color,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    rows=[0],
)
tbl.set_style_cell(
    background_color=Styles.SecondaryNeutral.shape_fill_color,
    text_style=Styles.SecondaryBold.patch(text_size=10.0),
    rows=[1, 2, 3, 4, 5, 6],
    columns=[0],
)
tbl.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=10.0),
    rows=[7, 8, 9, 10, 11, 12],
    columns=[0],
)

col_widths = [31.0, 23.0, 39.0, 63.0]
row_heights = [8.2] + [8.6] * 12

tbl.draw_flexible(
    xy=(3.0, 114.5),
    column_widths=col_widths,
    row_heights=row_heights,
    data=headers_and_rows,
    align="top_left",
)
save()
```

### 2.1 Deterministic Auto-Execution & `WorkflowFactsBundle` Persistence

Whenever `pni workflows get-action` (or `push-action`) reaches one of the 6 deterministic primitives (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, or `migration_analyze`), `_execute_deterministic_step_if_needed()` runs the corresponding Python analyzer **once**:

- **SQLite & JSON Dual Persistence**: The serialized analyzer output is stored in `action_runs.deterministic_output_json` inside `.pni/cache/workflow_state.db` and merged into `.pni/cache/<workflow_id>/facts.json` (`WorkflowFactsBundle`).
- **Zero Re-Execution on Retry**: Subsequent `get-action` calls read the cached JSON directly from SQLite unless the operator explicitly rewinds the workflow back to that step via `pni workflows rewind <run_id> <selector>`.

### 2.2 Grounding Gates & Synthesis Across Cognitive Primitives

- **Aspect-Separated Architecture Comprehension (`record_architecture` -> `architecture.json`)**: Parameterized via `with: {aspect: purpose_and_stack | layers_and_modules | flows_and_state}`, `record_architecture` splits codebase comprehension into three focused schemas (`SystemProfile`, `StructureMap`, `ExecutionFlowMap`). `_validate_and_persist_architecture()` checks every `layers[].paths`, `modules[].path`, `entry_points`, and `involved_files` entry against `AstFacts.module_inventory` and the workspace before persisting `.pni/cache/<workflow_id>/architecture.json`.
- **Per-Rule Compliance & Grounded Reasoning (`ai_interpret` -> `InterpretationInput`)**: Requires a `0..100` `step_score`, explicit `RuleCheckResult` verdicts (`pass`, `warn`, `fail`, `not_applicable`), grounded `findings`, and `P0`–`P2` `action_items`. On push, `engine.py` verifies every `file_path` and `target_files` entry and invokes `normalize_step_rule_checks()` (`aggregator.py`) so every active rule on the step is guaranteed a stamped compliance verdict.
- **Deterministic Digest & Score Stamping (`emit_score` -> `<target>_score.json`)**: `_enrich_score_result()` runs `compile_workflow_digest()` (`src/pni/_workflows/aggregator.py`) to deduplicate findings, group co-located violations into `consolidated_findings`, compute per-file `module_hotspots` (`0.0..1.0` risk density), derive canonical `S`–`D` `grade`, attach `RuntimeFacts` / `SecurityFacts` / `PentestFacts`, and overwrite `metrics_snapshot` directly from programmatic facts before writing `reports/<target>_score.json`.
- **Grounded Migration Plan Synthesis (`emit_migration_plan` -> `<target>_migration_plan.json`)**: `validate_and_persist_migration_plan()` (`_migration_engine.py`) validates `MigrationPlanResult` (`transformation_axes`, `target_architecture`, `component_mappings`, `phases`, `pr_backlog`, `decision_log`), verifies all referenced As-Is source paths exist in the repository, attaches deterministic `MigrationFacts`, and writes `reports/<target>_migration_plan.json`.
- **Blueprint-Guided Visual Report Gate (`write_drawlib_report` -> `ReportCompletionInput`)**: `render_drawlib_report_guide()` pre-computes `.pni/cache/<workflow_id>/blueprint.json` (or `migration_blueprint.json`) for the 7-chapter Drawlib `doc` report (`00_cover.md` .. `06_*.md`), and `_validate_report_completion()` verifies on disk that every file listed in `ReportCompletionInput.generated_files` exists inside the workspace with `st_size > 0`.

Continue to [Analyzers & Live Pentest](analyzers_and_pentest.md) for a deep dive into the 9 Tree-sitter AST checkers and the isolated Docker/Podman runtime, Trivy, and penetration testing engines, or see [7-Axis Scoring Model](../04_scoring_and_reports/scoring_model.md) for how `emit_score` computes final grades.
