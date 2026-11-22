# Code Quality Standards (Fortran)

## Core Principles
1. **Mandatory `implicit none` & Modern Free-Form Modules**: Begin every `program`, `module`, and `submodule` with `implicit none` (forbids silent I–N integer typing bugs; `AstFacts.bug_risk_idioms`), use free-form `.f90`+ modules with `private` default + explicit `public` exports, and format cleanly with `fprettify`.
2. **Eliminate Legacy `COMMON`, `EQUIVALENCE`, `GOTO` & Implicit `SAVE`**: Replace `COMMON` blocks and `EQUIVALENCE` memory aliasing with encapsulated `module` derived types passed as explicit arguments (`AstFacts.global_state_usages`). Note Fortran's subtle trap: initializing a local variable in its declaration (`integer :: x = 0`) implies `SAVE` (persistent global state across calls!) — assign on a separate executable line unless `SAVE` is explicitly intended.
3. **Explicit `intent` & `pure` Procedures**: Declare `intent(in)`, `intent(out)`, or `intent(inout)` on every dummy argument, mark side-effect-free numerical functions `pure` / `elemental`, and use explicit `only:` imports (`use my_mod, only: fn`; `AstFacts.wildcard_imports`).
4. **FORD Documentation & Bounded Subroutines**: Document modules and procedures with FORD (`!> ...`) comments (`AstFacts.docstring_coverage_pct`) and decompose sprawling numerical routines (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `implicit none` everywhere, zero `COMMON`/`EQUIVALENCE`/spaghetti `GOTO`, explicit `intent(...)` & `use ..., only:`, and documented modules.
- **`WARN`**: Missing `only:` clauses on `use` statements, missing FORD docs on helper routines, or oversized numerical procedures.
- **`FAIL`**: Missing `implicit none`, `COMMON` / `EQUIVALENCE` global memory aliasing, accidental implicit `SAVE` bugs, or unguarded `GOTO` spaghetti.
