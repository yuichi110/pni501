# Testing Standards (JavaScript)

## Core Principles
1. **Vitest / Jest / Node Test Runner**: Write unit and integration tests using Vitest, Jest, or `node --test` (`describe`, `it`/`test`, `expect`/`assert`) in `*.test.js` or `*.spec.js` files (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain statement and branch coverage of 80% or higher across core modules (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic & Isolated**: Mock external HTTP/database/filesystem dependencies cleanly and reset mocks between tests without shared global state.
4. **Meaningful Assertions**: Ensure every `it()` / `test()` block executes concrete `expect(...)` or `assert.*` verifications covering both valid inputs and error/edge cases (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated test suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated assertion/isolation gaps.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free/network-coupled tests.
