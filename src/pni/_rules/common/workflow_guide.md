# Workflow Authoring & Repository Inspection Guide (Common)

When asked to audit a project or create `.pni/workflows/*.yaml`, AI agents **must inspect the repository first** rather than blindly assuming default directory layouts or applying service-only rules to libraries. Follow this 4-step procedure to design accurate, hallucination-free workflows.

---

## Step 1: Inspect Repository Languages, Runtime Archetype & Boundaries

1. **Identify Manifests & Languages**:
   - Python: `pyproject.toml`, `setup.py`, `requirements.txt`, `uv.lock`
   - Java: `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle*`
   - TypeScript / JS: `package.json`, `tsconfig.json`
   - Go / Rust: `go.mod`, `Cargo.toml`
   - Legacy / Scripting assets: `.sh` (Bash), `.pl`/`.pm` (Perl), `.bat`/`.vbs`
2. **Determine Runtime Archetypes (`runtime_types: list[str]`)**:
   - **`web_api` / `worker`**: Networked APIs, microservices, or queue workers (`fastapi`, `flask`, `django`, `spring-boot`, `celery`, etc.) → evaluate **12-Factor App** & **Google SRE Production Readiness Review (PRR)**.
   - **`cli`**: Command-line tools (`[project.scripts]`, `typer`, `click`, `picocli`, `cobra`) → evaluate **CLI Guidelines (`clig.dev`)**.
   - **`library`**: Reusable packages / SDKs → evaluate **Library SemVer & API Purity (`common/library_guidelines`)** + **Diátaxis (`common/documentation`)**.
   - **Multi-Archetype Projects (e.g. `["cli", "library"]`, `["web_api", "cli"]`)**: Combine the audit actions corresponding to every archetype present in `runtime_types`.
3. **Determine Repository Topology**:
   - **Single-Package Repo**: One root manifest and a clear source tree (e.g., `src/` or `src/main/java`). Use or adapt `.pni/workflows/full_audit.yaml` (`root: "."`).
   - **Monorepo / Multi-Service / Examples Repo**: Multiple subprojects (e.g., `services/api/`, `services/worker/`, `examples/clean/`). Create **one workflow YAML per target** with distinct `targets.root` and distinct `target` names so `reports/<target>.pdf` and `reports_src/<target>_src/` never collide.
4. **Locate Exact Source, Test, Doc & Exclude Paths**:
   - Exclude generated code (via `targets.exclude`, e.g., `["**/*_generated.py"]`), virtual environments, migrations (`migrations/versions/**`), vendor directories, and build outputs (`build/`, `target/`, `dist/`).

---

## Step 2: Consult Language & Universal Engineering Standards

Read the workflow best-practice guide for each language present in the target:

```bash
pni rules show python/workflow_guide
pni rules show java/workflow_guide
pni rules list --all
```

Available universal & runtime-archetype rule scopes under `common/`:
- **Universal (all projects)**: `common/supply_chain` (OpenSSF Scorecard), `common/maintainability` (SIG / ISO 25010), `common/security` (OWASP ASVS), `common/documentation` (Standard Readme & Diátaxis), `common/architecture`, `common/git_workflow`
- **Archetype-Scoped**: `common/twelve_factor` + `common/production_readiness` (`"web_api"` / `"worker"` in `runtime_types`), `common/cli_guidelines` (`"cli"` in `runtime_types`), `common/library_guidelines` (`"library"` in `runtime_types`)

---

## Step 3: Assemble the Canonical Workflow Pipeline (`Universal` + `Language` + `Archetype`)

Compose steps orthogonally from universal checks, language AST checks, and the project's `runtime_types`:

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report
description: Deterministic fact extraction, aspect-separated architecture analysis, universal/archetype/language audits, scoring, and Drawlib report.

targets:
  root: "."
  source:
    - "src"          # Replace with actual source dir(s)
  tests:
    - "tests"        # Replace with actual test dir(s)
  docs:
    - "README.md"    # Include key architecture/design docs if present
  exclude: []        # Optional glob exclusions, e.g. ["**/*_generated.py"]

steps:
  # Stage 1: Deterministic repo, OpenSSF supply-chain, container & Diátaxis inspection
  - id: repo_and_deps
    uses: repo_structure_audit      # Optionally add `supply_chain_audit` for deep CI/Dockerfile review

  # Stage 2: Language AST + SIG Maintainability + operational signal extraction
  - id: ast_and_quality
    uses: python_ast_audit          # Or java_ast_audit

  # Stage 3: 3-aspect grounded AI architecture recording (verified against AST inventory)
  - id: architecture_map
    uses: architecture_analysis

  # Stage 4: Runtime-archetype evaluation (choose matching archetype action(s))
  # - Web API / Worker:  uses: service_readiness_audit   (12-Factor + Google SRE PRR)
  # - CLI Tool:          uses: cli_guidelines_audit      (clig.dev UX, streams, exit codes)
  # - Library / SDK:     uses: library_hygiene_audit     (SemVer bounds, API purity, Diátaxis)
  - id: archetype_audit
    uses: service_readiness_audit   # Replace with cli_guidelines_audit or library_hygiene_audit

  # Stage 5: Test suite, container runtime, supply-chain CVE & dynamic Web pentest (DAST)
  - id: test_health
    uses: python_test_audit         # Or java_test_audit / php_test_audit

  - id: runtime_verification
    uses: container_runtime_audit

  - id: security_audit
    uses: security_vulnerability_audit

  - id: web_pentest                 # Add for Web APIs/services; requires .pni/pentests/<target>/ implemented BEFORE 'pni workflows start'
    uses: web_penetration_audit

  # Stage 6: Validated intermediate score JSON & A4 PDF Drawlib report
  - id: output_score
    uses: emit_score
    with:
      target: "full_audit"
      save_file: false              # Set true if reports/full_audit_score.json should persist on disk

  - id: create_report
    uses: write_drawlib_report
    with:
      target: "full_audit"
      src_dir: "reports_src"
      output_dir: "reports"
      formats: ["pdf"]
```

For fast iterative CI/local checks (`quick_check.yaml`), you may omit `architecture_analysis` and `write_drawlib_report`, ending at `emit_score` with `save_file: true`.

---

## Step 4: Authoring Migration Execution Plan Workflows (`category: migration` + `based_on`)

When generating a To-Be Migration Execution Plan (`*_migration_plan.json` and `*_migration.pdf`), create a dedicated workflow YAML with `category: migration` and `based_on: <audit_workflow_id>` (see `common/migration_planning`):

1. **Link to Base Audit (`based_on`) & SQLite Prerequisite Enforcement**:
   - Declare `category: migration` and `based_on: <audit_workflow_id>`. `targets` (`root`, `source`, `tests`, `docs`) are automatically inherited from `<audit_workflow_id>`—omit `targets` unless overriding.
   - `pni workflows start <migration_id>` requires `<audit_workflow_id>` to have a `COMPLETED` run in `.pni/cache/workflow_state.db` (and automatically inherits its `ProjectFacts`, `AstFacts`, `RuntimeFacts`, `SecurityFacts`, `ArchitectureRecord`, and `ScoreResult`). **If `pni workflows start` returns a prerequisite error because the audit workflow has not completed yet, run `pni workflows start <audit_workflow_id>` and complete the audit workflow first.**
2. **Scrutinize & Clarify Before Execution (Mandatory Recommended Practice)**:
   - Cross-check the user's migration goals against As-Is facts (`*_score.json` / SQLite audit run).
   - If target runtime/framework versions, DB/Cache stores (e.g., PostgreSQL, Redis), architectural boundaries (e.g., Clean Architecture `domain`/`usecase`/`port`/`adapter`), external API backward compatibility, or legacy quirk policies are underspecified, **ask the user concise clarifying questions first**.
   - Materialize all confirmed decisions and Non-Goals into `with.brief: |` (or `with.brief_file`) and pin explicit guardrail values (`migration_strategy`, `api_compatibility`, `bug_handling_policy`, `codemod_tool`) inside `.pni/workflows/<migration_id>.yaml` **before** running `pni workflows start`.

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
      output_dir: "reports"
      target: "app_migration"

  - id: create_migration_pdf
    uses: write_migration_report
    with:
      src_dir: "reports_src"
      output_dir: "reports"
      target: "app_migration"
      lang: "ja"
      style: "google"
```

---

## Step 5: Authoring Project Progress & Git Governance Workflows (`category: progress`)

When tracking milestone delivery, branch/merge governance, non-destructive conflict simulations (`git merge-tree`), and historical LOC/test/audit trajectories (`*_progress.json` and `*_progress.pdf`), create a workflow YAML with `category: progress` (see `common/progress_tracking` and `common/git_workflow`):

1. **Scaffold & Validate `.pni/progress/<target>.yaml` First**:
   - `pni workflows start <progress_id>` fails closed unless `.pni/progress/<target>.yaml` exists and passes schema/DAG validation:
   ```bash
   pni progress init <progress_id>
   # Edit .pni/progress/<progress_id>.yaml (git_policy, milestones, tasks) directly
   pni progress validate <progress_id>
   ```
   - During workflow execution, treat `.pni/progress/<target>.yaml` as **strictly Read-Only** (`plan_sha256` is verified on `emit_progress`).
2. **Optional Lightweight Audit Linkage (`based_on`)**:
   - `based_on: <audit_workflow_id>` is **optional** on `category: progress`. When set, `targets` are inherited from `<audit_workflow_id>` and `progress_analyze` reads Git-tracked `.pni/history/audit/<audit_workflow_id>.jsonl` (plus `reports/<audit_workflow_id>_score.json`) without requiring `.gitignore`'d `.pni/cache/workflow_state.db`.

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
      output_dir: "reports"
      target: "project_progress"

  - id: create_progress_pdf
    uses: write_progress_report
    with:
      src_dir: "reports_src"
      output_dir: "reports"
      target: "project_progress"
      lang: "ja"
      style: "google"
```

---

## Step 6: Validate Workflow Expansion, Implement Prerequisites & Test Individual Actions Before Running

1. **Inspect Expanded Pipeline & Blocking Prerequisites**:
   ```bash
   pni workflows list
   pni workflows show <workflow_id>
   ```
2. **Implement Penetration Tests First (When `web_pentest` Is Included)**:
   - Workflows with `web_penetration_audit` fail closed on `pni workflows start` until `.pni/pentests/<target>/` is implemented:
   ```bash
   pni pentests init -w <workflow_id>
   # Customize .pni/pentests/<target>/test_*.py for the target's endpoints/auth
   pni workflows run-action <workflow_id> web_pentest
   ```
3. **Ad-Hoc Single-Action Verification (Zero Workflow Preparation)**:
   - Run any individual step or primitive (`ast_and_quality`, `runtime_verification`, `security_audit`, `web_pentest`, `assess_progress`, etc.) directly without creating a SQLite run:
   ```bash
   pni workflows run-action <workflow_id> <step_or_action>
   ```
4. Once verified (with pentests/progress plans validated, prerequisite audit completed, and zero unresolved migration preflight ambiguity hints), start the stateful run with `pni workflows start <workflow_id>`.
