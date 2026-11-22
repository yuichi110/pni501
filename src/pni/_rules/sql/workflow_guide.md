# SQL Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing SQL migration, database, or `dbt` analytics repositories (`*.sql`). In polyglot app repos, PNI also scans `.sql` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by SQL Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Database Migrations / dbt Project** | `migrations/*.sql`, `models/**/*.sql`, `tests/*.sql` | `source: ["migrations", "models", "sql", "db"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **App + SQL Migrations Monorepo** | `src/` (App) + `migrations/` (`*.sql`) | Audit the primary app language (`scope: repo`) so `migrations/` is scanned automatically as a Companion DSL |

---

## 2. Selecting SQL Actions & Rules

1. **Core Built-in SQL Actions**:
   - `repo_structure_audit` (`sql` scope): Auto-runs `project_inspect` for `.sqlfluff`, migration tooling, dbt manifests, and governance.
   - `sql_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="sql"`) to detect `DROP TABLE`, `SELECT *`, unguarded `DELETE`/`UPDATE`, dynamic SQLi, and `SECURITY DEFINER` risks.
   - `sql_test_audit` (`needs: [ast_and_quality]`): Evaluates ephemeral migration replay, `sqlfluff`/`squawk`, and `pgTAP`/`dbt test` coverage against `sql/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for SQL

```yaml
id: full_audit
category: audit
name: Full Database & SQL Audit & Report (SQL)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic SQL AST & security analysis, grounded schema/migration map, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "migrations"
    - "sql"
    - "db"
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: sql_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: sql_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
