# Testing Standards (C#)

## Core Principles
1. **Modern xUnit / NUnit / MSTest Suites**: Organize tests in dedicated `*.Tests` projects mirroring production namespaces using `[Fact]` / `[Theory]` (`[InlineData]`) or `[Test]` / `[TestCase]` (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line/branch coverage of 80% or higher via `coverlet.collector` (`dotnet test --collect:"XPlat Code Coverage"`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Async & Dependency Isolation**: Use `WebApplicationFactory<Program>` / Testcontainers or fakes (`NSubstitute`/`Moq`) for external boundaries, avoid `Thread.Sleep` timing flakiness, and test `CancellationToken` paths offline.
4. **Meaningful Assertions**: Every test method must assert concrete outcomes (`Assert.Equal`, `Assert.ThrowsAsync`, `Shouldly`/`FluentAssertions`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Dedicated automated test project exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated timing/mocking fragility.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / external-network-coupled tests.
