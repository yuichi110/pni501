# Testing Standards (Lua)

## Core Principles
1. **Busted / Plenary / LuaUnit Suites**: Organize automated specs under `spec/**/*_spec.lua` or `tests/**/*_test.lua` using `busted` (`describe`, `it`, `assert.are.same`), `plenary.busted` (Neovim), or `luaunit` (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher via `luacov` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Stub filesystem/HTTP/host-API boundaries via `busted` `stub`/`spy` or dependency injection, clean up modified `package.loaded` entries in `after_each`, and run offline.
4. **Meaningful Assertions**: Every `it()` / test function must assert concrete return values and error tuples (`assert.are.equal`, `assert.has_error`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Busted/LuaUnit suite exists, `assertion_free_tests == 0`, isolated fixtures, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `value, err` error-path tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / host-coupled tests.
