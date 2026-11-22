# Code Quality & Configuration Security Standards (JSON)

## Core Principles
1. **Strict RFC 8259 Syntax & Zero Duplicate Keys**: Ensure every `.json` file parses cleanly without trailing commas or non-standard comments (use `.jsonc` when comments are intentional, e.g. `tsconfig.json`), eliminate duplicate object keys (parsers disagree on first-vs-last wins; `AstFacts.bug_risk_idioms`), and format consistently with Prettier / Biome / `jq`.
2. **Zero Committed Secrets or Service-Account Key Files**: Never commit `credentials.json`, GCP service-account private key JSONs (`"type": "service_account"`), API tokens, or hardcoded passwords inside `.json` configuration files (`AstFacts.hardcoded_secrets`).
3. **Explicit `$schema` Declarations**: Include a `"$schema"` URL on structured configuration files (JSON Schema 2020-12, Renovate, Biome, VS Code, API contracts) so editors and CI catch typos immediately.
4. **Concise & Diff-Friendly Layout**: Keep tracked JSON configs pretty-printed (not single-line minified blobs) with deterministic key ordering so `git diff` reviews remain auditable.

## Evaluation Thresholds
- **`PASS`**: Strict valid JSON, zero duplicate keys, zero hardcoded secrets/service-account keys, `$schema` declarations on structured configs, and consistent formatting.
- **`WARN`**: Missing `$schema` on custom app config files or minified tracked configs obscuring diffs.
- **`FAIL`**: Hardcoded secrets/credentials committed in JSON, duplicate keys causing parser ambiguity, or invalid syntax breaking consumers.
