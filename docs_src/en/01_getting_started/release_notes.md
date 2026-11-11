# Release Notes

Complete release history, key architectural additions, and feature highlights for **Project Nemesis Index (`pni501`)**.

---

## Version 0.1.4

*Release Date: 2026/11/10*

Version `0.1.4` introduces official PNI501 brand assets and cover helper utilities for Drawlib PDF reports, the `pni cache clean` CLI subcommand for local and container artifact pruning, and deep static and runtime analysis improvements for **Go**, **TypeScript**, and **JavaScript** (including monorepo lockfile scoping, `.d.ts` companion declarations, IIFE/ES2022 `#private` classes, and Playwright headless Chromium auto-provisioning).

### 1. Official Brand Assets & Report Compiler Enhancements (`pni._reporter`)

- **Bundled Brand Assets & `draw_pni_logo()` Cover Helper**:
  - `pni report init` now copies official brand assets (`logo.png`, `logo_dark.png`, and `favicon.png`) into `<src_dir>/<target>_src/_assets/` across Audit, Migration, and Progress blueprints.
  - Scaffolded `utils.py` modules now include `draw_pni_logo(xy=(135.0, 48.0), width=9.0, *, dark=True)` for rendering the official PNI501 emblem on `00_cover.md` dark and light covers without boilerplate coordinate math.
- **Drawlib Linter Check for `ClassDiagram` / `ClassNode`**:
  - `lint_drawlib_chapters()` (`pni report check` and `pni report build`) now detects and warns when `ClassDiagram` or `ClassNode` uses `Styles.White` (which renders invisible white text on a white background) and recommends `Styles.Neutral`.
- **Multi-Portal Relative Link Verification (`--link-check-root`)**:
  - Added `--link-check-root <dir>` (`link_check_root`) to `pni report build` / `compile_report_project()` so reports nested inside multi-target HTML portals can validate parent-relative links (`../index.html`) against the portal root directory.

### 2. CLI Additions (`pni cache clean` & `--version`)

- **`pni cache clean` Subcommand**:
  - Added `pni cache clean [--docker] [--container-engine auto|docker|podman]` to clean local `.pni/cache/` directories and optionally prune temporary `pni-harness-*`, `pni-proj-*`, `pni-sec-*`, and `pni-pentest-*` container images, dangling layers, and builder caches.
  ```bash
  uv run pni cache clean --docker
  ```
- **Root `--version` / `-V` Flag**:
  - Added `pni --version` (`-V`) alongside `pni version` to display `pni501 v0.1.4` and exit immediately.
- **Automatic Workflow Superseding**:
  - `start_workflow_run()` now defaults to `supersede=True`, automatically marking older unfinished runs of the same workflow as `CANCELLED` (`superseded_by_<run_id>`) when starting a fresh run.

### 3. TypeScript & JavaScript Analysis & Runtime Harness Enhancements

- **AST Analysis Refinements (`ast_analyze/ts_js/`)**:
  - **Barrel Re-Export Cycle Separation**: Distinguishes intentional `index.ts` barrel re-export loops (`type_checking_cycles`) from true implementation `circular_dependencies`.
  - **IIFE / UMD Unwrapping & ES2022 `#private` Classes**: Unwraps top-level IIFE/UMD factory closures (`var lib = (() => { ... })()`) and inspects `private_field_definition` / `#private` methods for accurate symbol and doc-coverage metrics.
  - **Companion `.d.ts` Type Declarations**: Automatically detects companion `.d.ts` files (`package.json` `"types"`/`"typings"` or co-located `*.d.ts`) as `has_type_marker = True` for JavaScript packages and credits exported `.d.ts` type signatures.
  - **Type-Level & Helper Test Recognition**: Credits `expectTypeOf<T>()`, `assertType<T>()`, `// @ts-expect-error`, suffix-less test files under `test/`/`tests/` (while filtering out non-test helpers), custom `assert*`/`verify*`/`check*` helpers, and external CDN script dependencies in `web-test-runner.config.*`.
- **Playwright Browser Harness & Coverage Parsers (`runtime_check/`)**:
  - Updated `typescript/node.dockerfile` and `javascript/node.dockerfile` to pre-install `@vitest/coverage-v8` and automatically provision **Playwright Headless Chromium** (`PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`) and OS shared libraries whenever `@playwright/test`, `playwright`, or `@vitest/browser` is detected.
  - Added `lcov.info` (`parse_lcov_info`), `@web/test-runner` (WTR), and Mocha (`parse_node_test_output`) output parsers, multi-suite Vitest coverage merging (`--coverage.clean=false`), and monorepo subpackage `tsc --noEmit -p <subpkg>/tsconfig.json` scoping.
- **Monorepo Lockfile & Container Vulnerability Scoping (`security_scan/`)**:
  - `discover_non_core_packages()` now parses workspace importers across `pnpm-lock.yaml`, `package-lock.json`, and `yarn.lock` (isolating workspace/docs packages for zero-dependency targets) and classifies global container toolchain paths (`/usr/local/lib/node_modules`, etc.) as `harness_os` / `os_package`.

### 4. Go AST Refinements & Non-Root Container Harness (`go`)

- **Go AST Refinements (`ast_analyze/go/`)**:
  - Detects partially ignored error returns (`val, _ := ...`) in `check_exception_hygiene()`.
  - Exempts multiline raw backtick strings (SQL/HTML/templates) from function LOC bloat in `check_complexity()`.
  - Exempts `fmt.Printf`-style variadic `...any` / `...interface{}` parameters when accompanied by a `format string` parameter in `check_type_safety()`.
  - Credits `t.Run` method-value delegation and helper function assertions in `check_test_quality()`.
- **Hardened Go Container Template (`go/go.dockerfile`)**:
  - Enforces a Go `1.22` Bookworm image floor (`1.22`–`1.24`), runs tests as non-root `USER pni` (`UID 10001`), and pre-warms `/go/cache` during image build for reliable `--network=none` offline test execution.
  - Default `.pni/pni.toml` now includes `"go.sum"` in `include_gitignored` and excludes `"docs/**"` and `"docs_src/**"`.

---

## Version 0.1.3

*Release Date: 2026/11/10*

Version `0.1.3` expands **pni501** from 3 to **6 first-class target languages** by introducing complete Tree-sitter AST analyzers, engineering rule cascades, offline Docker harnesses, test/coverage parsers, and migration analyzers for **Go (`go`)**, **TypeScript (`typescript`)**, and **JavaScript (`javascript`)**, alongside major enhancements for **Java** and **PHP**.

### 1. Go, TypeScript, and JavaScript Support (`6` Supported Languages)

- **Tree-Sitter AST Analyzers (`27` New Checkers)**:
  - Implemented `9` deterministic AST checkers each for `go`, `typescript`, and `javascript` (`complexity`, `type_safety`, `doc_coverage`, `architecture`, `code_hygiene`, `exception_hygiene`, `test_quality`, `security_patterns`, and `resource_safety`).
- **Built-in Language Rule Cascades (`15` New Rule Files)**:
  - Added `coding_convention.md`, `architecture_design.md`, `test_strategy.md`, `security_policy.md`, and `audit_rubric.md` under `rules/go/`, `rules/typescript/`, and `rules/javascript/`.
- **Composite Actions, Workflows & Offline Container Templates**:
  - Added `go.audit_analyze`, `typescript.audit_analyze`, and `javascript.audit_analyze` composite actions, `full_audit` and `quick_check` workflows, and hermetic Docker templates (`go/go.dockerfile`, `typescript/node.dockerfile`, `javascript/node.dockerfile`) with `go-cover` and `istanbul-summary` coverage parsers.
- **Migration Analyzers**:
  - Added external dependency touchpoint scanners, public API contract extractors, and AST codemod candidate detectors for Go, TypeScript, and JavaScript.

### 2. Java & PHP Analyzer Enhancements

- **Java (`java`)**:
  - Recognizes JUnit 4 `@Test(expected=...)`, AssertJ, Hamcrest, and Spring `MockMvc` assertions; excludes Javadoc comments from method LOC; supports custom Maven build arguments; and filters `test`, `provided`, and `optional` scopes in `pom.xml`.
- **PHP (`php`)**:
  - Formats anonymous class symbols cleanly, distinguishes PSR-3 logger calls from raw `error_log()` debug statements, and auto-detects target source directories from `composer.json` PSR-4 mappings.

---

## Version 0.1.2

*Release Date: 2026/11/08*

Version `0.1.2` introduces granular **4-tier vulnerability scope classification** in `security_scan`, Python AST analyzer refinements, and workflow state management commands (`rewind` and `cancel`).

### 1. 4-Tier Vulnerability Scope Classification (`security_scan`)

- **`dep_scopes.py` Dependency Scope Classifier**:
  - Automatically classifies Trivy and OSV findings into four scopes to eliminate false-positive scoring penalties from dev/docs dependencies or container base images:
    1. `runtime_core`: Production application dependencies (full scoring impact).
    2. `dev_or_optional`: Test/linter/docs dependencies and optional extras.
    3. `os_package`: Debian/Alpine OS packages inside the application container.
    4. `harness_os`: Audit container harness packages (`pni-sec-*` / `pni-harness-*`).

### 2. Workflow Rewind & Cancellation CLI & Python AST Refinements

- **Workflow State Recovery (`pni workflows rewind` & `cancel`)**:
  - Added `pni workflows rewind <action_id>` (alias `retry-action`) to roll back a workflow run to any action and clear downstream artifacts, and `pni workflows cancel` (`--superseded` / `--supersede`) to clean up stale runs.
- **Python AST Refinements**:
  - Improved `TYPE_CHECKING` conditional import handling, `@overload` / `@abstractmethod` stub filtering, and docstring coverage calculation in `ast_analyze/python/`.

---

## Version 0.1.1

*Release Date: 2026/11/06*

- **PyPI Packaging & Metadata Refinements**:
  - Refined package classifiers, entry points (`pni` CLI), bundled rule/workflow package data, and release verification workflows.

---

## Version 0.1.0

*Release Date: 2026/11/06*

Initial public release of **Project Nemesis Index (`pni501`)** — an AI-orchestrated software engineering audit, security verification, migration planning, and visual reporting framework.

- **Core Architecture**:
  - Stateful **Pull-Push SQLite Workflow Engine** (`.pni/state.db`) with deterministic action execution and LLM judgment gates.
  - **3-Layer Cascading Rule System** (`common/` → `<language>/` → `.pni/rules/`) and **2-Tier Config Loader** (`.pni/pni.toml`).
  - Deterministic analyzers (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`) for **Python**, **Java**, and **PHP**.
  - **7-Axis `ScoreResult`** (100-point weighted rubric with `S`/`A`/`B`/`C`/`D` grades) and **`MigrationPlanResult`**.
  - **Drawlib Visual PDF Reporting** (`pni report init`, `pni report check`, `pni report build`) producing 7-chapter 16:9 vector PDF and HTML slide decks.
