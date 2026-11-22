# Typing, Declarations, CLOS & Condition Standards (Common Lisp)

## Core Principles
1. **Dynamic Typing Exemption & Runtime `check-type` / `etypecase`**: Common Lisp is dynamically (and strongly) typed — do **NOT** penalize idiomatic Lisp for omitting static type annotations on every parameter. Evaluate contract rigor via `check-type`, `etypecase`/`ecase` (signaling `type-error` on unexpected variants instead of silent `nil`), typed CLOS slots (`:type`), and optional `(declare (type ...))` / `declaim (ftype ...)` declarations.
2. **Never Lower Safety Blindly (`(optimize (safety 0))`)**: Forbid `(declare (optimize (speed 3) (safety 0)))` in general code (disables bounds/type checks and introduces memory corruption UB in SBCL; `AstFacts.unscoped_type_ignores`, `AstFacts.type_safety_issues`) unless isolated in a benchmarked, bounds-proven inner kernel.
3. **Structured Conditions & Restarts**: Define domain condition hierarchies via `define-condition` instead of signaling bare `error` strings, and handle specific conditions with `handler-case` / `handler-bind` rather than swallowing all `serious-condition`s (`AstFacts.bug_risk_idioms`).
4. **Structured Data (`defstruct` / `defclass`) Over Deep Nested Lists**: Model complex domain records with `defstruct` (with `:type` slots) or CLOS `defclass` rather than fragile `cadddr` positional list destructuring.

## Evaluation Thresholds
- **`PASS`**: `check-type`/`etypecase` boundary contracts, typed CLOS/struct models, custom `define-condition` errors, and safe compiler `(optimize (safety ...))` settings.
- **`WARN`**: Positional `caddr` list access on internal helpers or missing `etypecase` exhaustiveness checks.
- **`FAIL`**: Blanket `(optimize (safety 0))` in application code or silent swallowing of `serious-condition` / `error`.
