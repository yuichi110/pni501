# pni501 (Project Nemesis Index) — Official Documentation

**Project Nemesis Index (`pni501` `v0.1.4`)** is an AI-native software health auditing, security penetration testing, and migration planning framework for **Python**, **Java**, **PHP**, **Go**, **TypeScript**, and **JavaScript** repositories. By combining deterministic static and container analyzers with a SQLite-backed stateful Pull-Push workflow engine and Drawlib visual reporting, `pni501` eliminates LLM metric and path hallucinations while delivering reproducible 7-axis health scores, topological migration plans, and publication-grade A4 PDF reports.

```drawlib align=center code=fold file=pni_overview_pillars.png caption="Core Architectural Pillars & Polyglot Capabilities of pni501 (v0.1.4)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=156, height=90, dpi=150)

outer = Panel(
    "Project Nemesis Index (pni501 v0.1.4) — Four Foundational Pillars",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.5),
)
outer.draw(xy=(3.0, 24.0), width=150.0, height=63.0)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.8),
    description_style=Styles.Dark.patch(text_size=10.0),
    accent_position="left_pill",
    accent_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
    spacing=3.5,
)
cards.add(
    "P1",
    "Cascading Rules (_rules)",
    "52 built-in rules + .pni/ overrides\nPy, Java, PHP, Go, TS & JS",
    icon=phosphor.book_open_text,
)
cards.add(
    "P2",
    "Zero-Guess Analyzers (_actions)",
    "15 composite actions: AST, Docker,\nTrivy CVE/secrets, pentest & DAG",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=13.5),
    icon_style=Styles.SecondaryBold,
    icon=phosphor.cpu,
)
cards.add(
    "P3",
    "Stateful Engine (_workflows)",
    "6 workflow templates, SQLite Pull-Push,\npreflight gates & based_on chaining",
    icon=phosphor.database,
)
cards.add(
    "P4",
    "Blueprint Reporter (_reporter)",
    "7-axis ScoreResult, MigrationPlan\n& 7-chapter A4 PDF / HTML reports",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.SuccessBold,
    icon=phosphor.chart_polar,
)
cards.draw(xy=(6.5, 27.0), width=143.0, height=49.5, columns=2)

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.6),
    metric_style=Styles.PrimaryBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
kpis.add("6 Languages", "Py / Java / PHP / Go / TS / JS")
kpis.add("15 Actions", "Reusable Audit & Plan Steps")
kpis.add("6 Workflows", "Audit, Quick & Chained Runs")
kpis.add("7 Quality Axes", "0–100 Score & S–D Grades")
kpis.draw(xy=(3.0, 3.0), width=150.0, height=18.0, columns=4)
save()
```

## 1. Executive Overview: Hybrid Deterministic + AI Engineering Engine

Purely prompt-driven LLM code reviews suffer from non-deterministic counting errors, invented file paths, skipped audit categories, and blindness to container runtime behavior, dependency CVEs, and live HTTP attack surfaces. Conversely, purely static linters cannot evaluate domain boundary cohesion, aspect-separated system architecture, or phased modernization trade-offs.

`pni501` (`v0.1.4`) bridges both worlds across **6 languages** (`Python`, `Java`, `PHP`, `Go`, `TypeScript`, and `JavaScript`) by orchestrating **52 cascading engineering rules**, **15 composite actions**, and **6 stateful workflow templates** in a unified pipeline:

- **Programmatic Multi-Modal Fact Extraction**: `pni` executes deterministic analyzers—`project_inspect`, polyglot `ast_analyze` (Python `ast` and `ast-grep-py` across Java, PHP, Go, TypeScript, and JavaScript), isolated Docker `run_check` (offline unit tests, coverage, and HTTP boot probes), socketless Trivy `security_scan` (CVEs, IaC misconfigurations, and leaked secrets), loopback `pytest` + `httpx` `web_pentest`, topological `migration_analyze`, and Git `progress_analyze`—persisting exact telemetry into `.pni/cache/<workflow_id>/facts.json` and `.pni/cache/workflow_state.db`.
- **Schema-Enforced AI Reasoning & Visual Reporting**: Guided step-by-step via SQLite (`workflow_state.db`), the Code AI Agent loads scoped rules (`load_rules`), records path-verified 3-aspect architecture (`record_architecture` -> `architecture.json`), evaluates rule compliance (`ai_interpret`), emits a 7-axis `ScoreResult` (`reports/<target>_score.json`), optionally chains `based_on` migration (`reports/<target>_migration_plan.json`) or progress (`reports/<target>_progress.json`) workflows, and compiles a **Drawlib visual report** (`reports/<target>.pdf` and HTML).

```drawlib align=center code=fold file=pni_end_to_end_pipeline.png caption="End-to-End Execution Pipeline: From Deterministic Facts to 7-Axis Score, Chained Migration Plan & Drawlib A4 PDF"
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
    spacing=1.5,
    flat_left_end=True,
)
pipeline.add(
    "1. Static & Runtime\nFacts",
    description="AST + Docker +\nTrivy + Pentest",
)
pipeline.add(
    "2. Grounded AI\nAudit",
    description="3-Aspect Arch +\nScoped Rules",
    style=Styles.Neutral,
)
pipeline.add(
    "3. 7-Axis Score",
    description="Validated\n<target>_score.json",
    style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    description_style=Styles.White.patch(text_size=10.0),
)
pipeline.add(
    "4. Migration Plan\n(Optional)",
    description="based_on ->\n*_migration_plan.json",
    style=Styles.SecondaryNeutral,
)
pipeline.add(
    "5. 7-Chapter\nDrawlib PDF",
    description="Vector A4\nreports/<target>.pdf",
    style=Styles.SuccessFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    description_style=Styles.White.patch(text_size=10.0),
)
pipeline.draw(xy=(3.0, 43.0), width=150.0, height=23.0)

artifacts = CardList(
    style=Styles.Neutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.DarkBold,
    spacing=3.0,
)
artifacts.add(
    "facts.json",
    ".pni/cache/<wf>/facts.json\nAST, Docker, Trivy & pentest",
    icon=phosphor.file_magnifying_glass,
)
artifacts.add(
    "workflow_state.db",
    ".pni/cache/workflow_state.db\nPull-Push state & arch JSON",
    icon=phosphor.database,
)
artifacts.add(
    "Score & Plan JSON",
    "reports/<target>_score.json\n& *_migration_plan.json",
    icon=phosphor.medal,
)
artifacts.add(
    "Visual PDF Report",
    "reports/<target>.pdf\nVector A4 PDF & HTML",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.file_pdf,
)
artifacts.draw(xy=(3.0, 4.0), width=150.0, height=34.0)
save()
```

## 2. Key Capabilities at a Glance

| Capability Area | Built-In Assets (`v0.1.4`) | Primary Output / Guarantee |
| :--- | :--- | :--- |
| **Supported Languages** | **6 languages**: `Python`, `Java`, `PHP`, `Go`, `TypeScript`, `JavaScript` | Auto-detected from repository manifests & source files (`detect_active_language`) |
| **Cascading Engineering Rules** | **52 built-in rules** (`common/` + 6 language scopes) + `.pni/rules/` overrides | Enforces OWASP ASVS, OpenSSF Scorecard, 12-Factor, SRE PRR, CLI & library standards |
| **Composite Actions & Primitives** | **15 composite actions** per language scope expanding into **12+ canonical primitives** | Combines zero-guess deterministic analyzers with schema-validated AI interpretation |
| **Stateful Workflow Engine** | **6 language workflow sets** (`full_audit`, `quick_check`) + `migration` & `progress` | SQLite Pull-Push state machine (`workflow_state.db`) with fail-closed pre-flight gates |
| **7-Axis Quality Scoring** | `architecture`, `code_quality`, `typing`, `testing`, `dependencies`, `security`, `documentation` | Deterministic `0–100` axis & overall scores, `S`–`D` grades, and `P0`–`P2` action items |
| **Drawlib Visual Reporting** | Blueprint-driven 7-chapter Audit & Migration PDFs + 5-chapter Progress PDFs | High-density vector charts (`RadarChart`, `HeatmapChart`, `Roadmap`) via `pni report build` |

## 3. Quick Installation & First Audit

Install `pni501` via `pip` or `uv`, initialize `.pni/` in your repository, and launch a stateful workflow:

```bash
# Install pni501 from PyPI
pip install pni501
# Or with uv:
uv add pni501

# Initialize .pni/ configuration, rules, actions, and workflows
pni init
pni workflows list
pni workflows show full_audit

# Start the stateful Pull-Push workflow engine
pni workflows start full_audit
```

## 4. Documentation Roadmap

Explore the complete `pni501` documentation by section:

### 4.1 Getting Started
- [Background & Core Concepts](01_getting_started/concepts.md) — Why ad-hoc AI prompting fails on real-world repositories and how PNI's four pillars guarantee zero-hallucination audits.
- [Quickstart Guide](01_getting_started/quickstart.md) — Step-by-step installation, `.pni/` initialization, pre-flight readiness checks, and executing the `get-action` / `push-action` loop.
- [Primary Use Cases](01_getting_started/use_cases.md) — Continuous sprint health monitoring, black-box legacy auditing, and prerequisite-gated migration planning.
- [Release Notes](01_getting_started/release_notes.md) — Version history (`v0.1.0`–`v0.1.4`), new analyzer features, and CLI enhancements.

### 4.2 Architecture, Workflows, Scoring & Reference
- [Domain Architecture & Cascade](02_architecture/domain_architecture.md) and [Stateful Pull-Push Engine](02_architecture/stateful_engine.md) — Internal package design and SQLite state transitions.
- [Workflows & Pre-Flight Gates](03_workflows_and_actions/workflows_guide.md), [15 Actions & 12 Primitives](03_workflows_and_actions/actions_pipeline.md), and [Analyzers & Live Pentest](03_workflows_and_actions/analyzers_and_pentest.md) — Deep dive into YAML workflows and deterministic analyzers.
- [7-Axis Scoring Model](04_scoring_and_reports/scoring_model.md) and [Drawlib Visual Reporter](04_scoring_and_reports/drawlib_reporter.md) — Quantitative grading formulas and 7-chapter PDF report blueprints.
- [Supported 6 Languages](05_languages_and_reference/supported_languages.md) and [Rules & CLI Reference](05_languages_and_reference/rules_and_cli.md) — Polyglot analyzer matrix and complete CLI command reference.
