# Dependency & Alire/GPRbuild Management Standards (Ada)

## Core Principles
1. **Modern Alire (`alire.toml`) & Clean `*.gpr` Project Files**: Manage Ada crates and compiler toolchains declaratively via `alire.toml` (`[[depends-on]]` with SemVer constraints) and clean GPRbuild `*.gpr` files targeting Ada 2012 or Ada 2022 (`-gnat2022` / `-gnat2012`; `ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
2. **Reproducible Locking (`alire.lock`)**: Commit `alire.lock` for deployed applications/firmware (`ProjectFacts.lockfiles_found`). Pure Alire libraries or standalone zero-dependency GPRbuild projects legitimately omit `alire.lock` and must **NOT** be penalized.
3. **Clean Build Profiles (`development` / `validation` / `release`)**: Enable assertions (`-gnata`) and validity checks (`-gnatVa`) in development/validation profiles and isolate test crates (`aunit`) from production runtime dependencies.
4. **External C Binding & Supply-Chain Hygiene**: Document C/system libraries linked via `Linker_Options` explicitly for CVE auditing (Trivy).

## Evaluation Thresholds
- **`PASS`**: Clean `alire.toml` / `*.gpr` targeting Ada 2012/2022, bounded crate versions (`unpinned_dependencies == 0`), and `-gnata` validation profile.
- **`WARN`**: Missing `alire.toml` on multi-dependency GPR projects or missing `-gnatwa` compiler warnings.
- **`FAIL`**: Unpinned external git branches, legacy Ada 83/95 workarounds without justification, or broken non-portable `.gpr` paths.
