# Modern Zig (0.13 / 0.14+) & Systems Idioms (`zig/modern_stack`)

## Core Principles
1. **Modern Zig Standard Library**: Use `std.heap.GeneralPurposeAllocator` / `DebugAllocator` / `ArenaAllocator` purposefully, `std.log.scoped(.my_mod)` for structured logging instead of `std.debug.print` in production (`AstFacts.unstructured_logging`), and modern `build.zig` `b.addModule` / `b.createModule` APIs (`AstFacts.modernization_hints`).
2. **Safe Interop & CWE Mitigation**: Validate slice lengths before C FFI calls (`@cImport`), never invoke shell commands with unsanitized strings via `std.process.Child` (`AstFacts.dangerous_sinks`), and set explicit timeouts on sockets/HTTP clients (`AstFacts.missing_io_timeouts`).
3. **Compile-Time Validation (`comptime`)**: Use `comptime` assertions (`@compileError`) to catch invalid configuration/type invariants at build time rather than runtime panics.
4. **Memory-Zeroing for Secrets**: Scrub secret buffers with `std.crypto.utils.secureZero` before freeing.
