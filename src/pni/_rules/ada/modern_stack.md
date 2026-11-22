# Modern Ada (2012 / 2022) & SPARK Idioms (`ada/modern_stack`)

## Core Principles
1. **Ada 2012/2022 Expressiveness**: Prefer expression functions, `if`/`case` expressions, `for Elem of Container` iterators, `@` target-name shorthand, `Pre`/`Post`/`Static_Predicate`/`Dynamic_Predicate` aspects, and standard `Ada.Containers` over hand-rolled linked lists (`AstFacts.modernization_hints`).
2. **Tasking & Ravenscar / Jorvik Safety**: Synchronize concurrent tasks via `protected` types and deterministic Ravenscar/Jorvik profiles rather than ad-hoc shared variables or unbounded dynamic task creation (`AstFacts.bug_risk_idioms`).
3. **Safe String & Buffer Handling**: Prefer bounded strings (`Ada.Strings.Bounded`) or `Ada.Strings.Unbounded` over fixed-length `String` slicing bugs, and avoid C `strcpy`/`system` calls via `Interfaces.C` (`AstFacts.dangerous_sinks`).
4. **Clean Diagnostics**: Route operational diagnostics to structured logging or `Ada.Text_IO.Standard_Error` rather than raw `Put_Line` inside library packages (`AstFacts.unstructured_logging`).
