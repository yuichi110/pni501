# Background & Core Concepts

Modernizing legacy and evolving software across **55 programming languages**—from `Python`, `Java`, `Go`, `TypeScript`, `Rust`, `C#`, and `COBOL` to declarative scripts (`Bash`, `Solidity`, `Zig`) and companion IaC/schema files (`Dockerfile`, `Terraform/HCL`, `Protobuf`, `SQL`)—is one of the highest-leverage challenges in engineering organizations. `pni501` (`v0.2.0`) replaces fragile, ad-hoc LLM prompting with a deterministic **Workflow v2** harness that unites 356 cascading polyglot rules, 57 native `tree-sitter` CST grammars, isolated container telemetry, SQLite DAG state management, and flat, self-contained Drawlib visual reporting.

```drawlib align=center code=fold file=pni_why_comparison.png caption="The AI Modernization Gap: Ad-Hoc Prompting vs. Codified PNI501 (v0.2.0) 55-Language Audit & Migration Rigor"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.lines import line
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=156, height=74, dpi=150)

left_panel = Panel(
    "Ad-Hoc AI Prompting (Without PNI)",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
left_panel.draw(xy=(3.0, 3.0), width=68.0, height=68.0)

left_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.2,
)
left_cards.add(
    "Senior-Engineer Bottleneck",
    "Inconsistent standards across 55 langs",
    icon=phosphor.warning,
)
left_cards.add(
    "Metric & Path Hallucinations",
    "Guesses LOC, cycles & nonexistent files",
    icon=phosphor.question,
)
left_cards.add(
    "Runtime & Security Blind Spots",
    "Misses Docker tests, Trivy CVEs & pentests",
    icon=phosphor.shuffle,
)
left_cards.add(
    "Workflow Drift & Silent FPs",
    "Subjective scores & raw Markdown dumps",
    icon=phosphor.file_text,
)
left_cards.draw(xy=(5.5, 5.5), width=63.0, height=54.0)

line((72.5, 37.0), (83.5, 37.0), arrow_head="->", style=Styles.PrimaryBold.patch(line_width=2.5))
text((78.0, 41.5), "PNI501", style=Styles.PrimaryBold.patch(text_size=11.0))

right_panel = Panel(
    "PNI501 v0.2.0 Deterministic Facts x AI",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
right_panel.draw(xy=(85.0, 3.0), width=68.0, height=68.0)

right_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.2,
)
right_cards.add(
    "356 Rules & 182 Actions",
    "55 langs (Tier A/B/C) & 112 workflows",
    icon=phosphor.book_bookmark,
)
right_cards.add(
    "57 Tree-sitter CSTs + Runtime",
    "Exact inventory, Docker, Trivy & pentest",
    icon=phosphor.cpu,
)
right_cards.add(
    "Workflow v2 DAG & Delta",
    "confirm_plan, FP triage & rollup chain",
    icon=phosphor.git_commit,
)
right_cards.add(
    "Flat Self-Contained PDF",
    "pni_report_src/_facts -> pni_report PDF",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.chart_bar,
)
right_cards.draw(xy=(87.5, 5.5), width=63.0, height=54.0)
save()
```

## 1. Why Ad-Hoc AI Prompting Fails on Real Repositories

Across enterprise backends, cloud microservices, GPU/HPC kernels, embedded/HDL modules, mainframe workloads, frontend applications, and polyglot monorepos, engineering teams manage heterogeneous repositories spanning dozens of languages plus companion IaC, schema, and build definitions. Before any team can safely maintain, refactor, or migrate such codebases, engineers need an objective, reproducible baseline of structural quality, runtime reliability, and security posture.

While Code AI Agents (`Claude Code`, `Gemini CLI`, `Cursor`, `GitHub Copilot`, etc.) have transformed code comprehension, asking an LLM in a single chat prompt to *"audit this repository and score its quality"* suffers from four systemic failure modes:

1. **Senior-Engineer Prompt Bottleneck Across Ecosystems**: Crafting prompts that simultaneously enforce universal architecture standards (OWASP ASVS, OpenSSF supply-chain hygiene, Twelve-Factor readiness, Google SRE PRR, CLI ergonomics) alongside language- and framework-specific idioms across **55 languages** (`FastAPI`, `Spring Boot`, `Laravel`, `Go`, `Rust`, `C#`, `COBOL`, `Terraform`, `Dockerfile`, etc.) requires staff-level expertise on every run.
2. **Quantitative & Structural Hallucinations**: When inspecting repositories directly in chat, LLMs routinely guess LOC counts, fabricate type-annotation or generic coverage ratios, miss circular dependency SCCs (Strongly Connected Components), and cite file paths or line numbers that do not exist in the workspace.
3. **Runtime, Vulnerability & Penetration-Testing Blind Spots**: Static text reading never verifies whether unit tests actually pass inside a clean container, what line/branch coverage is achieved, whether `Trivy` flags critical CVEs, IaC misconfigurations, or hardcoded secrets, or whether live HTTP endpoints resist auth-bypass, SQLi/XSS, and SSRF probes under dynamic penetration testing.
4. **Subjective Score Drift, Silent Overrides & Wall-of-Text Overload**: In long chat sessions, agents vary evaluation criteria from run to run, silently waive noisy alerts without an audit trail, skip execution-plan alignment, propose risky "big-bang" rewrites disconnected from the real import graph, and output thousands of lines of raw Markdown that cannot be tracked as longitudinal governance metrics.

## 2. The PNI501 Approach: Four Foundational Pillars

**Project Nemesis Index (`pni501` `v0.2.0`)** solves these challenges by inverting control: instead of letting an LLM improvise the audit flow, the **deterministic `pni` CLI and SQLite Workflow v2 DAG engine** drive the process, delegating only bounded, evidence-grounded reasoning, false-positive triage, and visual report authoring to the AI agent.

```drawlib align=center code=fold file=pni_four_step_architecture.png caption="The Four-Step PNI501 (v0.2.0) Architecture: Uniting 55-Language CST Analyzers, Workflow v2 DAG Reasoning, Chained Plans & Flat Reports"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import (
    ArchitectureDiagram,
    Node,
    NodeGroup,
    PhosphorIcon,
)
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=158, height=66, dpi=150)

text(
    (4.5, 61.0),
    "How PNI501 v0.2.0 Unites 55-Lang Analyzers, Workflow v2 DAG, Plans & Flat Reports",
    style=Styles.DarkBold.patch(text_size=12.0, halign="left"),
)

white_card = Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=1.6)

diagram = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    node_card_style=white_card,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=10.0),
)

prep_group = diagram.add(
    NodeGroup(
        title="1. Rules & Objective Facts",
        padding=2.6,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.2, halign="left"),
    ),
    xy=(4.5, 4.0),
)
n_rules = prep_group.add(
    Node(
        "356 Rules & 182 Actions\n(55 Langs, 112 WFs)",
        width=31.0,
        height=17.5,
        icon=PhosphorIcon.BOOK_OPEN_TEXT,
        icon_size=5.2,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(18.0, 35.5),
)
n_ast = prep_group.add(
    Node(
        "57 Tree-sitter CSTs,\nDocker, Trivy & Pentest",
        width=31.0,
        height=17.5,
        icon=PhosphorIcon.CPU,
        icon_size=5.2,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(18.0, 14.0),
)

n_agent = diagram.add(
    Node(
        "2. Workflow v2 DAG\n& Grounded AI Audit\n(Plan + FP Triage)",
        width=27.0,
        height=27.0,
        icon=PhosphorIcon.ROBOT,
        icon_size=5.8,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    ),
    xy=(65.5, 31.0),
)

n_score_plan = diagram.add(
    Node(
        "3. Score + Delta,\nRollup & Migration\n(based_on Chain)",
        width=27.0,
        height=27.0,
        icon=PhosphorIcon.GIT_BRANCH,
        icon_size=5.8,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    ),
    xy=(102.5, 31.0),
)

n_report = diagram.add(
    Node(
        "4. Flat Drawlib\nReport & Decision\n(pni_report PDF)",
        width=27.0,
        height=27.0,
        icon=PhosphorIcon.CHART_POLAR,
        icon_size=5.8,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=2.0),
    ),
    xy=(139.5, 31.0),
)

diagram.connect(prep_group, n_agent, arrow="->", routing="direct")
diagram.connect(n_agent, n_score_plan, arrow="->", routing="direct")
diagram.connect(n_score_plan, n_report, arrow="->", routing="direct")

diagram.draw(xy=(0.0, 0.0))
save()
```

### 2.1 Pillar 1: Cascading 55-Language Rules & Action Templates (`_rules` & `_actions`)
Instead of relying on ad-hoc prompts, `pni501` ships **356 built-in rule files** across `common/` and **55 language scopes** organized into **Tier A Full Audit (20)**, **Tier B Declarative Static Audit (20)**, and **Tier C Companion IaC/Schema/Build/Config (15)**, paired with **182 action templates** and **112 workflow templates**. Every built-in rule, action, and workflow supports non-destructive `.pni/` local cascading overrides (`local > <lang> > common`) so organizations can codify team-specific conventions in Git. See [Domain Architecture & Cascade](../02_architecture/domain_architecture.md) and [Supported 55 Languages](../05_languages_and_reference/supported_languages.md) for details.

### 2.2 Pillar 2: Zero-Hallucination Native Tree-sitter CST, Container, Security & Pentest Analyzers
Anything countable, executable, or structurally provable is measured programmatically and cached in `.pni/cache/<workflow_id>/facts.json`:
- **57-Grammar Native `tree-sitter` CST & Manifest Inspection (`project_inspect`, `ast_analyze`)**: Replaces `ast-grep-py` with a unified parse-once `tree-sitter` engine powered by **52 official PyPI `tree-sitter-*` `abi3` wheels** plus **5 MIT grammars** (`COBOL`, `R`, `Vue`, `Protocol Buffers`, `Dockerfile`) lazily downloaded and SHA-256 verified from GitHub Releases (`pni grammars status` / `prefetch` / `clear`), preserving a pure-Python (`py3-none-any`) `pni501` package. Extracts exact `module_inventory`, LOC, type/generic coverage, cyclomatic complexity, API endpoints, security sinks, and cyclic import graphs across Tier A, Tier B, and companion Tier C assets.
- **Isolated Runtime, Security & Loopback Pentest Execution (`run_check`, `security_scan`, `web_pentest`)**: Runs unit suites, coverage collection, and HTTP smoke probes in isolated containers; runs socketless `Trivy` scans (`vuln,misconfig,secret`) with 4-tier dependency scope classification; and executes target-tailored `pytest` + `httpx` Web penetration tests against loopback containers.
- **Topological Wave & Progress Telemetry (`migration_analyze`, `progress_analyze`)**: Computes strongly connected dependency cycles, external boundary touchpoints, bottom-up `refactoring_waves`, and Git milestone/merge-tree conflict trajectories. See [Analyzers & Live Pentest](../03_workflows_and_actions/analyzers_and_pentest.md).

### 2.3 Pillar 3: Workflow v2 Conditional DAG Engine, Evidence Delta & FP Triage (`_workflows`)
`pni workflows` drives the agent through a SQLite **Workflow v2 DAG** state machine (`.pni/cache/workflow_state.db`) with `needs:` dependencies, deterministic `when:` guards, and parallel deterministic collection:
- **Plan-First Human Alignment (`pni workflows plan` & `confirm_plan`)**: Before heavy execution, Phase 0 reconnaissance inspects targets, container runtimes, and monorepo components and emits a deterministically validated Mermaid Execution DAG (always checkable with `pni validate-mermaid`), giving engineers a `confirm_plan` approval checkpoint (or `--auto-approve` for CI).
- **3-Aspect Grounded Architecture & Auditable FP Triage (`record_architecture`, `ai_interpret`)**: The agent records system comprehension across `purpose_and_stack`, `layers_and_modules`, and `flows_and_state` (path-verified against `module_inventory` in `.pni/cache/<workflow_id>/architecture.json`), and explicitly triages deterministic `det-*` findings via `finding_adjustments` (`waive` / `reclassify` with auditable rationale) instead of silent overrides.
- **Executed Audit DAG, 7-Axis Evidence Delta & Chained Workflows (`emit_score`, `based_on`, `rollup`)**: Emits `pni_report/<target>_score.json` (`schema_version="2.0"` capturing the Executed Audit DAG and baseline-to-adjusted 7-Axis Evidence Delta Δ), `*_summary.json`, and `*_findings.sarif` (SARIF 2.1.0). Supports prerequisite-gated migrations (`based_on: <audit_id>`) and multi-language monorepo rollups (`category: rollup`). See [Stateful Pull-Push Engine](../02_architecture/stateful_engine.md).

### 2.4 Pillar 4: Flat Self-Contained Visual Drawlib Reports (`_reporter`)
To eliminate wall-of-text review fatigue and directory indirection, `_reporter` uses a **flat, self-contained layout**: `--src-dir` (`pni_report_src` by default, or custom paths like `docs_src/reports/<slug>` for unified portals) directly houses `drawlib.toml`, `styles.py`, `utils.py`, chapter Markdown files (`00_cover.md`..`06_*.md`), and an automatically synced **`_facts/`** directory containing all verified JSON artifacts (`plan.json`, `facts.json`, `architecture.json`, `score.json`). Combining executive `KpiCards`, 7-axis `RadarChart`s, Evidence Delta breakdowns, 2D module `HeatmapChart`s, and phased `P0`–`P2` / wave `Roadmap`s, `pni report build` compiles crisp A4 vector PDFs and HTML into `pni_report/` (`pni_report/<target>.pdf`). See [Drawlib Visual Reporter](../04_scoring_and_reports/drawlib_reporter.md).
