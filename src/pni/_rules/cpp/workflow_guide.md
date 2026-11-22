# C++ Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for C++ (`CMakeLists.txt`, `meson.build`, `vcpkg.json`, `conanfile.*`) repositories.

---

## 1. Mapping `targets` by C++ Project Layout

Inspect `CMakeLists.txt`, `meson.build`, `vcpkg.json`, and `conanfile.*` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Library / App (`src/` + `include/`)** | `include/<pkg>/*.hpp`, `src/*.cpp`, `tests/*.cpp` | `source: ["src", "include"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Header-Only Library** | `include/<pkg>/*.hpp`, `tests/*.cpp` | `source: ["include"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo (e.g. Python/Pybind11 + C++)** | `cpp/`, `python/` | Create a `scope: component` workflow (`targets.root: "cpp"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting C++ Actions & Rules

1. **Core Built-in C++ Actions**:
   - `repo_structure_audit` (`cpp` scope): Auto-runs `project_inspect` for `CMakeLists.txt`/`meson.build`/`vcpkg.json`/`conanfile.*`, C++ standard, dependency pinning, and supply-chain hygiene.
   - `cpp_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="cpp"`) to extract Doxygen coverage, `using namespace` header pollution, raw `new`/`delete`, C-style casts, empty `catch (...)`, mutable globals, complexity, and CWE sinks.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records public header APIs, entry points, class/namespace layering, and ownership flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `cpp_test_audit` (`needs: [ast_and_quality]`): Evaluates GoogleTest/Catch2/CTest suites, ASan/UBSan readiness, and coverage against `cpp/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated C++ compiler + CMake harness image via `.pni/dockerfiles/cpp/`, compiles and runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for C++

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (C++)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic C++ AST/CMake analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

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
    uses: cpp_ast_audit
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
    uses: cpp_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
