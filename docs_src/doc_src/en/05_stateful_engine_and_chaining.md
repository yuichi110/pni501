# 5. Inside the Workflow Engine: Pull-Push Protocol, SQLite State & Migration Chaining

Once a workflow passes its pre-flight readiness gates, `pni501` transitions into a **deterministic stateful execution loop** orchestrated by `src/pni/_workflows/engine.py`, `state_db.py`, `aggregator.py`, and `_migration_engine.py`. Rather than trusting an AI agent to track multi-step progress in volatile chat memory or self-grade code paths without verification, the CLI acts as an authoritative state machine: executing static and container analyzers exactly once per step, synthesizing context-rich prompts on `get-action`, validating Pydantic schemas and repository path grounding on `push-action`, and chaining completed As-Is audit facts directly into downstream To-Be migration workflows.

```drawlib code=fold file=pull_push_sequence.png caption="Chronological Pull-Push Execution & Validation Sequence Across AI Agent, pni Engine, Grounding Analyzers, SQLite, and Cache"
from drawlib.canvas import save, setup
from drawlib.diagrams.sequence import Participant, PhosphorIcon, SequenceDiagram
from drawlib.styles import Styles

d = SequenceDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
    node_card_style=Styles.WhiteBordered.patch(
        text_color=Styles.Dark.text_color, shape_r=1.6
    ),
    autonumber=True,
    col_width=45.0,
    step_y=7.2,
    margin=5.0,
)

agent = d.add(
    Participant("AI Agent", width=23.0, height=15.0, icon=PhosphorIcon.ROBOT, icon_size=5.8)
)
engine = d.add(
    Participant(
        "pni Engine\n(CLI / engine.py)",
        width=28.0,
        height=15.0,
        icon=PhosphorIcon.GEAR_SIX,
        icon_size=5.8,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.8),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.6),
    )
)
analyzers = d.add(
    Participant(
        "Analyzers &\nGrounding",
        width=26.0,
        height=15.0,
        icon=PhosphorIcon.MAGNIFYING_GLASS,
        icon_size=5.8,
    )
)
db = d.add(
    Participant(
        "workflow_state.db\n(SQLite)",
        width=31.0,
        height=15.0,
        icon=PhosphorIcon.DATABASE,
        icon_size=5.8,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.6),
    )
)
cache = d.add(
    Participant(
        "Cache &\nReports",
        width=24.0,
        height=15.0,
        icon=PhosphorIcon.FILE_TEXT,
        icon_size=5.8,
    )
)

agent.request(engine, "workflows start <id> [--supersede]")
engine.request(analyzers, "Preflight: web_pentest & based_on")
with d.opt("--supersede"):
    engine.request(db, "Cancel active runs -> cancelled")
engine.request(db, "INSERT wf-<8hex> & act-01..NN (pending)")
engine.reply(agent, "Return run_id (wf-<8hex>)")

with d.loop("act-01..NN"):
    agent.request(engine, "get-action <run_id>")
    engine.request(db, "SELECT earliest pending/in_progress")
    with d.opt("NULL output"):
        engine.request(analyzers, "Run inspect/ast/run/sec/pentest/mig")
        engine.request(db, "Store deterministic_output_json")
        engine.request(cache, "Write .pni/cache/<wf>/facts.json")
    engine.reply(agent, "Prompt: facts + rules + digest + Schema")

    agent.request(engine, "push-action <run_id> <act_id> -f payload.json")
    engine.request(analyzers, "Check act_id, Pydantic & grounded paths")
    with d.alt("invalid"):
        engine.reply(agent, "Error detail (stays in_progress)")
    with d.else_("valid"):
        engine.request(cache, "Write arch/score/plan.json | check PDF>0B")
        engine.request(db, "Save agent_input_json (act = completed)")
        engine.reply(agent, "Advance -> Next act-YY")

engine.request(db, "SET workflow_runs.status = completed")
engine.reply(agent, "Workflow COMPLETED")

dw, dh = d.get_size()
setup(width=int(dw) + 8, height=int(dh) + 6, dpi=150)
d.draw(xy=(4.0, 3.0))
save()
```

---

## 5.1 Chronological Pull-Push Protocol & Grounding Verification

Every stateful workflow run progresses through three CLI phases in `src/pni/_workflows/engine.py`:

### 1. Session Initialization (`start_workflow_run`)
1. Loads `.pni/workflows/<id>.yaml` with `based_on` target inheritance resolved.
2. Enforces both pre-flight gates (`inspect_base_audit_status` and `inspect_pentests_prerequisite`), raising `WorkflowPrerequisiteError` before touching SQLite if any prerequisite is unmet.
3. Normalizes composite steps into flat `PrimitiveStep` entries (`act-01` .. `act-NN`) and resolves effective `WorkflowOutputs` (`facts`, `score`, `report`).
4. When `--supersede` is passed, calls `db.cancel_active_runs_for_workflow(workflow_id)` to mark older unfinished runs and their remaining steps `cancelled`.
5. Inserts a new `workflow_runs` row (`run_id = wf-<8hex>`, `status = in_progress`, recording `based_on` and `based_on_run_id` when applicable) and `N` sequential `action_runs` rows (`status = pending`).

### 2. Deterministic Execution & Prompt Synthesis (`get_workflow_action`)
When the agent invokes `pni workflows get-action <run_id>`:
- **Idempotent Single-Shot Analyzer Execution**: `_execute_deterministic_step_if_needed()` checks `action.deterministic_output_json is None`. For deterministic primitives (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, and `migration_analyze`), the engine runs the analyzer **once**, stores the serialized Pydantic JSON in `action_runs.deterministic_output_json` alongside `status = in_progress`, and writes the merged `WorkflowFactsBundle` to `.pni/cache/<workflow_id>/facts.json`. Calling `get-action <run_id>` again after an interruption or validation retry re-renders the prompt instantaneously from SQLite without re-running Docker builds, Trivy scans, or HTTP probes.
- **Context-Complete Markdown Synthesis (`_format_action_guide`)**: The CLI assembles and prints:
  1. Step header (`run_id`, `action_id`, sequence `seq/total`, `primitive_type`, `source_action`, and `based_on_run_id`).
  2. Task-specific directive body (`render_action_task_body`), including per-aspect instructions on `record_architecture`, mandatory per-rule verdict checklists on `ai_interpret`, and pre-computed `ReportBlueprint` / `MigrationReportBlueprint` layouts on `write_drawlib_report`.
  3. Accumulated deterministic facts (`ProjectFacts`, `AstFacts`, `RuntimeFacts`, `SecurityFacts`, `PentestFacts`, `MigrationFacts`, `ArchitectureRecord`, and inherited `ScoreResult`).
  4. Full Markdown bodies of active engineering rules (`_render_active_rules`).
  5. Prior `ai_interpret` summaries and—immediately before `emit_score`—the deterministic **`CompiledAuditDigest`** (`compile_workflow_digest` in `aggregator.py`), which pre-deduplicates findings, computes module hotspot density, aggregates rule compliance matrices, and suggests weighted category scores.
  6. Exact `push-action` CLI snippet and Pydantic JSON Schema (`get_expected_input_schema_json`).

### 3. Schema Validation, Grounding Gates & Side Effects (`push_workflow_action`)
When the agent submits `pni workflows push-action <run_id> <action_id> --file payload.json`:
1. **Strict Sequence Guard**: Verifies `action_id == current.action_id`; out-of-order pushes fail immediately without mutating SQLite.
2. **Pydantic Validation & Anti-Hallucination Grounding (`_verify_grounded_paths`)**: Every submitted payload is parsed against its canonical Pydantic v2 model and cross-checked against `AstFacts.module_inventory` and real workspace files (`_is_grounded_repo_path` strips `:symbol` / `#anchor` suffixes and prevents path traversal outside `project_root` / `target_root`):

| Primitive Type | Validated Pydantic Model | Grounding & Deliverable Side Effects on Valid Push |
| :--- | :--- | :--- |
| Deterministic (`project_inspect` .. `migration_analyze`) | `DeterministicAckInput` (`{"acknowledged": true}`) | Confirms analyzer output was reviewed and advances to the paired reasoning step |
| `record_architecture` | `SystemProfile` / `StructureMap` / `ExecutionFlowMap` / `ArchitectureRecord` | Verifies `layers[].paths`, `modules[].path`, `entry_points`, and `execution_flows[].involved_files`; writes `.pni/cache/<wf>/architecture.json` and updates `facts.json` |
| `ai_interpret` | `InterpretationInput` | Verifies `findings[].file_path` and `action_items[].target_files`; normalizes `rule_checks` against active step rules |
| `emit_score` | `ScoreResult` | Verifies finding/action paths; enriches `ScoreResult` with `CompiledAuditDigest`, `score_to_grade()`, and `metrics_snapshot`; writes `reports/<target>_score.json` |
| `emit_migration_plan` | `MigrationPlanResult` | Verifies `target_axes[].affected_files`, `component_mappings[].source_file`, `decision_log[].file_path`, and safe relative `pr_wbs[].target_files`; attaches `MigrationFacts` and writes `reports/<target>_migration_plan.json` |
| `write_drawlib_report` | `ReportCompletionInput` | Verifies every path in `generated_files` (e.g., `reports/<target>.pdf`) exists inside workspace and has `st_size > 0` bytes |

3. **Self-Correction Without State Corruption**: If Pydantic parsing fails, a hallucinated file path is detected, or a PDF deliverable is missing/empty, `push_workflow_action()` returns `(False, error_detail)` while keeping the step in `in_progress`—allowing the AI agent to fix the JSON payload or re-compile the report and retry cleanly. Once valid, `complete_action()` stores `agent_input_json`, marks the step `completed`, and transitions `workflow_runs.status` to `completed` when the final step finishes.

---

## 5.2 SQLite Persistence Schema & 4-State `RunStatus` Lifecycle

All stateful workflow sessions are stored in `.pni/cache/workflow_state.db` (`WorkflowStateDB` in `src/pni/_workflows/state_db.py`, configured with `timeout=30.0` and automatic lightweight `ALTER TABLE` schema migrations for backward compatibility):

```drawlib code=fold file=sqlite_er_and_lifecycle.png caption="SQLite Persistence Schema (workflow_runs & action_runs) and 4-State RunStatus Lifecycle in .pni/cache/workflow_state.db"
from drawlib.canvas import save, setup
from drawlib.diagrams.er import Entity, ERDiagram
from drawlib.diagrams.state import FinalState, InitialState, State, StateDiagram
from drawlib.icons import phosphor
from drawlib.smartarts import Panel
from drawlib.styles import Colors, Styles

setup(width=182, height=100, dpi=150)

left_panel = Panel(
    "SQLite Schema (.pni/cache/workflow_state.db)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
    icon=phosphor.database,
    icon_style=Styles.WhiteBold,
)
left_panel.draw(xy=(3.0, 3.0), width=78.0, height=94.0)

erd = ERDiagram(
    node_style=Styles.WhiteBordered.patch(
        text_color=Styles.Dark.text_color, text_size=9.5
    ),
    header_style=Styles.PrimaryNeutral.patch(text_size=10.2),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.PrimaryBold.patch(text_size=9.5),
)

wf_ent = erd.add(
    Entity(
        name="workflow_runs",
        width=68.0,
        header_height=4.6,
        row_height=3.05,
        header_style=Styles.PrimaryFlat.patch(text_color=Colors.White, text_size=10.2),
    ),
    xy=(42.0, 68.5),
)
wf_ent.add_column("run_id", type="TEXT", pk=True)
wf_ent.add_column("workflow_id", type="TEXT", nullable=False)
wf_ent.add_column("category", type="TEXT", nullable=False)
wf_ent.add_column("based_on", type="TEXT")
wf_ent.add_column("based_on_run_id", type="TEXT")
wf_ent.add_column("status", type="TEXT", nullable=False)
wf_ent.add_column("targets_json", type="TEXT", nullable=False)
wf_ent.add_column("outputs_json", type="TEXT", nullable=False)
wf_ent.add_column("updated_at", type="TEXT", nullable=False)

act_ent = erd.add(
    Entity(
        name="action_runs",
        width=68.0,
        header_height=4.6,
        row_height=3.05,
        header_style=Styles.SecondaryNeutral.patch(
            text_color=Styles.Dark.text_color, text_size=10.2
        ),
    ),
    xy=(42.0, 21.0),
)
act_ent.add_column("run_id", type="TEXT", pk=True, fk=True)
act_ent.add_column("action_id", type="TEXT", pk=True)
act_ent.add_column("seq", type="INTEGER", nullable=False)
act_ent.add_column("primitive_type", type="TEXT", nullable=False)
act_ent.add_column("source_action", type="TEXT")
act_ent.add_column("status", type="TEXT", nullable=False)
act_ent.add_column("deterministic_output_json", type="TEXT")
act_ent.add_column("agent_input_json", type="TEXT")

wf_ent.connect(
    act_ent,
    cardinality="1:1..*",
    start_side="bottom",
    end_side="top",
    label="1..N steps",
)
erd.draw(xy=(0.0, 0.0))

right_panel = Panel(
    "4-State RunStatus Lifecycle (Action & Run FSM)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.PrimaryBold.patch(text_size=10.8),
    icon=phosphor.git_commit,
    icon_style=Styles.PrimaryBold,
)
right_panel.draw(xy=(85.0, 3.0), width=94.0, height=94.0)

sd = StateDiagram(
    node_style=Styles.WhiteBordered.patch(
        text_color=Styles.Dark.text_color, shape_r=1.8, text_size=10.0
    ),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
)

s_init = sd.add(InitialState(), xy=(101.0, 75.5))
s_pend = sd.add(
    State(
        "pending",
        shape="box",
        entry="INSERT act-01..NN",
        width=34.0,
        style=Styles.WhiteBordered.patch(
            text_color=Styles.Dark.text_color, shape_r=1.8, text_size=10.0
        ),
    ),
    xy=(133.0, 75.5),
)
s_prog = sd.add(
    State(
        "in_progress",
        shape="box",
        entry="run analyzer once",
        do="validate push payload",
        width=38.0,
        style=Styles.PrimaryNeutral.patch(shape_r=1.8, text_size=10.0),
    ),
    xy=(133.0, 49.0),
)
s_done = sd.add(
    State(
        "completed",
        shape="box",
        entry="save agent_input_json",
        width=34.0,
        style=Styles.SuccessNeutral.patch(shape_r=1.8, text_size=10.0),
    ),
    xy=(109.0, 20.0),
)
s_canc = sd.add(
    State(
        "cancelled",
        shape="box",
        entry="abort remaining",
        width=32.0,
        style=Styles.DangerNeutral.patch(shape_r=1.8, text_size=10.0),
    ),
    xy=(155.0, 20.0),
)
s_final = sd.add(FinalState(), xy=(109.0, 7.2))

sd.connect(s_init, s_pend, start_side="right", end_side="left")
sd.connect(
    s_pend,
    s_prog,
    event="get-action",
    bend=-0.12,
    start_side="bottom",
    end_side="top",
    text_style=Styles.DarkBold.patch(text_size=9.5, halign="left"),
)
sd.connect(s_prog, s_prog, side="left", event="invalid")
sd.connect(
    s_prog,
    s_done,
    event="valid push",
    bend=0.14,
    start_side="bottom",
    end_side="top",
    style=Styles.SuccessBold,
    text_style=Styles.DarkBold.patch(text_size=9.5, halign="right"),
)
sd.connect(
    s_pend,
    s_canc,
    event="supersede",
    bend=-0.36,
    start_side="right",
    end_side="top",
    style=Styles.DangerBold,
    text_style=Styles.DarkBold.patch(text_size=9.5, halign="left"),
)
sd.connect(
    s_prog,
    s_canc,
    event="cancel",
    bend=0.14,
    start_side="bottom",
    end_side="top",
    style=Styles.DangerBold,
    text_style=Styles.DarkBold.patch(text_size=9.5, halign="right", valign="top"),
)
sd.connect(s_done, s_final, start_side="bottom", end_side="top")

sd.draw(xy=(0.0, 0.0))
save()
```

### Key Table Responsibilities & Cancellation Semantics

- **`workflow_runs`**: Stores session-level provenance, including `run_id` (`wf-<8hex>`), `workflow_id`, `category` (`audit` or `migration`), `based_on` (parent workflow ID), `based_on_run_id` (the exact `wf-<8hex>` audit run pinned at `start` time), frozen `targets_json` (`WorkflowTargets`), and resolved `outputs_json` (`WorkflowOutputs`). New workflow runs start immediately in `in_progress`.
- **`action_runs`**: Stores the ordered `1..N` flattened primitive steps (`PRIMARY KEY (run_id, action_id)`), capturing `rules_json`, `params_json`, `prompt`, `deterministic_output_json` (populated on first `get-action`), and `agent_input_json` (populated on valid `push-action`).
- **Four-State Lifecycle (`RunStatus`)**:
  - `pending` -> `in_progress` -> `completed` forms the standard forward progression for every `action_runs` row.
  - Both `pending` and `in_progress` steps (along with their parent `in_progress` workflow run) can transition to **`cancelled`** via three mechanisms:
    1. `pni workflows cancel <run_id>`: Explicitly aborts an abandoned `in_progress` session (`completed` runs are immutable and raise `ValueError` if cancellation is attempted).
    2. `pni workflows cancel --superseded [-w <workflow_id>]`: Queries `workflow_runs` for unfinished runs that have been overtaken by a newer non-cancelled run of the same `workflow_id` and marks them `cancelled`.
    3. `pni workflows start <workflow_id> --supersede`: Proactively cancels any active runs of `<workflow_id>` before inserting the new `wf-<8hex>` session.

---

## 5.3 Two-Stage Audit-to-Migration Workflow Chaining (`based_on` & `based_on_run_id`)

Large-scale modernization plans fail when an AI agent plans architectural refactoring from scratch without grounded As-Is diagnostics—or when every migration planning iteration has to re-build containers, re-run Trivy vulnerability scans, and re-execute live HTTP penetration probes. `pni501` solves both problems through **two-stage SQLite workflow chaining**:

```drawlib code=fold file=audit_to_migration_chaining.png caption="Two-Stage Audit-to-Migration Workflow Chaining via based_on_run_id and _assemble_facts_bundle() in workflow_state.db"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=166, height=96, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=9.6),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
    node_card_style=Styles.WhiteBordered.patch(
        text_color=Styles.Dark.text_color, shape_r=1.5
    ),
)

g_stage1 = diag.add(
    NodeGroup(
        title="Stage 1: Base Audit Workflow (category: audit, wf-da941741 = COMPLETED)",
        width=160.0,
        height=31.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(3.0, 61.0),
)

s1_static = g_stage1.add(
    Node(
        "ProjectFacts &\nAstFacts",
        width=33.0,
        height=17.5,
        icon=PhosphorIcon.TREE_STRUCTURE,
        icon_size=5.4,
    ),
    xy=(21.0, 12.5),
)
s1_dyn = g_stage1.add(
    Node(
        "Runtime, Security &\nPentestFacts",
        width=36.0,
        height=17.5,
        icon=PhosphorIcon.SHIELD_WARNING,
        icon_size=5.4,
    ),
    xy=(60.5, 12.5),
)
s1_arch = g_stage1.add(
    Node(
        "ArchitectureRecord\n(3 Grounded Aspects)",
        width=36.0,
        height=17.5,
        icon=PhosphorIcon.GRAPH,
        icon_size=5.4,
    ),
    xy=(101.5, 12.5),
)
s1_score = g_stage1.add(
    Node(
        "ScoreResult &\nAudit Report PDF",
        width=33.0,
        height=17.5,
        icon=PhosphorIcon.MEDAL,
        icon_size=5.4,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(140.5, 12.5),
)

n_bridge = diag.add(
    Node(
        "workflow_state.db Link (based_on -> based_on_run_id)\n_assemble_facts_bundle() Inherits All Parent As-Is Facts",
        width=92.0,
        height=13.0,
        icon=PhosphorIcon.DATABASE,
        icon_size=5.4,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.8),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.6),
    ),
    xy=(83.0, 48.0),
)

g_stage2 = diag.add(
    NodeGroup(
        title="Stage 2: Migration Workflow (category: migration, based_on: <audit_id>)",
        width=160.0,
        height=31.0,
        style=Styles.SecondaryNeutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(3.0, 4.0),
)

s2_mig = g_stage2.add(
    Node(
        "migration_analyze\nWaves 1..4, SCC Cuts,\nContracts & DEC-XX",
        width=44.0,
        height=18.5,
        icon=PhosphorIcon.GIT_DIFF,
        icon_size=5.4,
    ),
    xy=(27.0, 12.5),
)
s2_plan = g_stage2.add(
    Node(
        "emit_migration_plan\nValidate Grounding &\n*_migration_plan.json",
        width=46.0,
        height=18.5,
        icon=PhosphorIcon.CHECK_SQUARE_OFFSET,
        icon_size=5.4,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(81.0, 12.5),
)
s2_pdf = g_stage2.add(
    Node(
        "write_migration_report\n7-Chapter Migration\nExecution Plan PDF",
        width=44.0,
        height=18.5,
        icon=PhosphorIcon.FILE_PDF,
        icon_size=5.4,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=1.5),
    ),
    xy=(134.5, 12.5),
)

diag.connect(s1_static, s1_dyn, routing="orthogonal")
diag.connect(s1_dyn, s1_arch, routing="orthogonal")
diag.connect(s1_arch, s1_score, routing="orthogonal")

diag.connect(g_stage1, n_bridge, routing="orthogonal", style=Styles.PrimaryBold)
diag.connect(n_bridge, g_stage2, routing="orthogonal", style=Styles.PrimaryBold)

diag.connect(s2_mig, s2_plan, routing="orthogonal")
diag.connect(s2_plan, s2_pdf, routing="orthogonal", style=Styles.SuccessBold)

diag.draw(xy=(0.0, 0.0))
save()
```

### End-to-End Chaining Mechanics (`engine.py` & `_migration_engine.py`)

1. **Pinning `based_on_run_id` at Session Start**:
   - When `pni workflows start <migration_id>` executes, `inspect_base_audit_status()` locates the most recently `completed` run of `workflow_def.based_on` in `workflow_state.db` (e.g., `wf-da941741`) and records its exact identifier in `workflow_runs.based_on_run_id`.
   - Pinning `based_on_run_id` guarantees full reproducibility: even if someone later starts a new in-progress audit run, the active migration session remains bound to the exact completed audit snapshot it was validated against.

2. **Automatic Fact Bundle Reconstruction (`_assemble_facts_bundle`)**:
   - On every `get-action` and `push-action` inside Stage 2, `_assemble_facts_bundle(run, actions, db=db)` first extracts any facts produced in the current migration run, then queries `db.get_actions(run.based_on_run_id)` to hydrate:
     - `bundle.project_facts`, `bundle.ast_facts`, `bundle.runtime_facts`, `bundle.security_facts`, and `bundle.pentest_facts` from the parent audit's `deterministic_output_json` columns.
     - `bundle.architecture_record` reconstructed across the parent audit's completed `record_architecture` steps (`purpose_and_stack`, `layers_and_modules`, `flows_and_state`).
     - `bundle.base_score_result` deserialized from the parent audit's `emit_score` `agent_input_json`, rendered directly into Stage 2 prompts as the **Baseline Audit Score Summary** (`overall_score`, category scores, and top inherited findings).

3. **Deterministic Migration Intelligence (`migration_analyze`)**:
   - Consuming the inherited `ProjectFacts`, `AstFacts`, and `RuntimeFacts` alongside the pinned YAML `MigrationOptions` (`brief`, `migration_strategy`, `api_compatibility`, `bug_handling_policy`, `codemod_tool`), `execute_migration_analyze_json()` computes `MigrationFacts`:
     - **Topological Refactoring Waves (`Waves 1..4`) & SCC Cycle Cuts**: Orders internal modules from zero-dependency leaves (`Wave 1`) up to ingress/orchestrators (`Wave 4`) and computes minimum-impact `cycle_cuts` across strongly connected components.
     - **Implicit Endpoint & Environment Contracts**: Extracts HTTP/CLI request and response keys (`implicit_contracts`) plus scattered environment variables and defaults (`env_contracts`) to seed Phase 0 characterization tests.
     - **Stateful, Database & HTTP Boundary Touchpoints**: Locates process-local mutable state, raw SQL calls, and outbound RPCs (`boundary_touchpoints`) paired with recommended Clean Architecture Port/Adapter targets.
     - **Mechanical Codemod Recipes & `DEC-XX` Ambiguity Candidates**: Matches stack-appropriate OpenRewrite, Rector, or Ruff recipes (`mechanical_codemods`) and isolates Hyrum's Law legacy quirks—such as loose equality auth checks, MD5 digests, unsafe cookie deserialization, or hidden debug keys—into numbered **`DEC-01..NN`** `spec_vs_bug_candidates`.

4. **Grounded Plan Persistence & 7-Chapter Visual Compilation**:
   - On `emit_migration_plan`, `validate_and_persist_migration_plan()` verifies that every As-Is path referenced in `target_axes[].affected_files`, `target_architecture.component_mappings[].source_file`, and `decision_log[].file_path` exists in the inherited `AstFacts.module_inventory` or workspace, checks that `pr_wbs[].target_files` are safe relative paths, embeds `MigrationFacts`, and writes `reports/<target>_migration_plan.json`.
   - Finally, `write_migration_report` (`write_drawlib_report` configured with `report_kind: "migration"`) generates `.pni/cache/<migration_id>/migration_blueprint.json` and guides the agent through compiling the 7-chapter (`00_cover.md` .. `06_*.md`) Drawlib Migration Execution Plan PDF (`reports/<target>.pdf`), verified non-empty before `workflow_runs.status` transitions to `completed`.
