# Schema Reference & Config Governance Standards (JSON)

## Core Principles
1. **Immutable / Versioned `$schema` & `$ref` URIs**: Reference versioned JSON Schema URIs (rather than unversioned mutable branches) so CI validation does not drift unexpectedly (`ProjectFacts.unpinned_dependencies`).
2. **Zero-Lockfile Exemption**: Standalone JSON schema/config repositories do **not** require a lockfile unless paired with Node/Python schema-validation tooling.
3. **Clean Config Separation (Template vs. Local Override)**: Commit `config.example.json` templates with placeholder values and add real environment-specific secret configs to `.gitignore`.
4. **Secret & Supply-Chain Scanning**: Scan JSON files (including `package.json`, `composer.json`, `renovate.json`) with Trivy and secret detectors in CI.

## Evaluation Thresholds
- **`PASS`**: Versioned `$schema` URIs, clean example-vs-ignored-secret separation, and zero committed credential JSON files.
- **`WARN`**: Unversioned remote `$schema` links or missing `*.example.json` templates.
- **`FAIL`**: Committed credential JSON files (`service-account.json`, `auth.json`) or broken `$ref` schema links.
