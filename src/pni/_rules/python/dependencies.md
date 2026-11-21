# Dependency Management Standards (Python)

## Core Principles
1. **PEP 621 Standard**: Define metadata, `requires-python`, and runtime dependencies clearly in `pyproject.toml` (`ProjectFacts.manifest_files`).
2. **Deterministic Locking (Archetype-Aware)**: Commit a deterministic lockfile (`uv.lock` or `poetry.lock`, `ProjectFacts.lockfiles_found`) for deployed applications, services, and CLIs; for reusable libraries (`"library"` in `runtime_types`), prefer SemVer-compatible lower bounds (`>=`) in `pyproject.toml` rather than strict `==` pins (`common/library_guidelines`).
3. **Separate Dev & Runtime Dependencies**: Place testing and linting tools in `[dependency-groups].dev` (or optional extras) and eliminate undeclared/unused runtime dependencies (`AstFacts.undeclared_dependencies`, `AstFacts.unused_dependencies`).
4. **Regular Auditing & Version Bounds**: Avoid unpinned wildcard specs (`ProjectFacts.unpinned_dependencies`) and audit regularly for outdated or vulnerable packages.

## Evaluation Thresholds
- **`PASS`**: PEP 621 `pyproject.toml`, `unpinned_dependencies == 0`, `undeclared_dependencies == 0`, and lockfile committed (for non-library apps/services).
- **`WARN`**: Minor unused dependencies or missing lockfile on an internal CLI tool.
- **`FAIL`**: Missing modern manifest (`setup.py`-only or unpinned `requirements.txt`), undeclared runtime imports, or wildcard/unpinned dependency specs.
