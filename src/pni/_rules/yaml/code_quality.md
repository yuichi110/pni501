# Code Quality & CI/Kubernetes Security Standards (YAML)

## Core Principles
1. **GitHub Actions Least-Privilege & Expression-Injection Defense**:
   - Declare top-level `permissions: read-all` or `permissions: { contents: read }` and **forbid `permissions: write-all`** (CWE-269; `AstFacts.dangerous_sinks`).
   - Pin third-party `uses: owner/action@<40-char-commit-sha> # vX.Y.Z` rather than mutable branch/major tags (`AstFacts.bug_risk_idioms`).
   - Never interpolate untrusted PR/issue metadata (`${{ github.event.issue.title }}`, `github.head_ref`) directly inside `run:` shell commands (CWE-78 — pass via `env:` and double-quote `"$VAR"`).
2. **Kubernetes & Docker Compose Pod Hardening**:
   - Enforce `securityContext` (`runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, `capabilities: { drop: ["ALL"] }`), forbid `privileged: true` / `hostNetwork: true`, pin container image versions (never `:latest`), and declare explicit CPU/memory `requests` & `limits`.
3. **Zero Plaintext Secrets**: Never commit API tokens, passwords, or private keys inside YAML manifests, `values.yaml`, or `docker-compose.yml` (`AstFacts.hardcoded_secrets`).
4. **Zero Duplicate Keys, YAML 1.1 Traps & `yamllint` Hygiene**: Eliminate duplicate mapping keys (silently overwrite earlier values!), quote ambiguous YAML 1.1 booleans/octals (`"on"`, `"no"`, `"0644"`, `"1.10"`), and enforce consistent 2-space indentation (`yamllint`).

## Evaluation Thresholds
- **`PASS`**: Least-privilege CI `permissions`, SHA-pinned actions, hardened K8s `securityContext` + resource limits, zero plaintext secrets or duplicate keys, and `yamllint` clean.
- **`WARN`**: Tag-pinned (non-SHA) official GitHub Actions or missing K8s `readOnlyRootFilesystem`.
- **`FAIL`**: `permissions: write-all`, GitHub Actions `run:` expression injection, `privileged: true` pods, or hardcoded plaintext secrets in YAML.
