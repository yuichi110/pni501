# 6. 7-Axis Scoring, Blueprint Reporter, Benchmarks & CLI Reference

Once PNI completes its deterministic static, container runtime, supply-chain security, and dynamic HTTP penetration analyzers alongside schema-enforced AI evaluations, it synthesizes raw diagnostic evidence into two executive-ready outputs: canonical JSON artifacts (`ScoreResult` and `MigrationPlanResult`) and multi-chapter **Illustration-as-Code** deliverables compiled through `drawlib`. Rather than asking an LLM to sort tables or invent layout structures from scratch, PNI deterministically enriches, deduplicates, and pre-sorts every metric into a 7-file `ReportBlueprint` before `compiler.py` renders vector A4 PDFs.

```drawlib code=fold file=reporter_compilation_pipeline.png caption="Blueprint-Driven Drawlib Report Pipeline Across Health Audit and Migration Execution Tracks"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=158, height=76, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=9.8),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.5),
)

g_inputs = diag.add(
    NodeGroup(
        title="1. Enriched Inputs",
        width=33.5,
        height=68.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.2, halign="left", valign="top"),
    ),
    xy=(3.0, 4.0),
)
n_score = g_inputs.add(
    Node(
        "ScoreResult + agg\n(*_score.json)",
        width=29.0,
        height=15.5,
        icon=PhosphorIcon.MEDAL,
        icon_size=5.4,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(16.75, 50.0),
)
n_plan = g_inputs.add(
    Node(
        "MigrationPlanResult\n(*_migration_plan.json)",
        width=29.0,
        height=15.5,
        icon=PhosphorIcon.GIT_PULL_REQUEST,
        icon_size=5.4,
    ),
    xy=(16.75, 30.5),
)
n_cache = g_inputs.add(
    Node(
        "facts.json +\narchitecture.json",
        width=29.0,
        height=15.5,
        icon=PhosphorIcon.DATABASE,
        icon_size=5.4,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(16.75, 11.0),
)

g_bp = diag.add(
    NodeGroup(
        title="2. Blueprint Synthesis",
        width=33.5,
        height=68.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.2, halign="left", valign="top"),
    ),
    xy=(42.5, 4.0),
)
n_bp_eng = g_bp.add(
    Node(
        "blueprint.py /\nmigration_blueprint.py",
        width=29.0,
        height=18.0,
        icon=PhosphorIcon.SLIDERS_HORIZONTAL,
        icon_size=5.6,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.8),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(16.75, 46.5),
)
n_bp_json = g_bp.add(
    Node(
        "Blueprint JSON Cache\n(00_cover + 01..06)",
        width=29.0,
        height=18.0,
        icon=PhosphorIcon.LIST_NUMBERS,
        icon_size=5.6,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(16.75, 15.5),
)

g_author = diag.add(
    NodeGroup(
        title="3. AI Authoring & QA",
        width=33.5,
        height=68.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.2, halign="left", valign="top"),
    ),
    xy=(82.0, 4.0),
)
n_src = g_author.add(
    Node(
        "reports_src/\n<target>_src/00..06.md",
        width=29.0,
        height=18.0,
        icon=PhosphorIcon.FILE_CODE,
        icon_size=5.6,
    ),
    xy=(16.75, 46.5),
)
n_qa = g_author.add(
    Node(
        "drawlib rules show\n+ show -g Grid Check",
        width=29.0,
        height=18.0,
        icon=PhosphorIcon.MAGNIFYING_GLASS,
        icon_size=5.6,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(16.75, 15.5),
)

g_compile = diag.add(
    NodeGroup(
        title="4. compiler.py Build",
        width=33.5,
        height=68.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.2, halign="left", valign="top"),
    ),
    xy=(121.5, 4.0),
)
n_comp = g_compile.add(
    Node(
        "pni report build\n(lint + drawlib.tools)",
        width=29.0,
        height=15.5,
        icon=PhosphorIcon.GEAR_SIX,
        icon_size=5.4,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.8),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(16.75, 50.0),
)
n_pdf = g_compile.add(
    Node(
        "reports/<target>.pdf\n(A4 Vector + ToC)",
        width=29.0,
        height=15.5,
        icon=PhosphorIcon.FILE_PDF,
        icon_size=5.4,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=1.5),
    ),
    xy=(16.75, 30.5),
)
n_opt = g_compile.add(
    Node(
        "HTML / MD / PNG\n(scan_broken_links)",
        width=29.0,
        height=15.5,
        icon=PhosphorIcon.BROWSER,
        icon_size=5.4,
    ),
    xy=(16.75, 11.0),
)

diag.connect(n_bp_eng, n_bp_json, label="7 chapters", routing="orthogonal")
diag.connect(n_qa, n_src, label="self-heal", arrow="<->", routing="orthogonal")
diag.connect(n_comp, n_pdf, routing="orthogonal", style=Styles.SuccessBold)
diag.connect(n_pdf, n_opt, routing="orthogonal", style=Styles.MutedBold)

diag.connect(g_inputs, g_bp, routing="orthogonal", style=Styles.PrimaryBold)
diag.connect(g_bp, g_author, routing="orthogonal", style=Styles.PrimaryBold)
diag.connect(g_author, g_compile, routing="orthogonal", style=Styles.PrimaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

---

## 6.1 7-Axis `ScoreResult`, Deterministic `aggregator.py` & `MigrationPlanResult`

PNI enforces strict Pydantic v2 contracts on both terminal data artifacts—`ScoreResult` (`reports/<target>_score.json`) for health diagnostics and `MigrationPlanResult` (`reports/<target>_migration_plan.json`) for modernization execution plans—ensuring downstream automation, CI gates, and visual report compilers consume reproducible, path-verified records.

### 6.1.1 The 7 Core Engineering Axes & Grade Mapping

Every health audit evaluates a target project on a `0..100` integer scale across seven standardized engineering axes in `CategoryScores` (`src/pni/_actions/base_model.py`), accompanied by evidence-backed `CategoryRationales`:

1. **`architecture`**: Package/layer cohesion, dependency directionality, absence of strongly connected component (SCC) import cycles, and framework/domain boundary separation.
2. **`code_quality`**: SIG-aligned unit complexity, function length and parameter counts, idiomatic constructs, structured logging, I/O timeout hygiene, and absence of mutable global state.
3. **`typing`**: Type-annotation coverage (`type_safety_coverage_pct`), strictness declarations (`py.typed`, generics, `declare(strict_types=1)`), and static type-checker cleanliness.
4. **`testing`**: Automated test suite breadth, assertion density, containerized harness execution pass rate, smoke checks, and measured line/branch coverage.
5. **`dependencies`**: Manifest/lockfile determinism, version-pinning discipline, declared runtime compatibility (`language_version_mismatches`), and absence of undeclared imports.
6. **`security`**: Application and OS container CVE posture (Trivy), secret hygiene, IaC/Dockerfile hardening, CWE-classified AST sinks (`dangerous_sinks`), API authorization boundaries, and live HTTP penetration test verdicts (`web_pentest`).
7. **`documentation`**: Public module/callable docstring coverage (`docstring_coverage_pct`), onboarding/architecture docs, governance files (`SECURITY.md`, `LICENSE`), and operational runbooks.

Overall and per-step integer scores map deterministically to a five-tier `HealthGrade` via `score_to_grade()` in `src/pni/_workflows/aggregator.py`:

| Grade | Score Threshold | Engineering Interpretation |
| :--- | :--- | :--- |
| **`S`** | `90 .. 100` | Exemplary reference architecture with near-zero structural, runtime, or security debt. |
| **`A`** | `80 .. 89` | Production-ready engineering hygiene with minor, non-blocking improvement opportunities. |
| **`B`** | `70 .. 79` | Sound structural foundation carrying localized test coverage, dependency, or hardening gaps. |
| **`C`** | `60 .. 69` | Elevated maintainability or operational risk requiring prioritized remediation before scaling. |
| **`D`** | `< 60` | Critical architectural, build/runtime, or exploitable security debt requiring structured intervention. |

### 6.1.2 Deterministic Stamping (`_enrich_score_result`) & `aggregator.py` Pre-Sorting

When an agent submits `ScoreResult` during `emit_score`, `src/pni/_workflows/engine.py:_enrich_score_result()` never trusts raw LLM ordering or unverified metadata. Instead, it re-assembles the `WorkflowFactsBundle` from SQLite, verifies every referenced `file_path` and `target_files` entry against the real repository and `AstFacts.module_inventory` (`_verify_grounded_paths`), stamps immutable provenance (`workflow_id`, `workflow_run_id`, UTC `evaluated_at`, `target_root`, `facts_file`, recomputed `grade`, and deterministic `metrics_snapshot`), attaches `runtime_facts`, `security_facts`, `pentest_facts`, and `architecture_record`, and replaces list fields with the canonical output of `aggregator.py:compile_workflow_digest()`:

- **`audit_dimensions` (Weakest-First Step Scorecards)**: Aggregates every `ai_interpret` step into an `AuditDimensionScore` (`pass_count`, `warn_count`, `fail_count`, `score`, `grade`) sorted ascending by `(score, -fail_count, -warn_count, seq)` so the weakest engineering areas surface first. If an agent omits `step_score`, `_compute_step_score()` deterministically falls back to the mean of `suggested_scores` or `100 - sum(SEVERITY_DEDUCTION)` (`critical=35`, `high=20`, `medium=10`, `low=3`, `info=1`).
- **`rule_compliance` (`fail -> warn -> pass -> not_applicable`)**: `normalize_step_rule_checks()` guarantees every active rule on every step receives a stamped `RuleCheckResult` (inferring verdicts from findings if omitted). `merge_and_sort_rule_compliance()` deduplicates rules across steps—retaining the strictest status while concatenating unique evidence—and sorts by `(STATUS_RANK[status], rule_id)`.
- **`module_hotspots` (`0.00 .. 1.00` Risk Density Formula)**: `compute_module_hotspots()` scores every source module and flagged infrastructure file on a bounded `[0.0, 1.0]` scale sorted descending by `(-risk_score, -loc, file_path)`:
  - Clean modules with zero findings and zero structural/runtime/security bonuses receive a baseline score of **`0.06`** (`_BASE_HEALTHY_RISK`).
  - Otherwise, `risk_score = round(min(1.0, raw_weight + ast_bonus + cov_bonus + sec_bonus), 2)`, combining:
    - **Finding severity weights (`SEVERITY_RISK_WEIGHT`)**: `critical=+0.45`, `high=+0.28`, `medium=+0.15`, `low=+0.06`, `info=+0.02`.
    - **AST structural bonuses (`_ast_structural_risk_bonus`)**: complex functions (`+0.12`), global state usages (`+0.14`), hardcoded secrets (`+0.25`), and dangerous sinks (`min(0.30, 0.12 * sink_count)`).
    - **Low measured test-coverage bonus (`_build_low_coverage_bonus_map`)**: for modules with `>= 5` statements and `< 50%` measured line coverage, `+0.16` at `0.0%` coverage or `+0.10` at `0.1%..49.9%`.
    - **Trivy security bonus (`_build_security_scan_bonus_map`)**: `+0.15` per secret or IaC misconfiguration hit on that file (capped at `+0.30`).
- **`findings` & Location-Grouped `consolidated_findings`**: `deduplicate_and_sort_findings()` sorts raw findings by `critical -> high -> medium -> low -> info`. Next, `consolidate_findings_by_location()` (`src/pni/_actions/base_model.py`) buckets overlapping violations sharing the exact same `(file_path, line)` into single multi-rule `ConsolidatedFinding` records (`rule_ids`, `combined_evidence`, `merged_recommendation`) sorted by `(severity_rank, file_path, line, rule_ids[0])`—eliminating duplicate table rows when multiple rules flag the same line of code.
- **`action_plan` (`P0 -> P1 -> P2`)**: `deduplicate_and_sort_actions()` deduplicates remediation items by `(priority, title.lower())` and sorts deterministically by `(PRIORITY_RANK[priority], category, title)`.

### 6.1.3 `MigrationPlanResult` & Path-Grounded Modernization Schemas

For repositories requiring multi-phase modernization (`category: migration`, `based_on: <audit_workflow_id>`), `emit_migration_plan` validates and persists `MigrationPlanResult` (`src/pni/_actions/migration_analyze/models.py`), verifiable via `pni validate-migration-plan <path>`:

- **Execution Guardrails**: Pins `transformation_mode` (`same_lang_upgrade`, `architectural_restructure`, or `cross_stack_replacement`), `migration_strategy` (`phased_pr`, `strangler_fig`, or `rewrite`), `api_compatibility` (`strict`, `versioned_v2`, or `flexible`), and `bug_handling_policy` (`ask_human`, `preserve_behavior`, or `fix_in_phase3`), alongside `confirmed_assumptions` and explicit `non_goals`.
- **`target_axes` (`MigrationAxis`)**: Captures each As-Is $\to$ To-Be transformation vector (`language_runtime`, `framework`, `architecture_pattern`, `database_persistence`, `cache_state`, `auth_security`, `messaging_async`, `container_cicd`, `custom`) with `risk_level` and grounded `affected_files`.
- **`target_architecture` (`TargetArchitectureDesign`)**: Defines the To-Be architecture (`pattern_name`, `dependency_rules`, `target_layers` with `allowed_dependencies` and `forbidden_imports`) and file-level `component_mappings` (`source_file` $\to$ `target_layer`, `target_component`, `port_or_adapter_role`).
- **`decision_log` (`DecisionLogItem`)**: Isolates ambiguous legacy behaviors ("Spec vs. Bug" under Hyrum's Law, `DEC-01..NN`) with `current_behavior`, `impact_if_changed`, and `recommended_option` for Product Owner sign-off prior to Phase 3 business-logic changes.
- **`phase_gates` (`MigrationPhaseGate`, Phases `0..4`)**: Enforces a 5-stage gated roadmap—**Phase 0** (Characterization & Harness Recovery), **Phase 1** (Cycle Cutting & Port Extraction), **Phase 2** (Mechanical Codemods & DB/Cache Adapters), **Phase 3** (Typed DTOs & Approved Fixes), and **Phase 4** (Cutover & CI/Container Hardening)—each with explicit `exit_criteria` and `rollback_or_coexistence_note`.
- **`pr_wbs` (`MigrationPrTicket`) & Attached `migration_facts`**: Topologically ordered pull-request tickets (`PR-01..NN` with `phase_number`, `wave 1..4`, `target_files`, `automated_or_manual`, `verification_cmd`, `estimated_size`, `depends_on_prs`), enriched automatically with deterministic `MigrationFacts` (`refactoring_waves`, `cycle_cuts`, `implicit_contracts`, `env_contracts`, `boundary_touchpoints`, `mechanical_codemods`, `manual_blockers`, and `spec_vs_bug_candidates`). During persistence, `_migration_engine.py:validate_and_persist_migration_plan()` verifies that all As-Is paths exist in the repository while enforcing safe workspace-relative paths on To-Be `pr_wbs[].target_files`.

---

## 6.2 Dual 7-Chapter `ReportBlueprint` Architecture & Compiler Guardrails

During the final `write_drawlib_report` / `write_migration_report` step, `src/pni/_reporter/blueprint.py` and `src/pni/_reporter/migration_blueprint.py` convert the validated JSON artifacts into a cached `ReportBlueprint` (`.pni/cache/<workflow_id>/blueprint.json` or `migration_blueprint.json`). Both tracks standardize on an identical **7-file linear `doc` layout (`00_cover.md` + `01..06`)**, localized in English (`en`) or Japanese (`ja`), where Drawlib automatically injects a hyperlinked Table of Contents immediately after `00_cover.md`.

```drawlib file=blueprint_chapter_comparison.png caption="Side-by-Side 7-Chapter ReportBlueprint Architecture for Health Audits and Migration Execution Plans"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=158, height=110, dpi=150)

audit_panel = Panel(
    "Health Audit Blueprint (blueprint.py)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
audit_panel.draw(xy=(3.0, 3.0), width=73.5, height=104.0)

audit_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.8),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.0,
)
audit_cards.add(
    "00_cover.md — Diagnostic Cover",
    "Panel + KpiCards (Score/Grade, Rules) -> Auto ToC",
    badge_text="00",
    icon=phosphor.medal,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.WhiteBold,
)
audit_cards.add(
    "01_executive_summary.md",
    "7-Axis RadarChart + KpiCards + Strengths/Top Risks",
    badge_text="01",
    icon=phosphor.chart_polar,
)
audit_cards.add(
    "02_architecture_and_structure.md",
    "TreeNode/Table + ClassDiagram & HeatmapOverlay",
    badge_text="02",
    icon=phosphor.tree_structure,
)
audit_cards.add(
    "03_remediation_roadmap.md",
    "Phased P0 -> P1 -> P2 Roadmap + Traceability Table",
    badge_text="03",
    icon=phosphor.git_commit,
)
audit_cards.add(
    "04_standards_and_findings.md",
    "Weakest-First BarChart + Consolidated Findings Table",
    badge_text="04",
    icon=phosphor.list_checks,
)
audit_cards.add(
    "05_code_and_runtime_analysis.md",
    "Module Quality HeatmapChart + Runtime/Coverage Bars",
    badge_text="05",
    icon=phosphor.cpu,
)
audit_cards.add(
    "06_security_and_supply_chain.md",
    "App/OS CVE Table + CWE Sinks & API Auth Surface",
    badge_text="06",
    icon=phosphor.shield_check,
)
audit_cards.draw(xy=(5.5, 5.5), width=68.5, height=90.5)

mig_panel = Panel(
    "Migration Plan Blueprint (migration_blueprint.py)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
mig_panel.draw(xy=(81.5, 3.0), width=73.5, height=104.0)

mig_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.SecondaryBold.patch(text_size=9.8),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=2.0,
)
mig_cards.add(
    "00_cover.md — Migration Cover",
    "Panel + KpiCards (Mode, Strategy, PRs) -> Auto ToC",
    badge_text="00",
    icon=phosphor.compass,
    badge_style=Styles.SecondaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.WhiteBold,
)
mig_cards.add(
    "01_migration_strategy_summary.md",
    "Assumptions/Non-Goals + As-Is->To-Be Gap Table",
    badge_text="01",
    icon=phosphor.arrows_left_right,
)
mig_cards.add(
    "02_architecture_waves_and_contracts.md",
    "To-Be Port/Adapter ClassDiagram + Wave 1..4 Roadmap",
    badge_text="02",
    icon=phosphor.graph,
)
mig_cards.add(
    "03_spec_vs_bug_decision_log.md",
    "Hyrum's Law Decision Matrix + Sign-Off Workflow",
    badge_text="03",
    icon=phosphor.scales,
)
mig_cards.add(
    "04_five_phase_gate_roadmap.md",
    "Phase 0..4 Gated Timeline + Exit/Rollback Matrix",
    badge_text="04",
    icon=phosphor.flag_checkered,
)
mig_cards.add(
    "05_codemod_and_refactoring_design.md",
    "Codemod vs Manual BarChart + Touchpoint->Port Table",
    badge_text="05",
    icon=phosphor.wrench,
)
mig_cards.add(
    "06_pr_wbs_and_verification_gates.md",
    "Topological PR-01..NN WBS Table + Gate Summary",
    badge_text="06",
    icon=phosphor.git_pull_request,
)
mig_cards.draw(xy=(84.0, 5.5), width=68.5, height=90.5)

save()
```

### 6.2.1 Non-Destructive Scaffolding, On-Demand Rules & Compiler Preflight Checks

`src/pni/_reporter/compiler.py` and `drawlib_guide.py` enforce four engineering guardrails around visual report authoring and compilation:

1. **Non-Destructive `pni report init` (`scaffold_report_project`)**: Initializes `reports_src/<target>_src/` via `drawlib.tools.init_project("doc", ...)` with `drawlib.toml` and `<lang>/` localized chapter directories, and removes starter sample files (`<lang>/00_cover.md`, `01_overview.md`, `02_design.md`) on initial creation. If authored `<lang>/*.md` chapters already exist, `pni report init` preserves them intact—even when `--force` refreshes `drawlib.toml`, `styles.py`, `utils.py`, `style.css`, and `template.html`—so incremental re-audits produce clean `git diff` histories.
2. **On-Demand `drawlib rules show` Context Loading**: Rather than bloating early AST and rule-interpretation prompts with drawing documentation, PNI instructs agents to query `drawlib rules show` (`overview`, `project-doc`, `api`, `lib-smartarts-overview`, `lib-charts-overview`, `lib-diagrams-overview`, `lib-icons-overview`) right before authoring `reports_src/<target>_src/<lang>/*.md`, preventing guessed constructor arguments or coordinate-anchor inversions (`Bottom-Left` for Charts/Diagrams/Panels vs. `Top-Left` for `Table`/`TreeNode` vs. `Center` for primitives).
3. **Preflight Visual Linter (`lint_drawlib_chapters`)**: Before invoking `drawlib.tools.build_pdf()`, `compiler.py` scans every ```` ```drawlib ```` code fence across all chapter files to catch two recurring visual defects:
   - **Missing Multi-Series Legends**: Any `BarChart` or `LineChart` calling `.add_series(...)` two or more times must call `.draw_legend(...)`.
   - **Contour Label Collisions on UML Diagrams**: Combining `ClassDiagram` with `HeatmapOverlay(..., show_contour_lines=True)` emits a preflight warning (or raises `ValueError` under `strict_preflight=True`); authors must set `show_contour_lines=False` so thermal risk spots highlight high-risk classes cleanly without contour lines slicing through method signatures.
4. **Stage 2 Grid Verification (`-g`) & Multi-Format Link Scanning**: Agents export individual figures with the 10-unit/5-unit Cartesian grid overlaid (`uv run drawlib show ... -g -o .drawlib/scratch/<unique>_grid.png`) and inspect the rendered PNG multimodally to eliminate text clipping or box collisions prior to running `pni report build`. By default, `pni report build` compiles `reports/<target>.pdf` (`page_break=True`, `generate_index=True`, normalizing `<target>_<default_lang>.pdf` to `<target>.pdf`); when `-f html` is requested, `_verify_links()` automatically runs `drawlib.tools.scan_broken_links()` and fails closed (`strict_links=True`) on any broken asset or anchor reference.

---

## 6.3 9-Target Multi-Language Benchmark Matrix & Reference Migration Plans

To validate diagnostic fidelity across clean production architectures, CLI tooling, and severely degraded legacy codebases, `pni501` maintains **nine end-to-end benchmark repositories** under `examples/{python,java,php}/` along with their committed `ScoreResult` JSONs and compiled A4 PDF reports under `reports/{python,java,php}/`.

```drawlib file=benchmark_score_heatmap.png caption="Ground-Truth 7-Axis Health Scores Across All 9 Python, Java, and PHP Benchmark Targets"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=176, height=88, dpi=150)

chart = HeatmapChart(
    styles=[Styles.DangerNeutral, Styles.Neutral, Styles.PrimaryNeutral, Styles.PrimaryFlat],
    x_categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Documentation",
    ],
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.5,
    value_format="{:.0f}",
    auto_contrast_text=True,
    axis_line_style=Styles.Muted,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    width=148.0,
    height=62.0,
    title="9-Target Benchmark Matrix Across the 7 PNI Engineering Axes (0-100)",
    title_style=Styles.DarkBold.patch(text_size=12.0),
)

chart.add_row("py_lib_clean (95 / S)", [98, 96, 99, 93, 95, 94, 91])
chart.add_row("php_api_laravel_clean (94 / S)", [95, 96, 98, 95, 92, 91, 93])
chart.add_row("py_api_fastapi_clean (89 / A)", [94, 96, 98, 81, 88, 78, 90])
chart.add_row("java_api_spring_clean (78 / B)", [86, 82, 92, 66, 74, 58, 86])
chart.add_row("py_cli_audit_tool (77 / B)", [90, 80, 84, 64, 68, 78, 72])
chart.add_row("java_api_spring_messy (23 / D)", [29, 22, 35, 14, 18, 17, 26])
chart.add_row("py_api_legacy_messy (20 / D)", [22, 24, 26, 12, 18, 12, 28])
chart.add_row("php_wp_plugin_messy (20 / D)", [24, 26, 12, 18, 22, 10, 22])
chart.add_row("php_legacy_shop_messy (15 / D)", [18, 19, 12, 10, 18, 5, 24])

chart.draw(xy=(22.0, 21.0))
chart.draw_colorbar(
    xy=(78.0, 7.0),
    text_style=Styles.Dark.patch(text_size=9.5),
    length=60.0,
    thickness=2.4,
    num_ticks=6,
    value_format="{:.0f}",
    label="Category Health Score (0 = Critical Debt, 100 = Exemplary)",
)

save()
```

### 6.3.1 Multi-Language Health Audit Benchmark Summary

The nine benchmark targets span three clean reference implementations, two realistic mid-tier Grade `B` repositories (where PNI surfaces subtle container base-image CVEs, unauthenticated Actuator/API routes, or branch-coverage gaps despite clean code structure), and four severely degraded Grade `D` legacy applications:

| Workflow ID | Project Name | Stack Profile | Overall | Arch | Qual | Type | Test | Deps | Sec | Docs | Emitted Artifacts (`reports/...`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `py_lib_clean` | `metrics-kit` | Python 3.12 library | **95 (S)** | 98 | 96 | 99 | 93 | 95 | 94 | 91 | `python/lib_clean{_score.json,.pdf}` |
| `php_api_laravel_clean` | `order-fulfillment` | PHP 8.3 / Laravel 11 API | **94 (S)** | 95 | 96 | 98 | 95 | 92 | 91 | 93 | `php/api_laravel_clean{_score.json,.pdf}` |
| `py_api_fastapi_clean` | `order-dispatch` | Python 3.12 / FastAPI | **89 (A)** | 94 | 96 | 98 | 81 | 88 | 78 | 90 | `python/api_fastapi_clean{_score.json,.pdf}` |
| `java_api_spring_clean` | `inventory-service` | Java 21 / Spring Boot 3 | **78 (B)** | 86 | 82 | 92 | 66 | 74 | 58 | 86 | `java/api_spring_clean{_score.json,.pdf}` |
| `py_cli_audit_tool` | `logpulse` | Python CLI utility | **77 (B)** | 90 | 80 | 84 | 64 | 68 | 78 | 72 | `python/cli_audit_tool{_score.json,.pdf}` |
| `java_api_spring_messy` | `legacy-billing` | Legacy Java 8/11 Spring | **23 (D)** | 29 | 22 | 35 | 14 | 18 | 17 | 26 | `java/api_spring_messy{_score.json,.pdf}` |
| `py_api_legacy_messy` | `legacy-order-hub` | Legacy Python Flask API | **20 (D)** | 22 | 24 | 26 | 12 | 18 | 12 | 28 | `python/api_legacy_messy{_score.json,.pdf}` |
| `php_wp_plugin_messy` | `wp_plugin_messy` | Procedural WP plugin | **20 (D)** | 24 | 26 | 12 | 18 | 22 | 10 | 22 | `php/wp_plugin_messy{_score.json,.pdf}` |
| `php_legacy_shop_messy` | `legacy_shop_messy` | Procedural PHP 7.4 shop | **15 (D)** | 18 | 19 | 12 | 10 | 18 | 5 | 24 | `php/legacy_shop_messy{_score.json,.pdf}` |

### 6.3.2 Reference Migration Execution Plans (`based_on` Grade D Audits)

Building directly upon the completed SQLite audit runs of the two lowest-scoring enterprise web services, `pni501` ships two complete reference migration plans demonstrating distinct transformation modes and rollout strategies:

| Migration Workflow ID | Prerequisite Audit (`based_on`) | Mode & Rollout Strategy | Target Stack & To-Be Architecture | Axes | Decision Log | Gated WBS | Deliverables (`reports/...`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `java_api_spring_messy_migration` | `java_api_spring_messy` (`legacy-billing`, **23 / D**) | `architectural_restructure` / `phased_pr` (`strict` API, `ask_human`) | Java 21 LTS + Spring Boot 3.4 BOM + PostgreSQL 16 (JPA/Flyway) + Redis 7 in **Clean Architecture** (`domain` / `port` / `usecase` / `adapter`); OpenRewrite codemods isolated from manual cycle cuts (`BillingManager <-> BillingController`). | **`7` axes** | **`4` items** (`DEC-01..04`) | Phases `0..4`, **`10` PRs** (`PR-01..10`) | `java/api_spring_messy_migration{_plan.json,.pdf}` |
| `php_legacy_shop_messy_migration` | `php_legacy_shop_messy` (`legacy_shop_messy`, **15 / D**) | `cross_stack_replacement` / `strangler_fig` (`strict` API, `ask_human`) | Nginx reverse-proxy **Strangler Fig** routing endpoint-by-endpoint (`/product.php` $\to$ `/` $\to$ `/login.php` $\to$ `/admin_backup.php`) onto PHP 8.3 (`strict_types=1`) + **Modular Laravel 11** (`Domain` / `Actions` / `Http` / `Infrastructure`) + MySQL 8 Eloquent/PDO + Redis 7 cart/sessions, gated by all 19 `.pni/pentests/` DAST regression probes. | **`6` axes** | **`4` items** (`DEC-01..04`) | Phases `0..4`, **`10` PRs** (`PR-01..10`) | `php/legacy_shop_messy_migration{_plan.json,.pdf}` |

---

## 6.4 Complete `pni` CLI Quick Reference

All workspace initialization, rule inspection, stateful workflow execution, ad-hoc action debugging, live HTTP penetration testing, Drawlib report compilation, and JSON schema verification operations are exposed under the unified `pni` CLI (`src/pni/cli.py`):

| Command | Key Options & Arguments | Primary Purpose |
| :--- | :--- | :--- |
| `pni init` | `[--lang/-l python\|java\|php] [--force/-f]` | Scaffold `.pni/` (`rules/`, `actions/`, `workflows/`, `instructions.md`, and `.pni/cache/.gitignore`). |
| `pni instructions` | *(none)* | Print the Markdown AI agent bootstrap and stateful execution loop guide to `stdout`. |
| `pni rules list` | `[--all/-a]` | List active engineering rules and workflow guides with local `.pni/rules/` override status. |
| `pni rules show` | `<name> [--pretty/-p]` | Output a canonical or overridden rule/guide in clean Markdown (or a Rich panel with `--pretty`). |
| `pni workflows list` | `[--category/-c audit\|migration]` | List project workflows in `.pni/workflows/` with `based_on` links, step counts, targets, and outputs. |
| `pni workflows show` | `<workflow_id>` | Inspect resolved targets/outputs, normalized primitive steps, and pentest/migration preflight checks. |
| `pni workflows start` | `<workflow_id> [--supersede]` | Create a stateful run (`wf-...`) in `.pni/cache/workflow_state.db` (`--supersede` cancels prior active runs). |
| `pni workflows get-action` | `<run_id>` | Execute pending deterministic analyzers automatically and emit the next `act-XX` prompt & JSON schema. |
| `pni workflows push-action` | `<run_id> <action_id> [input_json] [--file/-f <path>]` | Validate agent JSON input against Pydantic schemas/repo paths, persist to SQLite, and advance state. |
| `pni workflows run-action` | `<workflow_id> <action> [--base-url <url>] [--force-pentests] [--fail-on-findings]` | Execute a single step/action directly with zero prior SQLite run preparation for rapid iteration or CI. |
| `pni workflows status` | `[run_id] [-w <wf>] [-s <status>] [--latest] [-n <limit>] [--json]` | Inspect run history or action-by-action step progress (`done/total`, current step) from SQLite. |
| `pni workflows inspect-action` | `<run_or_workflow> <action> [--agent-input \| --deterministic] [--json] [-o <path>]` | Export recorded deterministic JSON facts or pushed agent inputs from SQLite without raw DB queries. |
| `pni workflows cancel` | `<run_id> \| --superseded [-w <workflow_id>]` | Cancel an abandoned `in_progress` run or clean up older superseded runs in SQLite. |
| `pni pentests init` | `[-w <wf>] [-t <root>] [-s <src>] [-l <lang>] [--force/-f]` | Materialize explicit `Python + httpx` penetration test suites (`conftest.py`, `test_*.py`) in `.pni/pentests/`. |
| `pni pentests run` | `[-w <wf>] [-t <root>] [-s <src>] [--base-url <url>] [--workflow-id <id>] [--container-engine <eng>] [-f]` | Boot an isolated loopback target container (or probe `--base-url`) and run `.pni/pentests/<target>/`. |
| `pni report init` | `[target] [--src-dir reports_src] [-l en] [-s google] [--keep-samples] [-f]` | Non-destructively scaffold or refresh `reports_src/<target>_src/` while preserving existing `*.md` chapters. |
| `pni report build` | `[target] [--src-dir reports_src] [-o reports] [-f pdf\|html\|markdown\|images] [--toc/--no-toc] [--no-cache]` | Run `lint_drawlib_chapters`, compile `reports/<target>.pdf` (default), and verify HTML links when `-f html`. |
| `pni validate-score` | `[score_path]` | Validate a `*_score.json` file against the Pydantic `ScoreResult` schema. |
| `pni validate-migration-plan` | `[plan_path]` | Validate a `*_migration_plan.json` file against the Pydantic `MigrationPlanResult` schema. |
| `pni version` | *(none)* | Print the installed `pni501` package name and version. |
