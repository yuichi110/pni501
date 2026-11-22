# MATLAB Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for MATLAB (`*.m`) repositories.

---

## 1. Mapping `targets` by MATLAB Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard MATLAB Toolbox / Library** | `src/+pkg/*.m`, `tests/*Test.m`, `README.md` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Research / Algorithm Repo** | `matlab/*.m` or root `*.m`, `tests/` | `source: ["matlab", "."]`<br>`tests: ["tests", "test"]` |
| **Polyglot Scientific Monorepo (MATLAB + Python/C++)** | `matlab/`, `cpp/` | Create a `scope: component` workflow (`targets.root: "matlab"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting MATLAB Actions & Rules

1. **Core Built-in MATLAB Actions**:
   - `repo_structure_audit` (`matlab` scope): Auto-runs `project_inspect` for MATLAB layout, toolbox documentation, hardcoded paths, and supply-chain hygiene.
   - `matlab_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="matlab"`) to extract `eval`/`evalin`/`system` CWE sinks, `global` state, `help` header coverage, and function complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records `+package` namespaces, `classdef` models, algorithm entry points, and data flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `matlab_test_audit` (`needs: [ast_and_quality]`): Evaluates `matlab.unittest` / MOxUnit suites, numerical tolerances, and RNG determinism against `matlab/testing`.
   - `container_runtime_audit` (`when: "has_runtime_harness"`): Automatically skipped cleanly when proprietary MATLAB container runtime is unavailable (`has_runtime_harness=False`).
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for MATLAB

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (MATLAB)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic MATLAB AST analysis, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "matlab"
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
    uses: matlab_ast_audit
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
    uses: matlab_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
