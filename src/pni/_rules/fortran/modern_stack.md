# Modern Fortran (2008 / 2018 / 2023) & HPC Idioms (`fortran/modern_stack`)

## Core Principles
1. **Modern Fortran 2008/2018 Constructs**: Replace obsolete Fortran 77 features (fixed-form `.f`, arithmetic `IF`, `DO 10 ... 10 CONTINUE`, `ENTRY`, `PAUSE`) with free-form `do ... end do`, `do concurrent`, `block ... end block`, `associate`, `submodule`, and `error stop` (`AstFacts.modernization_hints`).
2. **Safe File Units (`newunit=`)**: Always use `open(newunit=u, file=..., status=..., iostat=ios)` instead of hardcoded integer unit numbers (`open(10, ...)`, which collide across modules; `AstFacts.bug_risk_idioms`).
3. **Memory-Layout & Vectorization Hygiene**: Traverse multi-dimensional arrays in column-major order (innermost loop over first index) and use array intrinsics (`matmul`, `dot_product`, `sum`) cleanly.
4. **Structured I/O & Safe System Calls**: Avoid passing unsanitized strings to `execute_command_line` (CWE-78; `AstFacts.dangerous_sinks`) and route diagnostics cleanly to `error_unit` (`iso_fortran_env`).
