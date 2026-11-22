# Bash / Shell Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Bash / Shell (`*.sh`, `*.bash`, `*.bats`) repositories.

---

## 1. Mapping `targets` by Shell Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Scripts / DevOps Automation Repo** | `scripts/*.sh`, `bin/*`, `tests/*.bats` | `source: ["scripts", "bin"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Root Shell CLI / Library** | `*.sh`, `lib/*.sh`, `tests/*.bats` | `source: ["."]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo (App + Ops Scripts)** | `services/`, `scripts/` | Create a `scope: component` workflow (`targets.root: "scripts"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Bash Actions & Rules

1. **Core Built-in Bash Actions**:
   - `repo_structure_audit` (`bash` scope): Auto-runs `project_inspect` for shell scripts, CI configs, supply-chain hygiene, and runtime prerequisites (exempting lockfiles).
   - `bash_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="bash"`) to extract strict-mode gaps, `eval`/unquoted expansion/command-injection CWE sinks, global state, and function complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records CLI entrypoints, sourced library scripts, external tool boundaries, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `bash_test_audit` (`needs: [ast_and_quality]`): Evaluates Bats / ShellSpec suites, isolation, and error-path assertions against `bash/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Bash + ShellCheck + Bats harness image via `.pni/dockerfiles/bash/bats.dockerfile`, runs `bash -n` / `bats` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Bash

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Bash)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Bash AST analysis, Bats/ShellCheck container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "scripts"
    - "bin"
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
    uses: bash_ast_audit
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
    uses: bash_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
