# Testing Standards (Objective-C)

## Core Principles
1. **XCTest Suites (`*Tests.m`)**: Organize unit tests in dedicated test targets (`Tests/*Tests.m`) subclassing `XCTestCase` (`test*` methods; `AstFacts.test_functions_count`).
2. **Coverage & Sanitizers**: Maintain `>= 80%` line coverage via Xcode/LLVM coverage (`RuntimeFacts.coverage.line_coverage_pct`) and run test targets with AddressSanitizer (`ASan`) and ThreadSanitizer (`TSan`) in CI.
3. **Deterministic Isolation**: Inject protocol-backed fakes (`id<NetworkClient>`) or `NSURLProtocol` stubs rather than hitting live servers, avoid `sleep()` timing flakiness (use `XCTestExpectation`), and isolate `NSUserDefaults` / temporary directories.
4. **Meaningful Assertions**: Every test method must verify concrete outcomes via `XCTAssertEqualObjects`, `XCTAssertNil`, `XCTAssertTrue`, and `NSError` inspection (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated XCTest suite exists, `assertion_free_tests == 0`, protocol-stub isolation, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated timing-sensitive async expectations.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
