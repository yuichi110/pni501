# Typing, Casts, Ownership & Const-Correctness Standards (C++)

## Core Principles
1. **Named C++ Casts Over C-Style Casts**: Replace C-style casts `(T)x` and unsafe `reinterpret_cast` / `const_cast` with explicit `static_cast` / `std::bit_cast` (`AstFacts.type_safety_issues`, `AstFacts.weak_type_usages`).
2. **Value Types, Views & Strong Enums**: Prefer `enum class` over unscoped `enum`, `std::string_view` / `std::span<const T>` over raw `(const T*, size_t)` pairs, `std::optional<T>` / `std::expected<T, E>` over sentinel error values, and `explicit` single-argument constructors.
3. **`const` & `noexcept` Correctness**: Mark non-mutating member functions `const`, use `constexpr` for compile-time constants instead of `#define` macros, and annotate move constructors/assignments `noexcept`.
4. **Avoid `void *` & Unbounded Varargs**: Replace `void *` type erasure and C `...` varargs with templates, concepts (`C++20`), or `std::variant` (`AstFacts.type_safety_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: `enum class`, `const`-correctness, named casts, `std::span`/`std::optional`, and zero unjustified `reinterpret_cast`/`void *` in domain logic.
- **`WARN`**: Isolated C-style casts or missing `explicit`/`const` qualifiers.
- **`FAIL`**: Pervasive C-style / `reinterpret_cast` UB, raw `void *` business logic, or macro-based untyped APIs.
