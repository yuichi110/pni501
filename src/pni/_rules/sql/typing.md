# Column Typing, Constraints & Referential Integrity Standards (SQL)

## Core Principles
1. **Exact Numeric & Timezone-Aware Types**: Store monetary/financial amounts in exact fixed-point `NUMERIC(p, s)` / `DECIMAL(p, s)` (or integer minor units `BIGINT`) — NEVER binary `FLOAT`/`REAL`/`DOUBLE PRECISION`; store timestamps in timezone-aware `TIMESTAMPTZ` (UTC) rather than naive `TIMESTAMP` without timezone (`AstFacts.type_safety_issues`).
2. **Explicit Primary Keys, Foreign Keys, `NOT NULL` & `CHECK` Constraints**: Every entity table must define a `PRIMARY KEY` (`BIGINT`/`UUID`), explicit `NOT NULL` defaults where applicable, `FOREIGN KEY` constraints (with explicit `ON DELETE` policy and supporting index on the referencing column!), and `CHECK` constraints enforcing domain invariants.
3. **Avoid Untyped `TEXT`/`JSONB` Dumping Grounds**: Model core relational attributes and query-filtered keys as typed columns rather than opaque JSON blobs (`AstFacts.weak_type_usages`).
4. **Consistent Identifier Naming & Collations**: Use consistent `snake_case` unquoted lowercase identifiers across schemas to avoid fragile case-sensitive quoting.

## Evaluation Thresholds
- **`PASS`**: `NUMERIC`/`BIGINT` for money, `TIMESTAMPTZ` for timestamps, explicit PK/FK/`NOT NULL`/`CHECK` constraints, and indexed foreign keys.
- **`WARN`**: Missing indexes on secondary FK columns or isolated naive `TIMESTAMP` columns.
- **`FAIL`**: Floating-point currency columns, missing primary keys, unindexed high-churn foreign keys, or unconstrained nullable schema sprawl.
