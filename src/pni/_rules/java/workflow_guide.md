# Java Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Java (Maven / Gradle) repositories.

---

## 1. Mapping `targets` by Java Build Layout

Inspect `pom.xml`, `build.gradle(.kts)`, and `settings.gradle(.kts)` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Single-Module Maven / Gradle** | `src/main/java`, `src/test/java`, `README.md` | `source: ["src/main/java"]`<br>`tests: ["src/test/java"]`<br>`docs: ["README.md"]` |
| **Multi-Module Maven / Gradle / Monorepo** | `core/src/main/java`, `api/src/main/java` | Either create per-module `scope: component` workflows (`core_audit.yaml` with `root: "core"`) + a `category: rollup` workflow, or list explicit module paths in `source` for a unified repo audit |
| **Generated Sources Present** | `target/generated-sources/`, `build/generated/` | Always target `src/main/java` explicitly so MapStruct/Protobuf/OpenAPI generated code under `target/` or `build/` is excluded |

---

## 2. Selecting Java Actions & Rules

1. **Core Built-in Java Actions**:
   - `repo_structure_audit` (`java` scope): Auto-runs `project_inspect` for Maven/Gradle manifests, wrapper/lockfiles (`mvnw`, `gradlew`, `gradle.lockfile`), Java version constraints, and dependency pinning.
   - `java_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` to evaluate import ordering/wildcards, raw generics & `@SuppressWarnings`, Javadoc coverage & `@param` consistency, cognitive complexity, mutable non-final static fields, package cycles, and Spring Boot best practices.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (`@SpringBootApplication`, `@RestController`, CLI `main`), package layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `java_test_audit` (`needs: [ast_and_quality]`): Evaluates JUnit 5 test structure, assertion-free test methods, and test coverage mapping.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Maven/Gradle harness image via `.pni/dockerfiles/.../Dockerfile`, runs Surefire/JUnit + JaCoCo offline (`--network=none`), probes Spring Boot / JAR startup & DI health, and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against project files and the resolved container image (using shared `.pni/cache/trivy-cache/`), evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints` against `common/security_vulnerability`.

2. **Spring Boot & Modernization Checks**:
   - When `spring-boot-starter-*` is present, check constructor injection vs `@Autowired` field injection, `@Transactional` visibility pitfalls, and `jakarta.*` vs legacy `javax.*` usage.
   - Recommend Java 21 LTS idioms (`record` DTOs, `sealed` hierarchies, pattern matching) when boilerplate POJOs or Java 8/11 targets are detected.

---

## 3. Recommended `full_audit.yaml` DAG Template for Java

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Java)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Java AST, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src/main/java"
  tests:
    - "src/test/java"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: java_ast_audit
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
    uses: java_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]
    with:
      target: "full_audit"

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
    with:
      target: "full_audit"
      lang: "en"
      style: "google"
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
