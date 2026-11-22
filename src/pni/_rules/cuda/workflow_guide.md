# CUDA Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for CUDA (`*.cu`, `*.cuh`, `CMakeLists.txt`) repositories.

---

## 1. Mapping `targets` by CUDA Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **CUDA Kernel Library** | `src/*.cu`, `include/*.cuh`, `tests/*.cu`, `CMakeLists.txt` | `source: ["src", "include", "kernels"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Python / PyTorch + CUDA Extension Monorepo** | `csrc/` (`*.cu`/`*.cpp`) + `python/` | Create separate `scope: component` workflows (`cuda` + `python`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting CUDA Actions & Rules

1. **Core Built-in CUDA Actions**:
   - `repo_structure_audit` (`cuda` scope): Auto-runs `project_inspect` for `CMakeLists.txt`, CUDA toolkit/architecture settings, and supply-chain hygiene.
   - `cuda_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="cuda"`) to extract kernel complexity, error-checking gaps, `__syncthreads()` divergence risks, global `__device__` state, and CWE sinks.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records host launchers, `__global__` kernels, stream/memory-transfer pipelines, and Python/C++ bindings into `.pni/cache/<workflow_id>/architecture.json`.
   - `cuda_test_audit` (`needs: [ast_and_quality]`): Evaluates CPU-oracle tests, tail-size coverage, and `compute-sanitizer` discipline against `cuda/testing`.
   - `container_runtime_audit` (`when: "has_runtime_harness"`): Automatically skipped cleanly on CPU-only hosts without GPU runtime harness (`has_runtime_harness=False`).
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for CUDA

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (CUDA)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic CUDA AST analysis, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "kernels"
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
    uses: cuda_ast_audit
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
    uses: cuda_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
