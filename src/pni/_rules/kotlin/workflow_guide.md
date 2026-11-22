# Kotlin Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Kotlin (Gradle Kotlin DSL / Maven) repositories.

---

## 1. Mapping `targets` by Kotlin Project Layout

Inspect `build.gradle.kts`, `settings.gradle.kts`, and `pom.xml` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard JVM Gradle / Maven** | `src/main/kotlin`, `src/test/kotlin`, `README.md` | `source: ["src/main/kotlin"]`<br>`tests: ["src/test/kotlin"]`<br>`docs: ["README.md"]` |
| **Kotlin Multiplatform (KMP)** | `src/commonMain/kotlin`, `src/jvmMain/kotlin`, `src/commonTest/kotlin` | `source: ["src/commonMain/kotlin", "src/jvmMain/kotlin"]`<br>`tests: ["src/commonTest/kotlin", "src/jvmTest/kotlin"]` |
| **Multi-Module / Polyglot Monorepo** | `core/src/main/kotlin`, `api/src/main/kotlin`, `web/` | Create per-module `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Kotlin Actions & Rules

1. **Core Built-in Kotlin Actions**:
   - `repo_structure_audit` (`kotlin` scope): Auto-runs `project_inspect` for `build.gradle.kts`, `pom.xml`, `gradle.lockfile`, JDK/Kotlin versions, dependency pinning, and supply-chain hygiene.
   - `kotlin_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="kotlin"`) to extract wildcard imports, KDoc coverage, `!!`/nullable/cast issues, `GlobalScope`/coroutine pitfalls, mutable `object` globals, CWE sinks, and Ktor/Spring routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (`Application.kt`, Ktor routing, Spring controllers), package layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `kotlin_test_audit` (`needs: [ast_and_quality]`): Evaluates JUnit 5 / Kotest / `kotlinx-coroutines-test` suites and coverage against `kotlin/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Gradle/Maven Kotlin harness image via `.pni/dockerfiles/kotlin/`, runs tests + coverage offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against dependencies/container images and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Kotlin

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Kotlin)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Kotlin AST/Gradle analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src/main/kotlin"
    - "src"
  tests:
    - "src/test/kotlin"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: kotlin_ast_audit
    needs: [repo_and_deps]

  - id: runtime_verification
    uses: container_runtime_audit
    needs: [repo_and_deps]
    when: "has_runtime_harness"

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  # Optional archetype audit: service_readiness_audit | cli_guidelines_audit | library_hygiene_audit
  - id: test_health
    uses: kotlin_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
