# 1. Background, Problem Statement & The PNI Approach

Modernizing legacy and evolving software across **`Python`**, **`Java`**, and **`PHP`** remains one of the highest-leverage—and highest-risk—challenges in engineering organizations, yet applying Code AI Agents reliably still bottlenecks on senior human supervision unless polyglot standards, static and runtime telemetry, stateful workflows, and visual reporting are unified into a single deterministic harness.

```drawlib file=modernization_gap_comparison.png caption="The AI Modernization Gap: Ad-Hoc Prompting vs. Codified PNI Polyglot Audit & Migration Rigor"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.lines import line
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=152, height=72, dpi=150)

left_panel = Panel(
    "Ad-Hoc AI Prompting (Without PNI)",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.5),
)
left_panel.draw(xy=(3.0, 3.0), width=66.5, height=66.0)

left_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="circle",
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.2,
)
left_cards.add(
    "Senior-Engineer Bottleneck",
    "Quality drops across Python, Java & PHP",
    icon=phosphor.warning,
)
left_cards.add(
    "Metric & Path Hallucinations",
    "Guesses LOC, cycles & nonexistent files",
    icon=phosphor.question,
)
left_cards.add(
    "Runtime & Security Blind Spots",
    "Misses container smoke, Trivy & pentests",
    icon=phosphor.shuffle,
)
left_cards.add(
    "Workflow Drift & Text Walls",
    "Ungrounded rewrites & raw Markdown dumps",
    icon=phosphor.file_text,
)
left_cards.draw(xy=(5.5, 5.5), width=61.5, height=52.5)

line((71.0, 36.0), (81.0, 36.0), arrow_head="->", style=Styles.PrimaryBold.patch(line_width=2.5))
text((76.0, 40.5), "PNI", style=Styles.PrimaryBold.patch(text_size=11.0))

right_panel = Panel(
    "PNI-Guided Polyglot Audit & Migration",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.5),
)
right_panel.draw(xy=(82.5, 3.0), width=66.5, height=66.0)

right_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.2,
)
right_cards.add(
    "36 Rules & 21 Composite Actions",
    "Universal, archetype & Py/Java/PHP rules",
    icon=phosphor.book_bookmark,
)
right_cards.add(
    "Static, Container, Trivy & Pentest",
    "Exact AST, Docker, CVE & httpx telemetry",
    icon=phosphor.cpu,
)
right_cards.add(
    "3-Aspect Arch & Chained Waves",
    "Verified paths, 7-axis score & based_on",
    icon=phosphor.git_commit,
)
right_cards.add(
    "7-Chapter Visual Drawlib PDF",
    "7-axis radar, heatmaps & wave roadmaps",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.chart_bar,
)
right_cards.draw(xy=(85.0, 5.5), width=61.5, height=52.5)
save()
```

---

## 1.1 Background: Multi-Language Legacy Modernization in the Generative AI Era

Across enterprise backends, SaaS platforms, and internal developer tooling, **legacy modernization spans heterogeneous language ecosystems—most notably `Python`, `Java`, and `PHP`**. Engineering teams routinely inherit Python services with flat script layouts and untyped boundaries, Java Spring or servlet applications with tangled package dependencies and aging Maven/Gradle trees, or PHP monoliths (`Laravel`, `WordPress`, or custom Composer/vanilla codebases) carrying raw SQL/template sinks and sparse automated tests. Before any team can safely refactor, re-architect, or migrate such repositories, engineers need an objective, reproducible baseline of structural health, runtime behavior, and security posture.

While **Code AI Agents** have dramatically accelerated code reading and transformation, unconstrained ad-hoc prompting suffers from four systemic failure modes:

1. **Senior-Engineer Prompt Bottleneck Across Ecosystems**: Crafting prompts that simultaneously enforce universal architecture principles (OWASP ASVS, OpenSSF supply-chain hygiene, Twelve-Factor readiness, CLI ergonomics) alongside language- and framework-specific idioms (`FastAPI`, `Spring Boot`, `Laravel`, `WordPress`) requires deep staff-level expertise on every run.
2. **Quantitative & Structural Hallucinations**: When asked to inspect a repository directly in chat, LLMs routinely guess LOC counts, fabricate type-annotation or generic coverage ratios, overlook cyclic dependency DAGs, and cite module paths that do not exist in the workspace.
3. **Runtime, Vulnerability & Penetration-Testing Blind Spots**: Static prompt-only reviews never verify whether tests actually pass inside a clean container, what line/branch coverage is achieved, whether `Trivy` flags critical CVEs, IaC misconfigurations, or hardcoded secrets, or whether live HTTP endpoints resist auth-bypass, SQLi/XSS, and SSRF probes under dynamic penetration testing.
4. **Workflow Drift, Ungrounded Migration Plans & Wall-of-Text Overload**: In long chat sessions, agents skip audit dimensions, propose risky "big-bang" rewrites disconnected from the real dependency graph, and dump thousands of lines of raw Markdown that overwhelm human reviewers.

---

## 1.2 The PNI Approach: Four Pillars of Deterministic AI Auditing & Migration

**Project Nemesis Index (`pni501` `v0.1.0`)** closes this gap by codifying senior engineering methodology into a deterministic CLI and SQLite state machine that guides any Code AI Agent (`Claude Code`, `Gemini CLI`, `Cursor`, `Antigravity`, etc.) from raw repository telemetry to a 7-axis health audit, an optional chained migration plan, and a 7-chapter visual report:

```drawlib file=pni_four_step_approach.png caption="The Four-Step PNI Approach: Orchestrating Polyglot Analyzers, Grounded AI Audits, Chained Migration Plans & 7-Chapter Visual Reports"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import (
    ArchitectureDiagram,
    Node,
    NodeGroup,
    PhosphorIcon,
)
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=64, dpi=150)

text(
    (4.5, 59.5),
    "How PNI Unites Polyglot Analyzers, Stateful AI Reasoning, Migration Chaining & Visual Reports",
    style=Styles.DarkBold.patch(text_size=11.5, halign="left"),
)

white_card = Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=1.6)

diagram = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=9.8),
    node_card_style=white_card,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=9.8),
)

prep_group = diagram.add(
    NodeGroup(
        title="1. Rules & Deterministic Facts",
        padding=2.4,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=9.8, halign="left"),
    ),
    xy=(4.5, 4.0),
)
n_rules = prep_group.add(
    Node(
        "36 Cascading Rules &\n21 Actions (Py/Java/PHP)",
        width=29.5,
        height=17.0,
        icon=PhosphorIcon.BOOK_OPEN_TEXT,
        icon_size=5.2,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(17.2, 34.5),
)
n_ast = prep_group.add(
    Node(
        "AST, Docker, Trivy,\nPentest & Wave Facts",
        width=29.5,
        height=17.0,
        icon=PhosphorIcon.CPU,
        icon_size=5.2,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(17.2, 13.5),
)

n_agent = diagram.add(
    Node(
        "2. SQLite Pull-Push\n& Grounded AI Audit\n(3-Aspect Arch)",
        width=26.5,
        height=26.0,
        icon=PhosphorIcon.ROBOT,
        icon_size=5.8,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.8),
        card_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    ),
    xy=(64.0, 30.5),
)

n_score_plan = diagram.add(
    Node(
        "3. 7-Axis Score &\nMigration Plan\n(based_on Chain)",
        width=26.5,
        height=26.0,
        icon=PhosphorIcon.GIT_BRANCH,
        icon_size=5.8,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    ),
    xy=(101.0, 30.5),
)

n_report = diagram.add(
    Node(
        "4. 7-Chapter Drawlib\nReport & Human\nDecision (A4 PDF)",
        width=26.5,
        height=26.0,
        icon=PhosphorIcon.CHART_POLAR,
        icon_size=5.8,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=2.0),
    ),
    xy=(138.0, 30.5),
)

diagram.connect(prep_group, n_agent, arrow="->", routing="direct")
diagram.connect(n_agent, n_score_plan, arrow="->", routing="direct")
diagram.connect(n_score_plan, n_report, arrow="->", routing="direct")

diagram.draw(xy=(0.0, 0.0))
save()
```

### 1. Cascading Multi-Language Rules, Actions & Workflows (`_rules` & `_actions`)
Instead of relying on ad-hoc prompts, `pni501` ships **`36` built-in engineering rules** across `common/`, `python/`, `java/`, and `php/`—covering universal architecture, security (`OWASP ASVS` + vulnerability/attack-surface standards), OpenSSF supply-chain governance, Twelve-Factor cloud-native readiness, CLI ergonomics, library hygiene, migration planning, and framework best practices (`FastAPI`, `Spring Boot`, `Laravel`, `WordPress`)—paired with **`21` composite actions** that expand into **`12` canonical `PrimitiveType`s**. Every built-in asset supports non-destructive `.pni/` local cascading overrides per repository.

### 2. Zero-Hallucination Static, Container, Security & Pentest Analyzers
Anything countable, executable, or structurally provable is measured programmatically and cached in `.pni/cache/<workflow_id>/facts.json`:
- **Polyglot Static & Manifest Inspection (`project_inspect`, `ast_analyze`)**: Parses `pyproject.toml`, `pom.xml`/`build.gradle`, `composer.json`, lockfiles, CI/governance metadata, Python `ast`, and `ast-grep-py` syntax trees for `Java` and `PHP` to extract exact `module_inventory`, LOC, typing/generics ratios, cyclomatic complexity, API endpoints, security sinks, and cyclic import graphs.
- **Isolated Runtime, Security & Loopback Pentest Execution (`run_check`, `security_scan`, `web_pentest`)**: Executes unit suites, coverage collection, and HTTP smoke probes in isolated containers; runs socketless `Trivy` scans (`-- vuln,misconfig,secret`) with zero Docker-daemon exposure; and runs target-tailored `pytest` + `httpx` Web penetration tests against loopback containers (enforcing fail-closed preflight checks on `.pni/pentests/<target>/`).
- **Topological Migration Wave Analysis (`migration_analyze`)**: Computes strongly connected dependency cycles, external boundary touchpoints, and bottom-up leaf-to-entrypoint `refactoring_waves` directly from the verified import DAG.

### 3. Stateful Pull-Push Execution, 3-Aspect Grounded Architecture & `audit -> migration` Chaining (`_workflows`)
`pni workflows` drives the agent through a SQLite state machine (`.pni/cache/workflow_state.db`) via `start`, `get-action`, and `push-action` (alongside zero-prep `run-action` for single-step iteration):
- **3-Aspect Grounded Architecture Recording (`record_architecture`)**: Before scoring, the agent records system comprehension across three explicit aspects—`purpose_and_stack`, `layers_and_modules`, and `flows_and_state`—while PNI validates every cited file and module path against `module_inventory` before persisting `.pni/cache/<workflow_id>/architecture.json`.
- **7-Axis Health Scoring (`emit_score`)**: The agent synthesizes rule compliance and prioritized findings into a schema-validated `ScoreResult` (`reports/<target>_score.json`) across **7 core engineering axes**: `architecture`, `code_quality`, `typing`, `testing`, `dependencies`, `security`, and `documentation`.
- **Prerequisite-Gated Migration Chaining (`based_on` -> `emit_migration_plan`)**: Migration workflows (`category: migration`) declare `based_on: <audit_workflow_id>`, failing closed unless a `COMPLETED` audit run exists in `workflow_state.db`, then inherit verified As-Is audit facts and architecture records to emit a path-validated `MigrationPlanResult` (`reports/<target>_migration_plan.json`).

### 4. Blueprint-Driven 7-Chapter Visual Drawlib Reports (`_reporter`)
To minimize human cognitive load during technical triage and architecture review, `_reporter` generates a deterministic JSON blueprint (`blueprint.json` or `migration_blueprint.json`) that guides the authoring of a **7-chapter Drawlib `doc` report** (`00_cover.md` + `01..06` under `reports_src/<target>_src/`). Combining executive `KpiCards`, 7-axis `RadarChart`s, 2D module `HeatmapChart`s, architectural risk `HeatmapOverlay`s, and phased `P0`–`P2` / wave `Roadmap`s, `pni report build` compiles crisp print-ready A4 vector PDFs (`reports/<target>.pdf`) and HTML deliverables with zero broken links.
