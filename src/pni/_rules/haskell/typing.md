# Typing, Strictness & ADT Standards (Haskell)

## Core Principles
1. **Explicit Top-Level Type Signatures & Newtypes**: Provide explicit type signatures on all top-level bindings (`-Wmissing-signatures`), wrap domain primitives in `newtype` (`newtype UserId = UserId UUID`), and model states with sum-type ADTs so `-Wincomplete-patterns` proves totality (`AstFacts.type_safety_coverage_pct`).
2. **Strict Data Fields & Space-Leak Prevention**: Annotate record fields as strict (`!Field` or `StrictData`) and use `foldl'` (`Data.List.foldl'`) instead of lazy `foldl` to prevent thunk buildup and OOM space leaks (`AstFacts.bug_risk_idioms`).
3. **Avoid Partial Record Fields & `Dynamic` / `unsafeCoerce`**: Do not define record selectors on multi-constructor sum types (partial field access crashes at runtime); avoid `Data.Dynamic` and `unsafeCoerce` (`AstFacts.type_safety_issues`, `AstFacts.weak_type_usages`).
4. **Scoped GHC Pragmas**: Avoid `-fno-warn-all` or broad `{-# OPTIONS_GHC -w #-}` pragmas (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: Top-level signatures everywhere, strict record fields (`!`/`StrictData`), zero `unsafeCoerce` or partial sum-type selectors, and scoped pragmas.
- **`WARN`**: Missing `newtype` wrappers on domain IDs or occasional lazy `foldl`.
- **`FAIL`**: `{-# OPTIONS_GHC -w #-}`, `unsafeCoerce` type-system bypasses, or pervasive partial record selectors / thunk leaks.
