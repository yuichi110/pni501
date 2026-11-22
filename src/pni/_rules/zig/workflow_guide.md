# Zig Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Zig (`build.zig`, `build.zig.zon`, `*.zig`) repositories.

---

## 1. Mapping `targets` by Zig Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Zig Package / CLI** | `src/root.zig`, `src/main.zig`, `tests/`, `build.zig` | `source: ["src"]`<br>`tests: ["tests", "src"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo (App + Zig Native Lib)** | `native-zig/`, `backend/` | Create a `scope: component` workflow (`targets.root: "native-zig"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Zig Actions & Rules

1. **Core Built-in Zig Actions**:
   - `repo_structure_audit` (`zig` scope): Auto-runs `project_inspect` for `build.zig`, `build.zig.zon`, Zig version pins, and supply-chain hygiene.
   - `zig_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="zig"`) to extract doc comments, `catch unreachable`/`@setRuntimeSafety(false)` hazards, mutable globals, complexity, and CWE sinks.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records modules, allocator ownership boundaries, FFI seams, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `zig_test_audit` (`needs: [ast_and_quality]`): Evaluates `test "..."` blocks, `std.testing.allocator` leak checking, and OOM tests against `zig/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Zig harness image via `.pni/dockerfiles/zig/zig.dockerfile`, runs `zig build test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Zig

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Zig)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Zig AST/build analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "."
  tests:
    - "tests"
    - "src"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: zig_ast_audit
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
    uses: zig_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
