# Dependency & NuGet Management Standards (C#)

## Core Principles
1. **Modern SDK-Style Projects & Supported .NET TFM**: Use SDK-style `.csproj` targeting an actively supported .NET LTS/STS (`net8.0`, `net9.0`, or `net10.0`; `ProjectFacts.language_version_constraint`), and pin the SDK major/minor via `global.json`.
2. **Central Package Management & Lockfiles**: For multi-project solutions, centralize versions in `Directory.Packages.props` (`ManagePackageVersionsCentrally=true`) and enable deterministic NuGet restore via `<RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>` (`packages.lock.json`; `ProjectFacts.lockfiles_found`).
3. **Pinned Versions & Private Assets**: Pin explicit NuGet `Version` ranges (avoid floating `*` versions; `ProjectFacts.unpinned_dependencies`), and mark build-only analyzers/test packages with `PrivateAssets="all"`.
4. **Vulnerability Auditing**: Regularly audit packages with `dotnet list package --vulnerable --include-transitive` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Supported `.NET 8+` TFM, explicit NuGet versions (`unpinned_dependencies == 0`), SDK-style `.csproj`, and reproducible restore configuration.
- **`WARN`**: Missing `packages.lock.json` or `Directory.Packages.props` in multi-project solutions, or minor analyzer packaging gaps.
- **`FAIL`**: EOL `.NET Core 3.1` / `.NET 5/6/7` or `.NET Framework 4.x` without migration plan, floating wildcard package versions, or vulnerable transitive NuGet packages.
