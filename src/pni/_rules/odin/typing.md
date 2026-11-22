# Typing, Slices, Distinct Types & Union Standards (Odin)

## Core Principles
1. **Bounds-Checked Slices (`[]T`) Over Raw Multi-Pointers (`[^]T`)**: Prefer Odin slices (`[]u8`, `[]Item`) and dynamic arrays (`[dynamic]T`) over raw `rawptr` or `[^]T` multi-pointers outside audited `foreign` C-FFI bindings (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Distinct Types, Tagged `union`s & `bit_set`s**: Model domain IDs with `distinct` types (`User_Id :: distinct u64`), state machines with `union` + `#partial`-free exhaustive `switch`, and flag masks with `bit_set[My_Flag]` instead of raw integer bit twiddling.
3. **Minimize `transmute` & `any`**: Confine `transmute(T)` and `any` type-erasure strictly to serialization/formatting/FFI layers (`AstFacts.weak_type_usages`), and leverage Odin's zero-initialization-by-default guarantee intentionally (avoid `---` uninitialized variables unless immediately overwritten).
4. **Explicit `Error` Enums**: Return concrete `enum` or `union` error types rather than bare booleans when callers need to distinguish failure causes.

## Evaluation Thresholds
- **`PASS`**: Bounds-checked slices, `distinct` domain types, exhaustive `union` switches, and isolated FFI-only `rawptr`/`transmute`.
- **`WARN`**: Occasional `#partial switch` on domain unions or `any` in internal helpers.
- **`FAIL`**: Pervasive `transmute`/`rawptr` bypassing memory safety, unchecked `---` uninitialized reads, or `[^]T` pointer arithmetic in core logic.
