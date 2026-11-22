# Code Quality & Cloud Security Standards (HCL / Terraform / OpenTofu)

## Core Principles
1. **Least-Privilege Cloud Security & Encryption-by-Default**: Never expose admin/DB ports to `0.0.0.0/0` (CWE-284), never disable storage/DB/transport encryption (`encrypted = false`; CWE-311), never attach wildcard IAM (`"Action": "*"`, `"Resource": "*"`), and never commit hardcoded secrets or `.tfstate` files (`AstFacts.dangerous_sinks`, `AstFacts.hardcoded_secrets`).
2. **Formatting, TFLint & Clean Module Layout**: Format with `terraform fmt -check -recursive`, lint with `tflint`, follow standard module layout (`versions.tf`, `main.tf`, `variables.tf`, `outputs.tf`), and document every `variable` and `output` with a clear `description` (`AstFacts.docstring_coverage_pct`).
3. **Remote Encrypted State & Locking**: Configure a remote encrypted backend (S3 + locking, GCS, Terraform Cloud) — never rely on local `terraform.tfstate` for shared environments — and guard stateful resources (databases, KMS keys, buckets) with `lifecycle { prevent_destroy = true }`.
4. **Stable Addressing (`for_each` Over `count`)**: Prefer `for_each` (keyed by stable names) over numeric `count` for lists of distinct resources so inserting/removing an element does not destroy unrelated infrastructure (`AstFacts.bug_risk_idioms`).

## Evaluation Thresholds
- **`PASS`**: Zero `0.0.0.0/0` admin exposure / `encrypted = false` / wildcard IAM / hardcoded secrets, remote state configured, `for_each` addressing, and variable/output descriptions `>= 80%`.
- **`WARN`**: Missing `description` on internal outputs/variables or `count` used on non-critical lists.
- **`FAIL`**: Public `0.0.0.0/0` DB/SSH ingress, `encrypted = false`, wildcard IAM `*:*`, committed `.tfstate`/secrets, or `local-exec` shell injection.
