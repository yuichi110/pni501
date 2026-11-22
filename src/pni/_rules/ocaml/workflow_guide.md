# OCaml Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for OCaml (`dune-project`, `*.opam`) repositories.

---

## 1. Mapping `targets` by OCaml Dune Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Dune Package** | `lib/*.ml`, `lib/*.mli`, `bin/main.ml`, `test/` | `source: ["lib", "bin"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **Multi-Library Dune Workspace** | `src/core/`, `src/server/`, `test/` | `source: ["src"]` (or per-package `scope: component` workflows + `category: rollup`)<br>`tests: ["test"]` |

---

## 2. Selecting OCaml Actions & Rules

1. **Core Built-in OCaml Actions**:
   - `repo_structure_audit` (`ocaml` scope): Auto-runs `project_inspect` for `dune-project`, `*.opam`, OCaml bounds, and supply-chain hygiene.
   - `ocaml_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="ocaml"`) to extract ODoc coverage, `Obj.magic`/`Marshal.from_*` CWE sinks, `open` pollution, mutable `ref` globals, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records Dune libraries, `.mli` module contracts, entrypoints (`bin/`), and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `ocaml_test_audit` (`needs: [ast_and_quality]`): Evaluates Alcotest/Expect/QCheck suites and `bisect_ppx` coverage against `ocaml/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated OCaml + Dune harness image via `.pni/dockerfiles/ocaml/dune.dockerfile`, runs `dune runtest` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for OCaml

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (OCaml)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic OCaml AST/Dune analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "lib"
    - "bin"
    - "src"
  tests:
    - "test"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: ocaml_ast_audit
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
    uses: ocaml_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
