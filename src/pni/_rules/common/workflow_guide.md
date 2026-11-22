# Workflow Authoring & Repository Inspection Guide (Common — Workflow v2)

When asked to audit a project or create `.pni/workflows/*.yaml`, AI agents **must inspect the repository first** rather than blindly assuming default directory layouts or applying service-only rules to libraries. Follow this 7-step Workflow v2 procedure to design accurate, DAG-parallel, hallucination-free workflows.

---

## Step 1: Inspect Repository Languages, Runtime Archetype & Topology

1. **Identify Manifests & Languages (55 Supported Languages)**:
   - Python: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`, `uv.lock`
   - Java: `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle*`
   - PHP: `composer.json`, `composer.lock`, `artisan`, `wp-config.php`, `phpunit.xml*`, root `*.php`
   - Go: `go.mod`, `go.work`, `go.sum`
   - TypeScript / JavaScript: `package.json`, `tsconfig.json`, `jsconfig.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`
   - Other Tier A/B Languages (`generic` workflow + native Tree-sitter AST & Docker harnesses where available): Rust (`Cargo.toml`), C# (`*.csproj`), Ruby (`Gemfile`), Kotlin, Swift, C/C++, Scala, Dart, Elixir, Perl, COBOL, R, Zig, Solidity, Verilog/VHDL, etc.
   - Companion DSLs (auto-scanned once on `scope: repo`): `Dockerfile`, Terraform/HCL, Bicep, Nix, Makefile, Starlark, Protobuf, SQL, HTML/CSS/SCSS, YAML/JSON/TOML/XML.
2. **Determine Runtime Archetypes (`runtime_types: list[str]`)**:
   - **`web_api` / `worker`**: Networked APIs, microservices, or queue workers (`fastapi`, `flask`, `django`, `spring-boot`, `celery`, etc.) → evaluate **12-Factor App** & **Google SRE Production Readiness Review (PRR)**.
   - **`cli`**: Command-line tools (`[project.scripts]`, `typer`, `click`, `picocli`, `cobra`) → evaluate **CLI Guidelines (`clig.dev`)**.
   - **`library`**: Reusable packages / SDKs → evaluate **Library SemVer & API Purity (`common/library_guidelines`)** + **Diátaxis (`common/documentation`)**.
   - **Multi-Archetype Projects (e.g. `["cli", "library"]`, `["web_api", "cli"]`)**: Combine the audit actions corresponding to every archetype present in `runtime_types`.
3. **Determine Repository Topology**:
   - **Single-Language Repo**: One root manifest and source tree (`scope: repo`, `targets.root: "."`). Use or adapt `.pni/workflows/full_audit.yaml`.
   - **Multi-Language / Monorepo**: Multiple subprojects or languages (e.g., `backend/` Python + `frontend/` TypeScript + `native/` Rust). Create one **`scope: component`** audit workflow per subproject PLUS one **`category: rollup`** workflow to synthesize a unified score, SARIF, and 6-chapter executive + per-component deep-dive report (see **Step 4**).
4. **Locate Exact Source, Test, Doc & Exclude Paths**:
   - Exclude generated code (`targets.exclude`, e.g., `["**/*_generated.py"]`), virtual environments, migrations (`migrations/versions/**`), vendor directories, and build outputs (`build/`, `target/`, `dist/`).

---

## Step 2: Consult Language & Universal Engineering Standards

Read the workflow best-practice guide for each language present in the target:

```bash
pni rules show python/workflow_guide
pni rules show java/workflow_guide
pni rules show php/workflow_guide
pni rules show go/workflow_guide
pni rules show typescript/workflow_guide
pni rules show javascript/workflow_guide
pni rules show generic/workflow_guide
pni rules list --all
```

Available universal & runtime-archetype rule scopes under `common/`:
- **Universal (all projects)**: `common/supply_chain` (OpenSSF Scorecard), `common/maintainability` (SIG / ISO 25010), `common/security` (OWASP ASVS), `common/documentation` (Standard Readme & Diátaxis), `common/architecture`, `common/git_workflow`
- **Archetype-Scoped**: `common/twelve_factor` + `common/production_readiness` (`"web_api"` / `"worker"` in `runtime_types`), `common/cli_guidelines` (`"cli"` in `runtime_types`), `common/library_guidelines` (`"library"` in `runtime_types`)

---

## Step 3: Assemble the Canonical Workflow v2 DAG (`needs:` + `when:`)

Workflow v2 runs a **native DAG**: PNI automatically prepends the `confirm_plan` human alignment gate (`act-01`), executes DAG-ready deterministic analyzers in parallel via `ThreadPoolExecutor` (zero empty ACKs), evaluates safe `when:` predicates (e.g., `has_runtime_harness`, `container_engine_available`, `'web_api' in runtime_types`), anchors 7-axis baselines (`±10pt`), and emits `*_score.json` (v2.0) + `*_summary.json` + `*_findings.sarif`:

```yaml
id: full_audit
category: audit
scope: repo                         # "repo" (default) or "component" (for monorepo sub-audits)
name: Full Project Health Audit & Report
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic collection, grounded architecture, anchored score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"                         # Replace with actual source dir(s)
  tests:
    - "tests"                       # Replace with actual test dir(s)
  docs:
    - "README.md"                   # Include key architecture/design docs if present
  exclude: []                       # Optional glob exclusions, e.g. ["**/*_generated.py"]

steps:
  # Wave 1: Deterministic project/supply-chain recon
  - id: repo_and_deps
    uses: repo_structure_audit      # Optionally add `supply_chain_audit` for deep CI/Dockerfile review

  # Wave 2 (Parallel fan-out after repo_and_deps): AST, Container Runtime, Security Scan
  - id: ast_and_quality
    uses: python_ast_audit          # Or java/php/go/typescript/javascript/generic_ast_audit
    needs: [repo_and_deps]

  - id: runtime_verification
    uses: container_runtime_audit
    needs: [repo_and_deps]
    when: "has_runtime_harness"     # Auto-skipped cleanly when no Docker harness exists for the language

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  # Wave 3 (Parallel after ast_and_quality): 3-aspect grounded architecture, archetype & test audits
  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  # Optional runtime-archetype evaluation (choose matching archetype action(s)):
  # - Web API / Worker:  uses: service_readiness_audit   (12-Factor + Google SRE PRR)
  # - CLI Tool:          uses: cli_guidelines_audit      (clig.dev UX, streams, exit codes)
  # - Library / SDK:     uses: library_hygiene_audit     (SemVer bounds, API purity, Diátaxis)
  - id: archetype_audit
    uses: service_readiness_audit   # Replace with cli_guidelines_audit or library_hygiene_audit
    needs: [ast_and_quality]

  - id: test_health
    uses: python_test_audit         # Or java/php/go/typescript/javascript_test_audit
    needs: [ast_and_quality]

  # Optional dynamic Web pentest (DAST); requires .pni/pentests/<target>/ implemented BEFORE start
  # - id: web_pentest
  #   uses: web_penetration_audit
  #   needs: [repo_and_deps]
  #   when: "'web_api' in runtime_types"

  # Fan-in: Anchored 7-axis score + ScoreSummary + SARIF 2.1.0 & A4 PDF Drawlib report
  - id: output_score
    uses: emit_score
    needs: [arch_recording, archetype_audit, test_health, runtime_verification, security_audit]
    with:
      target: "full_audit"
      save_file: true

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
    with:
      target: "full_audit"
      src_dir: "pni_report_src"
      output_dir: "pni_report"
      formats: ["pdf"]
```

For fast iterative CI/local checks (`quick_check.yaml`), omit `architecture_analysis`, `runtime_verification`, and `write_drawlib_report`, ending at `emit_score`.

---

## Step 4: Multi-Language / Monorepo Rollup Workflows (`scope: component` + `category: rollup`)

When one repository contains multiple primary languages or independently structured services/packages (e.g., `backend/` Python + `frontend/` TypeScript + `native/` Rust):

1. **Author Per-Component Sub-Audits (`scope: component`)**:
   - Create `.pni/workflows/audit_backend.yaml`, `audit_frontend.yaml`, etc., setting `scope: component` and `targets.root: "backend"` (or `"frontend"`).
   - Component sub-audits skip duplicate root governance/companion checks and end at `emit_score` (producing `pni_report/<component>_score.json`, `*_summary.json`, and `*_findings.sarif` without generating redundant standalone PDFs unless explicitly requested).
   - Optionally declare components centrally in `.pni/pni.toml` under `[[components]]`.
2. **Author One Unified Rollup Workflow (`category: rollup`)**:
   - PNI verifies all `includes:` sub-audits are `COMPLETED`, aggregates 7-axis scores via `log1p(LOC)` smoothing + `security`/`testing` weakest-link guardrails (`min_primary + 15`), normalizes every finding path to repository root with `component` tags, runs root governance + companion DSL scans once, and renders a unified 6-chapter Drawlib report (`report_mode: "unified"` default):

```yaml
id: monorepo_rollup
category: rollup
name: Unified Multi-Language Monorepo Audit
description: Synthesizes backend, frontend, and native sub-audits with weakest-link guardrails into a single executive + component deep-dive report.

includes:
  - id: backend
    workflow: audit_backend
    primary: true
  - id: frontend
    workflow: audit_frontend
    primary: true
  - id: native
    workflow: audit_native
    weight: 0.25

steps:
  - id: rollup_synthesis
    uses: synthesize_rollup
    with:
      target: "monorepo_rollup"
      report_mode: "unified"        # unified (default) | per_component | both

  - id: create_report
    uses: write_drawlib_report
    needs: [rollup_synthesis]
    with:
      target: "monorepo_rollup"
      src_dir: "pni_report_src"
      output_dir: "pni_report"
      formats: ["pdf"]
```

---

## Step 5: Authoring Migration Execution Plan Workflows (`category: migration` + `based_on`)

When generating a To-Be Migration Execution Plan (`*_migration_plan.json` and `*_migration.pdf`), create a dedicated workflow YAML with `category: migration` and `based_on: <audit_workflow_id>` (see `common/migration_planning`):

1. **Link to Base Audit (`based_on`) & SQLite Prerequisite Enforcement**:
   - Declare `category: migration` and `based_on: <audit_workflow_id>`. `targets` are automatically inherited from `<audit_workflow_id>`—omit `targets` unless overriding.
   - `pni workflows start <migration_id>` requires `<audit_workflow_id>` to have a `COMPLETED` run in `.pni/cache/workflow_state.db`. Complete `<audit_workflow_id>` first.
2. **Scrutinize & Clarify Before Execution**:
   - Cross-check migration goals against As-Is facts (`*_score.json` / SQLite audit run), ask the user concise clarifying questions for any ambiguous target versions, DB/Cache stores, architecture boundaries, API compatibility, or legacy quirk policies, and pin confirmed decisions in `with.brief: |` + explicit guardrail options before starting.

```yaml
id: app_migration_plan
category: migration
based_on: full_audit
name: Phased Migration Execution Plan & Report
description: Deterministic wave/contract/touchpoint analysis, multi-axis To-Be design, and 7-chapter Drawlib PDF plan.

steps:
  - id: gap_and_order
    uses: migration_proposal
    with:
      brief: |
        [Confirmed Target Stack, Architecture Boundaries, Compatibility Constraints & Non-Goals]
      migration_strategy: "phased_pr"     # phased_pr | strangler_fig | rewrite
      api_compatibility: "strict"         # strict | versioned_v2 | flexible
      bug_handling_policy: "ask_human"    # ask_human | preserve_behavior | fix_in_phase3
      codemod_tool: "openrewrite"         # openrewrite | rector | ruff | manual_only
      output_dir: "pni_report"
      target: "app_migration"

  - id: create_migration_pdf
    uses: write_migration_report
    needs: [gap_and_order]
    with:
      src_dir: "pni_report_src"
      output_dir: "pni_report"
      target: "app_migration"
      lang: "ja"
      style: "google"
```

---

## Step 6: Authoring Project Progress & Git Governance Workflows (`category: progress`)

When tracking milestone delivery, branch/merge governance, non-destructive conflict simulations (`git merge-tree`), and historical LOC/test/audit trajectories (`*_progress.json` and `*_progress.pdf`), create a workflow YAML with `category: progress` (see `common/progress_tracking` and `common/git_workflow`):

1. **Scaffold & Validate `.pni/progress/<target>.yaml` First**:
   ```bash
   pni progress init <progress_id>
   # Edit .pni/progress/<progress_id>.yaml (git_policy, milestones, tasks) directly
   pni progress validate <progress_id>
   ```
   - Treat `.pni/progress/<target>.yaml` as **strictly Read-Only** during measurement runs (`plan_sha256` is verified on `emit_progress`).
2. **Optional Lightweight Audit Linkage (`based_on`)**:
   - `based_on: <audit_workflow_id>` is optional on `category: progress` and links Git-tracked `.pni/history/audit/<audit_workflow_id>.jsonl` without requiring `.pni/cache/workflow_state.db`.

```yaml
id: project_progress
category: progress
based_on: full_audit                # Optional: links .pni/history/audit/full_audit.jsonl & inherits targets
name: Project Progress & Git Governance Tracking
description: Schedule vs. actual verification, branch merge-tree conflict checks, LOC/test trajectories, and 5-chapter PDF report.

steps:
  - id: assess_progress
    uses: progress_assessment
    with:
      plan_file: ".pni/progress/project_progress.yaml"
      lookback_weeks: 12
      output_dir: "pni_report"
      target: "project_progress"

  - id: create_progress_pdf
    uses: write_progress_report
    needs: [assess_progress]
    with:
      src_dir: "pni_report_src"
      output_dir: "pni_report"
      target: "project_progress"
      lang: "ja"
      style: "google"
```

---

## Step 7: Preview Phase 0 Plan, Validate Prerequisites & Launch

1. **Inspect Expanded DAG & Phase 0 Execution Plan**:
   ```bash
   pni workflows list
   pni workflows show <workflow_id>
   pni workflows plan <workflow_id>              # Preview Recon, discovered components, validated Mermaid DAG & questions
   ```
2. **Implement Penetration Tests First (When `web_pentest` Is Included)**:
   ```bash
   pni pentests init -w <workflow_id>
   # Customize .pni/pentests/<target>/test_*.py for the target's endpoints/auth
   pni workflows run-action <workflow_id> web_pentest
   ```
3. **Ad-Hoc Single-Action Verification (Zero Workflow Preparation)**:
   ```bash
   pni workflows run-action <workflow_id> <step_or_action>
   ```
4. **Launch Stateful Run & Confirm Plan with User (Single Simple Commands Only)**:
   - Run `pni workflows start <workflow_id> --pull` -> review the validated Mermaid DAG & alignment questions with the user -> write `PlanApprovalInput` to `.pni/cache/<workflow_id>/input_act-01.json` with your file-writing tool -> push with `pni workflows push-action <run_id> act-01 --file .pni/cache/<workflow_id>/input_act-01.json --next` (avoid pipes `|`, redirects `>`, `<<EOF`, or `&&` chaining; use `-o <path>` to save long outputs).
   - Use `--auto-approve --pull` (or `--plan <file.json> --pull`) for non-interactive CI/batch executions.
   - Validate any custom Mermaid diagram from a file before presenting it using `pni validate-mermaid <file> [--browser]`.
