# Modern Common Lisp (ASDF 3 / UIOP / SBCL) Idioms (`commonlisp/modern_stack`)

## Core Principles
1. **UIOP Portability & Alexandria/Serapeum**: Use `uiop` (built into ASDF 3: `uiop:getenv`, `uiop:run-program` with argument lists, `uiop:read-file-string`, `uiop:with-temporary-file`) instead of implementation-specific `sb-ext:` internals wherever portable (`AstFacts.modernization_hints`).
2. **Package-Inferred Systems & Local Nicknames**: Prefer `:local-nicknames` (`defpackage` or `uiop:define-package`) and clean module decomposition over flat multi-thousand-line single-package files.
3. **Hardened HTTP & SQL**: Configure explicit `:connect-timeout` and `:read-timeout` on `dexador` / `drakma` clients (`AstFacts.missing_io_timeouts`), use parameterized SQL (`sxql`/`cl-dbi`/`postmodern` placeholders — never `(format nil "SELECT ... ~A" user)`; `AstFacts.dangerous_sinks`), and never serialize untrusted network data via Lisp `read`.
4. **Structured Logging**: Prefer `log4cl` / `vom` / `verbose` over scattered `(format t ...)` calls in services (`AstFacts.unstructured_logging`).
