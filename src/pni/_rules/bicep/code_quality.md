# Code Quality & Azure Security Standards (Bicep)

## Core Principles
1. **Mandatory `@secure()` & Least-Privilege Azure Defaults**: Annotate every password, key, or connection-string parameter with `@secure()` (and **never** expose secrets in `output` blocks or hardcode default secret strings; `AstFacts.hardcoded_secrets`). Enforce `supportsHttpsTrafficOnly: true`, `minimumTlsVersion: 'TLS1_2'`, `allowBlobPublicAccess: false`, and Managed Identities (`identity: { type: 'SystemAssigned' | 'UserAssigned' }`) over static access keys (`AstFacts.dangerous_sinks`).
2. **Bicep Linter & Clean Modularization**: Enforce `bicep lint` with `bicepconfig.json` (warnings as errors for security rules), decompose complex deployments into reusable `modules/*.bicep`, and document every `param` and `output` with `@description('...')` (`AstFacts.docstring_coverage_pct`).
3. **Avoid Hardcoded Locations & Resource IDs**: Parameterize `location` (defaulting to `resourceGroup().location`) and use symbolic resource references (`storage.id`) instead of fragile `resourceId(...)` string concatenation (`AstFacts.bug_risk_idioms`).
4. **Scoped Diagnostics**: Avoid blanket `#disable-next-line` suppressions without inline justification (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `@secure()` on secrets (zero secrets in outputs/defaults), HTTPS/TLS 1.2+ & Managed Identity defaults, `@description` >= 80%, and `bicep lint` clean.
- **`WARN`**: Missing `@description` on internal params or missing `bicepconfig.json`.
- **`FAIL`**: Secrets exposed in `output` or hardcoded defaults, disabled HTTPS/TLS 1.2, public storage blobs, or `listKeys()` returned as template outputs.
