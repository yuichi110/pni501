# YAML Linting, Schema & Manifest Verification Standards (YAML)

## Core Principles
1. **Domain-Specific Static Linters in CI**:
   - General YAML: `yamllint` (syntax, duplicate keys, indentation, truthy checks).
   - GitHub Actions: `actionlint` (+ `zizmor` / `pinact` for security).
   - Kubernetes / Helm: `helm lint`, `helm template | kubeconform -strict`, and `trivy config`.
   - OpenAPI: `spectral lint` / `redocly lint` + contract tests.
2. **Schema Validation on Config Fixtures**: Validate application YAML configs against Pydantic / JSON Schema models in unit tests (`AstFacts.test_functions_count`).
3. **Policy-as-Code Enforcement**: Verify K8s/CI manifests against OPA/Conftest or Kyverno policies before deployment.
4. **DSL Exemption**: Evaluate YAML verification via `yamllint`/`actionlint`/`kubeconform`/schema-validation CI gates rather than code line-coverage tools.

## Evaluation Thresholds
- **`PASS`**: Automated `yamllint` + domain linter (`actionlint` / `kubeconform` / `spectral` / `trivy config`) wired in CI.
- **`WARN`**: Basic YAML parsing runs without domain-specific security/schema linters.
- **`FAIL`**: Zero automated validation on production Kubernetes, OpenAPI, or CI workflow YAML files.
