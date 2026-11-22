# Modern C (C11 / C17 / C23) & Safety Idioms (`c/modern_stack`)

## Core Principles
1. **Modern ISO C Standard**: Target C11/C17/C23 (`<stdint.h>`, `<stdbool.h>`, `_Static_assert` / `static_assert`, `<stdatomic.h>`, designated initializers, compound literals) rather than legacy C89/C90 constructs (`AstFacts.modernization_hints`).
2. **Eliminate Memory & Format-String CWE Sinks**: Replace `strcpy`/`strcat`/`sprintf`/`gets` (CWE-120), `system()`/`popen()` with unsanitized input (CWE-78), and non-literal `printf(msg)` (CWE-134) with safe bounded APIs and `execve` (`AstFacts.dangerous_sinks`).
3. **Thread & Signal Safety**: Use reentrant POSIX functions (`strtok_r`, `localtime_r`, `strerror_r`) instead of non-thread-safe `strtok`/`localtime`/`strerror` (`AstFacts.bug_risk_idioms`), and use `<stdatomic.h>` or POSIX mutexes for shared state.
4. **Deterministic Resource Cleanup**: Centralize multi-resource teardown via single-exit `goto cleanup;` blocks and zero-out sensitive key buffers (`explicit_bzero` / `memset_explicit`).
