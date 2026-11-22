# JSON Validation & Schema-Test Standards (JSON)

## Core Principles
1. **Automated Syntax & Schema CI Gates**: Validate all `.json` files in CI with `check-jsonschema`, `ajv-cli`, `biome check`, or `python -m json.tool` (plus duplicate-key checks) so malformed JSON never lands on `main`.
2. **Positive & Negative Schema Fixtures**: For repositories authoring `*.schema.json` contracts, test both valid payloads AND invalid payloads that MUST fail validation (`AstFacts.test_functions_count`).
3. **Deterministic Formatting Gate**: Enforce `prettier --check` or `biome format --check` on tracked JSON configs.
4. **DSL Exemption**: Evaluate JSON verification via schema validation and valid/invalid fixture tests rather than code line-coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Automated syntax + schema validation (`check-jsonschema`/`ajv`/Pydantic) wired in CI with valid/invalid fixture tests for authored schemas.
- **`WARN`**: Syntax check runs in CI without schema validation against `$schema`.
- **`FAIL`**: Zero automated validation on critical configuration or JSON Schema contract files.
