# Generic Multi-Language Dependency & Build Hygiene Standards

## Evaluation Criteria (`ProjectFacts` & `AstFacts`)
- **Reproducible Builds**: Commit the ecosystem lockfile (`Cargo.lock`, `Gemfile.lock`, `pubspec.lock`, `mix.lock`, `Package.resolved`, `packages.lock.json`, `renv.lock`, `flake.lock`, etc.) for applications and deployed services.
- **Acyclic Architecture**: Maintain zero circular internal module dependencies (`circular_dependencies == 0`).
- **Import Hygiene**: Avoid wildcard imports (`wildcard_imports == 0`) and keep external dependencies pinned to maintained, non-EOL releases.
- **Supply Chain**: Verify transitive dependencies against known CVEs (`security_scan`) and avoid vendored unpatched binaries.
