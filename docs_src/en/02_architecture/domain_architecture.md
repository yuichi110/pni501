# Domain Architecture & Three-Tier Cascade Resolution

`pni501` (`v0.1.4`) organizes its implementation under `src/pni/` around **seven vertical domain packages** (`_workflows`, `_actions`, `_reporter`, `_rules`, `_pentests`, `_dockerfiles`, and `_instructions`), a project manifest loader (`_config.py`), a self-healing cache utility (`_cache.py`), and a thin Typer + Rich CLI orchestrator (`cli.py`). Each domain colocates its Pydantic v2 schemas, execution or resolution logic, and built-in `.md`, `.yaml`, `.dockerfile`, or `.tmpl` assets across all **6 supported languages** (`python`, `java`, `php`, `go`, `typescript`, and `javascript`)—preserving a strict module-level Directed Acyclic Graph (`circular_dependencies = []`).

```drawlib align=center code=fold file=domain_layer_hierarchy.png caption="High-Cohesion Domain Package Hierarchy and Module-Level Dependency DAG in src/pni/"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Colors, Styles

setup(width=172, height=108, dpi=150)

diagram = ClassDiagram(
    node_style=Styles.Neutral.patch(text_size=10.0),
    header_style=Styles.PrimaryNeutral.patch(text_size=10.5),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
)

inst_node = ClassNode(
    "pni._instructions & _config",
    width=48.0,
    header_height=5.6,
    row_height=3.8,
)
inst_node.add_attribute("_config.py", ".pni/pni.toml & [[opt_out]]")
inst_node.add_attribute("manager.py", "agent.md cascade")
diagram.add(inst_node, xy=(29.0, 93.5))

cli_node = ClassNode(
    "pni.cli (CLI Orchestrator)",
    width=52.0,
    header_height=5.6,
    row_height=3.8,
    header_style=Styles.PrimaryFlat.patch(text_color=Colors.White, text_size=10.5),
)
cli_node.add_attribute("sub-apps", "rules, workflows, report, pentests, cache")
cli_node.add_attribute("commands", "init, instructions, validate-*, version")
diagram.add(cli_node, xy=(86.0, 93.5))

pentest_node = ClassNode(
    "pni._pentests",
    width=48.0,
    header_height=5.6,
    row_height=3.8,
)
pentest_node.add_attribute("manager.py", ".pni/pentests/<target>/")
pentest_node.add_attribute("surface_codegen.py", "AST route probes")
pentest_node.add_attribute("templates (2)", "conftest & baseline .tmpl")
diagram.add(pentest_node, xy=(29.0, 66.5))

wf_node = ClassNode(
    "pni._workflows",
    width=52.0,
    header_height=5.6,
    row_height=3.8,
    style=Styles.PrimaryNeutral.patch(text_size=10.0),
)
wf_node.add_attribute("engine + state_db", "SQLite + migration/progress")
wf_node.add_attribute("aggregator + adhoc", "digest, run-action, status")
wf_node.add_attribute("assets (12)", "6 langs x {full_audit, quick}")
diagram.add(wf_node, xy=(86.0, 66.5))

rep_node = ClassNode(
    "pni._reporter",
    width=48.0,
    header_height=5.6,
    row_height=3.8,
)
rep_node.add_attribute("blueprint.py", "audit & migration specs")
rep_node.add_attribute("drawlib_guide.py", "7-chapter report prompt")
rep_node.add_attribute("compiler.py", "lazy drawlib.tools build")
diagram.add(rep_node, xy=(143.0, 66.5))

docker_node = ClassNode(
    "pni._dockerfiles",
    width=48.0,
    header_height=5.6,
    row_height=3.8,
)
docker_node.add_attribute("manager.py", ".pni/dockerfiles/ harness")
docker_node.add_attribute("templates (10)", "py/java/php/go/ts/js")
diagram.add(docker_node, xy=(29.0, 39.0))

act_node = ClassNode(
    "pni._actions",
    width=52.0,
    header_height=5.6,
    row_height=3.8,
    style=Styles.SecondaryNeutral.patch(text_size=10.0),
    header_style=Styles.SecondaryNeutral.patch(text_size=10.5),
)
act_node.add_attribute("models + ai_actions", "12 core PrimitiveTypes")
act_node.add_attribute("analyzers (6+)", "inspect, ast, run, sec, pen, mig")
act_node.add_attribute("assets (15/lang)", "common (12) + 6 langs (3 ea)")
diagram.add(act_node, xy=(86.0, 39.0))

cache_node = ClassNode(
    "pni._cache (_cache.py)",
    width=48.0,
    header_height=5.6,
    row_height=3.8,
)
cache_node.add_attribute("self-healing", ".gitignore + CACHEDIR.TAG")
cache_node.add_attribute("workflow_state.db", "SQLite + trivy-cache/")
cache_node.add_attribute("cache/<wf>/", "facts, arch, blueprint, logs")
diagram.add(cache_node, xy=(143.0, 39.0))

rules_node = ClassNode(
    "pni._rules",
    width=52.0,
    header_height=5.6,
    row_height=3.8,
)
rules_node.add_attribute("base_model.py", "RuleInfo (<scope>/<name>)")
rules_node.add_attribute("manager.py", "detect_active_language() (6)")
rules_node.add_attribute("assets (50+)", "common + py/java/php/go/ts/js")
diagram.add(rules_node, xy=(86.0, 12.0))

diagram.connect(cli_node, inst_node, "dependency", start_side="left", end_side="right")
diagram.connect(cli_node, wf_node, "dependency", start_side="bottom", end_side="top")
diagram.connect(cli_node, rep_node, "dependency", start_side="right", end_side="top")
diagram.connect(wf_node, pentest_node, "dependency", start_side="left", end_side="right")
diagram.connect(wf_node, rep_node, "dependency", start_side="right", end_side="left")
diagram.connect(wf_node, act_node, "dependency", start_side="bottom", end_side="top")
diagram.connect(act_node, docker_node, "dependency", start_side="left", end_side="right")
diagram.connect(act_node, cache_node, "dependency", start_side="right", end_side="left")
diagram.connect(rep_node, cache_node, "dependency", start_side="bottom", end_side="top")
diagram.connect(act_node, rules_node, "dependency", start_side="bottom", end_side="top")

diagram.draw(xy=(0.0, 0.0))
save()
```

---

## 1. High-Cohesion Vertical Domain Packages (`src/pni/`)

Traditional CLI codebases often slice code horizontally—scattering Pydantic models across `models/`, YAML/Markdown loaders across `config/`, subprocess runners across `executors/`, and static files across `templates/`. Modifying a single audit capability then forces synchronized edits across four disconnected directories and inflates context overhead for both human maintainers and AI coding agents.

`pni501` instead organizes `src/pni/` into **self-contained vertical domain packages**. Top-level `src/pni/__init__.py` exports only package identity constants (`LIB_NAME = "pni501"`, `LIB_VERSION = "0.1.4"`, and `__version__`), while every subsystem colocates its schemas, orchestration modules, and packaged templates inside its own bounded directory:

| Package / Module | Core Python Modules | Key Schemas & Responsibilities | Packaged Built-in Assets |
| :--- | :--- | :--- | :--- |
| **`cli.py`** | `cli.py` | Typer root `app` + sub-apps (`rules`, `workflows`, `report`, `pentests`, `progress`, `cache`) and root commands (`init`, `instructions`, `validate-score`, `validate-migration-plan`, `version`, `--version` / `-V`) | Rich CLI help epilog & AI bootstrap instructions |
| **`_workflows/`** | `base_model.py`, `state_db.py`, `manager.py`, `engine.py`, `_migration_engine.py`, `_progress_engine.py`, `aggregator.py`, `adhoc.py`, `inspector.py` | `WorkflowDefinition`, `WorkflowFactsBundle`, `WorkflowStateDB`, `CompiledAuditDigest`; stateful pull/push engine, ad-hoc `run-action`, rewind, and run history inspection | `12` starter workflows across 6 languages (`{python,java,php,go,typescript,javascript}/{full_audit,quick_check}.yaml`) supporting 6 stateful workflow patterns |
| **`_actions/`** | `base_model.py`, `manager.py`, `ai_actions.py`, `project_inspect.py`, `_repo_governance.py`, plus `ast_analyze/`, `runtime_check/`, `security_scan/`, `pentest/`, `migration_analyze/`, `progress_analyze/` | `PrimitiveType` (`12` core audit/migration primitives), `ScoreResult` (7 axes), `ArchitectureRecord`, `MigrationPlanResult`, and deterministic fact extractors across 6 languages | `15` active composite YAML actions per language (`12` universal in `common/` + `3` in each `<lang>/` directory) |
| **`_reporter/`** | `base_model.py`, `blueprint.py`, `migration_blueprint.py`, `progress_blueprint.py`, `drawlib_guide.py`, `compiler.py` | `ReportBlueprint`, `ReportScaffoldResult`, `ReportBuildResult`; pre-sorts 7-chapter audit/migration blueprints, scaffolds `draw_pni_logo()` in `utils.py`, and lazily imports `drawlib.tools` in `compiler.py` | 7-chapter Drawlib `doc` scaffolding, automated chapter linter, and `_assets/{logo.png,logo_dark.png,favicon.png}` |
| **`_rules/`** | `base_model.py`, `manager.py` | `RuleInfo`, `SUPPORTED_LANGUAGES = ("python", "java", "php", "go", "typescript", "javascript")`, `detect_active_language()`, and `<scope>/<name>` cascade resolution | `50+` Markdown files across `common/` and 6 language packs (`python/`, `java/`, `php/`, `go/`, `typescript/`, `javascript/`) |
| **`_pentests/`** | `manager.py`, `surface_codegen.py` | Materializes and validates target-scoped `pytest + httpx` Web penetration suites in `.pni/pentests/<target>/`, generating `test_target_surface.py` from `AstFacts.api_endpoints` | `2` probe templates: `conftest.py.tmpl`, `test_baseline_http.py.tmpl` |
| **`_dockerfiles/`** | `manager.py` | Resolves `.pni/dockerfiles/_templates/` overrides or built-in container harnesses into `.pni/dockerfiles/` alongside an isolated `.dockerignore` and `prune_pni_container_artifacts()` | `10` templates: `python/{pip,poetry,uv}`, `java/{gradle,maven}`, `php/{composer,raw}`, `go/go`, `typescript/node`, `javascript/node.dockerfile` |
| **`_instructions/` & `_config.py`** | `base_model.py`, `manager.py`, `_config.py` | `InstructionInfo`, `PniConfig`, `OptOutEntry`; resolves `.pni/instructions.md` and `.pni/pni.toml` project manifests & `[[opt_out]]` waivers | `agent.md` & default `.pni/pni.toml` template |
| **`_cache.py`** | `_cache.py` | Self-healing `.pni/cache/` initializer (`ensure_cache_dir`, `ensure_cache_parent`) and workspace-safe path resolvers (`normalize_target_subpath`) | Auto-generated `.pni/cache/.gitignore` (`*`) and `CACHEDIR.TAG` |

Colocating Python modules and static assets inside each package makes `BUILTIN_*_DIR = Path(__file__).resolve().parent` deterministic in editable installs and packaged wheels alike.

---

## 2. Module-Level Dependency Hierarchy & Lazy Tooling Isolation

Every import across `src/pni/` forms a strict **module-level Directed Acyclic Graph**—verified continuously by `pni501` running `ast_analyze` on its own `src/pni/` tree (`circular_dependencies = []`):

1. **CLI Orchestrator (`src/pni/cli.py`)**: Parses user arguments, formats Rich tables and Markdown panels, and dispatches commands into `_workflows`, `_actions`, `_reporter`, `_rules`, `_pentests`, `_instructions`, `_config`, and `_cache`. No internal module ever imports `pni.cli`.
2. **Stateful Workflow Orchestration (`src/pni/_workflows/`)**:
   - `engine.py`, `_migration_engine.py`, and `_progress_engine.py` coordinate SQLite persistence (`state_db.py`), preflight prerequisite gates (`based_on` audit completion and `.pni/pentests/` readiness), deterministic step execution, path-grounding verification, and `aggregator.py` 7-axis score synthesis (`compile_workflow_digest`). See [Stateful Pull-Push Engine](stateful_engine.md) for full protocol details.
   - `adhoc.py` (`pni workflows run-action`) executes single workflow actions directly in memory with zero SQLite preparation, while `inspector.py` powers `pni workflows status` and `inspect-action` without exposing raw database queries.
3. **Action Subsystems & Supporting Harnesses (`_actions/`, `_reporter/`, `_pentests/`, `_dockerfiles/`)**:
   - Pure Pydantic data models in `_actions/base_model.py`, `_actions/ast_analyze/models.py`, and `_actions/migration_analyze/models.py` act as shared Leaf Schema contracts consumed cleanly by `_reporter/blueprint.py`, `_reporter/migration_blueprint.py`, and `_pentests/surface_codegen.py` without triggering cyclic runner imports.
   - Execution runners in `_actions/runtime_check/`, `_actions/security_scan/`, and `_actions/pentest/` delegate container harness setup to `_dockerfiles` and probe scaffolding to `_pentests`, while `_actions/ai_actions.py` delegates report prompt rendering to `_reporter/drawlib_guide.py`.
   - `_reporter/compiler.py` loads `drawlib.tools` **lazily** via `importlib.import_module("drawlib.tools")` behind a typed `_DrawlibToolsProtocol`, keeping `pni rules`, `pni workflows`, and `pni init` fast without importing Matplotlib/Cairo rendering stacks until `pni report` is invoked.
4. **Zero-Sibling Leaf Foundations (`_rules/`, `_instructions/`, `_cache.py`)**: Import zero sibling `pni._*` packages, providing pure language detection across all 6 languages, Markdown cascade lookup, and path-traversal-guarded cache management across the workspace.

---

## 3. Orthogonal Taxonomy: Universal Archetypes vs. Language Packs

A recurring anti-pattern in static analysis toolchains is rewriting architectural, security, and operational rules separately for every programming language. In `pni501`, rules (`src/pni/_rules/`) and composite actions (`src/pni/_actions/`) are partitioned along two orthogonal dimensions:

1. **Universal Standards (`common/*`)**: Govern invariants that hold true regardless of implementation language—such as layered dependency direction (`common/architecture`), SIG unit complexity limits (`common/maintainability`), OpenSSF lockfile and CI token hygiene (`common/supply_chain`), OWASP secret/injection defenses (`common/security`, `common/security_vulnerability`), 12-Factor statelessness (`common/twelve_factor`), Google SRE I/O timeouts (`common/production_readiness`), `clig.dev` CLI ergonomics (`common/cli_guidelines`), public library API contracts (`common/library_guidelines`), and Diátaxis documentation (`common/documentation`).
2. **Language Core Packs (`<lang>/*`)**: Govern syntax-level idioms, compiler/type-checker strictness, package manager manifests, and unit test conventions across **Python, Java, PHP, Go, TypeScript, and JavaScript**—paired with 3 language-scoped composite actions (`<lang>_ast_audit`, `<lang>_test_audit`, and `repo_structure_audit`).
3. **Framework Overlay Packs (`<lang>/frameworks/*`)**: Govern framework-specific lifecycle and DI patterns—such as `python/frameworks/fastapi`, `java/frameworks/spring_boot`, `php/frameworks/laravel`, and `php/frameworks/wordpress`.

```drawlib align=center code=fold file=scope_orthogonality_composition.png caption="Three-Layer Rule & Action Composition: Combining Universal Governance, Runtime Archetypes, and 6-Language Packs"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=158, height=64, dpi=150)

panel = Panel(
    "Composable Audit Formula = Common Foundation + Runtime Archetype + 6-Language/Framework Pack",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
panel.draw(xy=(3.0, 3.0), width=152.0, height=58.0)

layers = CardList(
    style=Styles.PrimaryNeutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.PrimaryBold,
    spacing=4.5,
)
layers.add(
    "Layer 1: Universal Core",
    "common/architecture\ncommon/maintainability\ncommon/supply_chain\ncommon/security & docs",
    icon=phosphor.shield_check,
)
layers.add(
    "Layer 2: Runtime Archetype",
    "Library -> library_guidelines\nCLI Tool -> cli_guidelines\nService -> twelve_factor +\nproduction_readiness",
    style=Styles.Neutral.patch(shape_r=1.6),
    badge_style=Styles.SecondaryFlat,
    icon=phosphor.cube,
)
layers.add(
    "Layer 3: 6 Languages & FW",
    "python, java, php\ngo, typescript, javascript\n+ FastAPI, Spring Boot,\nLaravel, WordPress",
    style=Styles.SecondaryNeutral.patch(shape_r=1.6),
    badge_style=Styles.SuccessFlat,
    icon=phosphor.brackets_curly,
)
layers.draw(xy=(7.0, 8.0), width=144.0, height=43.0)
save()
```

---

## 4. `.pni/` Workspace Layout & Three-Tier Cascade Resolution

Running `pni init [--lang/-l <python|java|php|go|typescript|javascript>] [--force/-f]` invokes `init_project()` in `src/pni/cli.py`, seeding a transparent `.pni/` configuration directory for the detected language while initializing the self-healing `.pni/cache/` hierarchy.

```drawlib align=center code=fold file=cascade_resolution_layout.png caption=".pni/ Workspace & Self-Healing Cache Hierarchy Alongside Three-Tier Cascade Resolution"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel, TreeNode
from drawlib.styles import Styles

setup(width=162, height=82, dpi=150)

left_panel = Panel(
    ".pni/ Workspace & Self-Healing Cache",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
left_panel.draw(xy=(3.0, 3.0), width=78.0, height=76.0)

root = TreeNode(
    ".pni/ (Committed Config + Isolated Cache)",
    text_style=Styles.PrimaryBold.patch(text_size=10.5),
    line_style=Styles.DarkBold,
    line_horizontal_margin=2.0,
    line_horizontal_length=2.2,
    line_vertical_margin=4.9,
)
root.add("pni.toml & instructions.md  (Manifest & Agent)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add("rules/{common,<lang>}/  (*.md rules)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add("actions/*.yaml  (15 composite actions)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add("workflows/*.yaml  (full_audit, quick_check)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add("dockerfiles/ & pentests/<target>/", text_style=Styles.DarkBold.patch(text_size=10.0))
cache_dir = root.add(
    "cache/  (.gitignore: '*' + CACHEDIR.TAG)",
    text_style=Styles.SecondaryBold.patch(text_size=10.0),
)
cache_dir.add("workflow_state.db & trivy-cache/", text_style=Styles.Dark.patch(text_size=10.0))
wf_cache = cache_dir.add("<workflow_id>/", text_style=Styles.SecondaryBold.patch(text_size=10.0))
wf_cache.add("facts.json, architecture.json, blueprint.json", text_style=Styles.Dark.patch(text_size=10.0))
wf_cache.add("runtime/, security/, pentest/  (logs & XML)", text_style=Styles.Dark.patch(text_size=10.0))
root.draw(xy=(6.0, 67.5))

cascade_cards = CardList(
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.5),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=3.8,
    show_arrows=True,
    arrow_style=Styles.DarkBold,
)
cascade_cards.add(
    "1. Local .pni/ Override",
    "Checks .pni/{pni.toml, instructions.md, rules/,\nactions/, dockerfiles/_templates/} first.",
    icon=phosphor.folder_open,
)
cascade_cards.add(
    "2. Language Scope (<lang>/)",
    "detect_active_language() resolves built-in\npython, java, php, go, ts, or js packs.",
    style=Styles.Neutral.patch(shape_r=1.8),
    icon=phosphor.code,
)
cascade_cards.add(
    "3. Universal Fallback (common/)",
    "Falls back to language-agnostic common/ rules\nand 12 universal composite actions.",
    style=Styles.SecondaryNeutral.patch(shape_r=1.8),
    badge_style=Styles.SecondaryBold,
    icon=phosphor.globe,
)
cascade_cards.draw(xy=(85.0, 3.0), width=74.0, height=76.0)
save()
```

### Self-Healing Cache & Target-Scoped Workspace Artifacts

Rather than modifying the host project's root `.gitignore`, `src/pni/_cache.py` (`ensure_cache_dir()` and `ensure_cache_parent()`) makes `.pni/cache/` **self-healing**:

- **Automatic Git & Backup Exclusion**: Every write into `.pni/cache/` automatically guarantees the existence of `.pni/cache/.gitignore` (`*`) and a standard `CACHEDIR.TAG` signature (`8a477f597d28d172789f06886806bc55`), keeping SQLite databases, Trivy vulnerability DB caches (`trivy-cache/`), JUnit XML reports, and container logs out of Git status and backup archives even in uninitialized repositories.
- **Workflow-Isolated Ephemeral State (`.pni/cache/<workflow_id>/`)**: Each workflow writes its aggregated snapshot to `facts.json`, grounded 3-aspect architecture model to `architecture.json`, pre-sorted report specification to `blueprint.json` (or `migration_facts.json` and `migration_blueprint.json`), and raw stage artifacts into `runtime/`, `security/`, and `pentest/`.
- **Path-Guarded Multi-Target Harnesses (`.pni/dockerfiles/` & `.pni/pentests/`)**: `normalize_target_subpath()` rejects absolute paths and `..` traversal while mapping monorepo targets cleanly—for example, `targets.root: examples/php/legacy_shop_messy` maps to `.pni/dockerfiles/examples/php/legacy_shop_messy/Dockerfile` and `.pni/pentests/examples/php/legacy_shop_messy/`.

### Three-Tier Cascade & 6-Language Resolution Rules

Teams can keep all seeded `.pni/` files or delete unmodified files and retain only targeted overrides:

1. **Active Language Detection (`_rules/manager.py`)**: `detect_active_language(project_root)` inspects manifests in strict priority order—Python (`pyproject.toml`, `setup.py`, `requirements.txt`), Java (`pom.xml`, `build.gradle*`, `settings.gradle*`), PHP (`composer.json`, `wp-config*.php`, `artisan`, `phpunit.xml*`), Go (`go.mod`, `go.work`), and Node/Frontend (`tsconfig*.json`, `jsconfig.json`, `package.json` distinguishing `typescript` vs. `javascript`)—before falling back to source-tree file heuristics (`*.java`, `*.php`, `*.go`, `*.ts`/`*.tsx`, `*.js`/`*.jsx`) and defaulting to `"python"`. See [Supported 6 Languages](../05_languages_and_reference/supported_languages.md) for language-specific analyzer details.
2. **Engineering Rules (`local > <lang> > common`)**: `list_rules()` merges `(scope, name)` candidates across built-in `src/pni/_rules/` and local `.pni/rules/` for `("common", active_lang)` (or all `SUPPORTED_LANGUAGES` with `--all`), preferring `.pni/rules/<scope>/<name>.md` (`is_local=True`). `get_rule_content()` resolves identifiers across hyphen/underscore normalization in four steps: exact `<scope>/<name>` -> `<active_lang>/<name>` -> `common/<name>` -> any matching rule name.
3. **Composite Actions (`local > <lang> > common`)**: `load_composite_action()` resolves `.pni/actions/<id>.yaml` (or scoped `.pni/actions/<scope>/<id>.yaml`) first, then built-in `<active_lang>/<id>.yaml` (enabling `uses: repo_structure_audit` to dispatch automatically to `python/`, `java/`, `php/`, `go/`, `typescript/`, or `javascript/`), and finally `common/<id>.yaml`. See [15 Actions & 12 Primitives](../03_workflows_and_actions/actions_pipeline.md) for the full catalog.
4. **Container Harnesses, Manifests & Instructions**: `resolve_template_dockerfile()` prioritizes `.pni/dockerfiles/_templates/<lang>/<tool>.dockerfile` over built-in `src/pni/_dockerfiles/<lang>/<tool>.dockerfile` (with per-language fallback to `pip`, `maven`, `composer`, `go`, or `node`), while `load_pni_config()` loads `.pni/pni.toml` and `get_instructions_info()` prioritizes `.pni/instructions.md` over `src/pni/_instructions/agent.md`.

```bash
# Inspect active rules, composite actions, and cascade override status
pni rules list --all
pni rules show common/architecture
pni workflows show full_audit
```
