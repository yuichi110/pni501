# Elixir Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Elixir (`mix.exs`) repositories.

---

## 1. Mapping `targets` by Elixir Project Layout

Inspect `mix.exs` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Mix / Phoenix App** | `lib/`, `test/`, `mix.exs`, `README.md` | `source: ["lib"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **Umbrella Application** | `apps/core/lib`, `apps/web/lib`, `apps/*/test` | List explicit `apps/*/lib` dirs or create per-app `scope: component` workflows + one `category: rollup` workflow |
| **Polyglot Monorepo (e.g. Elixir + TypeScript)** | `backend/` (Phoenix) + `frontend/` (TS/Vue) | Create per-component `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Elixir Actions & Rules

1. **Core Built-in Elixir Actions**:
   - `repo_structure_audit` (`elixir` scope): Auto-runs `project_inspect` for `mix.exs`, `mix.lock` (exempting pure Hex libs), Elixir/OTP version constraints, dependency scoping, and supply-chain hygiene.
   - `elixir_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="elixir"`) to extract `@moduledoc`/`@doc` coverage, `String.to_atom`/unsafe `binary_to_term`/`Code.eval_string` hazards, complexity, CWE sinks, and Phoenix/Plug routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records OTP supervision trees, entry points (`Application.start`, Phoenix router/LiveView, GenServers), context layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `elixir_test_audit` (`needs: [ast_and_quality]`): Evaluates ExUnit suites, doctests, `Mox` isolation, and coverage against `elixir/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Elixir/Mix harness image via `.pni/dockerfiles/elixir/mix.dockerfile`, runs `mix test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `mix.lock` / workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Elixir

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Elixir)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Elixir AST/Mix analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "lib"
  tests:
    - "test"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: elixir_ast_audit
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
    uses: elixir_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
