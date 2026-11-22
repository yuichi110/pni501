# Typing, Nullability & Lightweight Generics Standards (Objective-C)

## Core Principles
1. **Nullability Audits (`NS_ASSUME_NONNULL_BEGIN/END`)**: Annotate all public `.h` headers with `NS_ASSUME_NONNULL_BEGIN` / `NS_ASSUME_NONNULL_END` and explicit `nullable` / `nonnull` qualifiers so both Clang static analyzer and Swift interop enforce null contracts (`AstFacts.type_safety_coverage_pct`).
2. **Lightweight Generics & `instancetype`**: Parameterize `NSArray<Item *> *`, `NSDictionary<NSString *, Value *> *`, and `NSSet<T> *` instead of raw untyped collections, return `instancetype` instead of `id` from `init*` and factory methods, and avoid raw `id` outside generic protocol delegates (`id<MyDelegate>`; `AstFacts.weak_type_usages`).
3. **Typed Enums (`NS_ENUM` / `NS_OPTIONS`)**: Declare enums with `NS_ENUM(NSInteger, ...)` and bitmasks with `NS_OPTIONS(NSUInteger, ...)` rather than bare C `enum` or `#define` integer constants.
4. **Scoped Warning Hygiene**: Avoid `#pragma clang diagnostic ignored` without matching `push`/`pop` and explicit rationale (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: Nullability macros + lightweight generics + `instancetype` + `NS_ENUM` across public headers, with minimal raw `id`.
- **`WARN`**: Partial nullability or raw `NSArray *` in internal implementation files.
- **`FAIL`**: Unaudited public headers returning raw `id` everywhere, unsafe `void *` / `__bridge_transfer` casts, or global diagnostic suppressions.
