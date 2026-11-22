# Native TOML Types & Schema Validation Standards (TOML)

## Core Principles
1. **Use Native TOML Types (Booleans, Integers, Dates, Arrays)**: Represent booleans (`true`/`false`), numbers (`8080`, `1_000`), and RFC 3339 timestamps (`2026-01-15T00:00:00Z`) natively rather than quoting everything as strings (`"true"`, `"8080"`), and use literal strings `'...'` for regexes/Windows paths to eliminate backslash-escaping bugs.
2. **DSL Exemption**: TOML is a configuration format — evaluate structural rigor via Taplo JSON Schema bindings (`#:schema`), typed parser bindings (Pydantic/Serde `#[serde(deny_unknown_fields)]`), and native TOML scalar usage.
3. **Explicit Unknown-Field Hygiene**: Keep obsolete/deprecated config keys cleaned out so strict parsers (`deny_unknown_fields`, `extra="forbid"`) catch typos immediately.
4. **Consistent Array-of-Tables (`[[...]]`) Ordering**: Keep `[[...]]` entries grouped cleanly with consistent key order and clear `id`/`name` discriminators.

## Evaluation Thresholds
- **`PASS`**: Native TOML scalar types, literal `'...'` strings for regexes, zero dead/typo keys, and schema-backed config structure.
- **`WARN`**: Stringified numbers/booleans or inconsistent key ordering across `[[...]]` entries.
- **`FAIL`**: Type mismatches violating consuming Pydantic/Serde/PEP 621/Cargo schemas.
