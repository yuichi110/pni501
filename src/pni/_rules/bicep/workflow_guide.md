# Bicep Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing Azure Bicep infrastructure repositories (`*.bicep`, `*.bicepparam`, `bicepconfig.json`).

---

## 1. Mapping `targets` by Bicep Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Azure Infra Repo** | `infra/main.bicep`, `infra/modules/*.bicep`, `*.bicepparam` | `source: ["infra", "."]`<br>`docs: ["README.md"]` |
| **App + Azure Bicep Monorepo** | `src/` (C#/Python/TS) + `infra/` (`*.bicep`) | Create a `scope: component` workflow (`targets.root: "infra"`) + `category: rollup`, OR audit the app as `scope: repo` so `infra/` is scanned as Companion DSL |

---

## 2. Selecting Bicep Actions & Rules

1. **Core Built-in Bicep Actions**:
   - `repo_structure_audit` (`bicep` scope): Auto-runs `project_inspect` for `bicepconfig.json`, registry module pins, CI security gates, and governance.
   - `bicep_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="bicep"`) to extract `@secure()`/`@description` discipline, TLS/HTTPS/public-access security issues, hardcoded secrets, and typed params.
   - `bicep_test_audit` (`needs: [ast_and_quality]`): Evaluates `bicep lint`/`build`, PSRule/Trivy, and `what-if` CI gates against `bicep/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) Azure misconfiguration & secret scanning.

---

## 3. Recommended `full_audit.yaml` DAG Template for Bicep

```yaml
id: full_audit
category: audit
name: Full Azure IaC Audit & Report (Bicep)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Bicep AST & Trivy IaC analysis, grounded infrastructure topology, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
    - "infra"
    - "bicep"
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: bicep_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: bicep_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
