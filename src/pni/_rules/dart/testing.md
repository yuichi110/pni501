# Testing Standards (Dart)

## Core Principles
1. **Unit, Widget & Integration Tests**: Organize tests under `test/**/*_test.dart` mirroring `lib/` using `package:test` (`dart test`) or `package:flutter_test` (`testWidgets`; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher (`dart test --coverage=coverage` / `flutter test --coverage` LCOV; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Mock HTTP/storage/platform channels cleanly (`mocktail` / `mockito` / `http.MockClient`), avoid `Future.delayed` flakiness (use `fake_async` / `tester.pump`), and ensure offline execution.
4. **Meaningful Assertions**: Every `test()` / `testWidgets()` must verify concrete expectations via `expect(...)`, `throwsA(...)`, or `verify(...)` (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `*_test.dart` suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated timing-sensitive widget/async tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / live-network tests.
