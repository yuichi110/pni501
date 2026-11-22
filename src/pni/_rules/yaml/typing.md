# Schema Validation, YAML 1.2 Typing & Anchor Standards (YAML)

## Core Principles
1. **Explicit Schema Declarations (`# yaml-language-server: $schema=...`)**: Associate structured YAML configs (OpenAPI, GitHub Actions, Kubernetes, Helm, Renovate, PNI workflows) with canonical JSON Schemas / CRDs so editors and CI validate required fields and enums deterministically (`AstFacts.type_safety_coverage_pct`).
2. **Avoid YAML 1.1 Implicit-Type Coercion Bugs ("Norway Problem")**: Explicitly quote strings that YAML 1.1 parsers coerce into booleans, floats, or dates (`"NO"`, `"yes"`, `"on"`, `"off"`, `"3.10"`, `"0755"`), and use strictly `true`/`false` for booleans (`AstFacts.bug_risk_idioms`).
3. **Restrained Anchor (`&`) / Alias (`*`) Usage**: Avoid deeply chained anchors/merge keys (`<<: *a`, deprecated in YAML 1.2) that obscure effective config values or invite Billion Laughs alias-expansion DoS in untrusted YAML parsers.
4. **Clean Multi-Line Block Scalars**: Use `|` / `|-` / `>` cleanly for embedded scripts/prompts rather than unreadable escaped single-line strings.

## Evaluation Thresholds
- **`PASS`**: Schema-validated YAML, strictly `true`/`false` booleans, quoted version/mode strings (`"3.10"`, `"0644"`), and zero duplicate keys.
- **`WARN`**: Unquoted version strings or heavy YAML merge-key (`<<:`) chains.
- **`FAIL`**: Duplicate keys silently dropping config, broken schema compliance, or unsafe untrusted YAML deserialization tags (`!!python/object`).
