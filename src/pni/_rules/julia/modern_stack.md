# Modern Julia (1.10 LTS / 1.11+) & Scientific Computing Idioms (`julia/modern_stack`)

## Core Principles
1. **Julia 1.10+ LTS & Memory-Efficient Array Idioms**: Use `eachindex(a)` / `axes(a, d)` instead of `1:length(a)` (supports OffsetArrays), `@views` on array slices to eliminate copies, column-major loop ordering, and `public` keyword (1.11+) for non-exported public APIs (`AstFacts.modernization_hints`).
2. **Safe Concurrency**: Avoid data races in `Threads.@threads` (never push to a shared `Vector` without locks/atomics or per-task buffers; `AstFacts.bug_risk_idioms`).
3. **Hardened I/O & Timeouts**: Configure explicit `readtimeout` / `connect_timeout` on `HTTP.jl` / `Downloads.jl` requests (`AstFacts.missing_io_timeouts`) and keep TLS verification enabled (`AstFacts.dangerous_sinks`).
4. **Structured Logging**: Use stdlib `Logging` macros (`@info`, `@warn`, `@error` with key-value fields) instead of `println(...)` in packages and services (`AstFacts.unstructured_logging`).
