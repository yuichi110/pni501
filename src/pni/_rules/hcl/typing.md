# Variable Typing, Validation & Sensitivity Standards (HCL / Terraform)

## Core Principles
1. **Explicit `type` & `validation` Blocks on Every `variable`**: Declare strict Terraform types (`string`, `number`, `bool`, `object({ ... })`, `map(string)`) instead of untyped `any` variables (`AstFacts.weak_type_usages`), and add `validation { condition = ...; error_message = ... }` for enums, CIDRs, and naming constraints (`AstFacts.type_safety_coverage_pct`).
2. **Mandatory `sensitive = true` for Secret Variables & Outputs**: Mark every credential, token, connection string, or private key variable/output with `sensitive = true` (and `ephemeral = true` on Terraform 1.10+ / OpenTofu 1.10+) so secrets never print in `terraform plan` logs.
3. **Explicit `nullable = false` & `optional(...)` Attributes**: Use `nullable = false` where `null` is invalid and `optional(type, default)` in `object(...)` schemas to eliminate awkward `coalesce`/`try` fallbacks.
4. **Avoid Fragile String Interpolation & Untyped Maps**: Keep `locals` structured and avoid `jsonencode` / raw string templates when typed `data "aws_iam_policy_document"` or structured blocks exist.

## Evaluation Thresholds
- **`PASS`**: Explicit strict `type` + `validation` + `sensitive = true` on variables/outputs, minimal `any` types, and structured policy documents.
- **`WARN`**: Missing `validation` blocks on minor optional inputs or isolated `any` types.
- **`FAIL`**: Untyped variables across root/reusable modules or credentials missing `sensitive = true`.
