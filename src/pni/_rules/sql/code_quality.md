# Code Quality & Safe Migration Standards (SQL)

## Core Principles
1. **Zero Unguarded Destructive Statements**: Never issue `DELETE FROM tbl;` or `UPDATE tbl SET ...;` without an explicit `WHERE` clause, avoid unguarded `DROP TABLE` / `TRUNCATE` in forward migrations without safety rationale (`AstFacts.bug_risk_idioms`), and wrap multi-statement migrations in explicit transactions (`BEGIN; ... COMMIT;`) where supported by the dialect.
2. **Avoid `SELECT *` & Dynamic SQL Injection**: Specify explicit column lists instead of `SELECT *` in production queries/views (`AstFacts.bug_risk_idioms` — prevents silent schema-drift breakage and excessive I/O), and NEVER build dynamic SQL inside stored procedures via string concatenation (`EXECUTE 'SELECT ... ' || user_input`; CWE-89 — use `USING` bind params / `format('%I', ...)` for identifiers; `AstFacts.dangerous_sinks`).
3. **Zero-Downtime DDL Discipline**: For production databases, avoid long-holding table locks (`CREATE INDEX CONCURRENTLY` in PostgreSQL, add nullable columns before backfilling & setting `NOT NULL NOT VALID` -> `VALIDATE CONSTRAINT`, avoid destructive column drops in the same release as app reads).
4. **Formatting (`sqlfluff`) & Schema Documentation**: Lint and format SQL with `sqlfluff` (consistent keyword casing, explicit `JOIN ... ON` over comma joins), and document tables/views/migrations with comments (`COMMENT ON TABLE` or `--` headers; `AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Zero unguarded `DELETE`/`UPDATE`/`DROP` or dynamic SQLi sinks, explicit column lists (no `SELECT *`), zero-downtime DDL awareness, and clean `sqlfluff` hygiene.
- **`WARN`**: Occasional `SELECT *` in exploratory reports or missing `COMMENT ON` / header comments.
- **`FAIL`**: Unguarded `DELETE`/`UPDATE` without `WHERE`, dynamic SQL injection in stored procedures/functions, or hardcoded DB credentials (`CREATE USER ... PASSWORD '...'`).
