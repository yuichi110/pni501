# Testing Standards (Java)

## Core Principles
1. **JUnit 5 Framework**: Use JUnit Jupiter (`@Test`, `@ParameterizedTest`, `Assertions.assertThrows`) for unit and integration testing (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line and branch coverage of 80% or higher (verified via JaCoCo: `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`) across core packages.
3. **Deterministic & Isolated**: Isolate external I/O and collaborators using interfaces, fakes, or Mockito without live network or shared static state dependencies, and ensure every test executes assertions (`AstFacts.assertion_free_tests == 0`).
4. **Standard Package Mirror Layout**: Place unit tests under `src/test/java/` mirroring the `src/main/java/` package hierarchy (`*Test.java` / `*Tests.java`).

## Evaluation Thresholds
- **`PASS`**: Automated JUnit 5 suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, legacy JUnit 4 tests, or isolated assertion gaps.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free/network-coupled tests.
