# YAML Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing GitOps, Kubernetes/Helm, OpenAPI, or CI workflow repositories (`*.yaml`, `*.yml`). In application repos, PNI also scans YAML files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by YAML Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **GitOps / K8s / Helm Repo** | `charts/`, `manifests/`, `.github/workflows/` | `source: [".", ".github/workflows"]`<br>`docs: ["README.md"]` |
| **App Repo with CI / Compose / OpenAPI YAML** | `src/` (App) + `.github/workflows/` | Audit the primary app language (`scope: repo`) so YAML files are scanned automatically as a Companion DSL |

---

## 2. Selecting YAML Actions & Rules

1. **Core Built-in YAML Actions**:
   - `repo_structure_audit` (`yaml` scope): Auto-runs `project_inspect` for CI supply-chain issues, `Chart.lock`, Dependabot/Renovate, and governance.
   - `yaml_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="yaml"`) to detect `permissions: write-all` (CWE-269), unpinned Actions (missing commit SHA), K8s privileged/root misconfigs, duplicate keys, and hardcoded secrets.
   - `yaml_test_audit` (`needs: [ast_and_quality]`): Evaluates `yamllint`, `actionlint`, `kubeconform`, and `trivy config` CI gates against `yaml/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) IaC & secret scanning across all YAML files.

---

## 3. Recommended `full_audit.yaml` DAG Template for YAML

```yaml
id: full_audit
category: audit
name: Full Configuration, CI & GitOps Audit & Report (YAML)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic YAML AST & Trivy IaC analysis, grounded config/GitOps topology, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
    - ".github/workflows"
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: yaml_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: yaml_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
