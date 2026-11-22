# Svelte / SvelteKit Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Svelte (`*.svelte`, `svelte.config.js`/`ts`) repositories.

---

## 1. Mapping `targets` by Svelte Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard SvelteKit App** | `src/routes/`, `src/lib/`, `tests/` | `source: ["src"]`<br>`tests: ["tests", "src"]`<br>`docs: ["README.md"]` |
| **Full-Stack Monorepo (Backend + SvelteKit)** | `backend/`, `frontend/` | Create a `scope: component` workflow (`targets.root: "frontend"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Svelte Actions & Rules

1. **Core Built-in Svelte Actions**:
   - `repo_structure_audit` (`svelte` scope): Auto-runs `project_inspect` for `package.json`, `svelte.config.*`, lockfiles, Svelte version, and supply-chain hygiene.
   - `svelte_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="svelte"`) to extract `{@html}` XSS / `eval` CWE sinks, SSR store leaks, complexity, and SvelteKit server routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records SvelteKit routes (`+page.svelte`, `+server.ts`, `+page.server.ts`), `$lib` boundaries, and data flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `svelte_test_audit` (`needs: [ast_and_quality]`): Evaluates Vitest / `@testing-library/svelte` suites and coverage against `svelte/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Node/Svelte harness image via `.pni/dockerfiles/svelte/node.dockerfile`, runs Vitest / `svelte-check` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against lockfiles/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Svelte

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Svelte)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Svelte AST/package analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
  tests:
    - "tests"
    - "src"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: svelte_ast_audit
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
    uses: svelte_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
