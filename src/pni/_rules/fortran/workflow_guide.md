# Fortran Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Fortran (`fpm.toml`, `CMakeLists.txt`, `*.f90`) repositories.

---

## 1. Mapping `targets` by Fortran Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard `fpm` Package** | `src/*.f90`, `app/main.f90`, `test/*.f90`, `fpm.toml` | `source: ["src", "app"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **CMake / Legacy Scientific Repo** | `src/*.f90` or `*.f`, `tests/`, `CMakeLists.txt` | `source: ["src", "."]`<br>`tests: ["tests", "test"]` |
| **Polyglot Scientific Monorepo (Fortran + Python/f2py)** | `fortran/`, `python/` | Create a `scope: component` workflow (`targets.root: "fortran"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Fortran Actions & Rules

1. **Core Built-in Fortran Actions**:
   - `repo_structure_audit` (`fortran` scope): Auto-runs `project_inspect` for `fpm.toml`, `CMakeLists.txt`, compiler standards, and supply-chain hygiene.
   - `fortran_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="fortran"`) to extract `implicit none` coverage, `COMMON`/`EQUIVALENCE`/`GOTO` legacy risks, `execute_command_line` CWE sinks, and procedure complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records `program` entry points, `module`/`submodule` dependency graphs, and numerical pipeline flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `fortran_test_audit` (`needs: [ast_and_quality]`): Evaluates `fpm test` / `test-drive` / `pFUnit` suites and numerical tolerances against `fortran/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated `gfortran` / `fpm` harness image via `.pni/dockerfiles/fortran/`, compiles and runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Fortran

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Fortran)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Fortran AST analysis, gfortran/fpm container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "app"
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
    uses: fortran_ast_audit
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
    uses: fortran_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
