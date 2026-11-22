# Typing, Typespecs & Dialyzer Standards (Elixir)

## Core Principles
1. **Typespecs (`@type`, `@opaque`, `@spec`) & Dialyzer**: Because Elixir is dynamically typed (with gradual set-theoretic typing emerging in 1.17+), evaluate contract rigor via `@type`/`@spec` coverage on public module boundaries and `dialyxir` (`mix dialyzer`) cleanliness rather than penalizing idiomatic Elixir for lacking inline static type syntax (`AstFacts.type_safety_coverage_pct`).
2. **Structs & Behaviours Over Raw Maps**: Model domain entities with `defstruct` (using `@enforce_keys`) and polymorphism with `@behaviour` / `@callback` or `defprotocol` instead of untyped raw maps with dynamic string keys.
3. **Avoid Overly Broad `any()` / `term()` Specs**: Narrow public `@spec` return types to explicit tagged unions (`{:ok, User.t()} | {:error, Ecto.Changeset.t()}`) instead of `any()` (`AstFacts.weak_type_usages`).
4. **Scoped Dialyzer Ignores**: Minimize `@dialyzer {:nowarn_function, ...}` directives and document why each is required (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: Public APIs carry `@type`/`@spec` contracts and `defstruct`/`@behaviour` boundaries, with minimal `any()` or `@dialyzer` ignores.
- **`WARN`**: Partial `@spec` coverage on public functions or isolated untyped map bags.
- **`FAIL`**: Missing `@spec`/`defstruct` on complex domain APIs combined with pervasive `@dialyzer` suppression or contract mismatches.
