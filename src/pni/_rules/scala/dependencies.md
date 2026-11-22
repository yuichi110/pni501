# Dependency & sbt Build Management Standards (Scala)

## Core Principles
1. **Supported Scala & JVM Toolchains**: Target Scala `3.3+` LTS (or `2.13.x` with cross-build readiness) on an active LTS JDK (`17` / `21`), pinning `sbt.version` in `project/build.properties` (`ProjectFacts.language_version_constraint`).
2. **Binary Compatibility (`%%`) & Pinned Versions**: Use `%%` for Scala-versioned artifacts, pin exact dependency versions (avoid `latest.integration` or `SNAPSHOT`; `ProjectFacts.unpinned_dependencies`), and separate `% Test` / `% Provided` scopes cleanly.
3. **Reproducible Builds & Dependency Hygiene**: Audit unused/undeclared dependencies via `sbt-explicit-dependencies` and watch for Scala 2.13/3 binary-compat conflicts.
4. **Vulnerability Auditing**: Scan resolved Ivy/Coursier JAR dependencies with Trivy / OWASP Dependency-Check.

## Evaluation Thresholds
- **`PASS`**: Scala `3.3+` or `2.13+` with pinned `sbt.version`, zero `SNAPSHOT`/floating versions (`unpinned_dependencies == 0`), and clean `% Test` scope separation.
- **`WARN`**: Missing `project/build.properties` pin or Scala 2.13 project lacking Scala 3 migration flags (`-Xsource:3`).
- **`FAIL`**: EOL Scala `2.11`/`2.12` (outside legacy Spark constraints) without migration plan, floating release versions, or vulnerable transitive JARs.
