# Provider Schemas, Attribute Typing & Macro Contract Standards (Starlark / Bazel)

## Core Principles
1. **Dynamic Language Exemption & Explicit `provider(fields = ...)` / `attr.*`**: Starlark is dynamically typed — do **NOT** penalize `.bzl` files for lacking Python mypy annotations. Evaluate contract safety via typed `rule(attrs = { ... })` (`attr.label(providers = [MyInfo])`, `attr.string(values = [...])`, `attr.bool()`) and `provider(doc = ..., fields = { ... })` schemas (`AstFacts.type_safety_coverage_pct`).
2. **Mandatory `providers = [...]` Constraints on `attr.label`**: Specify required providers on `attr.label` / `attr.label_list` attributes so invalid target dependencies fail immediately at analysis time with clear diagnostics.
3. **Prefer `DefaultInfo` & Custom Typed Providers Over Legacy `struct`**: Return modern `provider(...)` instances (`[DefaultInfo(...), MyInfo(...)]`) instead of deprecated untyped `struct(...)` rule returns (`AstFacts.weak_type_usages`).
4. **Explicit `kwargs` Forwarding in Symbolic Macros**: Validate macro parameters cleanly (preferring Bazel 8 symbolic `macro(...)` over untyped `**kwargs` wrappers).

## Evaluation Thresholds
- **`PASS`**: Typed `attr.*` + `providers = [...]`, documented `provider(fields = ...)`, and zero legacy `struct` rule returns.
- **`WARN`**: Untyped `**kwargs` legacy macros or missing `fields` dict on internal providers.
- **`FAIL`**: Unconstrained `attr.label` graphs passing opaque dicts/structs causing cryptic analysis crashes.
