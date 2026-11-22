# Dependency & Crate Management Standards (Rust)

## Core Principles
1. **Modern Cargo Manifest & Edition**: Declare a modern Rust edition (`edition = "2021"` or `"2024"`), explicit `rust-version` (MSRV), crate metadata, and workspace dependency inheritance (`[workspace.dependencies]`) cleanly in `Cargo.toml` (`ProjectFacts.language_version_constraint`).
2. **Lockfile Policy (Binary vs. Library Distinction — Avoid False Positives)**:
   - **Binaries / Services / Workspaces with `[[bin]]`**: Commit `Cargo.lock` for deterministic, reproducible builds (`ProjectFacts.lockfiles_found`).
   - **Pure Library Crates (`src/lib.rs` only, published to crates.io)**: Omitting `Cargo.lock` is standard Cargo convention and must **NOT** be penalized as a missing-lockfile defect.
3. **Minimal Feature Flags & Pinned SemVer**: Disable unused default features (`default-features = false`) on heavy crates (e.g., `tokio`, `reqwest`, `serde`), avoid wildcard `*` or unpinned git branch dependencies (`ProjectFacts.unpinned_dependencies`), and keep `[dev-dependencies]` strictly separated from runtime `[dependencies]`.
4. **Supply-Chain Auditing**: Audit crates with `cargo audit` / `cargo deny` (advisories, licenses, duplicate crates) and Trivy.

## Evaluation Thresholds
- **`PASS`**: `edition >= 2021`, `unpinned_dependencies == 0`, `Cargo.lock` committed for binary/service repos (exempt for pure library crates), and clean `[dependencies]` vs `[dev-dependencies]` split.
- **`WARN`**: Missing `rust-version` (MSRV) or minor unused features / Cargo manifest tidiness gaps.
- **`FAIL`**: Wildcard (`*`) or mutable git branch dependencies, missing `Cargo.lock` on production services/binaries, or EOL `edition = "2015"` without migration plan.
