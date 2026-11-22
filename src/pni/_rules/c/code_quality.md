# Code Quality Standards (C)

## Core Principles
1. **Strict Compiler Warnings & Formatting**: Build with `-Wall -Wextra -Wpedantic` (and `-Wconversion` / `-Wshadow`), format with `clang-format`, and analyze with `clang-tidy` / `cppcheck` (`ProjectFacts.tooling_modernization_issues`).
2. **Memory Safety & Zero Unsafe Legacy APIs**: Forbid unbounded string/buffer functions (`gets`, `strcpy`, `strcat`, `sprintf`, `vsprintf`, `scanf("%s")`, `atoi` without validation; CWE-120/CWE-787) in favor of length-checked alternatives (`snprintf`, `strnlen`, `strtol` with `errno`; `AstFacts.dangerous_sinks`, `AstFacts.bug_risk_idioms`). Check every `malloc`/`calloc`/`realloc` return value and pair every allocation/file descriptor with deterministic cleanup (`goto cleanup;` is idiomatic single-exit resource cleanup in C and must **NOT** be penalized as spaghetti `goto`).
3. **Header Hygiene & Documentation**: Protect every `.h` file with `#ifndef ... #define ... #endif` (or `#pragma once`), document public header declarations with Doxygen comments (`/** ... */`; `AstFacts.docstring_coverage_pct`), and keep internal helpers `static`.
4. **Zero Mutable Global State & Bounded Functions**: Pass explicit context structs (`struct ctx *`) instead of mutable global variables (`AstFacts.global_state_usages`), check all error return codes explicitly, and decompose long functions (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: Zero banned unbounded C functions (`gets`/`strcpy`/`sprintf`), checked allocations & error returns, `docstring_coverage_pct >= 80%` on public headers, and zero unguarded mutable globals.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity / missing `static` linkage warnings.
- **`FAIL`**: Banned buffer-overflow functions (`gets`/`strcpy`/`sprintf`), unchecked `malloc`/I/O returns, format-string vulnerabilities (`printf(user_str)`), or pervasive mutable global state.
