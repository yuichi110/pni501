# Testing Standards (Swift)

## Core Principles
1. **Swift Testing & XCTest Suites**: Organize tests under `Tests/<Target>Tests/` using Swift Testing (`@Test`, `#expect`, `#require`) or `XCTestCase` (`test*`, `XCTAssertEqual`, `XCTUnwrap`; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher via `swift test --enable-code-coverage` + `llvm-cov` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Async & Protocol Isolation**: Mock network/filesystem/clock boundaries behind `Sendable` protocols, avoid `Task.sleep` timing flakiness, and ensure full offline execution on Linux/macOS CI.
4. **Meaningful Assertions**: Every test must assert concrete expectations (`#expect`, `XCTAssert*`, `XCTAssertThrowsError`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Swift Testing / XCTest suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated timing-sensitive async tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
