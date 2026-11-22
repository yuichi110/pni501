# Modern Odin & Systems Idioms (`odin/modern_stack`)

## Core Principles
1. **Modern Odin Core & Control Flow**: Use `or_return`, `or_else`, `or_break`, `or_continue`, `#(soa)` / `#soa` data-oriented slices where appropriate, and `core:mem/virtual` arenas for batch lifetimes (`AstFacts.modernization_hints`).
2. **Explicit Context & Structured Logging**: Use `core:log` (`log.info`, `log.error` via `context.logger`) instead of scattered `fmt.println` in libraries and services (`AstFacts.unstructured_logging`).
3. **Safe FFI & Command Execution**: Validate buffer lengths before crossing `foreign` C boundaries and avoid unsanitized shell invocation (`os2.process_start` with explicit arg arrays; `AstFacts.dangerous_sinks`).
4. **Explicit Bounds & Secret Zeroing**: Zero sensitive buffers via `crypto.zero_explicit` before freeing.
