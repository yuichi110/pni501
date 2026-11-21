# Dependency & Build Management Standards (Java)

## Core Principles
1. **Standard Build Manifest**: Declare project coordinates, supported LTS Java toolchain target (`17` / `21` LTS), and dependencies cleanly in `pom.xml` (Maven) or `build.gradle.kts` / `build.gradle` (Gradle) with zero `AstFacts.language_version_mismatches`.
2. **Reproducible Wrapper & Version Pinning**: Commit build wrappers (`mvnw` / `gradlew`, `ProjectFacts.lockfiles_found`) and pin exact dependency versions (via Maven `<dependencyManagement>` BOMs, Gradle `libs.versions.toml` / `platform(...)`, or `gradle.lockfile`). Avoid dynamic `+`, `RELEASE`, or `LATEST` versions (`ProjectFacts.unpinned_dependencies`).
3. **Strict Scope Separation**: Isolate test-only frameworks (`junit-jupiter`, `mockito`, `assertj`) under `<scope>test</scope>` or `testImplementation`.
4. **Vulnerability & Shade Hygiene**: Audit transitive dependencies regularly and avoid conflicting fat-jar classpath shadowing.

## Evaluation Thresholds
- **`PASS`**: Clean Maven/Gradle manifest with supported LTS target, committed wrapper/lockfile, `unpinned_dependencies == 0`, and `language_version_mismatches == 0`.
- **`WARN`**: Missing build wrapper or legacy EOL Java 11 target without unresolved dynamic versions.
- **`FAIL`**: Unpinned `LATEST`/`RELEASE`/`+` coordinates, EOL Java 8 target in active services, or language/API version mismatches.
