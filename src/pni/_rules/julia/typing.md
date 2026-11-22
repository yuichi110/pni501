# Typing, Type Stability & Multiple-Dispatch Standards (Julia)

## Core Principles
1. **Concrete Struct Fields & Type Stability (JIT Core Principle)**: Parameterize struct fields with concrete types (`struct Point{T<:Real} x::T; y::T end`) rather than abstract field types (`x::Real`, `data::Vector{Any}`, or untyped fields — which destroy JIT specialization and allocate heavily; `AstFacts.weak_type_usages`, `AstFacts.type_safety_issues`).
2. **Avoid Over-Constraining Function Arguments (Avoid False Positives)**: In idiomatic Julia multiple dispatch, accepting broad abstract types (`AbstractVector{<:Real}`, `AbstractString`) or unannotated generic parameters on functions is **good design** — evaluate return type stability (`@code_warntype` / `JET.jl`) and concrete container/struct types rather than demanding concrete annotations on every argument.
3. **Avoid `Vector{Any}` & Unstable Branches**: Ensure functions return a single concrete type (or small `Union{T, Nothing}`), initialize typed arrays (`Float64[]` instead of `[]`), and verify stability with `Test.@inferred`.
4. **Explicit `Nothing` / `Missing` Handling**: Distinguish `nothing` (absence of value) from `missing` (statistical missing data) intentionally.

## Evaluation Thresholds
- **`PASS`**: Concrete/parametric struct fields, zero `Any`-typed containers in hot paths, type-stable functions (`@inferred`), and idiomatic abstract dispatch on parameters.
- **`WARN`**: Occasional abstract struct fields or `[]` (`Vector{Any}`) allocations in non-hot setup helpers.
- **`FAIL`**: Pervasive `Any` struct fields / untyped containers causing type instability across numerical kernels.
