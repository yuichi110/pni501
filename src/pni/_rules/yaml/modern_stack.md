# Modern YAML (YAML 1.2, OpenAPI 3.1, K8s & OIDC CI) Idioms (`yaml/modern_stack`)

## Core Principles
1. **OIDC Short-Lived Credentials in CI**: Use GitHub Actions OIDC (`id-token: write` scoped strictly to the deploy job) + `timeout-minutes` + `concurrency: { group: ..., cancel-in-progress: true }` rather than long-lived static cloud secrets (`AstFacts.modernization_hints`).
2. **Kubernetes Modern Standards**: Use `apps/v1`, `networking.k8s.io/v1`, `PodSecurity` restricted profile compliance, explicit `livenessProbe`/`readinessProbe`, `PodDisruptionBudget`, and Kustomize/Helm over copy-pasted per-environment raw manifests.
3. **Modern OpenAPI 3.1 & Compose Specification**: Omit obsolete `version: "3.8"` top-level key in modern Docker Compose Specification files, and prefer OpenAPI 3.1 (full JSON Schema 2020-12 compatibility) over Swagger 2.0.
4. **Safe YAML Loading**: Remind consuming services to always use safe parsers (`yaml.safe_load` / `YAML.safe_load`, never unsafe `yaml.load`).
