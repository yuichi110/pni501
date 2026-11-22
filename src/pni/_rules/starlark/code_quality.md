# Code Quality & Hermetic Build Standards (Starlark / Bazel)

## Core Principles
1. **`buildifier` Formatting & Lint Cleanliness**: Format and lint every `BUILD.bazel`, `MODULE.bazel`, and `*.bzl` file with `buildifier --mode=check --lint=warn` (zero `unused-variable`, `load-on-top`, or `native-package` warnings; `AstFacts.unscoped_type_ignores == 0`).
2. **Hermetic Actions (`ctx.actions.run` Over `run_shell`)**: In custom rules (`*.bzl`), invoke binaries via `ctx.actions.run` with structured `ctx.actions.args()` rather than `ctx.actions.run_shell` with string interpolation (prevents shell injection CWE-78 and improves cross-platform portability; `AstFacts.dangerous_sinks`), and never depend on host `PATH` or ambient environment variables.
3. **Fine-Grained Targets, Explicit `visibility` & Zero `glob(["**"])` Bloat**: Keep `BUILD` targets small and cohesive (one library per package/concern), restrict `visibility` to exact consumer package groups instead of blanket `//visibility:public` on internal targets, and avoid greedy `glob(["**"])` pulling unrelated files into cache keys (`AstFacts.bug_risk_idioms`).
4. **Stardoc Documentation & `depset` Performance**: Document public rules, providers, and macros with Stardoc docstrings (`doc = "..."` on rule/attr definitions and `"""..."""` on macros; `AstFacts.docstring_coverage_pct`), and NEVER call `.to_list()` on transitive `depset`s during analysis phase (O(N^2) memory blowup!).

## Evaluation Thresholds
- **`PASS`**: `buildifier` clean, explicit `visibility`, `ctx.actions.run` + `depset` discipline, zero greedy `glob(["**"])`, and Stardoc `doc=` on public rules/attrs.
- **`WARN`**: Missing `doc = "..."` on internal helper attrs or overly broad `visibility`.
- **`FAIL`**: `run_shell` string-interpolated command injection, analysis-phase `depset.to_list()` blowups, or non-hermetic host-filesystem assumptions.
