# Modern SQL (SQL:2016+ / PostgreSQL 16+ / dbt) Idioms (`sql/modern_stack`)

## Core Principles
1. **CTEs, Window Functions & Explicit `JOIN`s**: Replace legacy comma-separated implicit joins (`FROM a, b WHERE a.id = b.a_id`) and correlated subqueries with explicit `INNER`/`LEFT JOIN ... ON`, readable `WITH` CTEs, and window functions (`ROW_NUMBER() OVER (...)`, `SUM(...) OVER (...)`; `AstFacts.modernization_hints`).
2. **Atomic Upserts & Safe Pagination**: Use `INSERT ... ON CONFLICT DO UPDATE` / `MERGE` instead of racy read-then-insert logic, and prefer keyset pagination (`WHERE id > $cursor LIMIT $n`) over deep `OFFSET` on large tables.
3. **Row-Level Security & Least-Privilege Views**: Use `SECURITY INVOKER` views (PostgreSQL 15+) and Row-Level Security (RLS) intentionally for multi-tenant isolation, avoiding unguarded `SECURITY DEFINER` functions with mutable `search_path` (CWE-426; `AstFacts.dangerous_sinks`).
4. **Declarative Schema & Analytics Hygiene**: Consider declarative migration diffing (`Atlas`, `dbt` contracts) for large schemas.
