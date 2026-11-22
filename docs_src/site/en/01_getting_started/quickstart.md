# Quickstart Guide

Get up and running with `pni501` (`v0.2.0`) in minutes. This guide walks through installing the pure-Python CLI, inspecting on-demand Tree-sitter grammars (`pni grammars`), initializing `.pni/` in any of the **55 supported languages**, previewing the Phase 0 recon plan & Mermaid DAG (`pni workflows plan`), executing the single-command **Workflow v2** Pull-Push loop (`--pull`, `--file`, `--next`, `-o`), and building a flat, self-contained A4 PDF report (`pni_report_src -> pni_report`).

```drawlib align=center code=fold file=pni_quickstart_flow.png caption="Four-Step Workflow v2 Quickstart Lifecycle: From pni init & Plan Gate to Validated Score + Delta & Flat A4 PDF Report"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, ChevronProcess
from drawlib.styles import Styles

setup(width=156, height=70, dpi=150)

pipeline = ChevronProcess(
    style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    corner_angle=65.0,
    spacing=1.8,
    flat_left_end=True,
)
pipeline.add(
    "1. Install & Init",
    description="pip install pni501\npni init",
)
pipeline.add(
    "2. Plan & Gates",
    description="pni workflows plan\n& confirm_plan",
    style=Styles.Neutral,
)
pipeline.add(
    "3. Single-Cmd Loop",
    description="start --pull ->\npush-action --next",
    style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    description_style=Styles.White.patch(text_size=10.0),
)
pipeline.add(
    "4. Flat PDF Report",
    description="pni report init/build\npni_report/<t>.pdf",
    style=Styles.SuccessFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    description_style=Styles.White.patch(text_size=10.0),
)
pipeline.draw(xy=(3.0, 43.0), width=150.0, height=23.0)

commands = CardList(
    style=Styles.Neutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.4),
    description_style=Styles.Dark.patch(text_size=9.8),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.DarkBold,
    spacing=3.0,
)
commands.add(
    "Scaffold .pni/",
    "55-lang auto-detect + lazy\nABI3 grammars (pni grammars)",
    icon=phosphor.folder_plus,
)
commands.add(
    "Plan & Pre-Flight",
    "Phase 0 recon, Mermaid DAG\n& confirm_plan approval",
    icon=phosphor.magnifying_glass,
)
commands.add(
    "Parallel DAG Exec",
    "Auto-runs CST/Docker/Trivy\nTriage FPs & Evidence Delta",
    icon=phosphor.arrows_left_right,
)
commands.add(
    "Flat Deliverables",
    "pni_report_src/_facts/ ->\nScore, SARIF & A4 PDF",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.file_pdf,
)
commands.draw(xy=(3.0, 4.0), width=150.0, height=34.0)
save()
```

## 1. Prerequisites, Installation & On-Demand Grammars

`pni501` requires **Python 3.11+** (`>=3.11`). For containerized runtime checks (`run_check`), vulnerability scans (`security_scan`), and loopback penetration tests (`web_pentest`), **Docker** (or Podman) should also be available on the host machine.

`pni501` ships as a pure-Python (`py3-none-any`) wheel backed by **52 official PyPI `tree-sitter-*` `abi3` wheels**. The remaining **5 MIT-licensed grammars** (`COBOL`, `R`, `Vue`, `Protocol Buffers`, and `Dockerfile`) are downloaded lazily on first use from GitHub Releases with pinned SHA-256 verification—or prefetched upfront for air-gapped / offline environments:

```bash
# Option A: Install via pip
pip install pni501

# Option B: Add to a uv project or tool environment
uv add pni501

# Verify installation and inspect CLI subcommands
pni --version   # or: pni version
pni --help

# Optional: inspect or prefetch the 5 GitHub Releases ABI3 grammars for offline use
pni grammars status
pni grammars prefetch --all
```

## 2. Step 1: Initialize `.pni/` in Your Repository

Navigate to the root of the repository you want to evaluate and run `pni init`:

```bash
pni init
```

`pni init` automatically detects the primary language across the **55-language registry** (20 Tier A Full Audit, 20 Tier B Declarative Static Audit, plus 15 Tier C Companion IaC/Schema/Build/Config languages) from repository manifests and source files, then scaffolds `.pni/`:

- `.pni/pni.toml` — Project-wide configuration for default target directories (`[targets]`) and flat Drawlib report settings (`[report]`, defaulting to `pni_report_src -> pni_report`).
- `.pni/workflows/full_audit.yaml` & `quick_check.yaml` — Language-tailored **Workflow v2** conditional DAG definitions (`needs:` / `when:`), sourced from the **112 built-in workflow templates**.
- `.pni/rules/` & `.pni/actions/` — Local override directories layering over the **356 built-in rules** and **182 action templates**.
- `.pni/instructions.md` — Workflow v2 bootstrap instructions for Code AI Agents.

## 3. Step 2: Preview Phase 0 Plan, Mermaid DAG & Pre-Flight Gates

Before launching a stateful run, verify that `targets.root`, `targets.source`, `targets.tests`, and `targets.docs` in `.pni/workflows/<id>.yaml` match your repository layout. Then run **`pni workflows plan <id>`** to execute lightweight Phase 0 reconnaissance, inspect pre-flight readiness gates, and render a Python-validated Mermaid Execution DAG:

```bash
# List available workflows (audit, rollup, migration, progress) and inspect steps
pni workflows list
pni workflows show full_audit

# Phase 0 recon + validated Mermaid Execution DAG preview (save with -o if needed)
pni workflows plan full_audit
pni workflows plan full_audit -o .pni/cache/plan_preview.md

# Validate any custom or AI-authored Mermaid diagram (Layer 1 static + optional Layer 2 Playwright)
pni validate-mermaid .pni/cache/plan_preview.md
```

```drawlib align=center code=fold file=pni_preflight_gates_flow.png caption="Workflow v2 Pre-Flight Gates, confirm_plan Alignment & Auto-Advance DAG Flowchart"
from drawlib.canvas import save, setup
from drawlib.diagrams.flow import Decision, End, FlowDiagram, Process, Start
from drawlib.styles import Styles

setup(width=164, height=96, dpi=150)

flow = FlowDiagram(
    node_style=Styles.WhiteBordered.patch(
        text_color=Styles.Dark.text_color, shape_r=1.6, text_size=10.0
    ),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=10.0),
    width=158.0,
    height=90.0,
)

flow.add_lane("1. Setup & Plan", width=44.0)
flow.add_lane("2. Gates & Approval", width=52.0)
flow.add_lane("3. Remedies & Output", width=62.0)

n_init = flow.add(
    Start(
        "pni init &\nTailor <id>.yaml",
        width=36.0,
        height=13.0,
        style=Styles.PrimaryNeutral.patch(shape_r=6.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.2),
    ),
    xy=(22.0, 72.0),
)

n_show = flow.add(
    Process(
        "pni workflows plan <id>\n(Recon + Mermaid DAG)",
        width=37.0,
        height=14.0,
        style=Styles.Neutral.patch(shape_r=1.6),
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(22.0, 46.0),
)

g_preflight = flow.add(
    Decision(
        "Gate 1: Pre-Flight\n(Pentest/based_on)?",
        width=40.0,
        height=16.5,
        style=Styles.SecondaryNeutral,
        text_style=Styles.DarkBold.patch(text_size=9.8),
    ),
    xy=(70.0, 70.0),
)

r_preflight = flow.add(
    Process(
        "pni pentests init -w <id>\nor Complete Base Audit",
        width=46.0,
        height=14.0,
        style=Styles.DangerNeutral.patch(shape_r=1.6),
        text_style=Styles.DangerBold.patch(text_size=10.0),
    ),
    xy=(131.0, 70.0),
)

g_confirm = flow.add(
    Decision(
        "Gate 2: confirm_plan\nApproved?",
        width=40.0,
        height=16.5,
        style=Styles.SecondaryNeutral,
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(70.0, 44.0),
)

r_confirm = flow.add(
    Process(
        "Align Scope / Answers or\nPass --auto-approve",
        width=46.0,
        height=14.0,
        style=Styles.WarningNeutral.patch(shape_r=1.6),
        text_style=Styles.DarkBold.patch(text_size=10.0),
    ),
    xy=(131.0, 44.0),
)

n_start = flow.add(
    Process(
        "Auto-Advance DAG\n(start --pull / --next)",
        width=40.0,
        height=14.0,
        style=Styles.PrimaryFlat.patch(shape_r=1.6),
        text_style=Styles.WhiteBold.patch(text_size=10.0),
    ),
    xy=(70.0, 14.0),
)

n_done = flow.add(
    End(
        "COMPLETED\n(pni_report/ + PDF)",
        width=42.0,
        height=13.0,
        style=Styles.SuccessNeutral.patch(shape_r=6.0),
        text_style=Styles.SuccessBold.patch(text_size=10.2),
    ),
    xy=(131.0, 14.0),
)

n_init.connect(n_show, start_side="bottom", end_side="top")
n_show.connect(g_preflight, label="Check", start_side="right", end_side="left")
g_preflight.connect(r_preflight, label="Missing", start_side="right", end_side="left", style=Styles.DangerBold)
g_preflight.connect(g_confirm, label="Pass", start_side="bottom", end_side="top")
g_confirm.connect(r_confirm, label="Pending", start_side="right", end_side="left", style=Styles.WarningBold)
g_confirm.connect(n_start, label="Ready", start_side="bottom", end_side="top")
n_start.connect(n_done, label="Done", start_side="right", end_side="left", style=Styles.SuccessBold)

flow.draw(xy=(3.0, 3.0))
save()
```

If your workflow includes dynamic Web penetration testing (`uses: web_penetration_audit`), initialize and verify the target's penetration test suite before starting the stateful run:

```bash
# Scaffold .pni/pentests/<target>/ and test the step directly with zero SQLite prep
pni pentests init -w full_audit
pni workflows run-action full_audit web_pentest
```

## 4. Step 3: Execute the Single-Command Workflow v2 Loop

Workflow v2 provides single-command ergonomics (`--pull`, `--file`, `--next`, and `-o/--output`) that eliminate shell pipes, redirects, and `&&` chaining while enabling parallel deterministic collection:

```bash
# 1a. Interactive start: starts run & pulls act-01 (confirm_plan) in one command
pni workflows start full_audit --pull

# 1b. Or CI / non-interactive start: auto-approve confirm_plan and immediately auto-advance collectors
pni workflows start full_audit --auto-approve --pull -o .pni/cache/action_next.md

# 2. Push validated JSON from file and auto-advance straight to the next ready AI step
pni workflows push-action wf-1a2b3c4d act-01 --file .pni/cache/wf-1a2b3c4d/input_act-01.json --next

# 3. Inspect all parallel DAG-ready actions or overall status at any time
pni workflows get-actions wf-1a2b3c4d --ready --json -o .pni/cache/ready_actions.json
pni workflows status wf-1a2b3c4d
```

During the loop:
1. **Zero Empty ACKs & Parallel Collection**: Whenever the DAG reaches deterministic steps (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`), `pni` runs all DAG-ready collectors in parallel, writes `.pni/cache/<workflow_id>/facts.json`, and advances straight to the next AI step.
2. **Schema, Path & FP Triage Validation on Push**: On `record_architecture`, `ai_interpret`, `emit_score`, `synthesize_rollup`, `emit_migration_plan`, and `emit_progress`, `push-action` validates Pydantic models, checks every file path against `module_inventory`, records auditable `finding_adjustments` (`waive` / `reclassify`), and emits `pni_report/<target>_score.json` (with Executed Audit DAG and 7-Axis Evidence Delta Δ), `*_summary.json`, and `*_findings.sarif`.

## 5. Step 4: Compile the Flat Self-Contained Drawlib Report

When `emit_score` finishes, PNI automatically syncs verified JSON evidence (`plan.json`, `facts.json`, `architecture.json`, `score.json`) into **`pni_report_src/_facts/`**. On the final `write_drawlib_report` step, scaffold the flat report project (`pni_report_src -> pni_report` by default, with no nested `<target>_src/` directory), verify diagrams with the coordinate grid (`-g`), compile the A4 vector PDF (and optional HTML), and push completion:

```bash
# Scaffold pni_report_src/ (default flat layout) and compile pni_report/full_audit.pdf
pni report init full_audit --lang en --style google
pni report build full_audit

# Push the final completion payload from file to mark the workflow COMPLETED
pni workflows push-action wf-1a2b3c4d act-12 --file .pni/cache/wf-1a2b3c4d/input_act-12.json
```

*(For multi-target portals such as this documentation site, pass custom flat paths like `--src-dir docs_src/reports/<slug> --output-dir docs/reports/<slug>`.)*

Next, explore the [Primary Use Cases](use_cases.md) or dive into [Workflows & Pre-Flight Gates](../03_workflows_and_actions/workflows_guide.md).
