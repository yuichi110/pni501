# Dependency & Gradle/Maven Management Standards (Groovy)

## Core Principles
1. **Supported Groovy 4+ & LTS JDK**: Target Groovy `4.x` (`org.apache.groovy:groovy`, note the Maven groupId changed from `org.codehaus.groovy` in 4.0) on an active LTS JDK (`17`/`21`; `ProjectFacts.language_version_constraint`).
2. **Wrapper, Locking & Explicit `@Grab` Pinning**: Commit `gradlew`/`mvnw` wrappers and `gradle.lockfile` for services (`ProjectFacts.lockfiles_found`). In standalone scripts using Grape `@Grab`, always pin explicit versions (never `@Grab('foo:bar:+')`; `ProjectFacts.unpinned_dependencies`).
3. **Clean Test Scope Separation**: Place Spock (`spock-core`), CodeNarc, and JUnit strictly under `testImplementation` / `test` scope.
4. **Vulnerability Auditing**: Audit JVM/Groovy dependencies (and avoid Groovy 2.x/3.x EOL CVEs) with Trivy / OWASP Dependency-Check.

## Evaluation Thresholds
- **`PASS`**: Groovy `4.x` (or maintained `3.x`) on LTS JDK, zero dynamic `+`/`SNAPSHOT` versions (`unpinned_dependencies == 0`), and clean test scoping.
- **`WARN`**: Legacy `org.codehaus.groovy` `3.x` without 4.x upgrade plan or missing `gradle.lockfile`.
- **`FAIL`**: EOL Groovy `2.x` with unpatched CVEs, dynamic `+` release versions, or unpinned `@Grab` script downloads.
