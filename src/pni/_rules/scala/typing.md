# Typing, ADTs, Variance & Typeclass Standards (Scala)

## Core Principles
1. **Algebraic Data Types & Exhaustive Pattern Matching**: Model domain states using Scala 3 `enum` or `sealed trait` hierarchies so the compiler proves match exhaustiveness without catch-all `case _ =>` swallowing new variants.
2. **Avoid `Any`, `asInstanceOf` & `isInstanceOf`**: Replace runtime casts (`asInstanceOf[T]`), `Any`, and `AnyRef` with parametric polymorphism, opaque types (`opaque type UserId = UUID`), and typeclasses (`given`/`using` or `implicit`; `AstFacts.type_safety_coverage_pct`, `AstFacts.weak_type_usages`, `AstFacts.type_safety_issues`).
3. **Explicit Public Return Types**: Declare explicit return types on all public `def` and `val` members (critical for binary compatibility and preventing accidental `Any`/`Product with Serializable` inference).
4. **Scoped Implicit / Given Discipline**: Avoid polluting global scope with implicit conversions (`scala.language.implicitConversions`); prefer explicit extension methods and well-scoped `given` instances.

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 95%`, zero `asInstanceOf`/`Any` domain abuse, explicit public return types, and exhaustive ADT matching.
- **`WARN`**: Isolated missing public return types or localized casts at Java interop boundaries.
- **`FAIL`**: Pervasive `asInstanceOf`/`Any`, unsafe implicit conversions, or non-exhaustive pattern matches throwing `MatchError`.
