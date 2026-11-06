# pni501 Human-Facing Documentation (`drawlib doc`)

This directory contains the official human-readable specifications and visual catalogs for **`pni501` (Project Nemesis Index)**, authored as English Google-style **Drawlib `doc` projects**.

> **Scope Boundary**: Human-oriented visual architecture specs, catalogs, and strategic roadmaps live here in `docs_src/`. AI-executable implementation plans and internal engineering task specs live under `.agents/plans/`.

---

## Drawlib Document Projects

### 1. Core Architecture, Workflow Engine & Mechanism Specification (`doc_src/`)
- **`doc_src/en/`** *(Source of Truth, configured via `doc_src/drawlib.toml`)*:
  - `00_cover.md`: Cover page, four foundational pillars (`36` rules, `21` composite actions, `12` primitives), and end-to-end Audit & Migration pipeline.
  - `01_background_and_approach.md`: Multi-language (`Python`, `Java`, `PHP`) modernization bottlenecks, ad-hoc prompting failure modes, and the four-pillar PNI approach.
  - `02_domain_architecture.md`: High-cohesion domain packages (`_instructions`, `_rules`, `_actions`, `_workflows`, `_reporter`, `_pentests`, `_dockerfiles`, `_cache.py`), `.pni/cache/` self-healing storage, and 3-tier cascade resolution.
  - `03_actions_and_facts.md`: Two-tier `CompositeAction` -> `PrimitiveStep` expansion, all `6` deterministic analyzers (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`), 3-aspect grounded `record_architecture`, and the `12`-primitive schema catalog.
  - `04_workflow_usage_and_preflight.md`: Practical `pni workflows` operator & agent guide—fail-closed pre-flight readiness flowchart (`web_pentest` & `based_on` migration gates), the three operating modes (`Pull-Push`, zero-SQLite `run-action`, and `status`/`inspect-action`/`cancel`), and YAML step normalization.
  - `05_stateful_engine_and_chaining.md`: Deep dive inside `_workflows`—chronological Pull-Push sequence with `module_inventory` grounding verification, SQLite ER schema & 4-state `RunStatus` lifecycle (`pending`/`in_progress`/`completed`/`cancelled`), and two-stage `audit -> migration` SQLite chaining (`based_on_run_id`).
  - `06_scoring_and_drawlib_reporter.md`: 7-axis `ScoreResult` & `aggregator.py`, `MigrationPlanResult`, dual 7-chapter `ReportBlueprint` pipeline, 9-target multi-language (`Python`/`Java`/`PHP`) benchmark matrix, and complete CLI reference.
- **Generated Deliverables**: `doc.pdf`, `doc_html/index.html` (`doc_html/en/index.html`), `doc_markdown/en/`, `doc_images/`.

### 2. Rules & Actions Reference Catalog & Roadmap (`rules_and_actions_src/`)
- **`rules_and_actions_src/en/`** *(Source of Truth, configured via `rules_and_actions_src/drawlib.toml`)*:
  - `00_cover.md`: Inventory KPIs (`25` built-in rules, `13` composite actions, `8` AST checkers, `3` language tiers) and the Map-Reduce-Blueprint dataflow.
  - `01_taxonomy_and_cascade.md`: Orthogonal layering (`common/*` universal standards vs. `<lang>/*` syntax & frameworks) and `.pni/` local override cascade.
  - `02_current_rules_catalog.md`: Complete catalog of implemented `common/*` (OpenSSF, SIG, OWASP, 12-Factor, SRE PRR, clig.dev, Library Hygiene, Diátaxis), `python/*`, and `java/*` rules with deterministic `Facts` / `AST` grounding signals.
  - `03_current_actions_and_pipeline.md`: Catalog of all `8` `PrimitiveType`s and `13` composite actions, plus the deterministic Python `aggregator.py` (`FAIL -> WARN -> PASS`, `CRITICAL -> INFO`) and 5-chapter `ReportBlueprint` pipeline.
  - `04_future_roadmap.md`: Clearly labeled **Planned Roadmap** covering the `Cat A / Cat B / Cat C` multi-language expansion matrix (TypeScript/TSX, Go, Rust, Kotlin, transitional & legacy advisories), framework packs, and sandboxed `run_check` external scanners.
- **Generated Deliverables**: `rules_and_actions.pdf`, `rules_and_actions_html/index.html` (`rules_and_actions_html/en/index.html`), `rules_and_actions_markdown/en/`, `rules_and_actions_images/`.

### 3. PNI501 Introduction Slide Deck — Japanese Google Style (`slide_src/`)
- **`slide_src/ja/`** *(Source of Truth — 16:9 `drawlib slide` project, `--style google --lang ja`, configured via `slide_src/drawlib.toml`)*:
  - `01_title.md` – `02_agenda.md`: Cover & 4-part roadmap.
  - `03_overview_concept.md` – `04_overview_workflow.md`: Core motivation (zero-hallucination deterministic + AI architecture) and Pull-Push workflow pipeline.
  - `05_scenario_continuous.md` – `07_scenario_migration.md`: Three primary use cases—continuous in-development quality tracking (original motivation), existing/legacy software health inspection, and `based_on`-chained migration planning.
  - `08_axes_current_seven.md` – `09_axes_future_dev_status.md`: Inspection axes catalog—the `7` implemented quality axes (`Architecture`, `Code Quality`, `Typing`, `Testing`, `Dependencies`, `Security`, `Documentation`) plus the planned/unimplemented `8th` axis (`開発ステータス`: Git commit activity × Gantt chart schedule variance).
  - `10_summary.md` – `11_thank_you.md`: Executive summary & closing Q&A slide.
- **Generated Deliverables**: `slide.pdf`, `slide_html/ja/index.html` (supports Presenter View via `?presenter=1` or `P`/`S` key), `slide_images/`.

---

## Building & Previewing

From the repository root:

```bash
# Build Core Architecture Specification (HTML + PDF + Markdown + Images)
./docs_src/doc_src/build.sh

# Build Rules & Actions Catalog & Roadmap (HTML + PDF + Markdown + Images)
./docs_src/rules_and_actions_src/build.sh

# Build Japanese Introduction Slide Deck (16:9 HTML + Vector PDF + Images)
./docs_src/slide_src/build.sh

# Preview HTML / Slide Decks locally
./docs_src/doc_src/serve.sh
./docs_src/rules_and_actions_src/serve.sh
./docs_src/slide_src/serve.sh
```
