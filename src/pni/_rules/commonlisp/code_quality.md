# Code Quality Standards (Common Lisp)

## Core Principles
1. **Disable `*read-eval*` on Untrusted Input & Ban Dynamic `eval`**: ALWAYS bind `(*read-eval* nil)` (or use `with-standard-io-syntax` + `(*read-eval* nil)`) before calling `read` / `read-from-string` on external input (`#.` reader-macro RCE; CWE-94), and forbid runtime `eval` / unsanitized `uiop:run-program` shell strings (CWE-78; `AstFacts.dangerous_sinks`).
2. **Explicit `defpackage`, `:export` & Zero `use` Pollution**: Define explicit packages with `(:use #:cl)` and `:local-nicknames` (`#:alex #:alexandria`) instead of `:use`-ing many external packages (avoids symbol clashes; `AstFacts.wildcard_imports`), and export public symbols explicitly via `:export`.
3. **Earmuffs for Special Variables & Hygienic Macros**: Always wrap `defvar`/`defparameter` dynamic specials in `*earmuffs*` (`*config*`; `AstFacts.global_state_usages`), avoid mutating global specials across threads without locks, and keep `defmacro` definitions hygienic via `gensym` / `alexandria:with-gensyms` and `once-only` (preventing variable capture and multiple evaluation; `AstFacts.bug_risk_idioms`).
4. **Docstrings & Clean Resource Cleanup**: Provide Common Lisp docstrings on public `defun`, `defgeneric`, `defclass`, and `defpackage` forms (`AstFacts.docstring_coverage_pct`), pair resources with `unwind-protect` / `with-open-file`, and keep functions modular (`AstFacts.complex_functions`).

## Evaluation Thresholds
- **`PASS`**: `(*read-eval* nil)` safety on `read`, zero `eval`/shell injection, clean `defpackage` + `:local-nicknames`, `*earmuffs*` specials, hygienic macros, and docstrings `>= 80%`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or broad `:use` package lists / minor complexity warnings.
- **`FAIL`**: Untrusted `read`/`read-from-string` with `*read-eval*` enabled, runtime `eval` RCE, unhygienic capturing macros, or unguarded global mutable specials.
