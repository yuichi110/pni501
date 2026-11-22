# Julia Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Julia (`Project.toml`, `*.jl`) repositories.

---

## 1. Mapping `targets` by Julia Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Julia Package** | `src/MyPkg.jl`, `test/runtests.jl`, `Project.toml` | `source: ["src"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **Polyglot Scientific Monorepo (Julia + Python)** | `julia-core/`, `python-api/` | Create a `scope: component` workflow (`targets.root: "julia-core"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Julia Actions & Rules

1. **Core Built-in Julia Actions**:
   - `repo_structure_audit` (`julia` scope): Auto-runs `project_inspect` for `Project.toml`, `Manifest.toml` (exempting published General packages), `[compat]` bounds, and supply-chain hygiene.
   - `julia_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="julia"`) to extract docstrings, mutable global state, `Any` struct fields, `eval(Meta.parse())` CWE sinks, complexity, and Oxygen/Genie routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records module exports, multiple-dispatch extension seams, and numerical/service flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `julia_test_audit` (`needs: [ast_and_quality]`): Evaluates `test/runtests.jl`, `@inferred`, `Aqua.jl`, and coverage against `julia/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Julia harness image via `.pni/dockerfiles/julia/pkg.dockerfile`, runs `Pkg.test()` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Julia

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Julia)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Julia AST/Pkg analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "."
  tests:
    - "test"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: julia_ast_audit
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
    uses: julia_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
