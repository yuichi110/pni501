# Testing Standards (Groovy)

## Core Principles
1. **Spock Specifications (`*Spec.groovy`) & JUnit 5**: Organize tests under `src/test/groovy` mirroring `src/main/groovy` using Spock (`given:` / `when:` / `then:` / `where:` data tables; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line/branch coverage of 80% or higher via JaCoCo (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Use Spock `Mock()`/`Stub()` (or `JenkinsPipelineUnit` for Jenkins Shared Libraries) to isolate external services and filesystem state so tests run offline.
4. **Meaningful Assertions**: Every Spock feature method must contain concrete `then:` / `expect:` / `thrown(...)` verifications (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Spock/JUnit suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `where:` boundary test cases.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
