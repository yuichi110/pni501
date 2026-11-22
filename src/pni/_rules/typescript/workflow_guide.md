# TypeScript Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for TypeScript (`package.json` + `tsconfig.json`) repositories.

---

## 1. Mapping `targets` by TypeScript Project Layout

Inspect `package.json` and `tsconfig.json` to configure `targets` accurately. Note that PNI automatically separates production `.ts`/`.tsx` files from co-located `*.test.ts(x)` / `*.spec.ts(x)` and `.d.ts` files:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard `src/` + `tests/`** | `src/**/*.ts`, `tests/**/*.test.ts` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Co-located Tests in `src/`** | `src/**/*.ts`, `src/**/*.test.ts` | `source: ["src"]`<br>`tests: ["src"]`<br>`docs: ["README.md"]` |
| **Next.js / App Router** | `src/app`, `src/components`, `src/lib` | `source: ["src"]` (or `["app", "components", "lib"]`)<br>`tests: ["tests", "src"]`<br>`docs: ["README.md"]` |
| **pnpm / Turborepo / Full-Stack Monorepo** | `packages/*/src`, `apps/*/src`, `backend/` | Create per-package `scope: component` workflows (`core_audit.yaml` with `root: "packages/core"`) + one `category: rollup` workflow (`includes:`), or list package paths in `source` and `tests` |

---

## 2. Selecting TypeScript Actions & Rules

1. **Core Built-in TypeScript Actions**:
   - `repo_structure_audit` (`typescript` scope): Auto-runs `project_inspect` for `package.json`, `tsconfig.json` (`strict` mode), lockfiles (`pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`), Node engine constraints, and dependency pinning.
   - `typescript_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` to extract ES import hygiene, parameter/return type coverage, `: any` / `as any` & `@ts-ignore` usage, TSDoc coverage, cognitive complexity, unhandled promises/empty catches, DOM/XSS/SQL/exec CWE sinks, and API routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (Express/Fastify/NestJS/Hono/Next.js routes, React components, CLI bins), module layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `typescript_test_audit` (`needs: [ast_and_quality]`): Evaluates Vitest/Jest test files (`*.test.ts`, `*.spec.ts`), assertion-free `it()`/`test()` blocks, and test coverage alignment.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Node harness image via `.pni/dockerfiles/.../Dockerfile`, runs Vitest/Jest + `tsc --noEmit` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `package.json`/lockfiles and the resolved container image, evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints`.

---

## 3. Recommended `full_audit.yaml` DAG Template for TypeScript

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (TypeScript)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic TypeScript AST/package.json/tsconfig analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

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
    uses: typescript_ast_audit
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
    uses: typescript_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
