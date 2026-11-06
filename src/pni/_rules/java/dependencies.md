# Dependency & Build Management Standards (Java)

## Core Principles
1. **Standard Build Manifest**: Declare project coordinates, Java toolchain target, and dependencies cleanly in `pom.xml` (Maven) or `build.gradle.kts` / `build.gradle` (Gradle).
2. **Reproducible Wrapper & Version Pinning**: Commit build wrappers (`mvnw` / `gradlew`) and pin exact dependency versions (via Maven `<dependencyManagement>` BOMs, Gradle `libs.versions.toml` / `platform(...)`, or `gradle.lockfile`). Avoid dynamic `+` or `LATEST` versions.
3. **Strict Scope Separation**: Isolate test-only frameworks (`junit-jupiter`, `mockito`, `assertj`) under `<scope>test</scope>` or `testImplementation`.
4. **Vulnerability & Shade Hygiene**: Audit transitive dependencies regularly and avoid conflicting fat-jar classpath shadowing.
