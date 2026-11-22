# Rule Analysis & Build-Test Standards (Starlark / Bazel)

## Core Principles
1. **`rules_testing` (`analysis_test`) & `bazel-skylib` `unittest`**: Test custom `.bzl` rules and macros under `tests/` using `rules_testing` (`analysis_test`, `truth` matchers verifying actions, argv, providers, and `expect_failure = True` error cases) and `build_test` (`AstFacts.test_functions_count`).
2. **Hermetic & Offline Execution (`--sandbox_default_allow_network=false`)**: Ensure `bazel test //...` passes inside sandboxes with zero network access and zero reliance on host environment variables.
3. **Lint & Format CI Gates**: Run `buildifier --mode=check --lint=warn` in CI alongside `bazel test //...`.
4. **Meaningful Assertions**: Every `analysis_test` must assert concrete action commands, outputs, or expected failure messages (`env.expect.that_target(...).action_named(...)`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `rules_testing` / `skylib` analysis tests + `buildifier` lint gates + hermetic `bazel test //...`.
- **`WARN`**: Only `build_test` smoke targets exist without `analysis_test` assertions on custom `.bzl` rules.
- **`FAIL`**: Custom `.bzl` rules with zero tests (`test_files_count == 0`) or non-hermetic flaky build tests.
