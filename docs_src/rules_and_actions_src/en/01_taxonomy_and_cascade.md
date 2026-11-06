# 1. Orthogonal Taxonomy & Local Cascade Architecture

To scale software health evaluation across diverse runtime archetypes and programming languages without combinatorial duplication, `pni501` organizes both **Rules** (`src/pni/_rules/`) and **Composite Actions** (`src/pni/_actions/`) along two orthogonal axes: **universal engineering governance** versus **language- and framework-specific mechanics**, backed by a deterministic local `.pni/` override cascade.

```drawlib file=ra_cascade_architecture.png caption="Two-Layer Local Cascade (.pni/ Overrides Over Built-In Packages) Across Common, Python, and Java Scopes"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=9.8),
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.6),
)

local_grp = diag.add(
    NodeGroup(
        title="Priority 1: Local Overrides (.pni/)",
        width=50.0,
        height=27.0,
        style=Styles.SecondaryNeutral.patch(shape_r=2.0),
        text_style=Styles.SecondaryBold.patch(text_size=9.8, halign="left", valign="top"),
    ),
    xy=(3.5, 36.5),
)
n_loc_rules = local_grp.add(
    Node(".pni/rules/\n<scope>/*.md", width=21.0, height=14.5, icon=PhosphorIcon.FOLDER_USER, icon_size=5.2),
    xy=(13.0, 10.5),
)
n_loc_acts = local_grp.add(
    Node(".pni/actions/\n<scope>/*.yaml", width=21.0, height=14.5, icon=PhosphorIcon.FILE_PLUS, icon_size=5.2),
    xy=(37.0, 10.5),
)

builtin_grp = diag.add(
    NodeGroup(
        title="Priority 2: Built-In Catalog (src/pni/)",
        width=50.0,
        height=29.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=9.8, halign="left", valign="top"),
    ),
    xy=(3.5, 3.5),
)
n_bi_common = builtin_grp.add(
    Node("common/*\n(12 Rules / 7 Acts)", width=21.5, height=15.5, icon=PhosphorIcon.GLOBE, icon_size=5.0),
    xy=(13.2, 11.0),
)
n_bi_lang = builtin_grp.add(
    Node("python/* & java/*\n(13 Rules / 6 Acts)", width=21.5, height=15.5, icon=PhosphorIcon.CODE, icon_size=5.0),
    xy=(37.2, 11.0),
)

resolver = diag.add(
    Node(
        "Cascade Resolver\n(RuleManager &\nActionManager)",
        width=27.0,
        height=24.0,
        icon=PhosphorIcon.FUNNEL,
        icon_size=6.0,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=9.8),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.8),
    ),
    xy=(81.5, 34.0),
)

wf_out = diag.add(
    Node(
        "Normalized Workflow\n(PrimitiveStep[] +\nActive Rule Texts)",
        width=30.0,
        height=24.0,
        icon=PhosphorIcon.CHECK_SQUARE_OFFSET,
        icon_size=6.0,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=1.8),
    ),
    xy=(126.0, 34.0),
)

diag.connect(local_grp, resolver, label="1st", routing="orthogonal", style=Styles.SecondaryBold)
diag.connect(builtin_grp, resolver, label="2nd", routing="orthogonal")
diag.connect(resolver, wf_out, label="expand", routing="direct", style=Styles.SuccessBold)

diag.draw(xy=(0.0, 0.0))
save()
```

---

## 1.1 Orthogonal Separation: Runtime Archetype vs. Language Syntax

A recurring anti-pattern in static analysis toolchains is rewriting architectural, security, and operational rules separately for every programming language. In `pni501`, rules are partitioned strictly by **what kind of engineering invariant they govern**:

1. **Universal Standards (`common/*`)**: Govern invariants that hold true regardless of implementation language—such as layered dependency direction (`common/architecture`), SIG unit complexity limits (`common/maintainability`), OpenSSF lockfile and CI token hygiene (`common/supply_chain`), OWASP secret/injection defenses (`common/security`), 12-Factor statelessness (`common/twelve_factor`), Google SRE I/O timeouts (`common/production_readiness`), `clig.dev` CLI ergonomics (`common/cli_guidelines`), public library API contracts (`common/library_guidelines`), and Diátaxis documentation (`common/documentation`).
2. **Language Core Packs (`<lang>/*`)**: Govern syntax-level idioms, compiler/type-checker strictness, package manager manifests, and unit test conventions—such as PEP 621 `pyproject.toml` + `uv.lock` and PEP 484 annotations in `python/*`, or Maven/Gradle wrappers, Generics safety, and JUnit 5 package mirrors in `java/*`.
3. **Framework Overlay Packs (`<lang>/frameworks/*`)**: Govern framework-specific lifecycle and DI patterns—such as `python/frameworks/fastapi` (lifespan context managers, `Depends()`, Pydantic boundary schemas) and `java/frameworks/spring_boot` (constructor injection over `@Autowired` fields, `@ConfigurationProperties`, transaction boundaries).

```drawlib file=ra_scope_orthogonality.png caption="Three-Layer Rule & Action Composition: Combining Universal Archetype Governance with Language & Framework Packs"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

panel = Panel(
    "Composable Audit Formula = Common Foundation + Runtime Archetype + Language/Framework Pack",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
panel.draw(xy=(3.0, 3.0), width=140.0, height=56.0)

layers = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.PrimaryBold,
    spacing=4.0,
)
layers.add(
    "Layer 1: Universal Core",
    "common/architecture\ncommon/maintainability\ncommon/supply_chain\ncommon/security & docs",
    icon=phosphor.shield_check,
)
layers.add(
    "Layer 2: Runtime Archetype",
    "Library -> library_guidelines\nCLI Tool -> cli_guidelines\nService -> twelve_factor +\nproduction_readiness",
    badge_style=Styles.SecondaryFlat,
    icon=phosphor.cube,
)
layers.add(
    "Layer 3: Language & FW",
    "python/* (+ fastapi)\njava/* (+ spring_boot)\n[Planned: ts/*, go/*,\nrust/*, kotlin/*]",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.brackets_curly,
)
layers.draw(xy=(7.0, 8.0), width=132.0, height=41.0)
save()
```

---

## 1.2 Scoped Resolution Precedence & CLI Inspection

Both `RuleManager` (`src/pni/_rules/manager.py`) and `ActionManager` (`src/pni/_actions/manager.py`) implement deterministic cascade resolution so teams can customize organizational rules without forking `pni501`:

- **Explicit Scoped IDs (`python/typing`, `common/supply_chain`)**: Resolved by checking `.pni/rules/<scope>/<name>.md` first; if absent, `pni` falls back to the built-in `src/pni/_rules/<scope>/<name>.md`.
- **Unqualified Action IDs in Workflows (`uses: repo_structure_audit`)**: When a workflow declares a top-level `lang: python` (or `lang: java`), unqualified action references automatically search `<lang>/<action_id>.yaml` before falling back to `common/<action_id>.yaml`, checking `.pni/actions/` ahead of built-in `src/pni/_actions/` at each step.
- **Transparent Inspection Commands**: Engineers can inspect which source (`local` vs. `builtin`) wins for every rule and composite action at any time via `pni rules list`, `pni rules show <id>`, `pni actions list`, and `pni actions show <id>`.
