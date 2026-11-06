# Typing & Generics Standards (Java)

## Core Principles
1. **Parameterized Generics**: Always specify type parameters on generic types (`List<String>`, `Map<String, Integer>`, `Optional<User>`). Never use raw types (`List`, `Map`, `Class`).
2. **Avoid `Object` & Unchecked Casts**: Avoid untyped `Object` parameters/returns and `@SuppressWarnings({"unchecked", "rawtypes"})` in domain APIs; model contracts via interfaces, bounded type parameters (`<T extends ...>`), or `sealed` hierarchies.
3. **Null Safety**: Return `Optional<T>` or empty collections instead of `null`, and validate non-null inputs explicitly (`Objects.requireNonNull` or `@Nullable`/`@NonNull` annotations).
4. **Explicit `@Override`**: Annotate every overridden or interface-implementing method with `@Override` so signature drift fails at compile time.
