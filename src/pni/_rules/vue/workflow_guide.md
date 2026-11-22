# Vue / Nuxt Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Vue (`*.vue`, `nuxt.config.ts`, `vue.config.js`) repositories.

---

## 1. Mapping `targets` by Vue / Nuxt Project Layout

Inspect `package.json`, `vite.config.ts`, and `nuxt.config.ts` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Vite + Vue 3 SPA** | `src/components/*.vue`, `src/composables/`, `tests/` | `source: ["src"]`<br>`tests: ["tests", "src"]`<br>`docs: ["README.md"]` |
| **Nuxt 3 Application** | `pages/`, `components/`, `composables/`, `server/` | `source: ["components", "pages", "composables", "server"]` (or `["app"]` for Nuxt 4 layout)<br>`tests: ["tests"]` |
| **Full-Stack Monorepo (e.g. Python/Go/PHP + Vue)** | `backend/`, `frontend/` | Create a `scope: component` workflow (`targets.root: "frontend"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Vue Actions & Rules

1. **Core Built-in Vue Actions**:
   - `repo_structure_audit` (`vue` scope): Auto-runs `project_inspect` for `package.json`, `nuxt.config.*`, lockfiles, Vue 3 vs EOL Vue 2 versions, dependency pinning, and supply-chain hygiene.
   - `vue_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="vue"`) to extract SFC script/template metrics, `v-html` XSS / `eval` CWE sinks, complexity, and composables.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records routes/pages, Pinia stores, API clients, component hierarchy, and data flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `vue_test_audit` (`needs: [ast_and_quality]`): Evaluates Vitest / `@vue/test-utils` suites, assertion quality, and coverage against `vue/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Node/Vue harness image via `.pni/dockerfiles/vue/node.dockerfile`, runs Vitest / `vue-tsc` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against lockfiles/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Vue

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Vue)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Vue SFC AST/package analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "components"
    - "pages"
  tests:
    - "tests"
    - "test"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: vue_ast_audit
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
    uses: vue_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
