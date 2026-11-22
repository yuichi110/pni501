# TOML Parsing, Taplo & Schema Verification Standards (TOML)

## Core Principles
1. **Automated Syntax & Schema CI Gate**: Run `taplo fmt --check` and `taplo check` (or Python `tomllib.loads` / `check-jsonschema`) across all tracked `.toml` files in CI.
2. **Round-Trip Config Loader Tests**: Verify application config TOML templates deserialize cleanly into the app's Pydantic / Serde / Go config structs with zero unknown fields (`AstFacts.test_functions_count`).
3. **Waiver & Governance Hygiene (`.pni/pni.toml`)**: Verify every `[[opt_out]]` waiver carries an explicit `id`, `scope`, and concrete `reason`.
4. **DSL Exemption**: Evaluate TOML verification via `taplo check` and config deserialization tests rather than code line-coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Automated `taplo check` / `tomllib` + config-struct deserialization tests in CI.
- **`WARN`**: TOML files parsed indirectly at runtime without an explicit CI lint/format gate.
- **`FAIL`**: Unvalidated or syntactically broken `.toml` config files committed to the repository.
