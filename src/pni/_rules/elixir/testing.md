# Testing Standards (Elixir)

## Core Principles
1. **ExUnit & Doctests**: Organize tests under `test/**/*_test.exs` mirroring `lib/` using `ExUnit.Case` (`async: true` whenever state-isolated) plus `doctest MyModule` for `@doc` examples (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher (`mix test --cover` / `ExCoveralls`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation (Mox / Ecto Sandbox)**: Define `@behaviour` contracts and mock external services with `Mox` (explicit per-process expectations safe under `async: true`) rather than global monkey-patching (`meck`), use `Ecto.Adapters.SQL.Sandbox` for DB isolation, and run offline.
4. **Meaningful Assertions**: Every `test "..."` block must assert concrete patterns or values (`assert`, `refute`, `assert_raise`, `assert_receive`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated ExUnit suite exists, `assertion_free_tests == 0`, deterministic isolated mocks, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated `:timer.sleep` flakiness.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
