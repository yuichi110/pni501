# Provider & Module Pinning Standards (HCL / Terraform / OpenTofu)

## Core Principles
1. **Pinned `required_version` & `required_providers`**: Declare `required_version` (e.g. `">= 1.8.0, < 2.0.0"`) and explicit pessimistic `~>` provider constraints in `versions.tf` (`ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
2. **Committed `.terraform.lock.hcl` (Root Config vs. Reusable Module)**:
   - **Root Deployable Configurations**: Commit `.terraform.lock.hcl` (`terraform providers lock`) for cryptographic provider checksum verification (`ProjectFacts.lockfiles_found`).
   - **Reusable Shared Modules**: Omitting `.terraform.lock.hcl` (relying on `required_providers` constraints) is official Terraform convention and must **NOT** be penalized.
3. **Pinned Module Sources**: Always pin registry modules with explicit `version = "x.y.z"` and Git modules with immutable `?ref=<tag_or_sha>` (never unpinned `main` branches).
4. **IaC Policy & Supply-Chain Scanning**: Scan modules/plans with Trivy (`trivy config`), `checkov`, or `tflint` + Renovate/Dependabot.

## Evaluation Thresholds
- **`PASS`**: Pinned `required_version`, `required_providers`, and module refs (`unpinned_dependencies == 0`), plus `.terraform.lock.hcl` on root stacks.
- **`WARN`**: Loose `>=` provider bounds without upper major cap or missing lockfile platform hashes.
- **`FAIL`**: Unpinned git `main` module sources, missing `required_providers`, or EOL Terraform `< 1.0` syntax.
