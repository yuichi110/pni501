# Testing Standards (Rust)

## Core Principles
1. **Unit, Integration & Doctests**: Combine co-located unit tests (`#[cfg(test)] mod tests`) with black-box integration tests under `tests/` (`AstFacts.test_functions_count`), and keep `///` rustdoc code examples compilable via `cargo test --doc`.
2. **Coverage Target**: Maintain line coverage of 80% or higher (`cargo llvm-cov` / `cargo tarpaulin`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`) across core crates.
3. **Deterministic Async & Property Testing**: Isolate network/filesystem/clock I/O behind traits (`#[tokio::test]` with mocked adapters, `tempfile::TempDir`), and use `proptest` / `quickcheck` for parsers and serialization boundaries.
4. **Meaningful Assertions**: Every `#[test]` / `#[tokio::test]` must verify concrete behavior via `assert_eq!`, `assert!`, `matches!`, or `#[should_panic(expected = "...")]` (`AstFacts.assertion_free_tests == 0`) — never rely solely on `#[should_panic]` without `expected = ...`.

## Evaluation Thresholds
- **`PASS`**: Automated unit/integration tests exist, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing error-path / doctest coverage.
- **`FAIL`**: No automated tests (`test_files_count == 0` and zero `#[test]` functions), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
