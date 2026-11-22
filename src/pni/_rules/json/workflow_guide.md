# JSON Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing JSON Schema libraries or JSON configuration repositories (`*.json`, `*.schema.json`). In application repos, PNI also scans `.json` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by JSON Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **JSON Schema / Config Repo** | `schemas/*.schema.json`, `config/*.json` | `source: ["."]` *(exclude `node_modules/**`, lockfiles)*<br>`docs: ["README.md"]` |
| **App Repo with JSON Configs** | `src/` (App) + `config/*.json` | Audit the primary app language (`scope: repo`) so `.json` is scanned automatically as a Companion DSL |

---

## 2. Selecting JSON Actions & Rules

1. **Core Built-in JSON Actions**:
   - `repo_structure_audit` (`json` scope): Auto-runs `project_inspect` for schema references, committed secret files, and governance.
   - `json_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="json"`) to detect syntax issues, duplicate keys, hardcoded secrets/credentials, and schema hygiene.
   - `json_test_audit` (`needs: [ast_and_quality]`): Evaluates `check-jsonschema`/`ajv`/fixture CI gates against `json/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for JSON

```yaml
id: full_audit
category: audit
name: Full Schema & Configuration Audit & Report (JSON)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic JSON AST & security analysis, grounded schema map, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
  tests: []
  docs:
    - "README.md"
  exclude:
    - "package-lock.json"
    - "node_modules/**"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: json_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: json_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
