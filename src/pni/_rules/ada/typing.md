# Typing, Range Subtypes & SPARK Verification Standards (Ada)

## Core Principles
1. **Domain-Specific Constrained Scalar Types**: Define distinct domain types with explicit ranges (`type Port_Number is range 1 .. 65535;`, `subtype Index is Positive range 1 .. Max;`) rather than raw `Integer`/`Float` everywhere so compiler & runtime range checks prevent invalid states (`AstFacts.type_safety_coverage_pct`).
2. **Encapsulated `private` / `limited private` Types & `not null`**: Hide internal representations in the `private` part of `.ads` specs, annotate non-nullable access parameters `not null access`, and prefer stack-allocated / bounded containers over heap `access` pointers (`AstFacts.type_safety_issues`).
3. **Explicit Parameter Modes & Discriminated Records**: Annotate every parameter with exact `in`, `out`, or `in out` modes (avoiding unnecessary `in out`), and model variant records cleanly with discriminants.
4. **SPARK-Friendly Subset Where Critical**: For safety-critical packages, enable `SPARK_Mode => On` and eliminate aliasing/side effects in functions so `gnatprove` can prove absence of runtime errors (AoRTE).

## Evaluation Thresholds
- **`PASS`**: Domain-constrained types/subtypes, `private` encapsulation in `.ads`, explicit `in`/`out` modes, and zero unjustified `Unchecked_Conversion` / `System.Address` casts.
- **`WARN`**: Over-use of raw `Integer` / `String` instead of domain subtypes in internal packages.
- **`FAIL`**: Raw `System.Address` pointer arithmetic in domain logic, unchecked access-type leaks, or suppressed range checks.
