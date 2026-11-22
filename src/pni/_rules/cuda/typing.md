# Typing, Precision, Alignment & Address-Space Standards (CUDA)

## Core Principles
1. **Explicit Numerical Precision & Mixed-Precision Discipline**: Distinguish `float` (`fp32`), `double` (`fp64`), `__half` (`fp16`), and `__nv_bfloat16` (`bf16`) explicitly; append `f` suffix to float literals (`1.0f`) inside `fp32` kernels so `double` promotion does not silently throttle throughput and inflate register pressure (`AstFacts.type_safety_coverage_pct`).
2. **Explicit `const` / `__restrict__` & 64-Bit Indexing**: Annotate read-only non-aliasing kernel pointer parameters `const T* __restrict__`, use `size_t` / `int64_t` for tensor offsets exceeding 2^31 elements (prevents signed 32-bit index overflow; CWE-190), and avoid unsafe C-style pointer casts (`AstFacts.type_safety_issues`).
3. **Host vs Device Pointer Separation**: Never dereference a device pointer on the host or vice versa; keep `__host__`, `__device__`, and `__global__` qualifiers explicit and clean.
4. **Explicit `constexpr` / Template Tile Dimensions**: Parameterize block/tile sizes as `constexpr` or template non-type parameters rather than untyped `#define` macros.

## Evaluation Thresholds
- **`PASS`**: Explicit `const T* __restrict__`, `1.0f` literal precision discipline, overflow-safe indexing, and clean `__host__`/`__device__` boundaries.
- **`WARN`**: Occasional untyped double-promoted literals in `fp32` kernels or missing `__restrict__`.
- **`FAIL`**: 32-bit signed index overflow on large tensors, unsafe `reinterpret_cast` alignment violations, or mixed host/device pointer dereferences.
