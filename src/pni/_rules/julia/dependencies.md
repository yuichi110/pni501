# Dependency & Pkg (`Project.toml`) Management Standards (Julia)

## Core Principles
1. **Complete `Project.toml` & `[compat]` Bounds**: Declare `name`, `uuid`, `version`, `[deps]`, and `[compat]` bounds (including `julia = "1.10"` / `"1.11"` LTS/stable) cleanly in `Project.toml` (`ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
2. **Lockfile Policy (`Manifest.toml` — App vs. General Registry Package)**:
   - **Applications / Pipelines / Reproducible Research Repos**: Commit `Manifest.toml` for exact environment reproducibility (`ProjectFacts.lockfiles_found`).
   - **Published Julia General Registry Packages**: Omitting `Manifest.toml` (relying on `[compat]` in `Project.toml`) is official Pkg convention and must **NOT** be penalized.
3. **Clean Test Dependencies**: Isolate test-only packages (`Test`, `Aqua`, `JET`, `Documenter`) in `[extras]` + `[targets] test` or `test/Project.toml`.
4. **Quality & Compatibility Auditing**: Verify no unbound/stale deps or ambiguities via `Aqua.test_all(MyPkg)` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Julia `>= 1.10` LTS, complete `[compat]` bounds (`unpinned_dependencies == 0`), `Manifest.toml` committed on apps (exempt on registry packages), and isolated test deps.
- **`WARN`**: Missing `[compat]` bounds on minor dependencies or missing `Aqua.jl` check.
- **`FAIL`**: EOL Julia `< 1.6`, missing `[compat]` entirely on registered packages, or unpinned mutable git dependencies in production apps.
