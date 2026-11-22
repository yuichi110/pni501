# Typing, Null Safety & Algebraic Data Standards (Kotlin)

## Core Principles
1. **First-Class Null Safety**: Leverage Kotlin's nullable type system (`?.`, `?:`, `let`, `requireNotNull`) and explicitly annotate Java platform types (`T!`) at interop boundaries instead of using `!!` (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Sealed Hierarchies & Inline Value Classes**: Model domain states and typed errors with `sealed interface` / `sealed class`, `data class`, and `@JvmInline value class` rather than raw `Any`, unchecked `as` casts, or stringly-typed flags (`AstFacts.weak_type_usages`).
3. **Explicit Public Return Types**: Declare explicit return types on public functions and properties (especially single-expression functions) so binary and source API contracts remain stable.
4. **Scoped Suppressions**: Never use broad `@Suppress("UNCHECKED_CAST")` without validating invariants or blanketing whole files (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 95%`, `unscoped_type_ignores == 0`, zero unchecked `Any`/`as` abuse or pervasive `!!` assertions.
- **`WARN`**: Isolated unchecked casts at Java/serialization boundaries or missing explicit return types on public helpers.
- **`FAIL`**: Pervasive `!!`, `Any` domain models, or file-wide `@Suppress` bypassing type checks.
