# 2. Implemented Rules Catalog & Deterministic Fact Grounding

`pni501` currently ships **25 built-in Markdown rule files** (`21` evaluation standards and `4` agent/workflow orchestration guides) across `common/`, `python/`, and `java/`. Crucially, every evaluation rule is paired with deterministic static extractors in `ProjectFacts` (`project_inspect`) and `AstFacts` (`ast_analyze`) so AI evaluations are anchored in exact repository evidence rather than unverified LLM impressions.

```drawlib file=ra_common_rules_table.png caption="Implemented Universal Rules Catalog (common/* — 12 Files): Industry Standards & Deterministic Grounding Signals"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=98, dpi=150)

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.4),
    border_style=Styles.MutedThin,
    has_header=True,
)
tbl.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=8.6),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=8.6),
)

rows = [
    ["Rule ID", "Anchor Standard", "Archetype", "Deterministic Grounding Signals (Facts / AST)"],
    ["common/architecture", "Clean / Layered Arch", "All Projects", "circular_dependencies, internal_import_graph, StructureMap"],
    ["common/maintainability", "SIG / ISO 25010", "All Projects", "complex_functions (McCabe>7/Cog>15), params>6, global_state"],
    ["common/supply_chain", "OpenSSF Scorecard", "All Projects", "lockfiles_found, unpinned_deps, ci_supply_chain_issues, LICENSE"],
    ["common/security", "OWASP ASVS Baseline", "All Projects", "committed_secret_files, hardcoded_secrets, bug_risk_idioms"],
    ["common/git_workflow", "Conventional Repo", "All Projects", "has_gitignore, committed caches/artifacts, workspace layout"],
    ["common/documentation", "Std Readme & Diataxis", "All Projects", "readme_headings, readme_line_count, docs_inventory, docstrings"],
    ["common/twelve_factor", "12 / 15-Factor App", "Service / API", "scattered_env_access, runtime_types, statelessness"],
    ["common/production_readiness", "Google SRE PRR", "Service / API", "missing_io_timeouts, unstructured_logging, container_hygiene"],
    ["common/cli_guidelines", "clig.dev Guidelines", "CLI Tool", "entry_points, exit codes, --help/--json, stdout vs stderr"],
    ["common/library_guidelines", "Public SDK Hygiene", "Library / SDK", "__all__ exports, py.typed, import-time purity, SemVer bounds"],
    ["common/agent_instruction", "PNI Agent Protocol", "Meta Guide", "Top-level Pull-Push protocol & zero-hallucination rules"],
    ["common/workflow_guide", "PNI Authoring Spec", "Meta Guide", "Declarative workflow YAML & action composition guide"],
]
tbl.draw_flexible(
    xy=(4.0, 94.0),
    column_widths=[34.0, 28.0, 20.0, 56.0],
    row_heights=[7.2] + [6.8] * 12,
    data=rows,
)
save()
```

---

## 2.1 Quantitative Thresholds in Universal Standards (`common/*`)

Each universal audit rule translates external engineering specifications into concrete, auditable checkpoints:

- **SIG / ISO 25010 Maintainability (`common/maintainability`)**: Enforces four quantitative code-health invariants—**Unit Size** (`<= 50` LOC target), **Unit Complexity** (`McCabe <= 7`, `cognitive <= 15`), **Unit Interfacing** (`<= 6` parameters; group larger signatures into typed config/DTO objects), and **Module Coupling** (`0` import cycles and `0` mutable module-level globals).
- **OpenSSF Supply-Chain Hygiene (`common/supply_chain`)**: Verifies committed dependency lockfiles (`uv.lock`, `poetry.lock`, `gradle.lockfile`, Maven wrapper), explicit GitHub Actions `permissions:` blocks, SHA-pinned third-party CI actions, non-root pinned `Dockerfile` base images, `SECURITY.md`, `LICENSE`, and Dependabot/Renovate automation.
- **12-Factor & Google SRE Readiness (`common/twelve_factor`, `common/production_readiness`)**: Flags scattered `os.environ` / `System.getenv` reads outside dedicated settings modules, external HTTP/DB/subprocess calls missing explicit `timeout=` budgets, unstructured `print` / `System.out.println` logging in services, and missing health/graceful-shutdown hooks.
- **CLI & Library Archetypes (`common/cli_guidelines`, `common/library_guidelines`)**: Ensures CLIs separate machine-readable `stdout` from diagnostic `stderr` with non-zero exit codes, and ensures libraries expose explicit public facades (`__all__`), ship `py.typed` markers, avoid import-time side effects, and avoid calling `sys.exit()` inside library routines.

---

## 2.2 Implemented Language & Framework Rules (`python/*` & `java/*`)

Alongside `common/*`, `pni501` implements full static AST analyzer suites (`LanguageAnalyzerSuite` across **8 abstract checker modules**: `imports`, `typing`, `docs`, `quality`, `dependencies`, `testing`, `framework`, and `operational`) for **Python** (via Python `ast` + `ast-grep-py`) and **Java** (via `ast-grep-py`).

```drawlib file=ra_lang_rules_table.png caption="Implemented Python (7 Files) & Java (6 Files) Language and Framework Rules Catalog"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=98, dpi=150)

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=8.2),
    header_cell_style=Styles.SecondaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.MutedThin,
    has_header=True,
)
tbl.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=8.2),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=8.2),
)

rows = [
    ["Rule ID", "Scope", "Key Engineering Criteria", "AST / Manifest Analyzer Signals"],
    ["python/code_quality", "Py Core", "Google docstrings, Bugbear idioms", "docstring_coverage_pct, bug_risk_idioms"],
    ["python/typing", "Py Core", "100% public hints, scoped ignores", "type_safety_coverage_pct, weak_types"],
    ["python/dependencies", "Py Core", "PEP 621 pyproject + uv.lock hygiene", "unpinned_deps, unused/undeclared_deps"],
    ["python/modern_stack", "Py Core", "Py 3.11+, pathlib, X|Y, isort order", "import_hygiene_pct, unsorted_imports"],
    ["python/testing", "Py Core", "pytest mirror layout & parametrize", "module_test_coverage_pct, test_smells"],
    ["python/frameworks/fastapi", "Py FW", "lifespan, Depends() DI, async purity", "framework_issues (on_event, sync IO)"],
    ["python/workflow_guide", "Guide", "Python workflow preset & rule guide", "pni rules show python/workflow_guide"],
    ["java/code_quality", "Java Core", "Javadoc @param sync & Records", "docstring_coverage_pct, sig_mismatch"],
    ["java/typing", "Java Core", "Generics safety, zero raw/unchecked", "type_safety_coverage_pct, weak_types"],
    ["java/dependencies", "Java Core", "pom.xml/Gradle + wrapper/lockfiles", "build_system, unpinned_dependencies"],
    ["java/testing", "Java Core", "src/test/java mirror & JUnit 5 @Test", "module_test_coverage_pct, test_smells"],
    ["java/frameworks/spring_boot", "Java FW", "Constructor DI & @ConfigProperties", "framework_issues (field @Autowired)"],
    ["java/workflow_guide", "Guide", "Maven/Gradle/Spring workflow guide", "pni rules show java/workflow_guide"],
]
tbl.draw_flexible(
    xy=(4.0, 94.5),
    column_widths=[36.0, 15.0, 44.0, 43.0],
    row_heights=[7.0] + [6.4] * 13,
    data=rows,
)
save()
```
