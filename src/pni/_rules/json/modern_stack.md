# Modern JSON Schema 2020-12 & Config Idioms (`json/modern_stack`)

## Core Principles
1. **JSON Schema Draft 2020-12**: Prefer Draft 2020-12 (`$defs` instead of legacy `definitions`, `prefixItems` instead of tuple `items`, `unevaluatedProperties`) over legacy Draft-04/Draft-07 when authoring new schemas (`AstFacts.modernization_hints`).
2. **JSON Lines (`.jsonl` / NDJSON) for Append-Only Logs & History**: Prefer newline-delimited JSON (`.jsonl`) for streaming telemetry and append-only audit history instead of rewriting giant multi-megabyte JSON arrays.
3. **JSON5 / JSONC vs Strict JSON Clarity**: Use `.jsonc` only for editor/compiler configs (`tsconfig.json`, `.vscode/settings.json`) and keep all interchange data files strictly RFC 8259 compliant.
4. **Canonical Encoding**: Always encode JSON files as UTF-8 without BOM.
