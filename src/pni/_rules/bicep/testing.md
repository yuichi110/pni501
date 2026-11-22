# Validation, What-If & PSRule Testing Standards (Bicep)

## Core Principles
1. **Compile, Lint & Policy Gates**: Run `az bicep build` / `bicep lint`, `PSRule for Azure`, and `trivy config` / `checkov` in CI for every `.bicep` and `.bicepparam` file.
2. **Preflight Validation & `what-if` Verification**: Run `az deployment group validate` and `az deployment group what-if` in PR pipelines before production deployments, and use Bicep experimental `test` / Pester assertion suites for reusable modules (`AstFacts.test_functions_count`).
3. **Environment Parameter Separation**: Keep environment-specific `.bicepparam` files cleanly separated (`main.dev.bicepparam`, `main.prod.bicepparam`) with Key Vault secret references rather than plaintext test values.
4. **DSL Exemption**: Do **NOT** demand software unit-test line coverage metrics on `.bicep` templates; evaluate verification via `bicep build`/`lint` + PSRule/Trivy + `what-if` gates.

## Evaluation Thresholds
- **`PASS`**: Automated `bicep lint`/`build` + PSRule/Trivy security gates + parameterized `.bicepparam` verification.
- **`WARN`**: `bicep build` runs in CI without security policy scanning (PSRule/Trivy).
- **`FAIL`**: Zero automated Bicep compilation, linting, or IaC security verification before deploy.
