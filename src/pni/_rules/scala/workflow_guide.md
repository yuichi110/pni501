# Scala Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Scala (`build.sbt`) repositories.

---

## 1. Mapping `targets` by Scala Build Layout

Inspect `build.sbt` and `project/build.properties` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard sbt Project** | `src/main/scala`, `src/test/scala`, `README.md` | `source: ["src/main/scala"]`<br>`tests: ["src/test/scala"]`<br>`docs: ["README.md"]` |
| **Multi-Project sbt Build** | `modules/core/src/main/scala`, `modules/api/src/main/scala` | List explicit module source dirs or create per-module `scope: component` workflows + one `category: rollup` workflow |
| **Polyglot Monorepo (e.g. Scala + Python/TS)** | `services/stream/`, `web/` | Create a `scope: component` workflow (`targets.root: "services/stream"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Scala Actions & Rules

1. **Core Built-in Scala Actions**:
   - `repo_structure_audit` (`scala` scope): Auto-runs `project_inspect` for `build.sbt`, `project/build.properties`, Scala/JVM versions, dependency pinning, and supply-chain hygiene.
   - `scala_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="scala"`) to extract Scaladoc coverage, `null`/`var`/`Await.result`/`.get`/`asInstanceOf` idioms, mutable `object` state, complexity, CWE sinks, and Play/http4s/Tapir routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (`@main`, HTTP routes, streaming jobs), algebra/service layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `scala_test_audit` (`needs: [ast_and_quality]`): Evaluates ScalaTest/MUnit/ZIO Test suites, ScalaCheck properties, and coverage against `scala/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated sbt harness image via `.pni/dockerfiles/scala/sbt.dockerfile`, runs `sbt test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against dependencies/container images and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Scala

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Scala)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Scala AST/sbt analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src/main/scala"
    - "src"
  tests:
    - "src/test/scala"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: scala_ast_audit
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
    uses: scala_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
