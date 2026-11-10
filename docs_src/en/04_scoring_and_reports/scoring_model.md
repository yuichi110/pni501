# 7-Axis Scoring Model & Deterministic Aggregation

Once `pni501` completes its deterministic static AST, container runtime, supply-chain security, and live HTTP penetration analyzers alongside schema-enforced AI evaluations, it synthesizes all diagnostic evidence into canonical JSON artifacts (`ScoreResult` and `MigrationPlanResult`). Rather than trusting raw LLM ordering or unverified file paths, `aggregator.py` and `engine.py` deterministically verify repository paths, apply `pni.toml` opt-out waivers, compute module hotspot risk densities, and pre-sort every finding, rule verdict, and remediation item.

```drawlib align=center code=fold file=seven_axes_scoring_hero.png caption="7-Axis Engineering Health Scoring Model (700-Point Pool), Deterministic aggregator.py Pipeline, and Roadmap 8th Axis"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=172, height=92, dpi=150)

axes_panel = Panel(
    "1. Seven Engineering Axes (7 x 100 pt = 700 pt)",
    header_variant="filled",
    header_height=8.0,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
axes_panel.draw(xy=(3.0, 3.0), width=81.0, height=86.0)

axes_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=1.5,
)
axes_cards.add(
    "Architecture (0-100 pt)",
    "Layer cohesion, SCC cycle absence & boundary rules",
    badge_text="01",
    icon=phosphor.git_fork,
    style=Styles.PrimaryNeutral.patch(shape_r=1.4),
)
axes_cards.add(
    "Code Quality (0-100 pt)",
    "SIG unit complexity, idiomatic style & global state",
    badge_text="02",
    icon=phosphor.code,
)
axes_cards.add(
    "Typing (0-100 pt)",
    "Annotation coverage, strictness & type checker pass",
    badge_text="03",
    icon=phosphor.brackets_angle,
    style=Styles.PrimaryNeutral.patch(shape_r=1.4),
)
axes_cards.add(
    "Testing (0-100 pt)",
    "Isolated container test suite pass & line coverage",
    badge_text="04",
    icon=phosphor.flask,
)
axes_cards.add(
    "Dependencies (0-100 pt)",
    "Lockfile determinism, pinning & runtime version parity",
    badge_text="05",
    icon=phosphor.package,
    style=Styles.PrimaryNeutral.patch(shape_r=1.4),
)
axes_cards.add(
    "Security (0-100 pt)",
    "Trivy CVEs, secret/IaC hygiene, AST sinks & live DAST",
    badge_text="06",
    icon=phosphor.shield_check,
)
axes_cards.add(
    "Documentation (0-100 pt)",
    "Docstring coverage, architecture docs & runbooks",
    badge_text="07",
    icon=phosphor.book_open,
    style=Styles.PrimaryNeutral.patch(shape_r=1.4),
)
axes_cards.draw(xy=(5.5, 5.5), width=76.0, height=73.0)

agg_panel = Panel(
    "2. Deterministic aggregator.py & ScoreResult Output",
    header_variant="filled",
    header_height=8.0,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
agg_panel.draw(xy=(88.0, 44.0), width=81.0, height=45.0)

agg_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=1.8,
)
agg_cards.add(
    "compile_workflow_digest()",
    "Weakest-first steps, merged rules & P0-P2 plan",
    badge_text="AGG",
    icon=phosphor.sliders_horizontal,
)
agg_cards.add(
    "Hotspot Risk Density (0.00 - 1.00)",
    "Severity weights + AST sinks + coverage + CVEs",
    badge_text="RISK",
    icon=phosphor.fire,
    style=Styles.Neutral.patch(shape_r=1.4),
)
agg_cards.add(
    "ScoreResult (0-100 & Grade S/A/B/C/D)",
    "Path check + pni.toml opt-outs -> *_score.json",
    badge_text="JSON",
    icon=phosphor.medal,
)
agg_cards.draw(xy=(90.5, 46.5), width=76.0, height=32.5)

future_panel = Panel(
    "3. Planned 8th Axis: Development Status (Roadmap)",
    header_variant="filled",
    header_height=8.0,
    style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
future_panel.draw(xy=(88.0, 3.0), width=81.0, height=37.5)

future_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.SecondaryBold.patch(text_size=10.0),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=1.8,
)
future_cards.add(
    "Git Commit Dynamics & Churn Analysis",
    "Detects code churn spikes and stalled modules",
    badge_text="GIT",
    icon=phosphor.git_commit,
)
future_cards.add(
    "Gantt Milestone Variance & Warning",
    "Schedule delay vs. pre-deadline quality risk",
    badge_text="PLAN",
    icon=phosphor.calendar_check,
    style=Styles.Neutral.patch(shape_r=1.4),
)
future_cards.draw(xy=(90.5, 5.5), width=76.0, height=25.0)

save()
```

---

## 1. The 7 Implemented Quality Axes (700-Point Pool & Grade Mapping)

Every health audit workflow evaluates a target repository across seven standardized engineering axes defined in `CategoryScores` (`src/pni/_actions/base_model.py`). Each axis is scored on a `0..100` integer scale (`700` total raw points across the seven axes) and paired with evidence-backed rationales in `CategoryRationales`, synthesizing into a normalized `0..100` `overall_score`:

| # | Axis Key | Points | Primary Deterministic Signals & Evaluation Scope |
| :--- | :--- | :--- | :--- |
| **1** | **`architecture`** | `0..100` | Package/layer cohesion, dependency directionality, absence of strongly connected component (SCC) import cycles, and framework/domain boundary separation. |
| **2** | **`code_quality`** | `0..100` | SIG-aligned unit complexity, function length and parameter counts, idiomatic constructs, structured logging, I/O timeout hygiene, and absence of mutable global state. |
| **3** | **`typing`** | `0..100` | Type-annotation coverage (`type_safety_coverage_pct`), strictness declarations (`py.typed`, generics, `strict_types=1`, `tsconfig` strict), and static type-checker cleanliness. |
| **4** | **`testing`** | `0..100` | Automated test suite breadth, assertion density, isolated container harness pass rate (`run_check`), smoke checks, and measured line/branch coverage. |
| **5** | **`dependencies`** | `0..100` | Manifest and lockfile determinism, version-pinning discipline, declared runtime compatibility (`language_version_mismatches`), and absence of undeclared imports. |
| **6** | **`security`** | `0..100` | Application and OS container CVE posture (`security_scan` via Trivy), secret hygiene, IaC/Dockerfile hardening, CWE-classified AST sinks (`dangerous_sinks`), and live HTTP penetration test verdicts (`web_pentest`). |
| **7** | **`documentation`** | `0..100` | Public module/callable docstring coverage (`docstring_coverage_pct`), onboarding/architecture guides, governance files (`SECURITY.md`, `LICENSE`), and operational runbooks. |

### 1.1 HealthGrade Mapping (S / A / B / C / D)

Both the repository's `overall_score` and each step's `AuditDimensionScore` map deterministically to a five-tier `HealthGrade` via `score_to_grade()` in `src/pni/_workflows/aggregator.py`:

| Grade | Score Threshold | Engineering Interpretation |
| :--- | :--- | :--- |
| **`S`** | `90 .. 100` | Exemplary reference architecture with near-zero structural, runtime, or security debt. |
| **`A`** | `80 .. 89` | Production-ready engineering hygiene with minor, non-blocking improvement opportunities. |
| **`B`** | `70 .. 79` | Sound structural foundation carrying localized test coverage, dependency, or hardening gaps. |
| **`C`** | `60 .. 69` | Elevated maintainability or operational risk requiring prioritized remediation before scaling. |
| **`D`** | `< 60` | Critical architectural, build/runtime, or exploitable security debt requiring structured intervention. |

### 1.2 Future Roadmap: 8th Axis (Development Status & Schedule Variance)

Beyond the seven implemented code and runtime axes, the `pni501` roadmap defines an eighth evaluation axis—**Development Status (`development_status`)**—to combine static engineering health with delivery trajectory monitoring:

- **Git Commit Velocity & Churn Dynamics**: Analyzes commit history to identify sudden code-churn spikes, hotfix clusters, or stalled core modules.
- **Gantt Milestone Variance Cross-Check**: Compares planned milestone schedules against actual repository implementation progress across features and subsystems.
- **Crunch-Time Quality Degradation Early Warning**: Detects when schedule slippage coincides with rapid pre-deadline commit churn, alerting engineering leads before test coverage or architectural boundaries are bypassed.

---

## 2. Deterministic Enrichment & Pre-Sorting in aggregator.py

When an AI agent submits `ScoreResult` during the terminal `emit_score` action, `src/pni/_workflows/engine.py:_enrich_score_result()` never trusts raw LLM sorting or unverified file references. Instead, it re-assembles the `WorkflowFactsBundle` from `.pni/cache/workflow_state.db`, verifies every referenced `file_path` and `target_files` entry against the real repository and `AstFacts.module_inventory`, stamps immutable provenance (`workflow_id`, `workflow_run_id`, UTC `evaluated_at`, `target_root`, `facts_file`, recomputed `grade`, and `metrics_snapshot`), and replaces list fields with the canonical output of `aggregator.py:compile_workflow_digest()`.

### 2.1 Weakest-First Dimensions, Rule Compliance & Consolidated Findings

- **`audit_dimensions` (Weakest-First Step Scorecards)**: Aggregates every completed `ai_interpret` action into an `AuditDimensionScore` (`pass_count`, `warn_count`, `fail_count`, `score`, `grade`) sorted ascending by `(score, -fail_count, -warn_count, seq)` so the weakest engineering dimensions appear first. If `step_score` is omitted, `_compute_step_score()` deterministically falls back to the mean of `suggested_scores` or `100 - sum(SEVERITY_DEDUCTION)` (`critical=35`, `high=20`, `medium=10`, `low=3`, `info=1`).
- **`rule_compliance` (`fail -> warn -> pass -> not_applicable`)**: `normalize_step_rule_checks()` guarantees every active rule on every step receives a stamped `RuleCheckResult` (inferring verdicts from step findings when omitted). `merge_and_sort_rule_compliance()` deduplicates rules across steps—retaining the strictest status while concatenating unique evidence—and sorts by `(STATUS_RANK[status], rule_id)`.
- **`findings` & Location-Grouped `consolidated_findings`**: `deduplicate_and_sort_findings()` orders raw findings by `critical -> high -> medium -> low -> info`. Next, `consolidate_findings_by_location()` (`src/pni/_actions/base_model.py`) buckets overlapping violations sharing the exact same `(file_path, line)` into a single multi-rule `ConsolidatedFinding` (`rule_ids`, `combined_evidence`, `merged_recommendation`), preventing duplicate table rows in downstream PDF reports.
- **`action_plan` (`P0 -> P1 -> P2`)**: `deduplicate_and_sort_actions()` deduplicates remediation items by `(priority, title.lower())` and sorts deterministically by `(PRIORITY_RANK[priority], category, title)`.
- **Declarative `pni.toml` Opt-Out Waivers (`opt_outs`)**: `_filter_findings_by_opt_out()` and `normalize_step_rule_checks()` honor `[[opt_out]]` entries declared in `pni.toml` (matching by rule/check `id` and optional file `scope` globs), waiving matching findings, marking repo-wide opted-out rules as `not_applicable`, and recording transparent `AppliedOptOut` audit trails in `ScoreResult.opt_outs`.

### 2.2 Module Hotspot Risk Density Formula (0.00 to 1.00)

`compute_module_hotspots()` scores every discovered source module and flagged infrastructure file on a bounded `[0.00, 1.00]` scale sorted descending by `(-risk_score, -loc, file_path)`. Clean modules with zero findings and zero structural/runtime/security bonuses receive a baseline healthy score of `0.06` (`_BASE_HEALTHY_RISK`), whereas flagged modules combine four deterministic signal sources:

```python
SEVERITY_RISK_WEIGHT = {
    "critical": 0.45,
    "high": 0.28,
    "medium": 0.15,
    "low": 0.06,
    "info": 0.02,
}
_BASE_HEALTHY_RISK = 0.06

# Per-file hotspot risk density in [0.00, 1.00]:
# 1. raw_weight = sum(SEVERITY_RISK_WEIGHT[f.severity] for f in file_findings)
# 2. ast_bonus  = +0.12 (complex_functions) + 0.14 (global_state)
#                 + 0.25 (hardcoded_secrets) + min(0.30, 0.12 * sink_count)
# 3. cov_bonus  = +0.16 (0.0% line coverage) or +0.10 (0.1%..49.9% coverage, >=5 stmts)
# 4. sec_bonus  = min(0.30, 0.15 * trivy_secret_or_iac_hits)
risk_score = round(min(1.0, raw_weight + ast_bonus + cov_bonus + sec_bonus), 2)
```

---

## 3. Path-Grounded MigrationPlanResult Schema

For repositories requiring structured modernization (`category: migration`, `based_on: <audit_workflow_id>`), the `emit_migration_plan` action validates and persists `MigrationPlanResult` (`src/pni/_actions/migration_analyze/models.py`), verifiable via `pni validate-migration-plan <path>`:

- **Execution Guardrails**: Pins `transformation_mode` (`same_lang_upgrade`, `architectural_restructure`, or `cross_stack_replacement`), `migration_strategy` (`phased_pr`, `strangler_fig`, or `rewrite`), `api_compatibility` (`strict`, `versioned_v2`, or `flexible`), and `bug_handling_policy` (`ask_human`, `preserve_behavior`, or `fix_in_phase3`), alongside `confirmed_assumptions` and explicit `non_goals`.
- **`target_axes` (`MigrationAxis`) & `target_architecture`**: Captures each As-Is to To-Be transformation vector (`language_runtime`, `framework`, `architecture_pattern`, `database_persistence`, `cache_state`, `auth_security`, `messaging_async`, `container_cicd`, `custom`) with grounded `affected_files`, plus `target_layers` (`allowed_dependencies`, `forbidden_imports`) and file-level `component_mappings`.
- **`decision_log` (`DecisionLogItem`, `DEC-01..NN`)**: Isolates ambiguous legacy behaviors ("Spec vs. Bug" under Hyrum's Law) with `current_behavior`, `impact_if_changed`, and `recommended_option` for Product Owner sign-off prior to Phase 3 business-logic changes.
- **`phase_gates` (`Phases 0..4`) & `pr_wbs` (`PR-01..NN`)**: Enforces a 5-stage gated roadmap—**Phase 0** (Characterization & Harness Recovery), **Phase 1** (Cycle Cutting & Port Extraction), **Phase 2** (Mechanical Codemods & DB/Cache Adapters), **Phase 3** (Typed DTOs & Approved Fixes), and **Phase 4** (Cutover & CI/Container Hardening)—paired with topologically ordered PR tickets enriched with deterministic `MigrationFacts` (`refactoring_waves`, `cycle_cuts`, `implicit_contracts`, `boundary_touchpoints`, and `mechanical_codemods`).

---

## 4. 9-Target Multi-Language Benchmark Matrix

To validate scoring calibration across clean production architectures, mid-tier services, and severely degraded legacy codebases, `pni501` maintains nine end-to-end benchmark repositories under `examples/{python,java,php}/` along with their committed `ScoreResult` JSONs and compiled A4 PDF reports under `reports/{python,java,php}/`.

```drawlib align=center code=fold file=benchmark_score_heatmap.png caption="Ground-Truth 7-Axis Health Scores Across All 9 Python, Java, and PHP Benchmark Targets"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=176, height=90, dpi=150)

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
    axis_text_style=Styles.DarkBold.patch(text_size=10.0),
    value_text_style=Styles.DarkBold.patch(text_size=10.5),
    width=144.0,
    height=62.0,
    title="9-Target Benchmark Matrix Across the 7 PNI Engineering Axes (0-100)",
    title_style=Styles.DarkBold.patch(text_size=12.5),
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

chart.draw(xy=(28.0, 21.0))
chart.draw_colorbar(
    xy=(80.0, 6.5),
    text_style=Styles.Dark.patch(text_size=10.0),
    length=60.0,
    thickness=2.4,
    num_ticks=6,
    value_format="{:.0f}",
    label="Category Health Score (0 = Critical Debt, 100 = Exemplary)",
)

save()
```

### 4.1 Ground-Truth Audit Scores Across Clean, Mid-Tier, and Legacy Targets

The nine benchmark targets span three Grade `S`/`A` reference implementations, two realistic mid-tier Grade `B` repositories (where `pni501` surfaces container base-image CVEs, unauthenticated Actuator/API routes, or branch-coverage gaps despite clean code structure), and four severely degraded Grade `D` legacy applications:

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

Next, see [Drawlib Visual Reporter](drawlib_reporter.md) for how `pni501` compiles `ScoreResult` and `MigrationPlanResult` into 7-chapter vector PDF reports, or [Supported 6 Languages](../05_languages_and_reference/supported_languages.md) for language-specific analyzer details.
