# Rules Customization & CLI Reference

`pni501` (`v0.2.0`) ships **356 built-in Markdown rule files**, **182 built-in composite action templates**, **112 built-in workflow templates**, and **40 container harness Dockerfiles** across **55 languages** (plus the `generic` fallback scope). Workspace customizations resolve cleanly through a deterministic `.pni/` override cascade, and every lifecycle operation is exposed via the unified `pni` CLI.

```drawlib align=center code=fold file=rules_taxonomy_and_override.png caption="v0.2.0 Rule Taxonomy (356 Built-in Files Across 55 Languages) and .pni/ Local Override Cascade"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=184, height=86, dpi=150)

tax_panel = Panel(
    "1. Built-in Catalog (356 Rules | 182 Actions | 112 WFs)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
)
tax_panel.draw(xy=(4.0, 4.0), width=85.5, height=78.0)

tax_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.6),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.8,
)
tax_cards.add(
    "Universal Standards & Guides (common/*)",
    "12 evaluation rules (Arch, SIG, OpenSSF, OWASP,\n"
    "12-Factor, SRE, CLI, Library) + 4 meta-guides\n"
    "(agent_instruction, workflow/migration/progress)",
    badge_text="16",
    icon=phosphor.globe,
)
tax_cards.add(
    "55 Languages + Generic (<lang>/*)",
    "code_quality, typing, dependencies, testing,\n"
    "modern_stack, workflow_guide across all 55\n"
    "Tier A/B/C languages + generic fallback (56 x 6)",
    badge_text="336",
    icon=phosphor.code,
)
tax_cards.add(
    "Framework Rules (<lang>/frameworks/*)",
    "python/frameworks/fastapi, java/frameworks/\n"
    "spring_boot, php/frameworks/laravel, and\n"
    "php/frameworks/wordpress",
    badge_text="4",
    icon=phosphor.stack,
)
tax_cards.draw(xy=(6.5, 6.5), width=80.5, height=64.5)

cas_panel = Panel(
    "2. Local .pni/ Override & Waiver Cascade",
    header_variant="filled",
    header_height=8.5,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
)
cas_panel.draw(xy=(94.5, 4.0), width=85.5, height=78.0)

cas_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.6),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.SecondaryBold.patch(text_size=10.0),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=2.8,
)
cas_cards.add(
    "Priority 1: Local .pni/ Workspace Files",
    ".pni/rules/<scope>/<name>.md, .pni/actions/*.yaml,\n"
    ".pni/dockerfiles/, and .pni/instructions.md\n"
    "automatically shadow built-in package defaults",
    badge_text="P1",
    icon=phosphor.folder_open,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
)
cas_cards.add(
    "Priority 2: Active Language Scope (<lang>/*)",
    "Short names (e.g. 'pni rules show testing' or\n"
    "'repo_structure_audit') resolve to the active\n"
    "language before falling back to common/*",
    badge_text="P2",
    icon=phosphor.magnifying_glass,
)
cas_cards.add(
    "Priority 3: Built-in common/* & [[opt_out]]",
    "Canonical src/pni/_rules/ fallback paired with\n"
    "declarative .pni/pni.toml [[opt_out]] waivers\n"
    "(requires scoped paths + reason >= 10 chars)",
    badge_text="P3",
    icon=phosphor.shield_check,
)
cas_cards.draw(xy=(97.0, 6.5), width=80.5, height=64.5)

save()
```

---

## 1. Orthogonal Rule, Action & Workflow Taxonomy

Every rule in `pni501` is stored as clean, human- and LLM-readable Markdown under `src/pni/_rules/` and paired with deterministic static, runtime, or security signals so AI evaluations stay anchored to verified facts:

| Built-in Asset Type | Total Count | Breakdown Across `common/*`, 55 Languages & `generic/*` |
| :--- | :--- | :--- |
| **Rule Files (`src/pni/_rules/`)** | **`356`** | `16` `common/*` rules & meta-guides + `336` core language rules (`6` each across 55 languages + `generic`) + `4` framework guides (`fastapi`, `spring_boot`, `laravel`, `wordpress`). |
| **Action Templates (`src/pni/_actions/`)** | **`182`** | `15` `common/*` actions (architecture, security, runtime, pentest, migration, progress, rollup, scoring, Drawlib reporting) + `165` language actions (`3` per language × 55) + `2` `generic/*` actions. |
| **Workflow Templates (`src/pni/_workflows/`)** | **`112`** | `2` ready-to-use workflows (`full_audit.yaml` & `quick_check.yaml`) × `56` scopes (55 languages + `generic`). |
| **Harness Dockerfiles (`src/pni/_dockerfiles/`)** | **`40`** | Isolated offline test, coverage, and smoke templates across all 20 Tier A languages and 15 Tier B ecosystems. |

### 1.1 Universal Standards & Meta-Guides (`common/*` — 16 Files)

The `common/` scope contains **12 universal engineering evaluation rules** (spanning all repositories plus `Service / API`, `CLI Tool`, and `Library / SDK` archetypes) and **4 orchestration meta-guides**:

| Rule Identifier | Anchor Standard | Target Archetype | Deterministic Grounding Signals (`ProjectFacts` / `AstFacts` / `RuntimeFacts`) |
| :--- | :--- | :--- | :--- |
| `common/architecture` | Clean / Layered Arch | All Projects | `circular_dependencies`, `internal_import_graph`, `boundary_violations`, `ArchitectureRecord` |
| `common/maintainability` | SIG / ISO 25010 | All Projects | `complex_functions` (`McCabe > 7`, `cognitive > 15`), `LOC <= 50`, `params <= 6`, `global_state_usages` |
| `common/supply_chain` | OpenSSF Scorecard | All Projects | `lockfiles_found`, `unpinned_dependencies`, `ci_supply_chain_issues`, `has_license`, `has_security_md` |
| `common/security` | OWASP ASVS Baseline | All Projects | `committed_secret_files`, `hardcoded_secrets`, `bug_risk_idioms`, `dangerous_sinks` |
| `common/security_vulnerability` | Trivy + CWE Sinks | All Projects | `SecurityFacts` (App/OS CVEs, IaC misconfigs, redacted secrets) + CST `dangerous_sinks` & `api_endpoints` |
| `common/runtime_verification` | Isolated Container QA | All Projects | `RuntimeFacts` (Dockerfile build, offline `--network=none` test pass rate, line/branch coverage, Stage 3 smoke probe) |
| `common/git_workflow` | Conventional Repo | All Projects | `has_gitignore`, committed caches/artifacts (`__pycache__`, `node_modules`, `.venv`), workspace hygiene |
| `common/documentation` | Std Readme & Diataxis | All Projects | `readme_headings`, `readme_line_count`, `docs_inventory`, `docstring_coverage_pct`, `docstring_issues` |
| `common/twelve_factor` | 12 / 15-Factor App | Service / API | `scattered_env_access` outside config modules, `runtime_types`, stateless worker readiness |
| `common/production_readiness` | Google SRE PRR | Service / API | `missing_io_timeouts`, `unstructured_logging`, health/readiness endpoints, container non-root hygiene |
| `common/cli_guidelines` | clig.dev Guidelines | CLI Tool | CLI entrypoints, `--help`/`--version`/`--json` support, `stdout` vs `stderr` separation, non-zero exit codes |
| `common/library_guidelines` | Public SDK Hygiene | Library / SDK | Explicit public exports (`__all__`), `py.typed` / `.d.ts` markers, import-time purity, zero `sys.exit()` in library code |
| `common/agent_instruction` | PNI Agent Protocol | Meta-Guide | Top-level deterministic pull-push execution loop & zero-hallucination protocol (`pni instructions`) |
| `common/workflow_guide` | PNI Authoring Spec | Meta-Guide | Guide for inspecting repository layout and authoring `.pni/workflows/*.yaml` & `.pni/actions/*.yaml` |
| `common/migration_planning` | Modernization Spec | Meta-Guide | Pre-flight user clarification checklist, `based_on` audit inheritance, and 5-phase gated migration planning |
| `common/progress_tracking` | Schedule & Git Gov | Meta-Guide | Guide for `.pni/progress/<target>.yaml` milestones, task DAG validation, and Git branch/commit governance |

### 1.2 Language & Framework Rule Catalog (`<lang>/*` + `generic/*` — 340 Files)

Every one of the **55 supported languages** (plus `generic`) provides a consistent 6-file rule bundle — `code_quality`, `typing`, `dependencies`, `modern_stack`, `testing`, and `workflow_guide` (`56 × 6 = 336` files) — augmented by **4 framework-specific standards**:

- `python/frameworks/fastapi` — FastAPI `lifespan`, `Depends()` DI, `response_model`, and async I/O hygiene.
- `java/frameworks/spring_boot` — Spring Boot constructor DI, `@ConfigurationProperties`, Jakarta EE migration, and Actuator hardening.
- `php/frameworks/laravel` — Laravel `config/` hygiene, FormRequest validation, Eloquent mass-assignment protection, and raw query safety.
- `php/frameworks/wordpress` — WordPress `$wpdb->prepare()`, escaping, CSRF nonces (`check_admin_referer`), REST permission callbacks, and `ABSPATH` guards.

---

## 2. The `.pni/` Local Override Cascade & `pni.toml` Waivers

Running `pni init` initializes the `.pni/` workspace directory. PNI resolves rules, composite actions, instructions, and container harnesses through a non-destructive override cascade so teams can tailor thresholds or container images without forking `pni501`:

| Workspace Path | Cascade Resolution Behavior | Purpose & Customization Pattern |
| :--- | :--- | :--- |
| `.pni/pni.toml` | Workspace root (or nearest ancestor `.pni/pni.toml`) | Configures `[project]`, default `[targets]`, `[scan]` exclusions, `[report]` defaults (`pni_report_src -> pni_report`), and `[[opt_out]]` waivers. |
| `.pni/rules/<scope>/<name>.md` | `.pni/rules/` $\to$ built-in `<active_lang>/` $\to$ built-in `common/` | Edit any copied `.md` rule in `.pni/rules/` to customize thresholds (shown as `Local (.pni)` in `pni rules list`). Meta-guides (`agent_instruction`, `workflow_guide`) always resolve from built-in package files. |
| `.pni/actions/*.yaml` | `.pni/actions/` $\to$ built-in `<active_lang>/` $\to$ built-in `common/` | Customize composite action step rules, parameters, or prompts per project. |
| `.pni/workflows/*.yaml` | Project-defined in `.pni/workflows/` | Declares `audit`, `migration` (`based_on`), `progress`, and `rollup` workflows. |
| `.pni/dockerfiles/` | `explicit_dockerfile` $\to$ `.pni/dockerfiles/_templates/<lang>/<tool>.dockerfile` $\to$ built-in `src/pni/_dockerfiles/` | Materializes target-scoped harness Dockerfiles (`.pni/dockerfiles/<target>/Dockerfile` + `.dockerignore`) for offline test/smoke execution. |
| `.pni/pentests/<target>/` | Scaffolded via `pni pentests init -w <workflow_id>` | Holds explicit `Python + httpx` dynamic penetration test probes (`conftest.py`, `test_*.py`). |
| `.pni/progress/<target>.yaml` | Scaffolded via `pni progress init` & verified via `pni progress validate` | Defines project milestones, task dependency DAG (`depends_on`), and `git_policy` governance rules. |

To suppress intentional design trade-offs (such as a sandboxed CLI subprocess call or a dev-only Dockerfile stage) without weakening global rules, declare scoped `[[opt_out]]` entries in `.pni/pni.toml` with an explicit engineering `reason` (`>= 10` non-whitespace characters):

```toml
[project]
name = "order-dispatch"
language_version = "3.12"
archetypes = ["web_api"]

[targets]
root = "."
source = ["src"]
tests = ["tests"]
docs = ["README.md"]
exclude = ["src/generated/**"]

[scan]
respect_gitignore = true
include_gitignored = ["uv.lock", "composer.lock", "go.sum"]

[report]
src_dir = "pni_report_src"
output_dir = "pni_report"
formats = ["pdf"]
lang = "en"
style = "google"

[[opt_out]]
id = "CWE-78"
scope = ["src/cli/sandbox_runner.py"]
reason = "Command arguments are validated against an allowlist and executed with shell=False."
```

---

## 3. Complete `pni` CLI Reference (`v0.2.0`)

The `pni` CLI (`src/pni/cli.py`) organizes all workspace initialization, rule discovery, stateful DAG workflow orchestration, Drawlib report compilation, live penetration testing, progress governance, cache cleanup, on-demand Tree-sitter grammar management, and schema/Mermaid validation into one cohesive command hierarchy.

```drawlib align=center code=fold file=cli_command_tree.png caption="The pni CLI Command Hierarchy (pni501 v0.2.0)"
from drawlib.canvas import save, setup
from drawlib.smartarts import MindMapNode
from drawlib.styles import Styles

setup(width=224, height=100, dpi=150)

txt_root = Styles.WhiteBold.patch(text_size=11.0)
txt_group = Styles.DarkBold.patch(text_size=10.0)
txt_leaf = Styles.Dark.patch(text_size=9.8)

root = MindMapNode(
    "pni CLI\n(pni501 v0.2.0)",
    shape="rectangle",
    width=28.0,
    height=13.0,
    style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=txt_root,
    line_style=Styles.DarkBold,
    line_length=5.5,
    horizontal_margin=2.5,
    vertical_margin=2.4,
    children=[
        MindMapNode(
            "Workspace, Rules\n& Validation",
            branch="left",
            shape="rectangle",
            width=34.0,
            height=10.0,
            style=Styles.PrimaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "init | instructions | version",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "rules list [--all] | show [-o]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "validate-score | plan | progress",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "validate-mermaid [--browser]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
        MindMapNode(
            "Grammars & Cache",
            branch="left",
            shape="rectangle",
            width=34.0,
            height=8.0,
            style=Styles.SecondaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "grammars status",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "grammars prefetch [--all] [-f]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "grammars clear",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "cache clean [--docker]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
        MindMapNode(
            "pni workflows",
            branch="right",
            shape="rectangle",
            width=34.0,
            height=8.0,
            style=Styles.PrimaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "list [-c] | show | plan [-o]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "start [--auto-approve] [-p]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "get-action | get-actions [-o]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "push-action [-f] [-n] [-o]",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "run-action | status | inspect",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "rewind [-p] | cancel",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
        MindMapNode(
            "Reports, Pentests\n& Progress",
            branch="right",
            shape="rectangle",
            width=34.0,
            height=10.0,
            style=Styles.SecondaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "pni report init | build",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni pentests init | run",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni progress init | validate",
                    shape="rectangle",
                    width=45.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
    ],
)

root.draw(xy=(112.0, 50.0))
save()
```

### 3.1 Workspace Bootstrap, Rules, Validation, Cache & Grammars Commands

| Command | Arguments & Key Options | Description |
| :--- | :--- | :--- |
| `pni version` | *(or `pni --version` / `-V`)* | Print the installed `pni501` package name and version (`pni501 v0.2.0`). |
| `pni init` | `[--lang/-l <lang>] [--force/-f]` | Auto-detect primary language across 55 languages and scaffold `.pni/` (`pni.toml`, `rules/`, `actions/`, `workflows/`, `instructions.md`, and `cache/.gitignore`). |
| `pni instructions` | *(alias: `pni instruction`)* | Print the AI agent bootstrap and stateful pull-push execution loop guide in Markdown to `stdout`. |
| `pni rules list` | `[--all/-a]` | List active rules for `common` + detected `<lang>` (or all 356 rules across 55 languages + `generic` with `--all`), showing `Builtin` vs `Local (.pni)` status. |
| `pni rules show` | `<name> [--pretty/-p] [--output/-o <path>]` | Output a rule or workflow guide (`common/workflow_guide`, `python/testing`, or short name `testing`) in Markdown, Rich panel (`--pretty`), or file (`-o`). |
| `pni validate-score` | `[score_path]` *(default: `pni_report/full_audit_score.json`)* | Validate an emitted score JSON file against the Pydantic `ScoreResult` v2.0 schema. |
| `pni validate-migration-plan` | `[plan_path]` *(default: `pni_report/migration_plan.json`)* | Validate an emitted migration plan JSON file against the Pydantic `MigrationPlanResult` schema. |
| `pni validate-progress` | `[progress_path]` *(default: `pni_report/project_progress.json`)* | Validate an emitted progress JSON file against the Pydantic `ProgressResult` schema. |
| `pni validate-mermaid` | `[path] [--browser] [--mermaid-js <path>] [--json]` | Validate Mermaid diagrams in `.mmd`/`.md` files (or `stdin`) via Layer 1 static parser and optional Layer 2 Playwright `mermaid.parse()`. |
| `pni cache clean` | `[--docker] [--container-engine auto\|docker\|podman]` | Clean `.pni/cache/` and optionally prune temporary `pni-*` container images, dangling layers, and builder caches. |
| `pni grammars status` | — | Show platform tag, GitHub Release tag (`grammars-v0.2.0`), local cache status, and pinned SHA-256 hashes for the 5 on-demand ABI3 grammars. |
| `pni grammars prefetch` | `[LANG ...] [--all/-a] [--force/-f]` | Pre-download and SHA-256-verify release-managed Tree-sitter grammars (`cobol`, `r`, `vue`, `protobuf`, `dockerfile`) for offline or air-gapped use. |
| `pni grammars clear` | — | Remove locally cached on-demand Tree-sitter grammar binaries from the grammar cache directory. |

```bash
# Initialize .pni/ workspace, inspect rules, and verify Mermaid & JSON artifacts
pni init
pni rules list --all
pni rules show common/workflow_guide -o /tmp/workflow_guide.md
pni validate-score pni_report/full_audit_score.json
pni validate-migration-plan pni_report/migration_plan.json
pni validate-progress pni_report/project_progress.json
pni validate-mermaid architecture_dag.mmd --browser

# Manage on-demand Tree-sitter grammars and clean local/Docker caches
pni grammars status
pni grammars prefetch --all
pni cache clean --docker
```

### 3.2 Stateful DAG Workflow Execution & Debugging Commands (`pni workflows`)

`pni workflows` manages the SQLite DAG state machine (`.pni/cache/workflow_state.db`), Phase 0 pre-flight planning (`plan`), parallel ready-action fan-out (`get-actions`), single-turn start/push chaining (`--pull`, `--next`, `-o`), ad-hoc step debugging (`run-action`), and non-destructive rewinding (`rewind`):

| Command | Arguments & Key Options | Description |
| :--- | :--- | :--- |
| `pni workflows list` | `[--category/-c audit\|migration\|progress\|rollup]` | List workflows in `.pni/workflows/` with category, `based_on` prerequisite link, step count, source targets, and outputs. |
| `pni workflows show` | `<workflow_id>` | Expand composite actions into normalized primitive steps (`1..N`) and run preflight readiness checks for pentests, migrations, and progress plans. |
| `pni workflows plan` | `<workflow_id> [--mermaid] [--json] [--no-container-probe] [-o/--output <path>]` | Preview Phase 0 lightweight recon, discovered monorepo components, human alignment questions, and the validated Mermaid DAG before starting. |
| `pni workflows start` | `<workflow_id> [--supersede] [--auto-approve] [--plan <file>] [--pull/-p] [--json] [-o/--output <path>]` | Start a stateful Workflow v2 run (`wf-...`) in SQLite; `--auto-approve` skips the Phase 1 human gate (CI/batch) and `--pull/-p` immediately fetches the first action. |
| `pni workflows run-action` | `<workflow_id> <action> [--base-url <url>] [--force-pentests] [--fail-on-findings]` | Execute a single step or analyzer directly with zero prior SQLite run setup (ideal for debugging Dockerfiles, pentests, or CI gates). |
| `pni workflows get-action` | `<run_id> [--json] [--full-schema] [-o/--output <path>]` | Auto-advance pending deterministic analyzers and emit the next DAG-ready `act-XX` prompt & compact JSON skeleton (or save cleanly via `-o`). |
| `pni workflows get-actions` | `<run_id> [--ready/--all] [--json] [--full-schema] [-o/--output <path>]` | Auto-advance deterministic steps and list all currently DAG-ready actionable steps for parallel agent/subagent dispatch. |
| `pni workflows push-action` | `<run_id> <action_id> [json] [--file/-f <path>] [--next/-n] [--full-schema] [--json] [-o/--output <path>]` | Validate agent JSON against Pydantic schemas & repo paths, persist to SQLite, and optionally auto-advance and emit the next action (`--next/-n`). |
| `pni workflows status` | `[run_or_wf] [-w <wf>] [-s <status>] [--latest] [-n <limit>] [--json]` | Inspect run history or action-by-action step progress (`done/total`, current step) from SQLite without raw `sqlite3` queries. |
| `pni workflows inspect-action` | `<run_or_wf> <action> [--agent-input \| --deterministic] [--json] [-o <path>]` | Export recorded deterministic analyzer JSON facts or submitted agent JSON inputs from SQLite. |
| `pni workflows rewind` | `<run_or_wf> <action> [--pull/-p] [-o/--output <path>]` *(alias: `retry-action`)* | Rewind a run back to `<action>`, re-sync `.pni/workflows/<id>.yaml` parameters, and clear downstream step outputs for clean re-execution. |
| `pni workflows cancel` | `<run_id> \| --superseded [-w <wf>]` | Cancel an abandoned `in_progress` workflow run or clean up superseded unfinished runs in SQLite. |

```bash
# Preview the execution DAG, start with auto-approve + immediate pull, and advance with --next
pni workflows plan full_audit -o .pni/cache/plan_preview.md
pni workflows start full_audit --supersede --auto-approve --pull -o .pni/cache/next_act.md
pni workflows get-actions wf-1a2b3c4d --json -o .pni/cache/ready_actions.json
pni workflows push-action wf-1a2b3c4d act-02 --file payload.json --next -o .pni/cache/next_act.md

# Debug a single step ad-hoc, inspect SQLite state, rewind, or clean up superseded runs
pni workflows run-action full_audit runtime_verification
pni workflows status wf-1a2b3c4d
pni workflows inspect-action full_audit emit_score --agent-input -o last_score.json
pni workflows rewind wf-1a2b3c4d runtime_verification --pull
pni workflows cancel --superseded
```

### 3.3 Visual Reports, Penetration Tests & Progress Governance Commands

Dedicated subcommand groups manage flat Drawlib report compilation (`pni report`), live loopback HTTP penetration test suites (`pni pentests`), and schedule/Git governance manifests (`pni progress`):

| Command | Arguments & Key Options | Description |
| :--- | :--- | :--- |
| `pni report init` | `[target] [--src-dir pni_report_src] [-l en\|ja] [-s google\|default\|monochrome] [--keep-samples] [-f]` | Non-destructively scaffold or refresh a flat `pni_report_src/` project (`drawlib.toml`, `styles.py`, `utils.py`, `_assets/`, `<lang>/`) while preserving existing authored `*.md` chapters. |
| `pni report build` | `[target] [--src-dir pni_report_src] [-o/--output-dir pni_report] [--html-output-dir <dir>] [--link-check-root <dir>] [-f pdf\|html\|markdown\|images] [--toc/--no-toc] [--no-cache]` | Automatically run `lint_drawlib_chapters()` preflight checks, compile `pni_report/<target>.pdf` (default A4 vector PDF with ToC) and optional HTML/Markdown/PNGs, and fail closed on broken HTML links. |
| `pni pentests init` | `[-w <wf>] [-t <root>] [-s <src>] [-l <lang>] [--force/-f]` | Discover API endpoints from CST facts and materialize explicit `Python + httpx` DAST suites (`conftest.py`, `test_*.py`) in `.pni/pentests/<target>/`. |
| `pni pentests run` | `[-w <wf>] [-t <root>] [-s <src>] [--base-url <url>] [--workflow-id <id>] [--container-engine auto\|docker\|podman\|none] [-f]` | Boot an isolated loopback container (or probe `--base-url`) and execute `.pni/pentests/<target>/` to verify exploitability (`PentestFacts`). |
| `pni progress init` | `[target] [-w <wf>] [--force/-f]` | Scaffold a starter `.pni/progress/<target>.yaml` manifest with milestones, tasks, and `git_policy`. |
| `pni progress validate` | `[target_or_path]` | Validate `.pni/progress/<target>.yaml` schema, ISO-8601 dates, `git_policy`, and acyclic `depends_on` task DAG before starting a progress workflow. |

```bash
# Scaffold and compile a flat self-contained Drawlib report (preflight linting runs automatically)
pni report init full_audit --src-dir pni_report_src --lang en --style google
pni report build full_audit --src-dir pni_report_src --output-dir pni_report -f pdf -f html

# Materialize and execute live HTTP penetration tests for a web service workflow
pni pentests init -w full_audit
pni pentests run -w full_audit

# Initialize and validate a project progress & Git governance plan
pni progress init project_progress -w full_audit
pni progress validate project_progress
```

For end-to-end walkthroughs of these commands in action, see the [Quickstart Guide](../01_getting_started/quickstart.md), [Workflows & Pre-Flight Gates](../03_workflows_and_actions/workflows_guide.md), and [Drawlib Visual Reporter](../04_scoring_and_reports/drawlib_reporter.md).
