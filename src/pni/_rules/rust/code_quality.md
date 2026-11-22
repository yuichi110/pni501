# Code Quality Standards (Rust)

## Core Principles
1. **Rustfmt & Clippy Cleanliness**: Format all crates with `cargo fmt` and enforce `cargo clippy --all-targets -- -D warnings` with explicit, narrow `#[allow(...)]` attributes accompanied by inline rationale (`AstFacts.unscoped_type_ignores == 0`, `AstFacts.import_hygiene_coverage_pct`).
2. **Rustdoc Coverage**: Document all public crates (`//!`), modules, structs, enums, traits, and functions with `///` doc comments (including `# Errors`, `# Panics`, and `# Safety` sections where applicable; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Zero Unchecked Panics in Production Paths**: Never call `.unwrap()`, `.expect(...)`, `panic!()`, `todo!()`, or `unimplemented!()` in library code or request/runtime handlers (`AstFacts.bug_risk_idioms`); propagate structured errors with `?`, `thiserror`, or `anyhow`. (Note: `.unwrap()` / `.expect()` inside `#[cfg(test)]` modules or `tests/` is idiomatic and NOT a defect.)
4. **Strict `unsafe` & Global State Isolation**: Minimize `unsafe` blocks and require a `// SAFETY:` invariant comment immediately above every `unsafe` block (`AstFacts.bug_risk_idioms`). Forbid `static mut` (`AstFacts.global_state_usages`); use `OnceLock` / `LazyLock`, `Atomic*`, or explicit dependency injection instead.
5. **Explicit Imports & Bounded Complexity**: Avoid wildcard glob imports (`use foo::*;`, except standard `prelude::*` modules; `AstFacts.wildcard_imports`) and keep functions modular (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero production `.unwrap()`/`static mut`, every `unsafe` block justified with `// SAFETY:`, and zero unscoped `#[allow(...)]`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity / wildcard-import warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, `static mut` races, undocumented `unsafe` blocks, or pervasive `.unwrap()` panics in library/service code.
