# Typing, `@CompileStatic` & Null Safety Standards (Groovy)

## Core Principles
1. **`@CompileStatic` / `@TypeChecked` for Production Classes**: Annotate production domain and service classes (`src/main/groovy`) with `@CompileStatic` (or `@TypeChecked`) so missing methods and type mismatches fail at compile time rather than runtime (`AstFacts.type_safety_coverage_pct`). (Note: Gradle DSL / Spock specs / Jenkins `vars/*.groovy` legitimately remain dynamic and must **NOT** be penalized.)
2. **Explicit Types Over `def` on Public APIs**: Replace untyped `def` parameters and return types on public methods with explicit concrete/generic types (`AstFacts.weak_type_usages`).
3. **Safe Navigation & Elvis Discipline**: Use `?.` and `?:` intentionally and avoid unvalidated `as` runtime coercions on untrusted maps/JSON.
4. **Scoped Type-Check Exclusions**: Use `@CompileStatic(TypeCheckingMode.SKIP)` only on isolated dynamic builder methods rather than disabling static checking across whole modules (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `@CompileStatic` and explicit parameter/return types across `src/main/groovy`, with minimal untyped `def` outside DSL/Spock code.
- **`WARN`**: Mixed `def` and explicit types in production helpers.
- **`FAIL`**: Pervasive untyped `def` / `Object` domain APIs with runtime `MissingMethodException` hazards.
