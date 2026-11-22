# JSON Schema 2020-12 & Data-Contract Standards (JSON)

## Core Principles
1. **Formal JSON Schema Contracts (`$schema`, `required`, `additionalProperties`)**: Author companion `*.schema.json` contracts using JSON Schema Draft 2020-12 (`https://json-schema.org/draft/2020-12/schema`) with explicit `type`, `required`, `enum`, `pattern`/`format`, and `additionalProperties: false` (or `unevaluatedProperties: false`) where strict validation is needed (`AstFacts.type_safety_coverage_pct`).
2. **Consistent Data Representations**: Avoid mixing stringified numbers (`"42"`) and JSON numbers (`42`), format timestamps strictly as ISO 8601 / RFC 3339 UTC strings, and avoid precision loss on 64-bit integers (> `2^53 - 1`, `Number.MAX_SAFE_INTEGER` in JS consumers — encode huge IDs/amounts as strings).
3. **DSL Exemption**: JSON is a data-interchange format — evaluate structural rigor via JSON Schema contracts and numeric/timestamp hygiene rather than programming-language type rules.
4. **Explicit Schema Versioning**: Include `"schema_version"` on persisted interchange payloads (`*_score.json`, API fixtures, event envelopes) so breaking format changes evolve cleanly.

## Evaluation Thresholds
- **`PASS`**: Companion JSON Schemas with strict constraints, ISO 8601 UTC dates, safe integer ranges, and versioned payload contracts.
- **`WARN`**: Missing `additionalProperties: false` or unversioned interchange schemas.
- **`FAIL`**: Unsafe > 53-bit integer IDs parsed by JS clients, contradictory field types across fixtures, or unvalidated untrusted JSON configs.
