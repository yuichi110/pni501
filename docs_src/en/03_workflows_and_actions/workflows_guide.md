# Workflows & Pre-Flight Readiness Gates

Executing a reliable software health audit, live penetration test, or phased modernization plan requires deterministic coordination before state is frozen into SQLite. `pni501` unifies this lifecycle under `pni workflows`, combining **three complementary operating modes**, **fail-closed pre-flight readiness gates**, and **declarative YAML target inheritance and composite step expansion** across Python, Java, PHP, Go, TypeScript, and JavaScript repositories.

```drawlib align=center code=fold file=workflow_three_modes.png caption="The Three Operating Modes of pni workflows: Stateful Pull-Push, Stateless Ad-Hoc Runner, and Run Monitoring & Inspection"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=174, height=84, dpi=150)

p1 = Panel(
    "Mode 1: Stateful Pull-Push",
    header_variant="filled",
    header_height=10.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
    icon=phosphor.database,
    icon_style=Styles.WhiteBold,
)
p1.draw(xy=(3.0, 3.0), width=54.0, height=78.0)
ix1, iw1, ih1 = p1.get_content_box(xy=(3.0, 3.0), width=54.0, height=78.0, padding=(2.5, 2.5))

c1 = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.4,
)
c1.add("start / get / push-action", "Persists wf-<8hex> & act-01..NN\nin .pni/cache/workflow_state.db", icon=phosphor.hard_drives)
c1.add("Grounding & Schema Gates", "Enforces step order, Pydantic\nmodels & AST path verification", icon=phosphor.shield_check)
c1.add("Official Deliverables", "Emits *_score.json, *_plan.json\nand compiled A4 vector PDF", icon=phosphor.file_pdf)
c1.draw(xy=ix1, width=iw1, height=ih1)

p2 = Panel(
    "Mode 2: Ad-Hoc Runner",
    header_variant="filled",
    header_height=10.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=11.2),
    icon=phosphor.lightning,
    icon_style=Styles.SecondaryBold,
)
p2.draw(xy=(60.0, 3.0), width=54.0, height=78.0)
ix2, iw2, ih2 = p2.get_content_box(xy=(60.0, 3.0), width=54.0, height=78.0, padding=(2.5, 2.5))

c2 = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.DarkBold.patch(text_size=10.0),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=2.4,
)
c2.add("run-action <wf> <selector>", "Stateless adhoc.py runner; zero\nSQLite reads, writes, or locks", icon=phosphor.prohibit)
c2.add("Lazy In-Memory Facts", "Computes Project & AST facts\non demand for target selector", icon=phosphor.cpu)
c2.add("Fast Iteration Flags", "--base-url, --force-pentests &\n--fail-on-findings for CI/probes", icon=phosphor.terminal_window)
c2.draw(xy=ix2, width=iw2, height=ih2)

p3 = Panel(
    "Mode 3: Monitor & Rewind",
    header_variant="filled",
    header_height=10.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.PrimaryBold.patch(text_size=11.2),
    icon=phosphor.magnifying_glass,
    icon_style=Styles.PrimaryBold,
)
p3.draw(xy=(117.0, 3.0), width=54.0, height=78.0)
ix3, iw3, ih3 = p3.get_content_box(xy=(117.0, 3.0), width=54.0, height=78.0, padding=(2.5, 2.5))

c3 = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.Neutral,
    badge_text_style=Styles.DarkBold.patch(text_size=10.0),
    icon_style=Styles.DarkBold,
    direction="vertical",
    spacing=2.4,
)
c3.add("status [--latest | <run>]", "Inspect active/completed runs\nand done/total step progress", icon=phosphor.list_checks)
c3.add("inspect-action <run> <act>", "Extract --agent-input or\n--deterministic [-o file.json]", icon=phosphor.export)
c3.add("rewind / cancel", "Rewind to step, re-sync YAML,\nor cancel superseded runs", icon=phosphor.broom)
c3.draw(xy=ix3, width=iw3, height=ih3)

save()
```

---

## 1. The Three Operating Modes of `pni workflows`

To support formal end-to-end evaluations, rapid single-step iteration, and non-invasive SQLite inspection without forcing operators or AI agents to write raw `sqlite3` queries, `pni workflows` provides three distinct operating modes:

| Mode | Subcommands & Key Flags | Touches `workflow_state.db`? | Primary Use Cases |
| :--- | :--- | :--- | :--- |
| **Mode 1: Full Stateful Pull-Push** (`engine.py`) | `start <wf> [--supersede]`<br>`get-action <run_id>`<br>`push-action <run_id> <act_id> [JSON \| -f file.json]` | **Read / Write** (creates `wf-<8hex>` & `act-01..NN`, persists outputs & inputs) | Official repository audits, `based_on` chained migration plans, score/plan JSON emission, and A4 PDF report compilation |
| **Mode 2: Ad-Hoc Single-Step Runner** (`adhoc.py`) | `run-action <wf> <selector>`<br>`[--base-url URL]`<br>`[--force-pentests]`<br>`[--fail-on-findings]` | **None** (100% stateless in-memory `WorkflowFactsBundle`) | Developing `.pni/pentests/<target>/` HTTP probes, tuning `.pni/dockerfiles/`, testing a single composite step, or CI gating |
| **Mode 3: Monitoring, Rewind & Cleanup** (`inspector.py`, `state_db.py`) | `status [run_or_wf] [--latest] [-w wf] [-s status]`<br>`inspect-action <run_or_wf> <action> [--agent-input \| --deterministic] [-o path]`<br>`rewind <run_or_wf> <action> [--pull]`<br>`cancel [<run_id> \| --superseded]` | **Read** (`status`, `inspect-action`) / **State Update** (`rewind`, `cancel`) | Checking `done/total` progress, exporting recorded JSON payloads, rewinding to re-run a modified step, and retiring superseded runs |

### 1.1 Stateless Lazy Evaluation in `run-action`

When an operator or agent runs `pni workflows run-action <workflow_id> <selector>`, `run_workflow_action_adhoc()` loads and normalizes `.pni/workflows/<workflow_id>.yaml` without creating a SQLite run or enforcing workflow-wide `based_on` prerequisites:

- **On-Demand Prerequisite Synthesis**: If the matched primitive requires upstream metadata—for example, `web_pentest` or `migration_analyze` needing `ProjectFacts` and `AstFacts`, or `run_check` / `security_scan` needing `ProjectFacts`—the runner computes them lazily in memory and suppresses silent helper outputs from the rendered Markdown.
- **Paired AI Guidance Preview**: When `<selector>` matches a composite `uses:` step (such as `repo_structure_audit` or `web_penetration_audit`), `adhoc.py` executes the deterministic primitive(s) and renders both the extracted facts and the paired `ai_interpret` checklist, active engineering rules, and expected JSON Schema in one stdout pass.
- **Exit-Code Gating**: Execution or container boot errors (`status in {"error", "timeout"}`) always exit with code `1`; passing `--fail-on-findings` additionally exits with code `1` whenever unit test failures, Trivy vulnerabilities/misconfigurations/secrets, or live penetration findings are detected.

### 1.2 Six Standard Workflow Patterns Across 6 Languages

Across **Python, Java, PHP, Go, TypeScript, and JavaScript**, `pni init` scaffolds starter `.pni/workflows/*.yaml` definitions (`full_audit` and `quick_check`) that can be tailored into six canonical workflow patterns:

| Workflow Pattern | Category | Included Composite Stages | Primary Deliverables |
| :--- | :--- | :--- | :--- |
| **`full_audit`** | `audit` | `architecture_analysis` + `<lang>` structure/AST/test + archetype audits + `container_runtime_audit` + `security_vulnerability_audit` (+ `web_penetration_audit`) + `emit_score` + `write_drawlib_report` | `reports/<target>_score.json` + 7-chapter A4 PDF (`reports/<target>.pdf`) |
| **`quick_check` / `scoring`** | `audit` | Fast static `<lang>` structure/AST/test audits + `emit_score` (omits container/Trivy/PDF steps) | `reports/<target>_score.json` |
| **`security_audit`** | `audit` | `repo_structure_audit` + `<lang>_ast_audit` + `supply_chain_audit` + `security_vulnerability_audit` + `emit_score` | Security & supply-chain focused `*_score.json` |
| **`pentest`** | `audit` | `<lang>_ast_audit` (endpoint discovery) + `web_penetration_audit` (`127.0.0.1` loopback container + `httpx` suite) + `emit_score` | `.pni/cache/<wf>/pentest/pentest_facts.json` + `*_score.json` |
| **`migration_plan`** | `migration` | Requires `based_on: <audit_id>`; executes `migration_proposal` (`migration_analyze` + `ai_interpret` + `emit_migration_plan`) + `write_migration_report` | `reports/<target>_migration_plan.json` + Migration A4 PDF |
| **`report`** | `audit` / `migration` | Re-invokes `write_drawlib_report` or `write_migration_report` (or via `pni workflows rewind <wf> create_report --pull`) | Refreshed `reports_src/<target>_src/` + compiled `reports/<target>.pdf` |

---

## 2. Fail-Closed Pre-Flight Readiness Workflow

Because `pni workflows start <id>` freezes resolved directory targets, action parameters, and rule bindings into `.pni/cache/workflow_state.db`, `.pni/workflows/<id>.yaml` serves as the **Single Source of Truth (SSOT)** for every run. Before starting a stateful workflow session, human operators and AI agents follow a four-step readiness sequence enforced by `pni workflows show <id>` and `start_workflow_run()`:

```drawlib align=center code=fold file=workflow_preflight_flowchart.png caption="End-to-End pni workflows Operator & Agent Readiness Flowchart: Setup, Fail-Closed Pre-Flight Gates, and Execution"
from drawlib.canvas import save, setup
from drawlib.diagrams.flow import Decision, End, FlowDiagram, Process, Start
from drawlib.styles import Styles

setup(width=176, height=112, dpi=150)

flow = FlowDiagram(
    node_style=Styles.WhiteBordered.patch(
        text_color=Styles.Dark.text_color, shape_r=1.6, text_size=10.0
    ),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=10.0),
    width=170.0,
    height=106.0,
)

flow.add_lane("1. Author & Inspect", width=48.0)
flow.add_lane("2. Pre-Flight Readiness Gates", width=58.0)
flow.add_lane("3. Remedies & Deliverables", width=64.0)

n_init = flow.add(
    Start(
        "pni init &\nTailor <id>.yaml",
        width=38.0,
        height=12.0,
        style=Styles.PrimaryNeutral.patch(shape_r=6.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.2),
    ),
    xy=(24.0, 86.0),
)

n_show = flow.add(
    Process(
        "pni workflows show <id>\n(Expand & Check Gates)",
        width=40.0,
        height=13.0,
        style=Styles.Neutral.patch(shape_r=1.6),
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(24.0, 62.0),
)

g_pentest = flow.add(
    Decision(
        "Gate 1: web_pentest\nSuite Ready?",
        width=42.0,
        height=16.0,
        style=Styles.SecondaryNeutral,
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(77.0, 84.5),
)

r_pentest = flow.add(
    Process(
        "Fail-Closed Block!\npni pentests init -w <id> + Probes\n-> run-action <id> web_pentest",
        width=50.0,
        height=15.0,
        style=Styles.DangerNeutral.patch(shape_r=1.6),
        text_style=Styles.DangerBold.patch(text_size=10.0),
    ),
    xy=(141.0, 84.5),
)

g_based = flow.add(
    Decision(
        "Gate 2a: Migration\nbased_on Done?",
        width=42.0,
        height=16.0,
        style=Styles.SecondaryNeutral,
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(77.0, 59.5),
)

r_based = flow.add(
    Process(
        "Audit Prerequisite Block!\npni workflows start <audit_id>\n& Complete Base Audit First",
        width=50.0,
        height=14.5,
        style=Styles.DangerNeutral.patch(shape_r=1.6),
        text_style=Styles.DangerBold.patch(text_size=10.0),
    ),
    xy=(141.0, 59.5),
)

g_brief = flow.add(
    Decision(
        "Gate 2b: Brief &\nGuardrails Pinned?",
        width=42.0,
        height=16.0,
        style=Styles.SecondaryNeutral,
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(77.0, 34.5),
)

r_brief = flow.add(
    Process(
        "Ambiguity Hints Found!\nAsk User -> Pin brief & non-auto\nYAML -> Re-run show <id>",
        width=50.0,
        height=15.0,
        style=Styles.WarningNeutral.patch(shape_r=1.6),
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(141.0, 34.5),
)

n_start = flow.add(
    Process(
        "pni workflows start <id>\n[--supersede] -> wf-<8hex>",
        width=40.0,
        height=13.0,
        style=Styles.PrimaryFlat.patch(shape_r=1.6),
        text_style=Styles.WhiteBold.patch(text_size=10.0),
    ),
    xy=(24.0, 11.5),
)

n_loop = flow.add(
    Process(
        "Stateful Pull-Push Loop\nget-action <-> push-action",
        width=42.0,
        height=13.0,
        style=Styles.PrimaryNeutral.patch(shape_r=1.6),
        text_style=Styles.PrimaryBold.patch(text_size=10.0),
    ),
    xy=(77.0, 11.5),
)

n_done = flow.add(
    End(
        "COMPLETED\n(JSON + A4 PDF)",
        width=42.0,
        height=12.0,
        style=Styles.SuccessNeutral.patch(shape_r=6.0),
        text_style=Styles.SuccessBold.patch(text_size=10.2),
    ),
    xy=(141.0, 11.5),
)

n_init.connect(n_show, start_side="bottom", end_side="top")
n_show.connect(g_pentest, label="Inspect", start_side="right", end_side="left")

g_pentest.connect(r_pentest, label="Missing", start_side="right", end_side="left", style=Styles.DangerBold)
g_pentest.connect(g_based, label="Pass / N/A", start_side="bottom", end_side="top")

g_based.connect(r_based, label="No", start_side="right", end_side="left", style=Styles.DangerBold)
g_based.connect(g_brief, label="Yes / Audit", start_side="bottom", end_side="top")

g_brief.connect(r_brief, label="Hints", start_side="right", end_side="left")
g_brief.connect(n_start, label="Ready", start_side="left", end_side="top", style=Styles.PrimaryBold)

n_start.connect(n_loop, start_side="right", end_side="left", style=Styles.PrimaryBold)
n_loop.connect(n_done, label="Done", start_side="right", end_side="left", style=Styles.SuccessBold)

flow.draw(xy=(3.0, 3.0))
save()
```

### 2.1 Gate 1: Fail-Closed Web Penetration Test Suite Check (`web_pentest`)

Whenever a workflow's normalized steps include `web_pentest` (typically via `uses: web_penetration_audit`) and `force_regenerate_pentests` is `false`, `inspect_pentests_prerequisite()` inspects `.pni/pentests/<target>/`:

- **Fail-Closed Enforcement**: If `.pni/pentests/<target>/` is missing `conftest.py` or at least one `test_*.py` probe suite, `pni workflows show <id>` prints a red blocking panel and `pni workflows start <id>` raises `WorkflowPrerequisiteError` immediately—preventing half-baked runs that would stall mid-pipeline.
- **Remedy Loop**: Materialize the target's `Python + httpx` suite with `pni pentests init`, inspect AST-discovered routes and authentication guards to add target-specific HTTP security probes in `.pni/pentests/<target>/test_*.py`, and verify statelessly via `run-action` before starting the stateful workflow:

```bash
# 1. Materialize baseline + AST-discovered route probes in .pni/pentests/<target>/
pni pentests init -w <workflow_id>

# 2. Customize .pni/pentests/<target>/test_*.py and verify statelessly in Mode 2
pni workflows run-action <workflow_id> web_pentest

# 3. Confirm all pre-flight readiness gates pass before starting Mode 1
pni workflows show <workflow_id>
```

### 2.2 Gate 2: Migration Prerequisite (`based_on`) & Guardrail Scrutiny

Migration workflows (`category: migration`) must declare `based_on: <audit_id>`:

- **Gate 2a — SQLite Base Audit Gate (`based_on`)**: On `show` and `start`, `inspect_base_audit_status()` queries `.pni/cache/workflow_state.db` for the latest `completed` run of `<audit_id>`. If `<audit_id>` has never run or its latest run is still `in_progress`, `start` blocks with an actionable error instructing the agent to start or resume `<audit_id>` and finish the As-Is audit first.
- **Gate 2b — Pre-Execution Brief & Guardrail Scrutiny**: `check_migration_preflight_hints()` inspects `MigrationOptions` and the merged `brief` / `brief_file` text, surfacing structured `PreflightReadinessHint` warnings whenever specifications are underspecified:

| Hint Code | Trigger Condition | Required Operator / Agent Action Before `workflows start` |
| :--- | :--- | :--- |
| **`MISSING_BRIEF`** | Both `with.brief` and `with.brief_file` resolve to empty text | Cross-check As-Is audit facts, ask the user for target stack, boundaries, and compatibility, and write `with.brief: \|` into YAML |
| **`BRIEF_TOO_TERSE`** | Resolved brief is shorter than `40` characters | Expand brief with concrete runtime/framework versions, DB/Cache backing stores, and explicit Non-Goals |
| **`VAGUE_BRIEF_TERMS`** | Brief contains placeholders such as `"to latest"`, `"TBD"`, `"TODO"`, `"undecided"`, `"最新"`, `"未定"`, or `"いい感じ"` | Replace vague placeholders with pinned target versions (e.g., `Java 21 LTS + Spring Boot 3.4`, `PHP 8.3 + Laravel 11`, `Go 1.23`, `Node 22 LTS`) |
| **`UNPINNED_STRATEGY`** | `migration_strategy` is left at `"auto"` | Confirm rollout model with user and pin `"phased_pr"`, `"strangler_fig"`, or `"rewrite"` |
| **`UNPINNED_CODEMOD_TOOL`** | `codemod_tool` is left at `"auto"` | Pin `"openrewrite"`, `"rector"`, `"ruff"`, `"gofmt"`, `"jscodeshift"`, or `"manual_only"` matching the confirmed target stack |

---

## 3. Workflow YAML Schema, Normalization & Action Selectors

Workflow files live in `.pni/workflows/<id>.yaml` and validate against `WorkflowDefinition`. During loading and normalization (`normalize_workflow_steps()`), declarative steps are transformed into flat `PrimitiveStep` sequences with deterministic parameter interpolation and cross-step output propagation.

### 3.1 Target Inheritance, Composite Expansion & Token Interpolation

1. **Category & `based_on` Invariants (`WorkflowDefinition`)**:
   - `category: audit` (default) cannot declare `based_on`.
   - `category: migration` (and `category: progress`) **must** declare `based_on: <workflow_id>` referencing an upstream workflow YAML (self-references and circular chains raise `WorkflowPrerequisiteError`).
   - `_merge_inherited_targets()` copies `root`, `source`, `tests`, `docs`, and `exclude` from the upstream workflow automatically while preserving any explicit child field overrides.
2. **Composite Expansion (`expand_composite_action`)**:
   - Steps declaring `uses: <composite_id>` resolve `<composite_id>.yaml` through the three-layer cascade (`.pni/actions/` > built-in `<lang>/` > built-in `common/`).
   - Each expanded primitive receives deterministic ID `{step_id}__{idx}_{primitive_type}` (for example, `repo_and_deps__1_project_inspect` and `repo_and_deps__2_ai_interpret`), deduplicated merged `rules`, merged `with` parameters (`step.with` overrides composite defaults), and `source_action = <composite_id>`.
   - Steps declaring `action: <primitive_type>` map 1-to-1 to a single `PrimitiveStep` with `id = step.id` and `source_action = None`.
3. **Placeholder Interpolation & Downstream Path Propagation**:
   - `_finalize_primitive_params()` injects workspace target context (`workflow_id`, `workflow_category`, `target_root`, `source_targets`, `test_targets`, `doc_targets`, `facts_path`) alongside canonical defaults (`src_dir: "reports_src"`, `output_dir: "reports"`, `target: "{workflow_id}"`, `score_path: "{output_dir}/{target}_score.json"`), then interpolates `{workflow_id}`, `{target}`, `{output_dir}`, and `{src_dir}` across all string parameters.
   - `_propagate_emitted_score()` forwards the resolved `score_path` from `emit_score` (or `plan_path` from `emit_migration_plan`) into subsequent `write_drawlib_report` steps automatically unless overridden explicitly on the report step.

### 3.2 Example A: Full Service Audit Workflow (`category: audit`)

```yaml
id: order_api_audit
category: audit
name: Order API Health, Security & Penetration Audit
description: Static AST/supply-chain audit, 3-aspect architecture comprehension, container/Trivy checks, and live HTTP pentest.

targets:
  root: "services/order_api"
  source: ["order_app"]
  tests: ["tests"]
  docs: ["README.md"]

steps:
  - id: arch_recording
    uses: architecture_analysis
  - id: repo_and_deps
    uses: repo_structure_audit
  - id: ast_and_quality
    uses: python_ast_audit
  - id: test_suite
    uses: python_test_audit
  - id: service_readiness
    uses: service_readiness_audit
  - id: runtime_verification
    uses: container_runtime_audit
  - id: security_audit
    uses: security_vulnerability_audit
  - id: web_pentest
    uses: web_penetration_audit
  - id: output_score
    uses: emit_score
    with:
      output_dir: "reports/python"
      target: "order_api"
  - id: create_report
    uses: write_drawlib_report
    with:
      src_dir: "reports_src/python"
      output_dir: "reports/python"
      target: "order_api"
      lang: "en"
      style: "google"
```

### 3.3 Example B: Chained Migration Workflow (`category: migration`)

```yaml
id: order_api_migration
category: migration
based_on: order_api_audit          # Inherits targets & requires COMPLETED run in workflow_state.db
name: Phased Migration Plan - Legacy Flask Order API -> Python 3.12 + FastAPI

steps:
  - id: migration_intelligence_and_plan
    uses: migration_proposal
    with:
      output_dir: "reports/python"
      target: "order_api_migration"
      migration_strategy: "phased_pr"     # Pinned (non-"auto"): phased_pr | strangler_fig | rewrite
      api_compatibility: "strict"         # Pinned: strict | versioned_v2 | flexible
      bug_handling_policy: "ask_human"    # Pinned: ask_human | preserve_behavior | fix_in_phase3
      codemod_tool: "ruff"                # Pinned: openrewrite | rector | ruff | manual_only
      brief: |
        Target Stack & Infrastructure (Confirmed):
          - Runtime & Web: Python 3.12 + FastAPI + Pydantic v2 DTOs (replace Flask untyped request.json)
          - Persistence & State: PostgreSQL 16 via SQLAlchemy 2.0 + Redis 7 TTL cache (eliminate module globals)
        Architecture & Compatibility Guardrails:
          - Clean Architecture rings (`domain` / `usecase` / `port` / `adapter`) with zero framework imports in `domain`.
          - Strict external HTTP route and JSON key backward compatibility; isolate Hyrum's Law quirks in DEC-XX log.
        Confirmed Non-Goals:
          - Do not split into separate microservices during this migration.

  - id: compile_migration_report
    uses: write_migration_report
    with:
      src_dir: "reports_src/python"
      output_dir: "reports/python"
      target: "order_api_migration"
      lang: "en"
      style: "google"
```

### 3.4 Action Selector Priority Rules (`run-action` & `inspect-action`)

Both `pni workflows run-action <wf> <selector>` and `pni workflows inspect-action <run_or_wf> <selector>` (as well as `pni workflows rewind <run_or_wf> <selector>`) accept flexible human- and agent-friendly selectors resolved in strict priority order:

| Priority | Selector Form | Example | `run-action` Match (`PrimitiveStep`) | `inspect-action` / `rewind` Match (`ActionRunRecord`) |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Step Index / `act-XX`** | `act-07` or `7` | 1-based index into normalized `primitives` | Exact `seq == 7` (or exact `action_id == "act-07"`) |
| **2** | **Expanded Primitive ID** | `web_pentest__1_web_pentest` | Exact `prim.id == selector` | Stored as `act-XX` in SQLite; matched via index or step name |
| **3** | **Workflow Step ID** | `web_pentest` or `repo_and_deps` | All primitives whose `prim.id` prefix before `__` equals `selector` | Matched when `name` or `source_action` equals `selector` |
| **4** | **Composite `uses` ID** | `web_penetration_audit` | All primitives with `source_action` (or leaf after `/`) matching `selector` | All recorded actions with `source_action` (or leaf) matching `selector` |
| **5** | **Primitive Type** | `ast_analyze` or `emit_score` | All primitives where `prim.type.value == selector` | All recorded actions where `primitive_type.value == selector` |

> **Multi-Step Narrowing in `inspect-action`**: When a composite selector such as `web_penetration_audit` matches both a deterministic step (`act-15: web_pentest`) and its paired AI step (`act-16: ai_interpret`), passing `--deterministic` automatically narrows the result to steps carrying `deterministic_output_json`, whereas passing `--agent-input` narrows the result to steps carrying substantive `agent_input_json`.

Next, explore the [15 Actions & 12 Primitives](actions_pipeline.md) catalog to see how composite YAML building blocks expand into deterministic and AI-grounded execution steps, or dive into [Analyzers & Live Pentest](analyzers_and_pentest.md) and the [Stateful Pull-Push Engine](../02_architecture/stateful_engine.md).
