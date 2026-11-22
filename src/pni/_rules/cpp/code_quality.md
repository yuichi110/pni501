# Code Quality Standards (C++)

## Core Principles
1. **RAII & Rule of Zero / Five**: Manage every resource (heap memory, file handles, mutexes, sockets) via RAII smart pointers (`std::unique_ptr`, `std::shared_ptr`, `std::lock_guard`/`std::scoped_lock`) rather than raw owning `new`/`delete` or `malloc`/`free` (`AstFacts.bug_risk_idioms`).
2. **Header Hygiene & Zero `using namespace` Pollution**: Guard every header with `#pragma once` or include guards, **never** write `using namespace std;` in header files (`.hpp`/`.h`; `AstFacts.wildcard_imports`), and document public classes/methods with Doxygen (`///` or `/** ... */`; `AstFacts.docstring_coverage_pct`).
3. **Clang-Tidy, Warnings & Formatting**: Format with `clang-format`, run `clang-tidy` (Core Guidelines / bugprone / modernize), compile with `-Wall -Wextra -Wpedantic`, and scope `// NOLINT(...)` comments narrowly (`AstFacts.unscoped_type_ignores == 0`).
4. **Exception Safety & Zero Mutable Globals**: Avoid mutable global singletons / static initialization order fiasco (`AstFacts.global_state_usages`), never let exceptions escape destructors, avoid empty `catch (...) {}` handlers, and keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, RAII ownership (zero raw owning `new`/`delete`), zero `using namespace` in headers, zero unguarded mutable globals, and scoped `NOLINT` comments.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity / style warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, raw manual memory management or banned C buffer sinks (`strcpy`/`sprintf`), empty `catch (...)`, or mutable global state races.
