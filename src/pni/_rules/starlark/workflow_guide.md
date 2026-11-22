# Starlark / Bazel Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing Bazel rulesets or Starlark build definitions (`MODULE.bazel`, `BUILD.bazel`, `*.bzl`). In polyglot Bazel monorepos, PNI also scans Starlark files automatically as a Companion DSL.

---

## 1. Mapping `targets` by Bazel / Starlark Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Bazel Ruleset Repo (`rules_*`)** | `<lang>/*.bzl`, `tests/`, `MODULE.bazel` | `source: ["."]` *(exclude `bazel-*` symlinks)*<br>`tests: ["tests"]` |
| **Polyglot Bazel Monorepo** | `services/` (Go/Java/Python/C++) + `MODULE.bazel` / `BUILD.bazel` | Create per-service `scope: component` workflows + `category: rollup` (automatically scans Starlark as Companion DSL) |

---

## 2. Selecting Starlark Actions & Rules

1. **Core Built-in Starlark Actions**:
   - `repo_structure_audit` (`starlark` scope): Auto-runs `project_inspect` for `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelversion`, and supply-chain hygiene.
   - `starlark_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="starlark"`) to check `run_shell` injection risks, `depset.to_list()` traps, `glob(["**"])`, `visibility`, and Stardoc coverage.
   - `starlark_test_audit` (`needs: [ast_and_quality]`): Evaluates `rules_testing` / `skylib` analysis tests and `buildifier` lint gates against `starlark/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for Starlark / Bazel

```yaml
id: full_audit
category: audit
name: Full Bazel / Starlark Build Audit & Report (Starlark)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Starlark AST & security analysis, grounded ruleset architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
  tests: []
  docs:
    - "README.md"
  exclude:
    - "bazel-*/**"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: starlark_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: starlark_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
