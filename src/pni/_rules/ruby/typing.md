# Typing, Signatures & Contract Standards (Ruby)

## Core Principles
1. **Explicit Type Contracts (RBS / Sorbet / YARD)**: Because Ruby is dynamically typed, do **not** penalize pure idiomatic Ruby for lacking inline syntax annotations unless Sorbet/RBS is configured; evaluate contract clarity via RBS (`sig/*.rbs`), Sorbet (`sig { ... }`, `# typed: strict`), or complete YARD `@param`/`@return` tags (`AstFacts.docstring_coverage_pct`, `AstFacts.type_safety_coverage_pct`).
2. **Avoid `T.untyped` & `T.unsafe` Escape Hatches (Sorbet Projects)**: In Sorbet-typed repos, minimize `T.untyped`, `T.unsafe`, and `# typed: ignore` overrides (`AstFacts.weak_type_usages`, `AstFacts.unscoped_type_ignores`).
3. **Strict Keyword Arguments & Value Objects**: Prefer explicit keyword arguments (`def create(user:, amount:)`) and `Data.define` / `Struct` value objects over untyped `options = {}` hash bags (`AstFacts.excessive_parameters`).
4. **Defensive Nil & Boundary Handling**: Guard `nil` transitions explicitly via `&.`, `fetch`, or domain Result objects rather than relying on implicit `nil` coercion or `NoMethodError`.

## Evaluation Thresholds
- **`PASS`**: Clear public contracts (RBS/Sorbet or YARD), keyword arguments over opaque hashes, and minimal `T.untyped`/`# typed: ignore` when Sorbet is enabled.
- **`WARN`**: Partial YARD/RBS coverage or isolated `options = {}` hash-bag APIs.
- **`FAIL`**: Undocumented public APIs combined with pervasive `T.unsafe`/`# typed: ignore` or runtime `NoMethodError` boundary hazards.
