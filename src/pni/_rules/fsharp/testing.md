# Testing Standards (F#)

## Core Principles
1. **Expecto / xUnit / FsUnit + FsCheck**: Organize unit and property tests in dedicated `*.Tests.fsproj` projects (`*Tests.fs`) using `Expecto`, `xUnit`, or `NUnit` plus `FsCheck` property-based tests for algebraic domain invariants (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line/branch coverage of 80% or higher via `coverlet` (`dotnet test --collect:"XPlat Code Coverage"`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Pure Core & Deterministic Isolation**: Pass pure function dependencies (higher-order functions or small record interfaces) so unit tests run completely offline without mocking frameworks or live services.
4. **Meaningful Assertions**: Every test must assert concrete outcomes (`Expect.equal`, `Assert.Equal`, `Expect.throws`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Expecto/xUnit suite exists, `assertion_free_tests == 0`, pure isolated execution, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `Result`/`Error` branch tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
