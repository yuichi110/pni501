# Bzlmod, `MODULE.bazel` & Toolchain Pinning Standards (Starlark / Bazel)

## Core Principles
1. **Bzlmod (`MODULE.bazel` + `MODULE.bazel.lock`) Over Legacy `WORKSPACE`**: Adopt Bzlmod (`MODULE.bazel` with exact `bazel_dep(name = ..., version = "...")`) and commit `MODULE.bazel.lock` + `.bazelversion` (`ProjectFacts.lockfiles_found`, `ProjectFacts.language_version_constraint`). Flag `WORKSPACE`-only builds on Bazel 7/8 as migration debt.
2. **Cryptographic Integrity Hashes & Pinned Toolchains**: Every `http_archive` / `http_file` / repository rule MUST pin an explicit `integrity = "sha256-..."` (or `sha256 = "..."`; `ProjectFacts.unpinned_dependencies`), and register hermetic toolchains (`register_toolchains`) instead of relying on host compilers.
3. **Separate `dev_dependency = True`**: Mark test, lint, and documentation-only Bzlmod dependencies (`rules_testing`, `stardoc`, `buildifier_prebuilt`) with `dev_dependency = True` so downstream consumers do not inherit them.
4. **Supply-Chain Hygiene**: Prefer Bazel Central Registry (`bcr.bazel.build`) verified modules and audit pinned archives with Trivy.

## Evaluation Thresholds
- **`PASS`**: `MODULE.bazel` + `MODULE.bazel.lock` + `.bazelversion`, `dev_dependency = True` scoping, and SHA-256 integrity on all external archives (`unpinned_dependencies == 0`).
- **`WARN`**: Legacy `WORKSPACE` with pinned SHA-256 hashes awaiting Bzlmod migration.
- **`FAIL`**: Unhashed `http_archive` / mutable git branches, missing `.bazelversion`, or non-hermetic host-toolchain leaks.
