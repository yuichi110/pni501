# Dependency & .NET/Paket Management Standards (F#)

## Core Principles
1. **Supported .NET LTS & SDK-Style `.fsproj`**: Target an actively supported .NET TFM (`net8.0`/`net9.0`/`net10.0`; `ProjectFacts.language_version_constraint`) with pinned SDK version in `global.json`.
2. **Deterministic Locking (NuGet or Paket)**: Use `Directory.Packages.props` + `packages.lock.json` OR `paket.dependencies` + `paket.lock` for reproducible restores (`ProjectFacts.lockfiles_found`).
3. **Pinned Versions & Clean Packaging**: Avoid floating `*` package versions (`ProjectFacts.unpinned_dependencies`), isolate `FSharp.Core` alignment cleanly for NuGet libraries, and keep analyzers/test frameworks out of runtime dependencies.
4. **Vulnerability Auditing**: Regularly audit NuGet packages with `dotnet list package --vulnerable --include-transitive` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Supported `.NET 8+` TFM, zero floating package versions (`unpinned_dependencies == 0`), and reproducible lockfile / `global.json` setup.
- **`WARN`**: Missing `packages.lock.json`/`paket.lock` or minor `FSharp.Core` version drift.
- **`FAIL`**: EOL `.NET Core 3.1` / `.NET 5/6/7` without migration plan, floating versions, or unpatched vulnerable NuGet dependencies.
