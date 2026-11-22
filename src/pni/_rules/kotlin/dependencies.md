# Dependency & Build Management Standards (Kotlin)

## Core Principles
1. **Gradle Kotlin DSL / Maven & Supported Toolchains**: Use Gradle Kotlin DSL (`build.gradle.kts`, `settings.gradle.kts`) with a Gradle Version Catalog (`gradle/libs.versions.toml`) and pinned JDK toolchain (`jvmToolchain(21)`) + Kotlin `2.0+` / `1.9+` (`ProjectFacts.language_version_constraint`).
2. **Wrapper & Reproducible Locking**: Commit the Gradle/Maven wrapper (`gradlew` / `mvnw`) and enable dependency locking (`gradle.lockfile`) or checksum verification (`verification-metadata.xml`) for production services (`ProjectFacts.lockfiles_found`).
3. **Pinned Versions & Scope Hygiene**: Avoid dynamic `+` or `SNAPSHOT` release versions (`ProjectFacts.unpinned_dependencies`), and separate `implementation` vs `api` vs `testImplementation` cleanly.
4. **Vulnerability Auditing**: Audit JVM/Kotlin dependencies with OWASP Dependency-Check / Trivy.

## Evaluation Thresholds
- **`PASS`**: Kotlin `>= 1.9` (2.0+ preferred) on supported LTS JDK, zero dynamic `+`/`SNAPSHOT` dependencies (`unpinned_dependencies == 0`), wrapper committed, and clean Gradle/Maven scopes.
- **`WARN`**: Missing version catalog or `gradle.lockfile` on service builds.
- **`FAIL`**: EOL Kotlin (`< 1.8`) or JDK 8/11 without migration plan, dynamic/floating release dependencies, or unpinned transitive vulnerabilities.
