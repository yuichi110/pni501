# TOML Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing TOML configuration repositories (`*.toml`). In application repos, PNI also scans `.toml` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by TOML Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Config / Policy Pack Repo** | `config/*.toml`, `taplo.toml`, `README.md` | `source: ["."]`<br>`docs: ["README.md"]` |
| **App Repo with TOML Manifests/Configs** | `src/` (Python/Rust) + `pyproject.toml`/`Cargo.toml` | Audit the primary app language (`scope: repo`) so `.toml` is scanned automatically as a Companion DSL |

---

## 2. Selecting TOML Actions & Rules

1. **Core Built-in TOML Actions**:
   - `repo_structure_audit` (`toml` scope): Auto-runs `project_inspect` for TOML layout, secret-file hygiene, and governance.
   - `toml_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="toml"`) to detect duplicate keys/tables, hardcoded secrets, and structural/schema hygiene.
   - `toml_test_audit` (`needs: [ast_and_quality]`): Evaluates `taplo check` and config deserialization tests against `toml/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for TOML

```yaml
id: full_audit
category: audit
name: Full Configuration Audit & Report (TOML)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic TOML AST & security analysis, grounded config structure review, score+SARIF emission, and Drawlib report.

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
    uses: toml_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: toml_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
