# Code Quality Standards (Odin)

## Core Principles
1. **Explicit Allocator Ownership & `defer` Cleanup**: Accept `allocator := context.allocator` on allocating procedures, pair every `make` / `new` / `os.open` with `defer delete(...)` / `defer free(...)` / `defer os.close(...)`, and clear `context.temp_allocator` explicitly (`free_all(context.temp_allocator)`) at frame or request boundaries (`AstFacts.bug_risk_idioms`).
2. **Checked Multiple Return Values (`or_return` / `ok`)**: Never silently discard error/boolean return values (`val, _ := ...`) or call `panic(...)` / `assert(...)` for recoverable runtime/I/O failures in libraries (`AstFacts.bug_risk_idioms`); propagate cleanly via `(T, Error)` + `or_return` or `or_else`.
3. **Strict Compiler Vet Flags & Doc Comments**: Compile with `-vet -strict-style` (`odin check -vet`) to catch unused variables/imports and shadowing, document public packages/structs/procs with `//` doc comments (`AstFacts.docstring_coverage_pct`), and avoid mutable package-level globals (`AstFacts.global_state_usages`).
4. **Zero `#no_bounds_check` Abuse & Bounded Procedures**: Confine `#no_bounds_check` strictly to benchmark-verified hot loops with explicit length proofs (`AstFacts.unscoped_type_ignores == 0`), and keep procedures modular (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, `allocator` + `defer` ownership hygiene, checked `(val, ok)`/`or_return` error paths, zero unguarded package globals, and `-vet` cleanliness.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity warnings.
- **`FAIL`**: Ignored allocation/I/O error returns, leaked heap allocations missing `defer`, pervasive `panic()` in libraries, or unjustified `#no_bounds_check`.
