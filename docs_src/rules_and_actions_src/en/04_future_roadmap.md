# 4. Future Expansion Roadmap: Multi-Language Matrix, Frameworks & Tooling

> **Roadmap Status Notice**: Chapters 1–3 document features **implemented and tested today** in `pni501`. Everything in Chapter 4 represents the **planned expansion architecture** for upcoming releases (detailed AI execution specifications are maintained separately under `.agents/plans/`).

Because `common/*` rules (`12` files), universal archetype actions (`7` actions), the SQLite workflow engine, `aggregator.py`, and the 5-chapter `ReportBlueprint` are **100% language-agnostic**, onboarding a new programming language requires zero changes to core orchestration.

```drawlib file=ra_language_matrix_heatmap.png caption="Current vs. Planned Multi-Language Capability Matrix Across PNI Audit Dimensions (% Implemented Today)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    styles=[Styles.Neutral, Styles.SecondaryNeutral, Styles.PrimaryFlat, Styles.SuccessFlat],
    x_categories=["Common Rules", "Manifest/Lock", "AST & Types", "Docs/Quality", "Test AST", "FW Packs"],
    axis_line_style=Styles.Primary,
    axis_text_style=Styles.Dark.patch(text_size=9.8),
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    width=128.0,
    height=47.0,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    title="Current Implementation Coverage Across Language Tiers (100% = Shipped, <100% = Planned)",
    title_style=Styles.DarkBold.patch(text_size=11.2),
    value_format="{:.0f}%",
    background_style=Styles.Neutral.patch(shape_r=1.8),
)
hm.add_row("Python (Cat A - Done)", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("Java (Cat A - Done)", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("TS / TSX (Cat A - Next)", [100.0, 20.0, 0.0, 0.0, 0.0, 0.0])
hm.add_row("Go (Cat A - Next)", [100.0, 20.0, 0.0, 0.0, 0.0, 0.0])
hm.add_row("Rust / Kotlin (Cat A)", [100.0, 15.0, 0.0, 0.0, 0.0, 0.0])
hm.add_row("JS / Bash / PHP (Cat B)", [100.0, 25.0, 15.0, 15.0, 0.0, 0.0])
hm.add_row("Perl / Batch (Cat C)", [100.0, 40.0, 30.0, 20.0, 0.0, 0.0])
hm.draw(xy=(10.0, 16.5))
hm.draw_colorbar(
    xy=(43.0, 4.5),
    text_style=Styles.Dark.patch(text_size=9.8),
    length=60.0,
    label="Current Implementation Readiness (%)",
)
save()
```

---

## 4.1 Plug-and-Play Language Extension Contract

Adding first-class support for any new language `<lang>` follows a bounded, repeatable four-part module contract without touching `_workflows` or `_reporter`:

1. **Manifest & Lockfile Inspector (`_actions/project_inspect.py`)**: Parse the ecosystem's manifest and lockfile (e.g., `package.json` + `pnpm-lock.yaml`/`package-lock.json`, `go.mod` + `go.sum`, `Cargo.toml` + `Cargo.lock`).
2. **8-Checker `LanguageAnalyzerSuite` (`_actions/ast_analyze/<lang>/`)**: Implement language-specific subclasses of `ast_analyze/base/` (`imports`, `typing`, `docs`, `quality`, `dependencies`, `testing`, `framework`, `operational`) powered by bundled `ast-grep-py` Tree-sitter grammars.
3. **Scoped Rules (`_rules/<lang>/*.md`)**: Author `<lang>/code_quality`, `<lang>/typing`, `<lang>/dependencies`, `<lang>/testing`, and optional `<lang>/frameworks/<fw>.md`.
4. **3 Scoped Composite Actions (`_actions/<lang>/*.yaml`)**: Add `repo_structure_audit.yaml`, `<lang>_ast_audit.yaml`, and `<lang>_test_audit.yaml`.

---

## 4.2 Three-Tier Language Matrix (`Cat A` / `Cat B` / `Cat C`)

Rather than treating legacy scripting languages identically to modern statically typed languages, the roadmap classifies languages into three pragmatic tiers:

- **Category A — Modern Mainstream Languages (Full 8-Checker `ast-grep-py` Suite)**:
  - *Shipped*: **Python** (`stdlib ast` + `ast-grep-py`) and **Java** (`ast-grep-py`).
  - *Phase 2 Priority*: **TypeScript / TSX** (`tsconfig` strictness, `any`/`as unknown` leakage, TSDoc, ESM import cycles, Vitest/Jest AST) and **Go** (`go.mod`/`go.sum`, unchecked `err`, `context.Context` propagation, `godoc`, table-driven `testing.T`).
  - *Phase 3 Priority*: **Rust** (`unsafe` blocks, `unwrap()`/`expect()` in library paths, `Cargo.lock` policy, rustdoc), **Kotlin** (null-safety `!!` abuse, coroutine structured concurrency), **C#**, and **Modern C++ (C++17/20)**.
- **Category B — Transitional & Scripting Languages (AST Audit + Modernization Advisory)**:
  - Covers **JavaScript (`.js`/`.mjs`)**, **Bash / Shell (`.sh`)**, **PHP (8.2+)**, **Ruby**, and **Raw C**.
  - Combines `ast-grep-py` defect checks (`set -euo pipefail` in Bash, `declare(strict_types=1)` in PHP, Sorbet/RBS hints in Ruby, unsafe buffer calls in C) with explicit **threshold advisories** (e.g., recommending migration from `.js` to TypeScript or rewriting `.sh` scripts exceeding `100` LOC into typed Python/Go CLIs).
- **Category C — Legacy Non-`ast-grep` Languages (Lightweight Scanner + Migration Roadmap)**:
  - Covers **Perl (`.pl`/`.pm`/`.cgi`)** (`use strict; use warnings;` verification) and **Windows Batch / VBScript (`.bat`/`.cmd`/`.vbs`)**.
  - Detected deterministically during `project_inspect` (`legacy_language_findings`) to surface P1/P2 modernization roadmaps without requiring heavy parser dependencies.

---

## 4.3 Framework Rule Packs & Sandboxed `run_check` Tooling

Beyond language syntax, two horizontal capability expansions are planned:

- **Framework Rule Packs (`<lang>/frameworks/*`)**: Expanding beyond `python/frameworks/fastapi` and `java/frameworks/spring_boot` to cover **Django** (ORM N+1 & migration safety), **React / Next.js** (hook purity, server/client boundary leaks), **Gin / Echo** (middleware timeout & context handling), and **Axum / Actix-Web**.
- **Deterministic External Scanner Integration (`run_check` Primitive)**: Optional opt-in recipes connecting `run_check` to local security and quality tools—such as **`osv-scanner` / `pip-audit`** (live CVE lookup against lockfiles), **`ruff` / `ty`** (compiler-grade diagnostics), **`pytest --cov` / `jacoco`** (line/branch execution coverage), and **`trivy`** (container/IaC scanning)—feeding structured counters directly into `WorkflowFactsBundle`.

```drawlib file=ra_expansion_roadmap.png caption="Phased Evolution Roadmap for pni501 Rules, Actions, Language Suites, and External Scanners"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=9.4),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.SuccessBold,
    direction="horizontal",
    card_shape="rounded_rect",
    alternating=False,
)
rm.add(
    "Phase 1 (Shipped)",
    "Common Standards (12)\nPython & Java Suites\nBlueprint Aggregator",
    badge_text="DONE",
    icon=phosphor.check_circle,
    badge_style=Styles.SuccessFlat,
    icon_style=Styles.SuccessBold,
)
rm.add(
    "Phase 2 (Next)",
    "TypeScript/TSX & Go\n8-Checker AST Suites\nReact & Gin FW Rules",
    badge_text="NEXT",
    icon=phosphor.code,
    badge_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
)
rm.add(
    "Phase 3 (Planned)",
    "Rust & Kotlin Suites\nCat B/C Modernization\nDjango & Axum Packs",
    badge_text="PLAN",
    icon=phosphor.stack,
    badge_style=Styles.SecondaryFlat,
    icon_style=Styles.SecondaryBold,
)
rm.add(
    "Phase 4 (Planned)",
    "run_check Scanners\n(OSV, Trivy, Coverage)\nCI Score Delta Gates",
    badge_text="PLAN",
    icon=phosphor.shield_check,
    badge_style=Styles.SecondaryFlat,
    icon_style=Styles.SecondaryBold,
)
rm.draw(xy=(4.0, 6.0), width=138.0, height=48.0)
save()
```
