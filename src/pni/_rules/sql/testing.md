# Migration Dry-Run, Lint & Data-Integrity Testing Standards (SQL)

## Core Principles
1. **Ephemeral Database Migration Replay**: Verify in CI that all migrations apply cleanly from scratch against an ephemeral database container (and test rollback / idempotency where down-migrations exist).
2. **Static SQL Linting (`sqlfluff` / `squawk`)**: Run `sqlfluff lint` for syntax/style consistency and `squawk` (PostgreSQL) to catch lock-unsafe DDL migrations automatically in PRs.
3. **Query, View & Stored-Procedure Unit Tests**: Test complex SQL functions, triggers, views, and `dbt` models via `pgTAP`, `dbt test` (`not_null`, `unique`, `relationships`, `accepted_values`), or integration fixtures (`AstFacts.test_functions_count`).
4. **Query Plan Verification**: Check `EXPLAIN (ANALYZE, BUFFERS)` on high-traffic queries to verify index usage and avoid full sequential table scans.

## Evaluation Thresholds
- **`PASS`**: Automated migration replay in CI + `sqlfluff`/`squawk` lint gates + `pgTAP`/`dbt`/integration constraint assertions.
- **`WARN`**: Migrations replay in CI without `sqlfluff`/`squawk` lock-safety linting.
- **`FAIL`**: Zero automated migration testing or broken SQL scripts failing on clean schema bootstrap.
