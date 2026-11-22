# C Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for C (`CMakeLists.txt`, `meson.build`, `Makefile`) repositories.

---

## 1. Mapping `targets` by C Project Layout

Inspect `CMakeLists.txt`, `meson.build`, or `Makefile` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Library / CLI (`src/` + `include/`)** | `include/*.h`, `src/*.c`, `tests/*.c` | `source: ["src", "include"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Flat C Project** | `*.c`, `*.h`, `Makefile`, `tests/` | `source: ["."]` *(exclude `build/` via `targets.exclude`)*<br>`tests: ["tests"]` |
| **Polyglot Monorepo (e.g. Python/Rust + C Extension)** | `csrc/`, `python/` | Create a `scope: component` workflow (`targets.root: "csrc"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting C Actions & Rules

1. **Core Built-in C Actions**:
   - `repo_structure_audit` (`c` scope): Auto-runs `project_inspect` for `CMakeLists.txt`/`meson.build`/`Makefile`, C standard constraints, vendored libraries, and supply-chain hygiene.
   - `c_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="c"`) to extract Doxygen header coverage, complexity, banned buffer-overflow functions (`gets`/`strcpy`/`sprintf`), format-string/command-injection CWE sinks, non-reentrant calls, and mutable globals.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records header API boundaries, entry points (`main`, shared-library exported symbols), module layering, and memory ownership flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `c_test_audit` (`needs: [ast_and_quality]`): Evaluates Unity/CMocka/Check/CTest suites, ASan/UBSan coverage, and boundary testing against `c/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated GCC/Clang + CMake/Make harness image via `.pni/dockerfiles/c/`, compiles and runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for C

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (C)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic C AST/CMake analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "include"
  tests:
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: c_ast_audit
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
    uses: c_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
