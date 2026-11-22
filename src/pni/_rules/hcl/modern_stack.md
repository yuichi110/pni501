# Modern Terraform / OpenTofu (1.8+) IaC Idioms (`hcl/modern_stack`)

## Core Principles
1. **Modern Declarative Lifecycle Blocks**: Use `moved { ... }`, `import { ... }`, `removed { ... }`, `check { ... }`, and `precondition`/`postcondition` blocks instead of brittle manual `terraform state mv` or `local-exec` shell scripts (`AstFacts.modernization_hints`).
2. **Zero `local-exec` / `remote-exec` Provisioner Abuse**: Avoid `provisioner "local-exec"` / `"remote-exec"` (breaks idempotency and invites command injection CWE-78; `AstFacts.dangerous_sinks`) — prefer cloud-init, Packer images, or native provider resources.
3. **Ephemeral Secrets & OIDC Workload Identity**: Prefer OIDC short-lived CI federation over static `AWS_ACCESS_KEY_ID` / service-account JSON keys, and adopt `ephemeral` resources / write-only attributes (`*_wo`) where supported to keep secrets completely out of `.tfstate`.
4. **Composable Small State Roots**: Split blast-radius domains (networking, data, compute) into separate small state roots rather than one giant monolithic state file.
