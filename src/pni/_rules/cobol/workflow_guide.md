# COBOL Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for COBOL (`*.cob`, `*.cbl`, `*.cpy`) repositories.

---

## 1. Mapping `targets` by COBOL Repository Layout

Inspect source directories, copybooks (`copybooks/`, `cpy/`), JCL, and test drivers to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard COBOL Layout (`src/` + `copybooks/`)** | `src/*.cob`, `copybooks/*.cpy`, `tests/test_*.cob` | `source: ["src", "copybooks"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Flat Batch Repo** | `*.cbl`, `*.cpy`, `Makefile`, `tests/` | `source: ["."]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Legacy Mainframe + Modern API Monorepo** | `cobol/` + `services/api/` (Java/Python) | Create a `scope: component` workflow (`targets.root: "cobol"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting COBOL Actions & Rules

1. **Core Built-in COBOL Actions**:
   - `repo_structure_audit` (`cobol` scope): Auto-runs `project_inspect` for build scripts, copybook structure, compiler dialect hints, and repository governance (exempting npm/Cargo-style lockfiles).
   - `cobol_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="cobol"`) to extract `PROGRAM-ID`/paragraph inventory, `GO TO`/`ALTER` idioms, complexity, mutable global `WORKING-STORAGE`, and embedded SQL/dynamic-`CALL` CWE sinks.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records batch/online entry programs (`PROGRAM-ID`), `CALL` trees, `.cpy` copybook boundaries, file/DB datasets, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `cobol_test_audit` (`needs: [ast_and_quality]`): Evaluates GnuCOBOL test drivers, `cobol-check` suites, and golden-dataset regression tests against `cobol/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated GnuCOBOL harness image via `.pni/dockerfiles/cobol/gnucobol.dockerfile`, compiles and executes tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for COBOL

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (COBOL)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic COBOL AST analysis, GnuCOBOL runtime verification, security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "cobol"
    - "cbl"
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
    uses: cobol_ast_audit
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
    uses: cobol_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
