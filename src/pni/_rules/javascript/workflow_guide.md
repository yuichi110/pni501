# JavaScript Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for JavaScript (`package.json`) repositories.

---

## 1. Mapping `targets` by JavaScript Project Layout

Inspect `package.json` and module directories to configure `targets` accurately. Note that PNI automatically separates production `.js`/`.jsx`/`.mjs`/`.cjs` files from co-located `*.test.js(x)` / `*.spec.js(x)` files:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard `src/` + `tests/`** | `src/**/*.js`, `tests/**/*.test.js` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Node Library (`lib/` + `test/`)** | `lib/**/*.js`, `test/**/*.js` | `source: ["lib"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **Co-located Tests in `src/`** | `src/**/*.js`, `src/**/*.test.js` | `source: ["src"]`<br>`tests: ["src"]`<br>`docs: ["README.md"]` |
| **Multi-Package / Full-Stack Monorepo** | `packages/*/src`, `frontend/`, `backend/` | Create per-package `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting JavaScript Actions & Rules

1. **Core Built-in JavaScript Actions**:
   - `repo_structure_audit` (`javascript` scope): Auto-runs `project_inspect` for `package.json`, `jsconfig.json`, lockfiles (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`), Node engine constraints, and dependency pinning.
   - `javascript_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` to extract ES import/require hygiene, JSDoc `@param`/`@returns` type contract coverage, cognitive complexity, loose equality (`==`), unhandled promises/empty catches, DOM/XSS/SQL/exec CWE sinks, and API routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (Express/Fastify/Hono routes, React components, CLI bins), module layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `javascript_test_audit` (`needs: [ast_and_quality]`): Evaluates Vitest/Jest/Mocha/Node test files (`*.test.js`, `*.spec.js`), assertion-free `it()`/`test()` blocks, and test coverage alignment.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Node harness image via `.pni/dockerfiles/.../Dockerfile`, runs Vitest/Jest/`npm test` + ESLint offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `package.json`/lockfiles and the resolved container image, evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints`.

---

## 3. Recommended `full_audit.yaml` DAG Template for JavaScript

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (JavaScript)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic JavaScript AST/package.json analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
  tests:
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: javascript_ast_audit
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
    uses: javascript_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
