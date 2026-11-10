# JavaScript Workflow Authoring Best Practices

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for JavaScript (`package.json`) repositories.

---

## 1. Mapping `targets` by JavaScript Project Layout

Inspect `package.json` and module directories to configure `targets` accurately. Note that PNI automatically separates production `.js`/`.jsx`/`.mjs`/`.cjs` files from co-located `*.test.js(x)` / `*.spec.js(x)` files:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard `src/` + `tests/`** | `src/**/*.js`, `tests/**/*.test.js` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Node Library (`lib/` + `test/`)** | `lib/**/*.js`, `test/**/*.js` | `source: ["lib"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **Co-located Tests in `src/`** | `src/**/*.js`, `src/**/*.test.js` | `source: ["src"]`<br>`tests: ["src"]`<br>`docs: ["README.md"]` |

---

## 2. Selecting JavaScript Actions & Rules

1. **Core Built-in JavaScript Actions**:
   - `repo_structure_audit` (`javascript` scope): Inspects `package.json`, `jsconfig.json`, lockfiles (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`), Node engine constraints, and dependency pinning.
   - `architecture_analysis`: Records system archetype, entry points (Express/Fastify/Hono routes, React components, CLI bins), module layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `javascript_ast_audit`: Parses `.js`/`.jsx`/`.mjs`/`.cjs` files once via `ast-grep-py` to extract ES import/require hygiene, JSDoc `@param`/`@returns` type contract coverage, cognitive complexity, loose equality (`==`), unhandled promises/empty catches, DOM/XSS/SQL/exec CWE sinks, and API routes.
   - `javascript_test_audit`: Evaluates Vitest/Jest/Mocha/Node test files (`*.test.js`, `*.spec.js`), assertion-free `it()`/`test()` blocks, and test coverage alignment.
   - `container_runtime_audit`: Builds an isolated Node harness image via `.pni/dockerfiles/.../Dockerfile`, runs Vitest/Jest/`npm test` + ESLint offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit`: Runs Trivy (`security_scan`) against `package.json`/lockfiles and the resolved container image, evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints`.

---

## 3. Recommended `full_audit.yaml` Template for JavaScript

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (JavaScript)
description: Deterministic JavaScript AST/package.json analysis, 3-aspect grounded architecture recording, AI rule interpretation, score emission, and drawlib report creation.

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

  - id: arch_recording
    uses: architecture_analysis

  - id: test_health
    uses: javascript_test_audit

  - id: runtime_verification
    uses: container_runtime_audit

  - id: security_audit
    uses: security_vulnerability_audit

  - id: output_score
    uses: emit_score

  - id: create_report
    uses: write_drawlib_report
```
