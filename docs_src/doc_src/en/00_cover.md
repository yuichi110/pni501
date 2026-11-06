# pni501 (Project Nemesis Index) — Architecture & Mechanism Specification

**Package**: `pni501` (`v0.1.0` | `import pni` / CLI: `pni`) | **Languages**: `Python`, `Java`, `PHP` | **Theme**: Google Style (`en`) | **Architecture**: AI-Native Deterministic Software Health & Migration Engine

**Project Nemesis Index (`pni501`)** is an AI-native software health evaluation, security auditing, and migration planning framework supporting **`Python`**, **`Java`**, and **`PHP`** repositories. By uniting **cascading multi-language engineering rules** (`_rules`), **zero-hallucination static, container, security, and penetration analyzers** (`_actions`), a **SQLite-backed stateful Pull-Push workflow engine** (`_workflows`), and **blueprint-driven Drawlib visual reporting** (`_reporter`), `pni501` eliminates LLM metric and path hallucinations while producing actionable 7-axis health scores, topological migration plans, and publication-grade 7-chapter A4 PDF reports.

```drawlib file=pni_cover_pillars.png caption="Core Architectural Pillars of pni501 (Project Nemesis Index v0.1.0)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=152, height=70, dpi=150)

outer = Panel(
    "Project Nemesis Index (pni501 v0.1.0) — Four Foundational Pillars",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
outer.draw(xy=(3.0, 3.0), width=146.0, height=64.0)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    accent_position="left_pill",
    accent_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
    spacing=3.5,
)
cards.add(
    "P1",
    "Cascading Rules (_rules)",
    "36 built-in rules + .pni/ overrides\nUniversal, archetype & Py/Java/PHP",
    icon=phosphor.book_open_text,
)
cards.add(
    "P2",
    "Zero-Guess Analyzers (_actions)",
    "AST, container tests/smoke, Trivy\nCVE/secrets, pentest & wave DAG",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=13.5),
    icon_style=Styles.SecondaryBold,
    icon=phosphor.cpu,
)
cards.add(
    "P3",
    "Stateful Engine (_workflows)",
    "SQLite Pull-Push, ad-hoc run-action,\npreflight gates & based_on chain",
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
cards.draw(xy=(6.5, 6.0), width=139.0, height=50.5, columns=2)
save()
```

---

## Executive Overview: Hybrid Deterministic + Cognitive Auditing & Migration

Purely LLM-driven code reviews suffer from non-deterministic counting errors, invented module paths, skipped checklist categories, and complete blindness to runtime container behavior, dependency CVEs, and live HTTP attack surfaces. Conversely, purely static linters cannot evaluate domain boundary cohesion, aspect-separated system architecture, or phased modernization trade-offs.

`pni501` (`v0.1.0`) bridges both worlds across **`Python`**, **`Java`**, and **`PHP`** through **`36` built-in cascading rules** (`common/`, `python/`, `java/`, `php/`), **`21` reusable composite actions**, and **`12` canonical `PrimitiveType`s** orchestrated in a dual-track audit-to-migration pipeline:

- **Programmatic Multi-Modal Fact Extraction (`6` Deterministic Primitives)**: `pni` executes `project_inspect`, polyglot `ast_analyze` (Python `ast` + `ast-grep-py` for Java/PHP), isolated Docker `run_check` (unit tests, coverage, HTTP smoke checks), socketless Trivy `security_scan` (SCA CVEs, IaC misconfigurations, leaked secrets), loopback `pytest` + `httpx` `web_pentest`, and topological `migration_analyze`—persisting exact telemetry into `.pni/cache/<workflow_id>/facts.json` and `.pni/cache/workflow_state.db`.
- **Schema-Enforced Cognitive Audit, Chained Migration & Visual Reporting (`6` AI/Report Primitives)**: Guided step-by-step via `workflow_state.db`, the Code AI Agent loads scoped rules (`load_rules`), records path-verified 3-aspect architecture (`record_architecture` -> `architecture.json`), evaluates rule compliance (`ai_interpret`), emits a 7-axis `ScoreResult` (`reports/<target>_score.json`), optionally chains a `based_on` migration workflow into a validated `MigrationPlanResult` (`reports/<target>_migration_plan.json`), and compiles a 7-chapter **Drawlib visual report** (`reports/<target>.pdf` and optional HTML).

```drawlib file=pni_end_to_end_pipeline.png caption="End-to-End Dual-Track Execution Pipeline: From Deterministic Facts to 7-Axis Score, Optional Migration Plan & 7-Chapter Drawlib PDF"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, ChevronProcess
from drawlib.styles import Styles

setup(width=154, height=68, dpi=150)

pipeline = ChevronProcess(
    style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
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
    text_style=Styles.WhiteBold.patch(text_size=10.0),
    description_style=Styles.White.patch(text_size=9.5),
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
    text_style=Styles.WhiteBold.patch(text_size=10.0),
    description_style=Styles.White.patch(text_size=9.5),
)
pipeline.draw(xy=(3.0, 42.5), width=148.0, height=21.5)

artifacts = CardList(
    style=Styles.Neutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
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
    "Score & Migration JSON",
    "reports/<target>_score.json\n& *_migration_plan.json",
    icon=phosphor.medal,
)
artifacts.add(
    "7-Chapter Report",
    "reports/<target>.pdf\nVector A4 PDF & HTML",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.file_pdf,
)
artifacts.draw(xy=(3.0, 4.5), width=148.0, height=32.5)
save()
```
