# Code Quality & Configuration Standards (TOML)

## Core Principles
1. **Strict TOML v1.0.0 Validity & Zero Duplicate Keys/Tables**: Ensure every `.toml` file (`pyproject.toml`, `Cargo.toml`, `mise.toml`, `.pni/pni.toml`, app configs) conforms strictly to TOML v1.0.0 with zero duplicate keys or redefined table headers (`AstFacts.bug_risk_idioms`), formatted cleanly with `taplo fmt`.
2. **Zero Hardcoded Secrets**: Never commit API keys, database passwords, JWT signing keys, or OAuth client secrets inside `.toml` files (`AstFacts.hardcoded_secrets`) — use environment variables or secret-manager references.
3. **Clear Table Hierarchy & Inline Comments**: Group settings into logical `[section]` / `[[array_of_tables]]` blocks, avoid deeply nested inline tables `{ a = { b = { c = 1 } } }` that hurt readability, and document non-obvious flags/waivers with `#` comments (`AstFacts.docstring_coverage_pct`).
4. **Schema Header Directives**: Add `#:schema <url_or_path>` (supported by Taplo / Even Better TOML) on structured custom configs for editor & CI validation.

## Evaluation Thresholds
- **`PASS`**: Strict TOML v1.0.0 compliance, zero duplicate keys/tables, zero committed secrets, clean section structure, and documented flags/waivers.
- **`WARN`**: Overly wide inline tables or missing `#:schema` / comments on custom app config options.
- **`FAIL`**: Hardcoded secrets in `.toml`, duplicate key/table syntax errors, or invalid TOML breaking build/runtime tooling.
