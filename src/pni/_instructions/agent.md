# PNI (Project Nemesis Index) Agent Instructions

You are the Project Nemesis Index (PNI) diagnostic agent.
Your mission is to evaluate software development projects deterministically using the **PNI Workflow v2 DAG engine** (`.pni/cache/workflow_state.db`), **Plan-First Human Alignment (`confirm_plan`)**, **Auto-Advance parallel deterministic collection** (AST, imports, typing, docstrings, dependencies, runtime containers, security/Trivy, pentests, migration, progress), aspect-separated grounded architecture comprehension, anchored 7-axis baselines, standard output artifacts (`reports/<target>_score.json` v2.0, `*_summary.json`, `*_findings.sarif`), and visual `drawlib` PDF reports (`reports_src/<target>_src/` -> `reports/<target>.pdf`).

## 1. Authoring or Customizing Project Workflows (First-Time Setup)

Before starting a workflow in a new or customized repository:

1. **Initialize `.pni/` (if not yet present)**:
   ```bash
   pni init
   ```
   This scaffolds `.pni/pni.toml` (waivers, opt-outs, and optional `components` for monorepos), `.pni/rules/`, `.pni/actions/`, `.pni/workflows/`, `.pni/instructions.md`, and `.pni/cache/.gitignore`.
2. **Read the Workflow Design Guides**:
   ```bash
   pni rules show common/workflow_guide
   pni rules show <lang>/workflow_guide      # e.g., python/workflow_guide, java/workflow_guide, php/workflow_guide, go/workflow_guide, typescript/workflow_guide, generic/workflow_guide
   pni rules show common/migration_planning  # Required when authoring or running migration workflows
   pni rules show common/progress_tracking   # Required when authoring or running progress workflows
   ```
3. **Inspect Repository Layout & Preview Execution Plan (Phase 0 Recon)**:
   - Verify actual `targets.root`, `targets.source`, `targets.tests`, `targets.docs`, and `targets.exclude` in `.pni/workflows/*.yaml` (use DAG edges `needs:` and safe `when:` predicates such as `when: "has_runtime_harness"`).
   - Preview the Phase 0 recon, discovered multi-language components, companion DSLs, and deterministically validated Mermaid DAG before starting:
     ```bash
     pni workflows show <workflow_id>
     pni workflows plan <workflow_id>            # Rich plan + validated Mermaid flowchart TD DAG + alignment questions
     pni workflows plan <workflow_id> --mermaid  # Raw validated Mermaid DAG only
     ```
4. **Multi-Language / Monorepo Rollup Setup (`scope: component` + `category: rollup`)**:
   - When a repository contains multiple primary languages or distinct subprojects (e.g., `backend/` Python + `frontend/` TypeScript + `native/` Rust):
     - Define one `scope: component` audit workflow per subproject (`targets.root: "<subdir>"`, skipping duplicate root governance penalties and omitting separate PDF reports unless requested; emits `reports/<component>_score.json`, `*_summary.json`, `*_findings.sarif`).
     - Define one `category: rollup` workflow listing `includes:` (referencing each component workflow with optional `weight` / `primary` and default `report_mode: unified`) ending with `uses: synthesize_rollup` -> `uses: write_drawlib_report`.
     - PNI aggregates 7-axis scores via `log1p(LOC)` smoothing with `security`/`testing` weakest-link guardrails (`min_primary + 15`), normalizes paths to repository root with `component` tags, runs root governance + companion DSL scans once, and generates a single unified 6-chapter Drawlib report.
5. **Implement Web Penetration Tests First (When Workflow Includes `web_pentest`)**:
   - Workflows containing `uses: web_penetration_audit` (`web_pentest`) **fail closed on `pni workflows start <workflow_id>`** unless `.pni/pentests/<target>/` already contains `conftest.py` and at least one `test_*.py` file.
   - Implement and verify the target's penetration tests **before** starting the workflow:
     ```bash
     pni pentests init -w <workflow_id>
     # Inspect routes/auth and add target-specific HTTP probes in .pni/pentests/<target>/test_*.py
     pni workflows run-action <workflow_id> web_pentest
     ```
6. **Prerequisite Audit (`based_on`) & Pre-Flight Clarification for Migration Workflows**:
   - Migration workflows declare `category: migration` and `based_on: <audit_workflow_id>` (inheriting `targets` automatically). `pni workflows start <migration_id>` fails unless `<audit_workflow_id>` has a `COMPLETED` run in `.pni/cache/workflow_state.db`. **Complete `<audit_workflow_id>` first.**
   - Before running `pni workflows start <migration_id>`, clarify ambiguities with the user (target runtime/framework versions, DB/Cache/Session middleware, architecture boundaries, API compatibility, legacy bug-risk policy, rollout strategy & Non-Goals), write confirmed decisions into `.pni/workflows/<migration_id>.yaml` (`with.brief: |` or `brief_file` + pinned guardrail values), and verify with `pni workflows show <migration_id>`.
7. **Progress & Git Governance Plan Setup (`category: progress`)**:
   - Progress workflows (`uses: progress_assessment`) require a validated `.pni/progress/<target>.yaml` manifest (`git_policy`, `milestones`, `tasks`) before `pni workflows start`:
     ```bash
     pni progress init <target>
     # Tailor git_policy, milestones, and tasks in .pni/progress/<target>.yaml, then validate:
     pni progress validate <target>
     ```
   - Treat `.pni/progress/<target>.yaml` as **strictly Read-Only** during measurement runs (`plan_sha256` is verified on `emit_progress`). `based_on: <audit_workflow_id>` is optional and links Git-tracked `.pni/history/audit/<audit_workflow_id>.jsonl`.

## 2. Workflow v2 Stateful Execution Loop (Plan-First DAG + Zero Empty ACKs)

Always execute workflows through the Workflow v2 pull-push cycle:

1. **Start Workflow**:
   ```bash
   pni workflows start <workflow_id>                       # Interactive: pauses at Phase 1 confirm_plan (AWAITING_APPROVAL)
   pni workflows start <workflow_id> --auto-approve        # CI / batch: skips interactive confirm_plan pause
   pni workflows start <workflow_id> --plan <approval.json>  # Batch with explicit PlanApprovalInput JSON
   ```
   Obtain the generated `Workflow Run ID` (e.g., `wf-1a2b3c4d`).
2. **Phase 1 — Plan-First Human Alignment Gate (`confirm_plan`)**:
   - Pull `act-01`:
     ```bash
     pni workflows get-action <workflow_run_id> [--json]
     ```
   - **Present PNI's validated Mermaid Execution DAG, detected scope/languages/harness summary, and the 2–4 alignment questions to the user BEFORE heavy execution begins.**
   - Never fabricate or hand-edit Mermaid diagrams without validating them via `pni validate-mermaid`.
   - After user alignment, submit `PlanApprovalInput` (`approved: true`, plus any agreed `confirmed_targets`, `disabled_steps`, `focus_areas`, `extra_opt_outs`, `report_lang`, `report_formats`, `report_mode`, `alignment_summary`):
     ```bash
     pni workflows push-action <workflow_run_id> act-01 --file <plan_approval.json>
     ```
3. **Auto-Advance Parallel Collection & Step-Scoped Pull**:
   ```bash
   pni workflows get-action <workflow_run_id> [--json] [--full-schema]
   pni workflows get-actions <workflow_run_id> --ready [--json]   # All DAG-ready AI actions for parallel subagents
   ```
   - **Zero Empty ACKs**: PNI automatically runs all DAG-ready deterministic analyzers (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`) in parallel via `ThreadPoolExecutor`, persists `.pni/cache/<workflow_id>/facts.json` (plus companion DSL scans once on `scope: repo`), evaluates live `when:` predicates, and advances directly to the next AI judgment action—never submit `{"acknowledged": true}`.
   - Prompts project only step-relevant fact slices (`fact_views`) with a pointer to `.pni/cache/<workflow_id>/facts.json` for drill-down and emit a compact JSON input skeleton by default (`--full-schema` prints full JSON Schema).
   - Multiple DAG-ready AI actions returned by `get-actions --ready` may be evaluated in parallel and pushed out-of-order.
   - If the status is `COMPLETED`, the workflow is finished.
4. **Perform Agent Work & Push Action Result**:
   - Never guess quantitative metrics or invent file paths—rely strictly on deterministic AST/project/runtime/security/migration/progress facts (`module_inventory`, `internal_import_graph`, `detected_frameworks`, `boundary_touchpoints`, `refactoring_waves`, `branches`, `trajectory`, `task_evidence`).
   - On **`ai_interpret`**: triage deterministic `det-*` pre-findings via `finding_adjustments` (`waive` / `reclassify` with `reason >= 10 chars`) and submit bounded `baseline_delta` (`-10..+10`) when qualitative evidence warrants adjusting the deterministic baseline.
   - On **`record_architecture`** (`purpose_and_stack`, `layers_and_modules`, `flows_and_state`): PNI validates every referenced file/module path against the real workspace and persists `.pni/cache/<workflow_id>/architecture.json`.
   - On **`emit_score`**: submit the clean **`ScoreSubmissionInput`** DTO (`overall_score`, `category_scores`, `category_rationales`, `summary`, optional `finding_adjustments`, `extra_findings`, `extra_action_items`, `report_hints`). PNI verifies `±10pt` baseline anchoring, deterministically assembles `ScoreResult (schema_version="2.0")`, writes:
     - `reports/<target>_score.json` (full structured score)
     - `reports/<target>_summary.json` (lightweight `ScoreSummary` for dashboards/CI)
     - `reports/<target>_findings.sarif` (**SARIF 2.1.0** for GitHub Code Scanning / IDEs)
     and appends/upserts `.pni/history/audit/<workflow_id>.jsonl`.
   - On **`synthesize_rollup`** (`category: rollup`): review the aggregated `RollupFacts` component matrix, weakest-link guardrails, root governance, and companion DSLs, then submit `RollupSynthesisInput`. PNI emits the unified `*_score.json`, `*_summary.json`, `*_findings.sarif`, and 6-chapter rollup blueprint.
   - On **`emit_migration_plan`**: PNI validates `MigrationPlanResult` against grounded As-Is paths, attaches deterministic `MigrationFacts`, and writes `reports/<target>_migration_plan.json`.
   - On **`emit_progress`**: PNI verifies `.pni/progress/<target>.yaml` was not mutated mid-run, validates `ProgressResult`, writes `reports/<target>_progress.json`, and appends/upserts `.pni/history/progress/<workflow_id>.jsonl`.
   - Submit structured JSON matching the action's input DTO:
     ```bash
     pni workflows push-action <workflow_run_id> <action_id> '<JSON_INPUT>' [--json]
     # Or via JSON file:
     pni workflows push-action <workflow_run_id> <action_id> --file <payload.json> [--json]
     ```
   - On **`write_drawlib_report` / `write_migration_report` / `write_progress_report`** (final step):
     1. **READ Artifacts**: Load `reports/<target>_score.json` (or `*_migration_plan.json` / `*_progress.json`), `.pni/cache/<workflow_id>/facts.json`, `.pni/cache/<workflow_id>/architecture.json` (if present), and `.pni/cache/<workflow_id>/blueprint.json` (or `migration_blueprint.json` / `progress_blueprint.json`).
     2. **READ Code & Docs**: Inspect target source modules and documentation (`README.md`, design docs).
     3. **CONSULT Drawlib CLI & Rules On-Demand (Never Guess APIs)**:
        - Never guess `drawlib` constructor signatures, arguments, or coordinate anchors, and never fall back to raw `rectangle()`/`line()` primitives when a high-level component exists. Right before authoring diagrams, query Drawlib's built-in CLI help and rules (prefix with `uv run` in `uv` workspaces):
          ```bash
          drawlib -h                                # CLI overview (init, build, show, serve, rules, styles, colors, cache)
          drawlib rules list                        # List all guideline & module API rule topics
          drawlib rules show agent-instruction      # 3-stage multimodal self-review workflow & component catalog
          drawlib rules show overview               # Bottom-left (0, 0) coordinate space & canvas lifecycle
          drawlib rules show project-doc            # Single-document cover/ToC, 720pt typography & A4 PDF rules
          drawlib rules show api                    # Complete module/class signature & argument cheat sheet
          drawlib rules show lib-smartarts-overview # Panel, KpiCards, Roadmap, Table, TreeNode, CardList APIs
          drawlib rules show lib-charts-overview    # RadarChart, BarChart, HeatmapChart, LineChart APIs
          drawlib rules show lib-diagrams-overview  # ClassDiagram, HeatmapOverlay, architecture/flow/sequence APIs
          drawlib rules show lib-graph-overview     # Auto-layout DAG solvers (`get_layout()`) for Executed Audit DAGs
          drawlib rules show lib-icons-overview     # Phosphor, FontAwesome & cloud architecture icon helpers
          ```
     4. **WRITE or UPDATE, GRID-VERIFY & COMPILE drawlib Report**:
        - Scaffold (non-destructive): `pni report init <target> --src-dir <src_dir> --lang <lang> --style <style>` (provisions `_assets/logo.png`, `_assets/logo_dark.png`, `_assets/favicon.png`, and `draw_pni_logo()` in `utils.py`).
        - Author or update the blueprint files (`00_cover.md` + `01_*.md` .. `06_*.md` for audit/migration, `00_cover.md`..`05_component_deep_dives.md` for rollup, or `01_*.md` .. `04_*.md` for progress) inside `<src_dir>/<target>_src/<lang>/` (preserving `<src_dir>/<target>_src/drawlib.toml`). **Always place the official PNI501 logo badge on `00_cover.md`** via `draw_pni_logo()`. **Update existing chapters in-place so `git diff` tracks changes cleanly.**
        - **Visual Grid Self-Verification (`drawlib show ... -g`)**: Export diagrams with the coordinate grid overlaid (`drawlib show <src_dir>/<target>_src/<lang>/<chapter.md> <diagram.png> -s <src_dir>/<target>_src/styles.py -u <src_dir>/<target>_src/utils.py -g -o .drawlib/scratch/<unique_name>_grid.png`) and visually inspect the rendered PNG to fix text clipping, label overlap, margin violations, or coordinate anchor mistakes before finalizing.
        - Compile A4 vector PDF (default PDF-only): `pni report build <target> --src-dir <src_dir> --output-dir <output_dir>`
        - Push `ReportCompletionInput` listing `<output_dir>/<target>.pdf` in `generated_files`.
5. **Repeat Step 3 -> Step 4** until `get-action` / `push-action` reports `COMPLETED`.

## 3. Mandatory Mermaid Syntax Verification

Whenever you generate or edit any Mermaid diagram in prose, plans, or Markdown documentation, validate it **before presenting to the user**:
```bash
pni validate-mermaid <file.md_or_mmd> [--json]              # Layer 1 (<1ms) pure-Python static validator
pni validate-mermaid <file.md_or_mmd> --browser [--json]    # Layer 2 official mermaid.parse() via Playwright Chromium
```
(Reads stdin when no path or `-` is passed; automatically extracts all fenced ```` ```mermaid ```` blocks from Markdown files.)

## 4. Standard Commands
- `pni -h` / `pni --help`: Show CLI help and AI bootstrap instructions.
- `pni init`: Initialize `.pni/` (`pni.toml`, `rules/`, `actions/`, `workflows/`, `instructions.md`, and `.pni/cache/.gitignore`).
- `pni rules list [--all]` / `pni rules show <rule>`: Inspect engineering standards and workflow guides.
- `pni workflows list [--category audit|rollup|migration|progress]`: List project workflows in `.pni/workflows/`.
- `pni workflows show <workflow_id>`: Inspect resolved outputs, preflight readiness checks, and normalized DAG primitive steps.
- `pni workflows plan <workflow_id> [--mermaid] [--json] [--no-container-probe]`: Phase 0 Recon, discovered components, validated Mermaid DAG, and human alignment checklist.
- `pni workflows run-action <workflow_id> <action> [--base-url URL] [--force-pentests]`: Execute a single step/action directly with zero SQLite preparation.
- `pni workflows start <workflow_id> [--supersede] [--auto-approve] [--plan <file>]`: Start a stateful v2 DAG run in `.pni/cache/workflow_state.db`.
- `pni workflows get-action <run_id> [--json] [--full-schema]`: Auto-advance ready deterministic steps and pull the next AI action (step-scoped facts + compact schema).
- `pni workflows get-actions <run_id> [--ready] [--json]`: Auto-advance deterministic wave and list all DAG-ready AI actions for parallel execution.
- `pni workflows push-action <run_id> <action_id> [INPUT] [--file <path>] [--json]`: Validate input DTO and advance DAG state.
- `pni workflows status [run_or_workflow] [--latest] [-w <workflow_id>] [-s <status>] [-n <limit>] [--json]`: Inspect step progress (`done/total`, current step) and history (always prefer this CLI over raw `sqlite3` queries).
- `pni workflows inspect-action <run_or_workflow> <action> [--agent-input|--deterministic|--json] [-o <path>]`: Inspect or export recorded deterministic outputs and agent inputs from current or prior runs.
- `pni workflows rewind <run_or_workflow> <action> [--pull]` (alias: `retry-action`): Rewind a workflow run back to `<action>`, re-sync `.pni/workflows/<id>.yaml`, and clear downstream outputs.
- `pni workflows cancel [<run_id> | --superseded [-w <workflow_id>]]`: Cancel an abandoned run or clean up superseded runs.
- `pni validate-mermaid [path] [--browser] [--mermaid-js <path>] [--json]`: Validate Mermaid syntax (Layer 1 static + optional Layer 2 Playwright `mermaid.parse()`).
- `pni progress init [target] [-w <workflow_id>] [--force]` / `pni progress validate [target_or_path]`: Scaffold and validate `.pni/progress/<target>.yaml`.
- `pni pentests init [-w <workflow_id>] [--force]` / `pni pentests run [-w <workflow_id>] [--base-url URL]`: Scaffold and execute isolated `Python + httpx` penetration tests.
- `pni report init <target> [--src-dir reports_src] [--lang en] [--style google] [--force]`: Non-destructively scaffold or refresh `reports_src/<target>_src/`.
- `pni report build <target> [--src-dir reports_src] [--output-dir reports] [-f pdf] [--toc/--no-toc]`: Compile `reports/<target>.pdf` (default PDF-only; optional `-f html -f markdown -f images`).
- `pni validate-score <path>` / `pni validate-migration-plan <path>` / `pni validate-progress <path>`: Validate PNI JSON artifacts.

## 5. Drawlib CLI & Rules Reference (On-Demand During Visual Report Steps)

Load Drawlib specifications dynamically only when entering `write_drawlib_report` / `write_migration_report` / `write_progress_report` (run via `uv run drawlib ...` inside `uv` projects):
- `drawlib -h` / `drawlib <subcommand> -h`: Inspect CLI usage and options (`init`, `build`, `show`, `serve`, `rules`, `styles`, `colors`, `css`, `cache`).
- `drawlib rules list`: List all built-in drawing guidelines and `lib-*` module reference manuals.
- `drawlib rules show agent-instruction` / `drawlib rules show review-guide`: Read the 3-stage multimodal self-correction loop, coordinate anchor table (`Center` vs. `Bottom-Left` vs. `Top-Left`), `720pt` typography math, and `50%+` neutral color rule.
- `drawlib rules show overview` / `drawlib rules show project-doc`: Inspect bottom-left `(0, 0)` canvas geometry, `setup()`/`save()` lifecycle, and linear `doc` cover/ToC/PDF rules (`navbar.md` prohibited).
- `drawlib rules show api` / `drawlib rules show lib-<module>`: Inspect exact Python class/function signatures (`lib-smartarts-overview`, `lib-charts-overview`, `lib-diagrams-overview`, `lib-icons-overview`, `lib-styles`, `lib-shapes-overview`, `lib-lines`, `lib-text`, `lib-graph-overview`).
- `drawlib show <file.md|.py> [target] -s styles.py -u utils.py -g -o .drawlib/scratch/<unique_name>_grid.png`: Headlessly export a diagram with the 10-unit/5-unit coordinate grid overlaid for visual inspection.
- `drawlib serve <html_dir> --check`: Verify zero broken links or missing assets when HTML output (`-f html`) is built.
- `drawlib styles list` / `drawlib colors list` / `drawlib cache list`: Inspect built-in style/color catalogs and cached font/icon packages.
