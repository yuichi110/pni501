# Testing Standards (Vue)

## Core Principles
1. **Vitest & `@vue/test-utils` / Testing Library**: Test SFCs and composables under `tests/` or co-located `*.spec.ts` / `*.test.ts` using `vitest` + `@vue/test-utils` (`mount`) or `@testing-library/vue` (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line/branch coverage of 80% or higher on composables, stores, and core UI components via `@vitest/coverage-v8` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Behavior-Focused & Deterministic Isolation**: Assert rendered DOM output, user interactions (`trigger`, `setValue`), emitted events, and Pinia state transitions rather than private component internals; mock HTTP calls with MSW/Vitest mocks and run offline without real browsers for unit tests.
4. **Meaningful Assertions**: Every `it()` / `test()` block must verify concrete DOM/event/state assertions (`expect(...)`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Vitest/component suite exists, `assertion_free_tests == 0`, deterministic mocks, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or over-reliance on brittle snapshot-only assertions.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
