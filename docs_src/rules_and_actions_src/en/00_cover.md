# pni501 Rules & Actions — Reference Catalog & Multi-Language Roadmap

**Package**: `pni501` (`import pni` / CLI: `pni`) | **Theme**: Google Style (`en`) | **Scope**: Built-In Standards, Actions & Expansion Plan

This specification provides the human-oriented engineering reference for **Rules (`_rules`)** and **Actions (`_actions`)** in **Project Nemesis Index (`pni501`)**. It documents both the **currently implemented built-in catalog** (Chapters 1–3) and the **planned multi-language, framework, and external scanner roadmap** (Chapter 4), while AI-executable implementation plans remain cleanly separated under `.agents/plans/`.

```drawlib file=ra_cover_kpis.png caption="pni501 Rules & Actions Inventory at a Glance: Implemented Core vs. Multi-Language Expansion"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

outer = Panel(
    "pni501 Rules & Actions — Current Baseline & Extensible Architecture",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
outer.draw(xy=(3.0, 3.0), width=140.0, height=56.0)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Muted.patch(text_size=9.8),
    accent_position="left_pill",
    accent_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
    spacing=3.5,
)
cards.add(
    "25 Rules",
    "Built-In Markdown Standards",
    "12 Common + 7 Python + 6 Java",
    icon=phosphor.book_open_text,
)
cards.add(
    "13 Actions",
    "Composable Audit Bundles",
    "7 Universal + 3 Python + 3 Java",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=14.0),
    icon_style=Styles.SecondaryBold,
    icon=phosphor.stack,
)
cards.add(
    "8 Checkers",
    "Deterministic AST Suite",
    "Imports, Types, Docs, SIG, Ops",
    icon=phosphor.tree_structure,
)
cards.add(
    "3 Tiers",
    "Language Expansion Matrix",
    "Cat A Mainstream / Cat B / Cat C",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=14.0),
    icon_style=Styles.SuccessBold,
    icon=phosphor.globe_hemisphere_west,
)
cards.draw(xy=(7.0, 6.5), width=132.0, height=42.5, columns=2)
save()
```

---

## Executive Overview: Orthogonal Standards & Deterministic Synthesis

Modern software engineering audits fail when language-specific syntax checks are entangled with architectural governance, or when Large Language Models are asked to both invent evaluation criteria and summarize findings ad hoc. `pni501` solves both problems through two core design principles:

- **Orthogonal Rule & Action Layering**: Universal engineering standards—such as OpenSSF supply-chain security, 12-Factor configuration, Google SRE production readiness, SIG maintainability thresholds, clig.dev CLI ergonomics, public library hygiene, and Diátaxis documentation—are defined once in `common/*`. Language packs (`python/*`, `java/*`, and future `typescript/*`, `go/*`, `rust/*`) focus strictly on language idioms, build manifests, type systems, and framework rules.
- **Action-Driven Map → Deterministic Python Reduce → 5-Chapter Blueprint**: Every audit action requires structured, schema-validated outputs (`step_score`, per-rule `rule_checks`, and file-grounded `findings`) at push time. Python (`aggregator.py` and `blueprint.py`) deterministically deduplicates, computes module risk hotspots, and sorts all compliance checks (`FAIL → WARN → PASS`) and findings (`CRITICAL → INFO`) before the AI renders the final 5-chapter Drawlib report.

```drawlib file=ra_cover_pipeline.png caption="End-to-End Rule-to-Blueprint Pipeline: Grounded Map Step Submissions Followed by Deterministic Python Sorting"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, ChevronProcess
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

pipeline = ChevronProcess(
    style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.3),
    corner_angle=60.0,
    spacing=1.6,
    flat_left_end=True,
)
pipeline.add("1. Extract Facts", description="AST & Manifests")
pipeline.add("2. Inject Rules", description="Scoped Standards", style=Styles.Neutral)
pipeline.add(
    "3. Push Action",
    description="Per-Rule Checks",
    style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.3),
)
pipeline.add("4. Python Sort", description="Deterministic Digest", style=Styles.SecondaryNeutral)
pipeline.add(
    "5. Blueprint Doc",
    description="5-Chapter HTML/PDF",
    style=Styles.SuccessFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.3),
)
pipeline.draw(xy=(4.0, 41.0), width=138.0, height=18.0)

artifacts = CardList(
    style=Styles.Neutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.DarkBold,
    spacing=3.5,
)
artifacts.add(
    "_rules/*.md",
    "Universal & Lang\nAudit Criteria",
    icon=phosphor.book_bookmark,
)
artifacts.add(
    "_actions/*.yaml",
    "Facts + Grounded\nAI Prompts",
    icon=phosphor.gear_six,
)
artifacts.add(
    "aggregator.py",
    "FAIL->PASS &\nCRITICAL->INFO Sort",
    icon=phosphor.funnel,
)
artifacts.add(
    "blueprint.json",
    "Fixed 5-Chapter\nVisual Spec",
    icon=phosphor.file_pdf,
)
artifacts.draw(xy=(4.0, 5.0), width=138.0, height=30.0)
save()
```
