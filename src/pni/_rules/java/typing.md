# Typing & Generics Standards (Java)

## Core Principles
1. **Parameterized Generics**: Always specify type parameters on generic types (`List<String>`, `Map<String, Integer>`, `Optional<User>`). Never use raw types (`List`, `Map`, `Class`; `AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Avoid `Object` & Unchecked Casts**: Avoid untyped `Object` parameters/returns (`AstFacts.weak_type_usages`) and `@SuppressWarnings({"unchecked", "rawtypes"})` (`AstFacts.unscoped_type_ignores`) in domain APIs; model contracts via interfaces, bounded type parameters (`<T extends ...>`), or `sealed` hierarchies.
3. **Null Safety**: Return `Optional<T>` or empty collections instead of `null`, and validate non-null inputs explicitly (`Objects.requireNonNull` or `@Nullable`/`@NonNull` annotations).
4. **Explicit `@Override`**: Annotate every overridden or interface-implementing method with `@Override` so signature drift fails at compile time.

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 90%`, zero raw generic types, and `unscoped_type_ignores == 0`.
- **`WARN`**: `type_safety_coverage_pct` between `70%` and `89.9%`, or isolated `Object` / `@SuppressWarnings` usages.
- **`FAIL`**: `type_safety_coverage_pct < 70%` or pervasive raw generics / unchecked casts in domain models.
