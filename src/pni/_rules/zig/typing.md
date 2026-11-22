# Typing, Slices, Optionals & Error-Set Standards (Zig)

## Core Principles
1. **Slices (`[]const T`) Over Raw Sentinel/Many-Item Pointers**: Prefer bounds-checked slices (`[]const u8`, `[]T`) over raw `[*]T` / `[*c]T` C pointers outside direct `@cImport` FFI boundaries (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Explicit Error Sets & Tagged Unions**: Declare narrow, explicit error sets on public APIs (`MyError!T`) rather than opaque `anyerror!T`, and model state machines with `union(enum)` + exhaustive `switch` statements.
3. **Minimize Unsafe Casts (`@ptrCast`, `@alignCast`, `@bitCast`)**: Confine `@ptrCast`, `@alignCast`, and `@intFromPtr` strictly to audited allocator/FFI layers and avoid `*anyopaque` type erasure where `comptime` generics suffice (`AstFacts.weak_type_usages`).
4. **Checked Arithmetic & Explicit Integer Widths**: Use explicit integer widths (`u8`, `u32`, `usize`) and saturating/wrapping operators (`+|`, `+%`) intentionally rather than overflowing silently.

## Evaluation Thresholds
- **`PASS`**: Bounds-checked slices, narrow error sets, `union(enum)` state modeling, and isolated FFI-only pointer casts.
- **`WARN`**: Broad `anyerror` returns on public library APIs or occasional raw pointer casts.
- **`FAIL`**: Pervasive `@ptrCast`/`*anyopaque` bypassing safety, unvalidated `[*c]` C pointers in core logic, or `@setRuntimeSafety(false)` abuse.
