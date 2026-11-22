# Typing, Nullability & Generics Standards (C#)

## Core Principles
1. **Nullable Reference Types Enabled**: Enable `<Nullable>enable</Nullable>` in `.csproj` or `Directory.Build.props` and eliminate unchecked null-forgiving operators (`!`) and unvalidated dereferences (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Avoid `dynamic` & Untyped `object`**: Prefer strongly typed generics, `record` DTOs, `IReadOnlyList<T>`, and discriminated patterns over `dynamic`, non-generic `ArrayList`/`Hashtable`, or raw `object` casting (`AstFacts.weak_type_usages`).
3. **Explicit Contracts on Public APIs**: Avoid exposing `var`-inferred anonymous types or mutable concrete collections (`List<T>`) across public boundaries; expose narrow interfaces (`IReadOnlyCollection<T>`, `IEnumerable<T>`).
4. **Scoped Suppression Hygiene**: Avoid bare `#pragma warning disable` without warning IDs or `[SuppressMessage]` without justification (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `<Nullable>enable</Nullable>`, `type_safety_coverage_pct >= 90%`, `unscoped_type_ignores == 0`, and zero `dynamic` / non-generic legacy collections in business logic.
- **`WARN`**: `type_safety_coverage_pct` between `75%` and `89.9%`, or isolated null-forgiving `!` usages.
- **`FAIL`**: Nullable reference types disabled on .NET 6+ projects, pervasive `dynamic`/`object` casting, or unscoped compiler warning suppression.
