# Typing, Ownership, Traits & Error Type Standards (Rust)

## Core Principles
1. **Type-Driven State Modeling (Make Invalid States Unrepresentable)**: Model domain invariants using `enum` ADTs, newtype wrappers (`struct UserId(Uuid)`), and `NonZero*` types rather than primitive strings/integers or boolean flag tuples (`AstFacts.excessive_parameters`).
2. **Rich Domain Errors Over Stringly-Typed Failures**: Return concrete `Result<T, E>` error enums (e.g., via `thiserror`) from library APIs rather than `Result<T, String>` or `Box<dyn std::error::Error>` (`AstFacts.type_safety_coverage_pct`, `AstFacts.weak_type_usages`).
3. **Sound Lifetimes, Ownership & `Send + Sync`**: Prefer borrowing (`&str`, `&[T]`, `Cow<'_, str>`) over gratuitous `.clone()` on hot paths, avoid `std::mem::transmute` or raw pointer casts unless isolated in an audited FFI boundary (`AstFacts.type_safety_issues`), and avoid holding `std::sync::MutexGuard` across `.await` points.
4. **Scoped Lint & Warning Overrides**: Never suppress compiler or Clippy safety diagnostics crate-wide (`#![allow(warnings)]`, `#![allow(clippy::all)]`; `AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 95%`, `unscoped_type_ignores == 0`, structured `Result<T, E>` error types, and zero unjustified raw pointer / `transmute` casts.
- **`WARN`**: Isolated `Box<dyn Error>` / `String` error returns in internal helpers or minor `#[allow(...)]` scope gaps.
- **`FAIL`**: Crate-wide warning suppression (`#![allow(warnings)]`), unsound `unsafe` casts/transmutes, or `std::sync::Mutex` held across `.await`.
