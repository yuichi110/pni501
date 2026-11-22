# Ada Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Ada (`alire.toml`, `*.gpr`, `*.ads`, `*.adb`) repositories.

---

## 1. Mapping `targets` by Ada Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Alire / GPRbuild Crate** | `src/*.ads`, `src/*.adb`, `tests/*.adb`, `alire.toml` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Safety-Critical Embedded + Host Monorepo** | `ada-core/`, `tools-python/` | Create separate `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Ada Actions & Rules

1. **Core Built-in Ada Actions**:
   - `repo_structure_audit` (`ada` scope): Auto-runs `project_inspect` for `alire.toml`, `*.gpr`, Ada standard flags, and supply-chain hygiene.
   - `ada_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="ada"`) to extract `.ads` spec documentation, `Unchecked_Conversion`/`pragma Suppress`/`when others => null` hazards, global state, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records package specs (`.ads`), task/protected boundaries, FFI seams, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `ada_test_audit` (`needs: [ast_and_quality]`): Evaluates AUnit/Ahven/GPR test suites, `-gnata` contract checks, and coverage against `ada/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated GNAT/Alire harness image via `.pni/dockerfiles/ada/gnat.dockerfile`, compiles and runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Ada

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Ada)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Ada AST/Alire analysis, GNAT container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

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
    uses: ada_ast_audit
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
    uses: ada_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
