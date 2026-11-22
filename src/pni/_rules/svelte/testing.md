# Testing Standards (Svelte)

## Core Principles
1. **Vitest + `@testing-library/svelte` & Playwright**: Test Svelte components and utilities under `tests/` or co-located `*.test.ts` / `*.spec.ts` using Vitest + `@testing-library/svelte` (`render`, `fireEvent`/`userEvent`) and Playwright for critical SvelteKit E2E flows (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line/branch coverage of 80% or higher on stores, server loaders, and core components via `@vitest/coverage-v8` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Mock SvelteKit `$app/*` modules and outbound `fetch` deterministically (MSW / `vi.fn()`) so unit/component suites run completely offline.
4. **Meaningful Assertions**: Every `it()` / `test()` block must verify visible DOM state, form action responses, or emitted callbacks (`expect(...)`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Vitest/Testing-Library suite exists, `assertion_free_tests == 0`, isolated mocks, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `+page.server.ts` loader/action tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
