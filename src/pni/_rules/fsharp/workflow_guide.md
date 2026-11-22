# F# Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for F# (`*.fsproj`, `*.fs`, `*.fsi`) repositories.

---

## 1. Mapping `targets` by F# Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Solution (`src/` + `tests/`)** | `src/App/*.fs`, `tests/App.Tests/*.fs` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Polyglot .NET Monorepo (F# Core + C# / TS)** | `src/Domain.FSharp/`, `src/Api.CSharp/` | Create per-component `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting F# Actions & Rules

1. **Core Built-in F# Actions**:
   - `repo_structure_audit` (`fsharp` scope): Auto-runs `project_inspect` for `*.fsproj`, `packages.lock.json`/`paket.lock`, .NET TFM, and supply-chain hygiene.
   - `fsharp_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="fsharp"`) to extract XML doc coverage, `mutable`/`null`/`unbox`/`Async.RunSynchronously` hazards, complexity, and CWE sinks.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records top-down module dependency order, entry points (`Program.fs`, Giraffe/Saturn routers), and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `fsharp_test_audit` (`needs: [ast_and_quality]`): Evaluates Expecto/xUnit/FsCheck suites and coverage against `fsharp/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated .NET SDK F# harness image via `.pni/dockerfiles/fsharp/dotnet.dockerfile`, runs `dotnet test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against NuGet dependencies/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for F#

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (F#)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic F# AST/.NET analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "."
  tests:
    - "tests"
    - "test"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: fsharp_ast_audit
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
    uses: fsharp_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
