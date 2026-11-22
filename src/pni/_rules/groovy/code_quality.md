# Code Quality Standards (Groovy)

## Core Principles
1. **CodeNarc & Explicit Imports**: Lint Groovy sources with `CodeNarc`, eliminate wildcard imports (`import foo.*`; `AstFacts.wildcard_imports`), and avoid unscoped `@SuppressWarnings` (`AstFacts.unscoped_type_ignores == 0`).
2. **Eliminate Dynamic Code Execution & GString Injection**: Never pass untrusted input into `Eval.me`, `GroovyShell.evaluate`, `String.execute()` (CWE-78/CWE-94), or interpolated GString SQL (`sql.rows("SELECT ... ${x}")` — note Groovy `Sql` handles GStrings safely only when NOT converted via `.toString()` or string `+`; `AstFacts.dangerous_sinks`).
3. **Groovydoc & Clean Jenkins/DSL Separation**: Document public classes, methods, and Jenkins Shared Library `vars/*.groovy` entrypoints with Groovydoc (`/** ... */`; `AstFacts.docstring_coverage_pct`), and keep business logic out of monolithic build/pipeline scripts (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).
4. **Zero Mutable Static State & Clean Error Handling**: Avoid mutable `static` globals (`AstFacts.global_state_usages`) and empty `catch (Exception e) {}` blocks (`AstFacts.bug_risk_idioms`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero `Eval.me`/`GroovyShell`/`String.execute()` injection sinks, zero empty catches or mutable static globals, and clean CodeNarc hygiene.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated dynamic script complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, RCE sinks (`Eval.me`/`GroovyShell`/shell exec on user input), or unguarded mutable static state.
