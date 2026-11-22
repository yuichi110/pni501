# Dependency & SwiftPM Management Standards (Swift)

## Core Principles
1. **Modern `Package.swift` & Swift Toolchain**: Pin a supported `// swift-tools-version: 5.10` or `6.0` header and explicit platform minimums in `Package.swift` (`ProjectFacts.language_version_constraint`).
2. **Lockfile Policy (`Package.resolved` — App vs. Library Distinction)**:
   - **Applications / Server Executables / CLI Tools**: Commit `Package.resolved` for deterministic builds (`ProjectFacts.lockfiles_found`).
   - **Pure SwiftPM Libraries**: Omitting `Package.resolved` is acceptable SwiftPM convention and must **NOT** be penalized.
3. **Pinned SemVer Tags**: Pin dependencies via `.package(url: ..., from: "x.y.z")` or exact versions rather than mutable `branch: "main"` references (`ProjectFacts.unpinned_dependencies`), and separate `.testTarget` dependencies cleanly.
4. **Supply-Chain Hygiene**: Prefer official HTTPS package registries / signed releases and audit third-party dependencies with Trivy.

## Evaluation Thresholds
- **`PASS`**: `swift-tools-version >= 5.10`, zero mutable branch dependencies (`unpinned_dependencies == 0`), and `Package.resolved` committed for executables/services (exempt for pure libraries).
- **`WARN`**: Minor target dependency tidiness gaps or missing `swift-tools-version` 6 migration settings.
- **`FAIL`**: EOL Swift `< 5.8`, mutable git branch dependencies in production builds, or missing `Package.resolved` in shipped applications.
