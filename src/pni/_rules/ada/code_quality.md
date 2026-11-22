# Code Quality & High-Integrity Standards (Ada)

## Core Principles
1. **Contract-Based Programming & Strict GNAT Checks**: Express preconditions, postconditions, and invariants via Ada 2012/2022 aspects (`Pre =>`, `Post =>`, `Type_Invariant =>`), compile with `-gnatwa -gnatVa -gnatf`, format with `gnatpp`, and never disable runtime safety checks via `pragma Suppress (All_Checks)` (`AstFacts.unscoped_type_ignores == 0`).
2. **Isolate Unchecked Operations & Global Mutable State**: Confine `Ada.Unchecked_Conversion`, `Ada.Unchecked_Deallocation`, and `System.Address` overlays strictly to audited hardware/FFI packages (`AstFacts.dangerous_sinks`, `AstFacts.bug_risk_idioms`), and encapsulate mutable state inside `protected` objects or explicit private records rather than raw package globals (`AstFacts.global_state_usages`).
3. **Avoid Blanket `use` Clauses & Document `.ads` Specs**: Prefer qualified names (`Pkg.Proc`) or `use type` over broad `use Pkg;` clauses (`AstFacts.wildcard_imports`), and document every public `.ads` package specification, type, and subprogram with GNATdoc comments (`AstFacts.docstring_coverage_pct`).
4. **Explicit Exception Handling & Bounded Subprograms**: Never write silent `when others => null;` exception swallowers (`AstFacts.bug_risk_idioms`), and keep procedures concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `.ads` GNATdoc coverage `>= 80%`, zero `pragma Suppress (All_Checks)` / silent `when others => null` / unaudited `Unchecked_Conversion`, and minimal broad `use` clauses.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated `use` clauses / subprogram complexity.
- **`FAIL`**: `pragma Suppress (All_Checks)`, silent `when others => null`, unguarded shared task variables without `protected`, or pervasive `Unchecked_Conversion`.
