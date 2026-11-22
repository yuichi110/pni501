# Code Quality Standards (Julia)

## Core Principles
1. **JuliaFormatter, Zero Non-`const` Globals & Performance Hygiene**: Format with `JuliaFormatter.jl` (`BlueStyle` / `SciMLStyle`), forbid untyped mutable global variables (`AstFacts.global_state_usages` — catastrophic for both thread safety and JIT type stability; use `const` or pass structs), and avoid `@inbounds` without explicit bounds invariants (`AstFacts.bug_risk_idioms`).
2. **Eliminate Dynamic Code & Command Injection Sinks**: Never pass untrusted input into `eval(Meta.parse(...))` (CWE-94) or `run(\`sh -c $cmd\`)` (CWE-78; note Julia's native `Cmd` backtick interpolation `run(\`ls $arg\`)` escapes arguments safely without a shell, so only `sh -c` / `bash -c` or `eval` are injection sinks; `AstFacts.dangerous_sinks`).
3. **Docstrings & Clean Namespaces**: Document exported modules, structs, and functions with `"""..."""` Markdown docstrings (`AstFacts.docstring_coverage_pct`), prefer explicit `import Pkg: sym` or `using Pkg: sym` over bare `using` pollution (`AstFacts.wildcard_imports`), and avoid type piracy (extending foreign functions on foreign types).
4. **Cohesive Functions & Resource Cleanup**: Close files/sockets deterministically with `open(...) do io ... end` and decompose long numerical kernels (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero non-`const` mutable globals, zero `eval(Meta.parse())`/type-piracy/unbounded `@inbounds` bugs, and clean `do`-block resource cleanup.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated bare `using` / complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, `eval(Meta.parse())` RCE sinks, pervasive non-`const` globals, or broken type piracy.
