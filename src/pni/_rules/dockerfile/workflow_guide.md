# Dockerfile Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing standalone container repositories or Dockerfile components (`Dockerfile`, `Containerfile`, `*.dockerfile`). Note that in polyglot repos, PNI automatically scans Dockerfiles via `companion_ast_facts` during `scope: repo` and `category: rollup` audits.

---

## 1. Mapping `targets` by Container Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Base-Image / Container Pack Repo** | `Dockerfile`, `docker/**/*.dockerfile`, `.dockerignore` | `source: ["."]`<br>`docs: ["README.md"]` |
| **Application Repo with Dockerfiles** | `src/` + root `Dockerfile` | Prefer auditing the primary app language (`scope: repo`) so `Dockerfile` is scanned automatically as a Companion DSL |

---

## 2. Selecting Dockerfile Actions & Rules

1. **Core Built-in Dockerfile Actions**:
   - `repo_structure_audit` (`dockerfile` scope): Auto-runs `project_inspect` for container hygiene, `.dockerignore`, CI config, and governance.
   - `dockerfile_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="dockerfile"`) to detect `:latest` tags (AVD-DS-0001), `USER root` (AVD-DS-0002), `curl | sh` (CWE-829), hardcoded secrets, and multi-stage hygiene.
   - `dockerfile_test_audit` (`needs: [ast_and_quality]`): Evaluates `hadolint`, Trivy config/image gates, and CI build/smoke verification against `dockerfile/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) IaC misconfiguration & secret scanning.

---

## 3. Recommended `full_audit.yaml` DAG Template for Dockerfile

```yaml
id: full_audit
category: audit
name: Full Container Definition Audit & Report (Dockerfile)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Dockerfile AST & Trivy IaC analysis, architecture/stage review, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: dockerfile_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: dockerfile_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
