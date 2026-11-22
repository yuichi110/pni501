# Testing Standards (Kotlin)

## Core Principles
1. **JUnit 5 / Kotest & Coroutine Testing**: Organize tests under `src/test/kotlin` mirroring production packages (`*Test.kt`, `*Spec.kt`), using `runTest` (`kotlinx-coroutines-test`) for deterministic virtual-time testing of `suspend` functions (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line/branch coverage of 80% or higher via JaCoCo or Kover (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Inject `CoroutineDispatcher`s (never hardcode `Dispatchers.IO` without injection), use `MockK` / fakes or Testcontainers for external boundaries, and ensure offline execution.
4. **Meaningful Assertions**: Every test must assert concrete values or exceptions (`assertEquals`, `assertThrows`, Kotest `shouldBe`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated JUnit 5/Kotest suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated `runBlocking` / `Thread.sleep` flakiness.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
