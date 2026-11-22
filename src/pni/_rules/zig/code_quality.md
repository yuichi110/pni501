# Code Quality Standards (Zig)

## Core Principles
1. **Explicit Allocators, `defer` & `errdefer` Ownership**: Pass `std.mem.Allocator` explicitly into every allocating function (never hide global allocators) and pair every allocation/handle immediately with `defer` or `errdefer` so zero memory leaks occur on error paths (`AstFacts.bug_risk_idioms`).
2. **Zero Production `catch unreachable` / `orelse unreachable`**: Never discard errors via `catch unreachable`, `catch {}`, or `.?` optional force-unwraps on fallible runtime/I/O paths (`AstFacts.bug_risk_idioms`); propagate structured error unions with `try`.
3. **Formatting, Doc Comments & Zero Mutable Globals**: Format all code with `zig fmt`, document public declarations with `///` doc comments (`AstFacts.docstring_coverage_pct`), avoid mutable top-level `var` globals (`AstFacts.global_state_usages`), and keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).
4. **Scoped `@setRuntimeSafety(false)`**: Never disable runtime bounds/overflow safety checks (`@setRuntimeSafety(false)`) outside benchmark-verified inner loops with documented invariants (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, explicit `Allocator` + `defer`/`errdefer` hygiene, zero production `catch unreachable`/`.?` panics, and zero unguarded mutable globals.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, leaked allocations missing `errdefer`, pervasive `catch unreachable`, or unjustified `@setRuntimeSafety(false)`.
