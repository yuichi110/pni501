# Testing Standards (Scala)

## Core Principles
1. **ScalaTest / MUnit / Weaver / ZIO Test Suites**: Organize specs under `src/test/scala` mirroring production packages (`*Spec.scala`, `*Suite.scala`), combining example-based tests with ScalaCheck property-based tests for pure domain logic (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain statement/branch coverage of 80% or higher via `sbt-scoverage` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Effect & Async Testing**: Avoid `Thread.sleep` and `Await.result` in async tests; use `AsyncFlatSpec`, `munit-cats-effect`, or ZIO `TestClock` with offline in-memory algebras/stubs.
4. **Meaningful Assertions**: Every test must verify concrete expectations (`assertEquals`, `shouldBe`, `intercept`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated ScalaTest/MUnit/ZIO Test suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated timing-sensitive `Future` tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
