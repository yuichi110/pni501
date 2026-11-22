# Container Verification, Linting & Smoke-Test Standards (Dockerfile)

## Core Principles
1. **Static Lint & Misconfiguration Gates**: Validate every `Dockerfile` / `Containerfile` in CI with `hadolint` and `trivy config` (AVD-DS checks) before building images.
2. **Container Structure & Runtime Smoke Tests**: Verify built images boot non-root (`id -u != 0`), respond to health probes, pass `container-structure-test` (or equivalent smoke checks), and have zero `HIGH`/`CRITICAL` fixable OS CVEs (`trivy image`).
3. **Offline / Deterministic Reproducibility**: Ensure `docker build` succeeds cleanly from repository contents without implicit host files or unpinned live mutable downloads.
4. **DSL Exemption**: Do **NOT** demand unit-test line coverage metrics on `Dockerfile`s themselves; evaluate verification via `hadolint` + Trivy + build/boot smoke checks.

## Evaluation Thresholds
- **`PASS`**: `hadolint` / Trivy config clean, automated CI image build + non-root boot smoke verification.
- **`WARN`**: Image builds in CI without `hadolint` or Trivy CVE gate.
- **`FAIL`**: Broken `Dockerfile` build or unverified root containers shipped directly to production.
