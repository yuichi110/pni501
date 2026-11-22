# Dependency & Zig Build Management Standards (Zig)

## Core Principles
1. **Declarative `build.zig` & `build.zig.zon`**: Pin the target Zig version (`minimum_zig_version`) and all external dependencies with cryptographic content hashes (`.hash = "..."`) inside `build.zig.zon` (`ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
2. **Zero-Lockfile Exemption**: Because `build.zig.zon` embeds immutable content hashes directly (and pure stdlib Zig projects have zero external deps), do **NOT** penalize Zig repositories for lacking a separate lockfile.
3. **Cross-Compilation & Release Modes**: Support `zig build test` cleanly in `build.zig` and distinguish `Debug` / `ReleaseSafe` / `ReleaseFast` build options intentionally (avoid shipping `ReleaseFast` without fuzz/safety verification on untrusted parsers).
4. **C-Dependency & SBOM Hygiene**: Track bundled C libraries linked via `addCSourceFiles` explicitly for CVE auditing (Trivy).

## Evaluation Thresholds
- **`PASS`**: Clean `build.zig` + hashed `build.zig.zon` dependencies (`unpinned_dependencies == 0`) and explicit `minimum_zig_version`.
- **`WARN`**: Missing `minimum_zig_version` or undocumented C system library requirements.
- **`FAIL`**: Unhashed / mutable external fetches or broken non-reproducible build scripts.
