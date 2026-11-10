# Testing Standards (JavaScript)

## Core Principles
1. **Vitest / Jest / Node Test Runner**: Write unit and integration tests using Vitest, Jest, or `node --test` (`describe`, `it`/`test`, `expect`/`assert`) in `*.test.js` or `*.spec.js` files.
2. **Coverage Target**: Maintain statement and branch coverage of 80% or higher across core modules.
3. **Deterministic & Isolated**: Mock external HTTP/database/filesystem dependencies cleanly and reset mocks between tests without shared global state.
4. **Meaningful Assertions**: Ensure every `it()` / `test()` block executes concrete `expect(...)` or `assert.*` verifications covering both valid inputs and error/edge cases.
