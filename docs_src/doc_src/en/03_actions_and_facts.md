# 3. Two-Tier Action System & Deterministic Fact Extraction

To eliminate LLM guesswork over code metrics, dependency versions, runtime test pass rates, CVE counts, and refactoring blast radius, `pni501` decouples **declarative workflow authoring** from **execution mechanics**. Project workflows compose `21` language-aware YAML building blocks that flatten into **`12` canonical `PrimitiveType`s**—pairing `6` auto-executed Python analyzers with `6` schema-enforced, repository-grounded AI and gate primitives.

```drawlib align=center code=fold file=two_tier_action_expansion.png caption="Two-Tier Action Expansion: 21 Cascading Composite Actions Flatten into 6 Deterministic Python Analyzers and 6 Grounded AI/Gate Primitives"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=162, height=96, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=10.0),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.6),
)

wf_node = diag.add(
    Node(
        "Workflow YAML\n(uses / action / with)",
        width=33.0,
        height=19.0,
        icon=PhosphorIcon.FILE_CODE,
        icon_size=6.0,
    ),
    xy=(19.0, 69.0),
)

mgr_node = diag.add(
    Node(
        "Action Manager\n(Cascade & Flatten)",
        width=33.0,
        height=19.0,
        icon=PhosphorIcon.STACK,
        icon_size=6.0,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.6),
    ),
    xy=(19.0, 27.0),
)

det_group = diag.add(
    NodeGroup(
        title="6 Deterministic Auto-Executed Python Primitives",
        width=114.0,
        height=43.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(44.0, 50.0),
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
    xy=(44.0, 3.0),
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
mgr_node.fork([det_group, ai_group], at_x=39.8, style=Styles.PrimaryBold)
diag.connect(d3, facts_node, routing="orthogonal", style=Styles.SecondaryBold)
diag.connect(d6, facts_node, routing="orthogonal", style=Styles.SecondaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

---

## 3.1 Two-Tier Action Expansion (`21` Composite Actions -> `12` Primitives)

Workflow definitions in `.pni/workflows/*.yaml` (`WorkflowDefinition`) stay concise because `src/pni/_actions/base_model.py` separates reusable audit bundles from low-level execution steps:

1. **Tier 1 — Composite Actions (`CompositeActionDefinition`)**: Domain-focused YAML specifications invoked via `uses: <action_id>`. Each composite action bundles default `rules`, ordered `CompositePrimitiveSpec` entries, default `with` parameters, and domain-specific prompt instructions.
2. **Tier 2 — Canonical Primitives (`PrimitiveStep` & `PrimitiveType`)**: The `12` execution primitives referenced inside composite YAMLs or directly in a workflow step via `action: <primitive_type>`. Every stateful workflow run and ad-hoc `run-action` call operates over flattened `PrimitiveStep` instances.

### Built-In Catalog of `21` Composite YAML Actions

`src/pni/_actions/` packages **`21` composite YAML actions** across `common/` (`12`) and `python/`, `java/`, `php/` (`3` each):

- **`12` Universal Actions (`common/`)**:
  - **`architecture_analysis`**: Expands into three sequential `record_architecture` steps (`aspect: purpose_and_stack`, `layers_and_modules`, `flows_and_state`) under `common/architecture`.
  - **Dynamic & Security Audits**: `container_runtime_audit` (`run_check` + `ai_interpret`), `security_vulnerability_audit` (`security_scan` + `ai_interpret`), and `web_penetration_audit` (`web_pentest` + `ai_interpret`).
  - **Archetype & Governance Audits**: `supply_chain_audit`, `cli_guidelines_audit`, `library_hygiene_audit`, and `service_readiness_audit` (specialized `ai_interpret` steps bound to OpenSSF supply-chain, CLI, library, 12-Factor, and SRE Production Readiness rules).
  - **Migration Planning**: `migration_proposal` (`migration_analyze` + `ai_interpret` + `emit_migration_plan` under `common/migration_planning`).
  - **Synthesis & Visual Reporting**: `emit_score` (`emit_score`), `write_drawlib_report` (`write_drawlib_report` with `report_kind: audit`), and `write_migration_report` (`write_drawlib_report` with `report_kind: migration`).
- **`9` Language-Scoped Actions (`python/`, `java/`, `php/`)**:
  - **`repo_structure_audit`** (one per language): Pairs `project_inspect` + `ai_interpret` with `<lang>/dependencies` (plus `php/modern_stack` for PHP) and universal supply-chain/documentation/Git/security rules.
  - **`python_ast_audit` / `java_ast_audit` / `php_ast_audit`**: Pairs `ast_analyze` + `ai_interpret` with `<lang>/code_quality`, `<lang>/typing`, modernization rules, and framework standards (`spring_boot`, `laravel`, `wordpress`).
  - **`python_test_audit` / `java_test_audit` / `php_test_audit`**: Evaluates test isolation, mirror layout, and assertion quality under `<lang>/testing`.

### Cascade Flattening & Three-Layer Merging (`_actions/manager.py`)

When `normalize_workflow_steps()` (`src/pni/_workflows/manager.py`) expands a workflow, `expand_composite_action()` resolves `uses:` via `local (.pni/actions/) > <active_lang>/ > common/` and merges three configuration layers:

- **Parameters (`params`)**: Workflow-level target/output paths (`workflow_id`, `target_root`, `source_targets`, `test_targets`, `doc_targets`, `facts_path`, `score_path`, `output_dir`) merge with the workflow step's `with:` block, overriding primitive-level `with:` defaults (`{**prim.with_params, **override_params}`).
- **Rules (`rules`)**: Composite rules, workflow-step `rules:` additions, and primitive-level rules are concatenated and deduplicated in declaration order (`dict.fromkeys`).
- **Provenance IDs**: Workflow-step `prompt:` overrides append cleanly below base prompts, producing compound step IDs (`{step_id}__{idx}_{prim.type.value}`) with `source_action=comp.id` before SQLite assigns sequential action IDs (`act-01`, `act-02`, ...).

---

## 3.2 Six Deterministic Python Fact Extractors

Whenever `pni workflows get-action` (or `push-action`) reaches a deterministic primitive, `_execute_deterministic_step_if_needed()` runs the corresponding Python analyzer **once**, stores its JSON in `action_runs.deterministic_output_json` inside `.pni/cache/workflow_state.db`, and updates `.pni/cache/<workflow_id>/facts.json` (`WorkflowFactsBundle`).

### 1. Repository, Supply-Chain & Governance Inspector (`project_inspect` -> `ProjectFacts`)

Implemented in `src/pni/_actions/project_inspect.py` and `src/pni/_actions/_repo_governance.py`, `run_project_inspect()` extracts language-agnostic structural, dependency, documentation, and OpenSSF supply-chain signals without invoking external package managers:

- **Multi-Language Manifests & Lockfiles**: Parses `pyproject.toml` / `setup.py` / `requirements.txt` (Python), `pom.xml` / `build.gradle*` / Gradle version catalogs (Java), and `composer.json` / WordPress plugin & theme headers (PHP). Detects `lockfiles_found` (`uv.lock`, `poetry.lock`, `gradle.lockfile`, `composer.lock`, etc.), `unpinned_dependencies`, `detected_frameworks`, `runtime_types` (`["library"]`, `["cli"]`, `["cli", "library"]`, `["web_api"]`, `["worker"]`), `legacy_language_findings`, and `tooling_modernization_issues`.
- **OpenSSF Supply-Chain & Repo Governance (`_repo_governance.py`)**: Audits `has_license`, `has_security_policy` (`SECURITY.md`), `has_dependency_automation` (Dependabot / Renovate), GitHub Actions `ci_supply_chain_issues` (mutable `@main`/`@master` action refs, missing `permissions:` blocks, fat inline bash scripts), `committed_secret_files` (`.env`, `.pem`, `.key`, service-account JSONs), Diátaxis `readme_headings` / `docs_inventory`, and static `container_hygiene_issues` (`:latest` base tags, root `USER`).

### 2. Multi-Language CST/AST Static Analyzer (`ast_analyze` -> `AstFacts`)

Implemented in `src/pni/_actions/ast_analyze/`, `run_ast_analyze()` parses each target file **once** via `ast-grep-py` into an immutable `ParsedUnit` (`SgNode` CST) without importing or executing untrusted code, then runs **9 modular checkers** (`ast_analyze/base/` with concrete `python/`, `java/`, and `php/` implementations):

1. **Import Hygiene (`imports.py`)**: `import_hygiene_coverage_pct`, `unsorted_imports`, `wildcard_imports`, and `late_imports`.
2. **Type Safety (`typing.py`)**: `type_safety_coverage_pct`, missing parameter/return/field annotations (`type_safety_issues`), `Any`/raw-generic/`mixed` usages (`weak_type_usages`), and `unscoped_type_ignores`.
3. **API Documentation (`docs.py`)**: `docstring_coverage_pct`, `missing_docstrings`, `empty_docstrings`, and parameter/return `doc_signature_mismatches` across PEP 257, Javadoc, and PHPDoc.
4. **Code Quality & Inventory (`quality.py`)**: Exact `total_files`, `total_loc`, `total_classes`, `total_functions`, per-file `module_inventory` (`public_types`, `public_callables`), `complex_functions` (`> 50` lines, `> 7` branches, or cognitive complexity `> 15`), `excessive_parameters` (`> 6`), `global_state_usages`, and `bug_risk_idioms`.
5. **Dependencies & Boundaries (`dependencies.py`)**: `internal_import_graph`, Tarjan SCC `circular_dependencies`, static-only `type_checking_cycles`, `unused_dependencies`, `undeclared_dependencies`, and architectural `boundary_violations`.
6. **Test Suite Health (`testing.py`)**: `test_functions_count`, `module_test_coverage_pct`, `assertion_free_tests`, and `conftest.py` hook-aware `test_harness_notes`.
7. **Framework & Version Compatibility (`frameworks.py`, `version_compat.py`)**: `framework_issues`, `modernization_hints`, and `language_version_mismatches` against declared runtime constraints.
8. **Operational & 12-Factor Signals (`operational.py`)**: `missing_io_timeouts`, `scattered_env_access`, `unstructured_logging`, and AST-level `hardcoded_secrets`.
9. **Security Sinks & Attack Surface (`security.py`)**: CWE-classified `dangerous_sinks` (`sql_injection`, `xss`, `command_injection`, `unsafe_deserialization`, `code_execution`, etc.) and extracted HTTP routes (`api_endpoints` with `http_method`, `path`, `handler`, and `auth_mechanisms`).

### 3. Isolated Container Runtime Verification (`run_check` -> `RuntimeFacts`)

Implemented in `src/pni/_actions/runtime_check/`, `run_runtime_check()` verifies dynamic buildability, test execution, coverage, and boot health inside an isolated Docker or Podman container (persisting `.pni/cache/<workflow_id>/runtime/runtime_facts.json`):

- **Harness Materialization & Image Build**: Selects the matching `.pni/dockerfiles/` template (`uv`, `poetry`, `pip`, `maven`, `gradle`, `composer`, `raw`) via `selector.py`, validates any project `Dockerfile`, and builds the test harness image.
- **Offline Unit Tests & Measured Coverage**: Executes the test suite with **`--network=none`** (with optional `pre_test_cmd` and `pytest_extra_args`) so external network calls fail deterministically, parses JUnit XML (`TestExecutionResult` + `FailedTestCase` excerpts), and extracts line/branch coverage (`CoverageResult` + `lowest_covered_modules`) from `pytest-cov` JSON, JaCoCo XML, or Clover XML.
- **Archetype-Aware Smoke Probe (`smoke.py`)**: Runs a container startup probe tailored to `runtime_types`—`library` (clean module import), `cli` (`--help` exit `0`), `cli+library` (combined `--help` + SDK import), or `web_api` (boot + loopback HTTP probe)—classifying failures into `BootFailureKind`.

### 4. Socketless Containerized Vulnerability & Secret Scan (`security_scan` -> `SecurityFacts`)

Implemented in `src/pni/_actions/security_scan/`, `run_security_scan()` executes Aqua **Trivy** (`ghcr.io/aquasecurity/trivy`) inside a socketless container mounting a shared vulnerability DB cache at `.pni/cache/trivy-cache/` (persisting `.pni/cache/<workflow_id>/security/security_facts.json`):

- **Dual-Surface Scanning**: Scans both the repository filesystem (`scan_filesystem`) and an exported `docker save` / `podman save` tarball of the resolved container image (`scan_resolved_image`) without mounting `/var/run/docker.sock`.
- **App vs. OS CVE Separation & Redacted Secrets**: Splits deduplicated CVEs into `app_vuln_counts` (language lockfiles/manifests, annotating `is_unpinned_specifier` range matches) and `os_vuln_counts` (base image OS packages), alongside IaC/Dockerfile `misconfigurations` and redacted `SecretFindingItem` leaks.

### 5. Live Loopback Web Penetration Testing (`web_pentest` -> `PentestFacts`)

Implemented in `src/pni/_actions/pentest/`, `run_web_pentest()` performs dynamic black-box HTTP security probing against web applications (persisting `.pni/cache/<workflow_id>/pentest/pentest_facts.json`):

- **Fail-Closed Explicit Probe Suite**: Workflows containing `web_pentest` fail closed at `pni workflows start` unless `.pni/pentests/<target>/` contains `conftest.py` and `test_*.py` (scaffolded via `pni pentests init`, which combines baseline HTTP header/CORS/method checks with AST-derived `test_target_surface.py` route probes).
- **Loopback Container Execution**: Boots the target web server bound strictly to host loopback (`127.0.0.1:<port>`), runs `pytest + httpx` against the live container (or an explicit `--base-url`), tears down the container cleanly, and parses JUnit XML failures into CWE-tagged `PentestFindingItem` records.

### 6. Graph- & Contract-Driven Migration Intelligence (`migration_analyze` -> `MigrationFacts`)

Implemented in `src/pni/_actions/migration_analyze/`, `run_migration_analyze()` powers `category: migration` workflows anchored to a completed `based_on` audit run (persisting `.pni/cache/<workflow_id>/migration_facts.json`):

- **Tarjan SCC Cycle Cuts & Topological Waves `1..4` (`graph_waves.py`)**: Detects strongly connected components in `internal_import_graph`, recommends minimal `cycle_cuts` (`CycleCutSuggestion`), and partitions modules from leaf DTOs/utilities (`Wave 1`) through domain/services (`Waves 2..3`) to entrypoints (`Wave 4`).
- **Implicit Contracts, Touchpoints & `DEC-XX` Candidates**: Reconstructs untyped request/response keys (`implicit_contracts` in `contracts.py`) and `env_contracts`, locates `in_memory_state`, `persistence_db`, and `external_http_rpc` couplings (`boundary_touchpoints` in `touchpoints.py`), matches automated codemods (`ruff`, `openrewrite`, `rector` in `codemods.py`), and flags ambiguous legacy behaviors as `DEC-XX` `spec_vs_bug_candidates` (`ambiguities.py`).

---

## 3.3 Complete Catalog of the `12` Canonical Primitives & Grounding Gates

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
        "Runs 9 ast-grep-py checkers (Py/Java/PHP)\n-> .pni/cache/<wf>/facts.json",
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

### Grounding & Synthesis Mechanics Across the Cognitive Primitives

- **Aspect-Separated Architecture Comprehension (`record_architecture` -> `architecture.json`)**: Parameterized via `with: {aspect: purpose_and_stack | layers_and_modules | flows_and_state}`, `record_architecture` splits codebase comprehension into three focused schemas (`SystemProfile`, `StructureMap`, `ExecutionFlowMap`). `_validate_and_persist_architecture()` checks every `layers[].paths`, `modules[].path`, `entry_points`, and `involved_files` entry against `AstFacts.module_inventory` and the workspace before persisting `.pni/cache/<workflow_id>/architecture.json`.
- **Per-Rule Compliance & Grounded Reasoning (`ai_interpret` -> `InterpretationInput`)**: Requires a `0..100` `step_score`, explicit `RuleCheckResult` verdicts (`pass`, `warn`, `fail`, `not_applicable`), grounded `findings`, and `P0`–`P2` `action_items`. On push, `engine.py` verifies every `file_path` and `target_files` entry and invokes `normalize_step_rule_checks()` (`aggregator.py`) so every active rule on the step is guaranteed a stamped compliance verdict.
- **Deterministic Digest & Score Stamping (`emit_score` -> `<target>_score.json`)**: `_enrich_score_result()` runs `compile_workflow_digest()` (`src/pni/_workflows/aggregator.py`) to deduplicate findings, group co-located violations into `consolidated_findings`, compute per-file `module_hotspots` (`0.0..1.0` risk density), derive canonical `S`–`D` `grade`, attach `RuntimeFacts` / `SecurityFacts` / `PentestFacts`, and overwrite `metrics_snapshot` directly from programmatic facts before writing `reports/<target>_score.json`.
- **Grounded Migration Plan Synthesis (`emit_migration_plan` -> `<target>_migration_plan.json`)**: `validate_and_persist_migration_plan()` (`_migration_engine.py`) validates `MigrationPlanResult` (`transformation_axes`, `target_architecture`, `component_mappings`, `phases`, `pr_backlog`, `decision_log`), verifies all referenced As-Is source paths exist in the repository, attaches deterministic `MigrationFacts`, and writes `reports/<target>_migration_plan.json`.
- **Blueprint-Guided Visual Report Gate (`write_drawlib_report` -> `ReportCompletionInput`)**: `render_drawlib_report_guide()` pre-computes `.pni/cache/<workflow_id>/blueprint.json` (or `migration_blueprint.json`) for the 7-chapter Drawlib `doc` report (`00_cover.md` .. `06_*.md`), and `_validate_report_completion()` verifies on disk that every file listed in `ReportCompletionInput.generated_files` exists inside the workspace with `st_size > 0`.
