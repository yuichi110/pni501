# Typing, Fixed-Width Integers & Const-Correctness Standards (C)

## Core Principles
1. **Fixed-Width & Semantic Types**: Use `<stdint.h>` (`uint8_t`, `int32_t`, `uint64_t`), `size_t` for sizes/indices, `ptrdiff_t` for pointer offsets, and `<stdbool.h>` (`bool`) rather than platform-dependent `int`/`long` for wire formats and byte lengths (`AstFacts.type_safety_coverage_pct`).
2. **`const`-Correctness & Strict Prototypes**: Mark read-only pointer parameters `const T *`, avoid implicit `int` or empty-parameter prototypes `int f()` (write `int f(void)`), and avoid unsafe `void *` casts outside generic container/callback APIs (`AstFacts.weak_type_usages`, `AstFacts.type_safety_issues`).
3. **Signed/Unsigned & Overflow Hygiene**: Guard arithmetic on untrusted lengths before `malloc(n * size)` against integer overflow (CWE-190), avoid signed integer overflow UB, and never cast away `const` or violate strict aliasing.
4. **Opaque Struct Encapsulation**: Hide internal struct layouts in `.c` files behind forward-declared opaque handles in public `.h` headers.

## Evaluation Thresholds
- **`PASS`**: Consistent `size_t`/`<stdint.h>`/`const`-correctness, explicit `(void)` prototypes, guarded allocation arithmetic, and minimal raw `void *` casting.
- **`WARN`**: Isolated missing `const` qualifiers or mixed signed/unsigned loop counters.
- **`FAIL`**: Unchecked integer-overflow allocation sizing, pervasive unsafe pointer casts / strict-aliasing UB, or K&R / unprototyped function declarations.
