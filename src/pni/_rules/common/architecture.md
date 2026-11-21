# Architecture Standards (Common)

## Core Principles (`ARCH-01` – `ARCH-04`)

1. **`ARCH-01` — Separation of Concerns (SoC)**: Separate presentation/HTTP/CLI delivery, domain/application business logic, and data/infrastructure persistence across explicit layers (`ArchitectureRecord.structure_map.layers`).
2. **`ARCH-02` — Acyclic Layer Hierarchy**: Modules must depend downward on lower layers (`AstFacts.circular_dependencies == 0`, `AstFacts.boundary_violations == 0`).
   - `PASS`: `0` runtime circular dependencies and `0` boundary violations (`type_checking_cycles` may be noted as informational only).
   - `WARN`: Minor layering leaks without runtime cycles.
   - `FAIL`: Any runtime circular dependency (`len(circular_dependencies) > 0`) or inverted core-to-delivery boundary violation.
3. **`ARCH-03` — Loose Coupling & High Cohesion**: Keep modules focused on a single responsibility without mutable module/class-level shared state (`AstFacts.global_state_usages == 0` in stateless/service layers).
4. **`ARCH-04` — Single Source of Truth**: Define canonical domain models, configuration schemas, and shared constants in a single authoritative module rather than duplicating parallel definitions across layers.
