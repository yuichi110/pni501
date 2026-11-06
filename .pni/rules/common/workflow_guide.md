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
2. **Determine Runtime Archetype (`runtime_type_hint`)**:
   - **`web_api` / `worker`**: Networked APIs, microservices, or queue workers (`fastapi`, `flask`, `django`, `spring-boot`, `celery`, etc.) → evaluate **12-Factor App** & **Google SRE Production Readiness Review (PRR)**.
   - **`cli`**: Command-line tools (`[project.scripts]`, `typer`, `click`, `picocli`, `cobra`) → evaluate **CLI Guidelines (`clig.dev`)**.
   - **`library`**: Reusable packages / SDKs without service daemons → evaluate **Library SemVer & API Purity (`common/library_guidelines`)** + **Diátaxis (`common/documentation`)**.
   - **`hybrid`**: Projects exposing both a CLI/service and an importable SDK → combine the relevant archetype steps.
3. **Determine Repository Topology**:
   - **Single-Package Repo**: One root manifest and a clear source tree (e.g., `src/` or `src/main/java`). Use or adapt `.pni/workflows/full_audit.yaml` (`root: "."`).
   - **Monorepo / Multi-Service / Examples Repo**: Multiple subprojects (e.g., `services/api/`, `services/worker/`, `examples/clean/`). Create **one workflow YAML per target** with distinct `targets.root` and distinct `target` names so `reports/<target>.pdf` and `reports_src/<target>_src/` never collide.
4. **Locate Exact Source, Test & Doc Paths**:
   - Exclude generated code, virtual environments, migrations (`migrations/versions`), vendor directories, and build outputs (`build/`, `target/`, `dist/`).

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
- **Archetype-Scoped**: `common/twelve_factor` + `common/production_readiness` (`web_api` / `worker`), `common/cli_guidelines` (`cli`), `common/library_guidelines` (`library`)

---

## Step 3: Assemble the Canonical Workflow Pipeline (`Universal` + `Language` + `Archetype`)

Compose steps orthogonally from universal checks, language AST checks, and the project's runtime archetype:

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

  # Stage 5: Test suite effectiveness audit
  - id: test_health
    uses: python_test_audit         # Or java_test_audit

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

## Step 5: Validate Workflow Expansion, Implement Pentests & Test Individual Actions Before Running

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
   - Run any individual step or primitive (`ast_and_quality`, `runtime_verification`, `security_audit`, `web_pentest`, etc.) directly without creating a SQLite run:
   ```bash
   pni workflows run-action <workflow_id> <step_or_action>
   ```
4. Once verified (with pentests implemented, prerequisite audit completed, and zero unresolved migration preflight ambiguity hints), start the stateful run with `pni workflows start <workflow_id>`.
