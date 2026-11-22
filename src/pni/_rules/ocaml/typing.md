# Typing, Abstract Interfaces & Exhaustive ADT Standards (OCaml)

## Core Principles
1. **Abstract Types in `.mli` & Variant Exhaustiveness**: Expose domain invariants as abstract types in `.mli` (`type t`) with smart constructors returning `('a, err) result`, and use closed algebraic variants so warning 8 proves pattern-match exhaustiveness without catch-all `| _ ->` hiding new cases (`AstFacts.type_safety_coverage_pct`).
2. **Avoid Polymorphic Comparison (`=` / `compare`) on Abstract/Function Values**: Prefer type-specific equality (`Int.equal`, `String.equal`, `[@@deriving eq, ord]`) over polymorphic structural `=` (which raises `Invalid_argument` on functions and breaks abstract invariants).
3. **Zero `Obj.magic` / `Obj.repr` Escape Hatches**: Never bypass the OCaml type system with `Obj.*` (`AstFacts.type_safety_issues`, `AstFacts.weak_type_usages`).
4. **Scoped Warning Attributes**: Never disable exhaustiveness warnings (`[@@warning "-8"]`) across modules (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: Abstract `.mli` invariants, exhaustive variant matching, type-specific equality, and zero `Obj.magic` or `[@@warning "-8"]` abuse.
- **`WARN`**: Occasional polymorphic `=` on records or missing `.mli` signatures on library modules.
- **`FAIL`**: `Obj.magic` casts, disabled exhaustiveness warnings, or untyped stringly-encoded domain states.
