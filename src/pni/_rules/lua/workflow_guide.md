# Lua Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Lua (`*.lua`, `*.rockspec`) repositories.

---

## 1. Mapping `targets` by Lua Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard LuaRocks Library / OpenResty Module** | `src/` or `lib/`, `spec/*_spec.lua`, `*.rockspec` | `source: ["src", "lib"]`<br>`tests: ["spec", "tests"]`<br>`docs: ["README.md"]` |
| **Neovim Plugin** | `lua/<plugin>/*.lua`, `tests/*_spec.lua` | `source: ["lua"]`<br>`tests: ["tests", "spec"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo (e.g. C/Rust + Lua Scripting)** | `src/`, `lua/` | Create a `scope: component` workflow (`targets.root: "lua"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Lua Actions & Rules

1. **Core Built-in Lua Actions**:
   - `repo_structure_audit` (`lua` scope): Auto-runs `project_inspect` for `*.rockspec`, Lua/LuaJIT runtime bounds, and supply-chain hygiene.
   - `lua_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="lua"`) to extract accidental global leaks, `load`/`loadstring`/`os.execute` CWE sinks, complexity, and LuaCATS coverage.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records module return tables, host/OpenResty/Neovim hooks, and data flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `lua_test_audit` (`needs: [ast_and_quality]`): Evaluates Busted/LuaUnit suites and coverage against `lua/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Lua + Busted harness image via `.pni/dockerfiles/lua/busted.dockerfile`, runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Lua

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Lua)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Lua AST analysis, Busted container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "lua"
    - "src"
    - "lib"
    - "."
  tests:
    - "spec"
    - "tests"
    - "test"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: lua_ast_audit
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
    uses: lua_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
