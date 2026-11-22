# Common Lisp Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Common Lisp (`*.asd`, `*.lisp`) repositories.

---

## 1. Mapping `targets` by Common Lisp Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard ASDF System** | `src/*.lisp`, `tests/*.lisp`, `my-pkg.asd` | `source: ["src"]`<br>`tests: ["tests", "t"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo (Common Lisp + Web/Python)** | `lisp-engine/`, `web/` | Create separate `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Common Lisp Actions & Rules

1. **Core Built-in Common Lisp Actions**:
   - `repo_structure_audit` (`commonlisp` scope): Auto-runs `project_inspect` for `*.asd`, `qlfile.lock`, ASDF test system separation, and supply-chain hygiene.
   - `commonlisp_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="commonlisp"`) to extract docstrings, `*read-eval*` / `eval` / shell-injection CWE sinks, `(safety 0)` hazards, dynamic special globals, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records ASDF systems, `defpackage` boundaries, CLOS/protocol generics, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `commonlisp_test_audit` (`needs: [ast_and_quality]`): Evaluates FiveAM/Rove/Parachute suites, `--non-interactive` exit hygiene, and `sb-cover` coverage against `commonlisp/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated SBCL harness image via `.pni/dockerfiles/commonlisp/sbcl.dockerfile`, loads and runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Common Lisp

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Common Lisp)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Common Lisp AST/ASDF analysis, SBCL container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "."
  tests:
    - "tests"
    - "t"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: commonlisp_ast_audit
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
    uses: commonlisp_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
