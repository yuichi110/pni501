# Migration Tooling & Dialect Governance Standards (SQL)

## Core Principles
1. **Ordered Versioned Migration Tooling**: Manage DDL evolutions via an explicit migration tool (`Flyway`, `Liquibase`, `Alembic`, `golang-migrate`, `Atlas`, `sqitch`, `Prisma`, `dbt`) with immutable, monotonically ordered migration files — never edit already-applied historical migrations in place.
2. **Explicit Dialect & Engine Version**: Declare the target SQL dialect and database engine version (`PostgreSQL 16`, `MySQL 8.4`, `SQLite 3.45`, `Snowflake`, `BigQuery`) in `.sqlfluff` / migration config (`ProjectFacts.language_version_constraint`).
3. **Zero-Lockfile Exemption**: Pure SQL migration directories do **not** use npm-style lockfiles — do **NOT** penalize SQL directories for lacking one; instead verify reproducible migration ordering and extension version pinning (`CREATE EXTENSION IF NOT EXISTS ...`).
4. **Least-Privilege DB Roles**: Separate migration DDL roles from runtime app DML roles (`SELECT`/`INSERT`/`UPDATE`/`DELETE` only — never run application traffic as `postgres` / `SUPERUSER`).

## Evaluation Thresholds
- **`PASS`**: Versioned immutable migrations with explicit dialect config (`.sqlfluff`), least-privilege roles, and documented DB engine target.
- **`WARN`**: Missing `.sqlfluff` dialect pin or missing down/rollback migration guidance.
- **`FAIL`**: Ad-hoc unversioned `schema.sql` edits applied manually, hardcoded `SUPERUSER` credentials, or mutated historical migrations.
