# Code Quality Standards (OCaml)

## Core Principles
1. **Dune Strict Warnings, `ocamlformat` & `.mli` Interfaces**: Format with `ocamlformat` (`.ocamlformat` pinned), compile with Dune strict warnings (fatal warnings in dev profile), and provide explicit `.mli` interface files for public library modules to encapsulate abstract types (`AstFacts.unscoped_type_ignores == 0`).
2. **Zero `Obj.magic` & Partial Exception Traps**: Strictly forbid `Obj.magic` (unsound memory/segfault escape hatch; `AstFacts.dangerous_sinks`), avoid partial Stdlib functions (`List.hd`, `List.tl`, `Option.get`, `failwith` on recoverable errors; `AstFacts.bug_risk_idioms`), and never catch-all `with _ ->` swallowing `Out_of_memory` / `Sys.Break`.
3. **ODoc Documentation & Explicit Imports**: Document public `.mli` types and values with ODoc (`(** ... *)`; `AstFacts.docstring_coverage_pct`) and minimize top-level `open Module` namespace shadowing (prefer local `Module.(...)` or `let open Module in`; `AstFacts.wildcard_imports`).
4. **Immutable Pure Core & Zero Mutable `ref` Globals**: Avoid top-level mutable `ref` / `Hashtbl` global state (`AstFacts.global_state_usages`) and keep functions modular (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: Zero `Obj.magic`/partial-`List.hd`/top-level `ref` globals, `.mli` files with ODoc `>= 80%`, and minimal top-level `open` pollution.
- **`WARN`**: Missing `.mli` on internal helpers or isolated `open` / complexity warnings.
- **`FAIL`**: `Obj.magic` in business logic, pervasive `with _ ->` exception swallowing, or unguarded global mutable `ref`/`Hashtbl` state.
