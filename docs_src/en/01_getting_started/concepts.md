# Background & Core Concepts

Modernizing legacy and evolving software across **Python**, **Java**, **PHP**, **Go**, **TypeScript**, and **JavaScript** is one of the highest-leverage challenges in engineering organizations. `pni501` replaces fragile, ad-hoc LLM prompting with a deterministic harness that unites cascading polyglot rules, static and container telemetry, SQLite Pull-Push state management, and Drawlib visual reporting.

```drawlib align=center code=fold file=pni_why_comparison.png caption="The AI Modernization Gap: Ad-Hoc Prompting vs. Codified PNI501 Polyglot Audit & Migration Rigor"
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
    "Inconsistent standards across 6 languages",
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
    "Workflow Drift & Text Walls",
    "Subjective scores & raw Markdown dumps",
    icon=phosphor.file_text,
)
left_cards.draw(xy=(5.5, 5.5), width=63.0, height=54.0)

line((72.5, 37.0), (83.5, 37.0), arrow_head="->", style=Styles.PrimaryBold.patch(line_width=2.5))
text((78.0, 41.5), "PNI501", style=Styles.PrimaryBold.patch(text_size=11.0))

right_panel = Panel(
    "PNI501 Deterministic Facts x AI",
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
    "52 Rules & 15 Composite Actions",
    "Universal, archetype & 6-language standards",
    icon=phosphor.book_bookmark,
)
right_cards.add(
    "AST, Docker, Trivy & Pentest",
    "Exact inventory, coverage, CVE & httpx facts",
    icon=phosphor.cpu,
)
right_cards.add(
    "3-Aspect Arch & 7-Axis Grades",
    "Path-verified JSON, S-D grades & based_on",
    icon=phosphor.git_commit,
)
right_cards.add(
    "7-Chapter Visual Drawlib PDF",
    "Radar charts, heatmaps & PR wave roadmaps",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.chart_bar,
)
right_cards.draw(xy=(87.5, 5.5), width=63.0, height=54.0)
save()
```

## 1. Why Ad-Hoc AI Prompting Fails on Real Repositories

Across enterprise backends, cloud microservices, frontend applications, and internal developer tooling, engineering teams manage heterogeneous repositories spanning **Python**, **Java**, **PHP**, **Go**, **TypeScript**, and **JavaScript**. Before any team can safely maintain, refactor, or migrate such codebases, engineers need an objective, reproducible baseline of structural quality, runtime reliability, and security posture.

While Code AI Agents (`Claude Code`, `Gemini CLI`, `Cursor`, `GitHub Copilot`, etc.) have transformed code comprehension, asking an LLM in a single chat prompt to *"audit this repository and score its quality"* suffers from four systemic failure modes:

1. **Senior-Engineer Prompt Bottleneck Across Ecosystems**: Crafting prompts that simultaneously enforce universal architecture standards (OWASP ASVS, OpenSSF supply-chain hygiene, Twelve-Factor readiness, Google SRE PRR, CLI ergonomics) alongside language- and framework-specific idioms (`FastAPI`, `Spring Boot`, `Laravel`, `WordPress`, `Go` modules, `TypeScript` strictness) requires staff-level expertise on every run.
2. **Quantitative & Structural Hallucinations**: When inspecting repositories directly in chat, LLMs routinely guess LOC counts, fabricate type-annotation or generic coverage ratios, miss circular dependency SCCs (Strongly Connected Components), and cite file paths or line numbers that do not exist in the workspace.
3. **Runtime, Vulnerability & Penetration-Testing Blind Spots**: Static text reading never verifies whether unit tests actually pass inside a clean container, what line/branch coverage is achieved, whether `Trivy` flags critical CVEs, IaC misconfigurations, or hardcoded secrets, or whether live HTTP endpoints resist auth-bypass, SQLi/XSS, and SSRF probes under dynamic penetration testing.
4. **Subjective Score Drift & Wall-of-Text Overload**: In long chat sessions, agents vary their evaluation criteria from run to run, propose risky "big-bang" rewrites disconnected from the real import graph, and output thousands of lines of raw Markdown that cannot be tracked as longitudinal governance metrics.

## 2. The PNI501 Approach: Four Foundational Pillars

**Project Nemesis Index (`pni501` `v0.1.3`)** solves these challenges by inverting control: instead of letting an LLM improvise the audit flow, the **deterministic `pni` CLI and SQLite state machine** drive the process, delegating only bounded, evidence-grounded reasoning and visual report authoring to the AI agent.

```drawlib align=center code=fold file=pni_four_step_architecture.png caption="The Four-Step PNI501 Architecture: Uniting Polyglot Analyzers, SQLite Pull-Push Reasoning, Chained Plans & Visual Reports"
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
    "How PNI501 Unites Polyglot Analyzers, Stateful AI Reasoning, Chained Plans & Visual Reports",
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
        "52 Cascading Rules &\n15 Actions (6 Languages)",
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
        "AST, Docker, Trivy,\nPentest & Wave Facts",
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
        "2. SQLite Pull-Push\n& Grounded AI Audit\n(3-Aspect Arch)",
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
        "3. 7-Axis Score &\nMigration Plan\n(based_on Chain)",
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
        "4. 7-Chapter Drawlib\nReport & Human\nDecision (A4 PDF)",
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

### 2.1 Pillar 1: Cascading Multi-Language Rules & Composite Actions (`_rules` & `_actions`)
Instead of relying on ad-hoc prompts, `pni501` ships **52 built-in engineering rules** across `common/` and 6 language directories (`python/`, `java/`, `php/`, `go/`, `typescript/`, `javascript/`), paired with **15 composite actions** per active language scope. Every built-in rule, action, and workflow supports non-destructive `.pni/` local cascading overrides (`local > <lang> > common`) so organizations can codify team-specific conventions in Git. See [Domain Architecture & Cascade](../02_architecture/domain_architecture.md) for details.

### 2.2 Pillar 2: Zero-Hallucination Static, Container, Security & Pentest Analyzers
Anything countable, executable, or structurally provable is measured programmatically and cached in `.pni/cache/<workflow_id>/facts.json`:
- **Polyglot Static & Manifest Inspection (`project_inspect`, `ast_analyze`)**: Parses manifests (`pyproject.toml`, `pom.xml`, `build.gradle`, `composer.json`, `go.mod`, `package.json`, `tsconfig.json`), CI/governance files, Python `ast`, and `ast-grep-py` syntax trees to extract exact `module_inventory`, LOC, type/generic/JSDoc ratios, cyclomatic complexity, API endpoints, security sinks, and cyclic import graphs.
- **Isolated Runtime, Security & Loopback Pentest Execution (`run_check`, `security_scan`, `web_pentest`)**: Runs unit suites, coverage collection, and HTTP smoke probes in isolated containers; runs socketless `Trivy` scans (`vuln,misconfig,secret`); and executes target-tailored `pytest` + `httpx` Web penetration tests against loopback containers.
- **Topological Wave & Progress Telemetry (`migration_analyze`, `progress_analyze`)**: Computes strongly connected dependency cycles, external boundary touchpoints, bottom-up `refactoring_waves`, and Git milestone/merge-tree conflict trajectories. See [Analyzers & Live Pentest](../03_workflows_and_actions/analyzers_and_pentest.md).

### 2.3 Pillar 3: Stateful Pull-Push Engine & Grounded Architecture (`_workflows`)
`pni workflows` drives the agent through a SQLite state machine (`.pni/cache/workflow_state.db`) via `start`, `get-action`, and `push-action`:
- **3-Aspect Grounded Architecture Recording (`record_architecture`)**: Before scoring, the agent records system comprehension across `purpose_and_stack`, `layers_and_modules`, and `flows_and_state`, while PNI validates every cited file path against `module_inventory` before writing `.pni/cache/<workflow_id>/architecture.json`.
- **7-Axis Health Scoring (`emit_score`)**: Synthesizes rule evaluations and deterministic penalties (`aggregator.py`) into a validated `ScoreResult` (`reports/<target>_score.json`) across `architecture`, `code_quality`, `typing`, `testing`, `dependencies`, `security`, and `documentation`.
- **Prerequisite-Gated Chaining (`based_on`)**: Migration workflows (`category: migration`) require a `COMPLETED` audit run in `workflow_state.db` and inherit its verified As-Is facts to emit `reports/<target>_migration_plan.json`. See [Stateful Pull-Push Engine](../02_architecture/stateful_engine.md).

### 2.4 Pillar 4: Blueprint-Driven Visual Drawlib Reports (`_reporter`)
To eliminate wall-of-text review fatigue, `_reporter` generates a deterministic JSON blueprint (`blueprint.json`, `migration_blueprint.json`, or `progress_blueprint.json`) that guides the creation of a **7-chapter Drawlib report** (`00_cover.md` + `01..06` under `reports_src/<target>_src/`). Combining executive `KpiCards`, 7-axis `RadarChart`s, 2D module `HeatmapChart`s, and phased `P0`–`P2` / wave `Roadmap`s, `pni report build` compiles crisp A4 vector PDFs (`reports/<target>.pdf`). See [Drawlib Visual Reporter](../04_scoring_and_reports/drawlib_reporter.md).
