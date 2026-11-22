# Package Collections, `vendor:` & Toolchain Standards (Odin)

## Core Principles
1. **Standard `core:` / `vendor:` Libraries & Explicit Compiler Release**: Document the target Odin release tag (e.g., `dev-2025-01+`) and collection flags (`-collection:shared=...`) cleanly in `ols.json`, `Makefile`, or build scripts (`ProjectFacts.language_version_constraint`).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: Odin intentionally ships batteries-included (`core:` + `vendor:`) without an external package registry or lockfile — do **NOT** penalize Odin repositories for lacking a package lockfile. Evaluate reproducibility via pinned git submodules / vendored third-party packages (`ProjectFacts.unpinned_dependencies`).
3. **Clean Package Boundaries**: Organize code into cohesive Odin packages (one directory per package, avoiding circular package imports; `AstFacts.circular_dependencies == 0`).
4. **Foreign C Library Hygiene**: Document system/static libraries referenced in `foreign import` blocks explicitly for reproducible builds and CVE auditing (Trivy).

## Evaluation Thresholds
- **`PASS`**: Documented Odin release & build script (`ols.json`/`Makefile`), acyclic package layout, and pinned vendored/C dependencies.
- **`WARN`**: Missing documented Odin release version or missing `-vet` check command.
- **`FAIL`**: Unpinned external C/Odin fetches or hardcoded developer machine paths in `foreign import` / build scripts.
