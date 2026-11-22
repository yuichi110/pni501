# Modern C++ (C++20 / C++23) & Safety Idioms (`cpp/modern_stack`)

## Core Principles
1. **Modern C++20/23 Standard Library**: Prefer `std::make_unique` / `std::make_shared`, `std::span`, `std::string_view`, `std::format` / `{fmt}`, `std::filesystem`, `std::jthread`, and `<ranges>` over raw C arrays, `sprintf`, or `pthread` boilerplate (`AstFacts.modernization_hints`).
2. **Eliminate C-Heritage Security Sinks**: Ban `strcpy`/`sprintf`/`gets` (CWE-120), raw `system()` with unsanitized strings (CWE-78), and unchecked `operator[]` indexing on untrusted input (`AstFacts.dangerous_sinks`).
3. **Structured Observability**: Prefer `spdlog` or structured logger sinks over raw `std::cout` / `printf` in production services (`AstFacts.unstructured_logging`).
4. **Concurrency Safety**: Use `std::scoped_lock`, `std::atomic`, and clear thread ownership (`std::jthread` + `std::stop_token`) rather than detached threads (`thread.detach()`).
