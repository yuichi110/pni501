# HCL / Terraform / OpenTofu Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing Terraform / OpenTofu infrastructure repositories (`*.tf`, `*.tfvars`, `*.hcl`).

---

## 1. Mapping `targets` by IaC Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Terraform Module / Infra Repo** | `main.tf`, `variables.tf`, `modules/*/`, `tests/*.tftest.hcl` | `source: [".", "modules"]`<br>`tests: ["tests"]`<br>`exclude: [".terraform/**"]` |
| **App + Terraform Monorepo** | `src/` (App) + `infra/` (`*.tf`) | Create a `scope: component` workflow (`targets.root: "infra"`) + `category: rollup`, OR audit the app as `scope: repo` so `infra/` is scanned as Companion DSL |

---

## 2. Selecting HCL Actions & Rules

1. **Core Built-in HCL Actions**:
   - `repo_structure_audit` (`hcl` scope): Auto-runs `project_inspect` for `versions.tf`, `.terraform.lock.hcl`, CI supply-chain config, and governance.
   - `hcl_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="hcl"`) to detect `0.0.0.0/0` exposure (CWE-284), `encrypted = false` (CWE-311), wildcard IAM, hardcoded secrets, and variable typing/description coverage.
   - `hcl_test_audit` (`needs: [ast_and_quality]`): Evaluates `*.tftest.hcl` / `validate` / `tflint` / Checkov gates against `hcl/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) Terraform misconfiguration & secret scanning.

---

## 3. Recommended `full_audit.yaml` DAG Template for HCL / Terraform

```yaml
id: full_audit
category: audit
name: Full Infrastructure-as-Code Audit & Report (HCL / Terraform)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic HCL AST & Trivy IaC analysis, grounded infrastructure topology, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
    - "infra"
    - "terraform"
  tests: []
  docs:
    - "README.md"
  exclude:
    - ".terraform/**"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: hcl_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: hcl_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
