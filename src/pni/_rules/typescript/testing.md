# Testing Standards (TypeScript)

## Core Principles
1. **Vitest / Jest Test Runner**: Write unit and integration tests using Vitest or Jest (`describe`, `it`/`test`, `expect`) in `*.test.ts(x)` or `*.spec.ts(x)` files.
2. **Coverage Target**: Maintain statement and branch coverage of 80% or higher across `src/` modules.
3. **Deterministic & Isolated**: Mock external HTTP/database/filesystem boundaries cleanly (`vi.fn()`, `jest.fn()`, MSW) and reset mocks between tests without shared global state.
4. **Meaningful Assertions**: Ensure every `it()` / `test()` block executes concrete `expect(...)` or `assert.*` verifications covering both valid inputs and error/edge cases.
