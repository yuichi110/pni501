# Odin Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Odin (`*.odin`) repositories.

---

## 1. Mapping `targets` by Odin Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Odin Application / Library** | `src/*.odin`, `tests/*_test.odin`, `ols.json` | `source: ["src"]`<br>`tests: ["tests", "src"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo (Odin Engine + Tooling)** | `engine/` (Odin) + `tools/` (Python) | Create separate `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Odin Actions & Rules

1. **Core Built-in Odin Actions**:
   - `repo_structure_audit` (`odin` scope): Auto-runs `project_inspect` for Odin layout, `ols.json`/`Makefile`, vendored C deps, and governance (exempting npm-style lockfiles).
   - `odin_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="odin"`) to extract doc comments, allocator/`defer` & error-check discipline, `#no_bounds_check`/`transmute` risks, mutable globals, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records Odin packages, allocator/arena boundaries, `foreign` C bindings, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `odin_test_audit` (`needs: [ast_and_quality]`): Evaluates `@(test)` suites, tracking-allocator leak safety, and assertions against `odin/testing`.
   - `container_runtime_audit` (`when: "has_runtime_harness"`): Automatically skipped cleanly when no built-in Odin container harness is configured (`has_runtime_harness=False`).
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Odin

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Odin)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Odin AST analysis, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "."
  tests:
    - "tests"
    - "src"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: odin_ast_audit
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
    uses: odin_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
