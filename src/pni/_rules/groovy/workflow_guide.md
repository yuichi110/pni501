# Groovy Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Groovy (`*.groovy`, Gradle, Spock, Jenkins Shared Libraries) repositories.

---

## 1. Mapping `targets` by Groovy Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Gradle / Maven Groovy App** | `src/main/groovy`, `src/test/groovy`, `build.gradle` | `source: ["src/main/groovy"]`<br>`tests: ["src/test/groovy"]`<br>`docs: ["README.md"]` |
| **Jenkins Shared Library** | `vars/*.groovy`, `src/**/*.groovy`, `test/` | `source: ["vars", "src"]`<br>`tests: ["test", "tests"]` |
| **Polyglot JVM Monorepo (Java/Kotlin + Groovy)** | `services/`, `build-logic/` | Create per-component `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Groovy Actions & Rules

1. **Core Built-in Groovy Actions**:
   - `repo_structure_audit` (`groovy` scope): Auto-runs `project_inspect` for `build.gradle`/`pom.xml`, Groovy 4 vs legacy 2/3 versions, `@Grab` pinning, and supply-chain hygiene.
   - `groovy_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="groovy"`) to extract Groovydoc coverage, `@CompileStatic`/`def` typing, `Eval.me`/`GroovyShell`/shell-exec/XXE CWE sinks, complexity, and Grails/Micronaut endpoints.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records entry points, `vars/` pipeline steps, service layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `groovy_test_audit` (`needs: [ast_and_quality]`): Evaluates Spock `*Spec.groovy` / JUnit suites and coverage against `groovy/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Groovy harness image via `.pni/dockerfiles/groovy/`, runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against dependencies/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Groovy

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Groovy)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Groovy AST analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src/main/groovy"
    - "src"
    - "vars"
  tests:
    - "src/test/groovy"
    - "test"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: groovy_ast_audit
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

  - id: test_health
    uses: groovy_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
