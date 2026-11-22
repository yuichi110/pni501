# Testing Standards (Haskell)

## Core Principles
1. **Hspec / Tasty + Property-Based Testing**: Organize tests under `test/` (`*Spec.hs` / `*Test.hs`) wired to `cabal test` / `stack test`, combining Hspec/Tasty unit specs with QuickCheck or Hedgehog property tests for pure domain laws (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain expression/branch coverage of 80% or higher via HPC (`cabal test --enable-coverage`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Pure Logic Isolation & Deterministic IO**: Keep tests centered on pure functions and tagless-final / effect-system mocks so suites run offline without databases or live HTTP endpoints.
4. **Meaningful Assertions**: Every `it` / `testCase` / `property` block must assert concrete expectations (`shouldBe`, `shouldThrow`, `===`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Hspec/Tasty + property test suite exists, `assertion_free_tests == 0`, pure deterministic execution, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or unit-only tests without property tests on serializers/parsers.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
