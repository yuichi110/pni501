# Validation, Plan & Native Test Standards (HCL / Terraform / OpenTofu)

## Core Principles
1. **Static Validation & Policy-as-Code Gates**: Run `terraform fmt -check`, `terraform validate`, `tflint`, and `trivy config` / `checkov` / OPA Conftest in CI on every change.
2. **Native `terraform test` (`*.tftest.hcl`) & Terratest Suites**: Verify reusable modules with Terraform 1.6+ native `tests/*.tftest.hcl` (`command = plan` mock-provider unit tests + `assert { condition = ... }`) or Terratest (`AstFacts.test_functions_count`).
3. **Deterministic Plan Review**: Review `terraform plan` diffs in PRs before `apply` and test variable `validation` failure cases (`expect_failures = [var.foo]`) offline using mocked providers (`mock_provider`).
4. **Meaningful Assertions**: Every `run` block in `*.tftest.hcl` must contain explicit `assert` or `expect_failures` checks (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `fmt`/`validate`/`tflint`/Trivy gates plus `*.tftest.hcl` (or Terratest) assertions covering valid and invalid inputs.
- **`WARN`**: Static lint/validate gates exist without `*.tftest.hcl` module assertions.
- **`FAIL`**: Zero automated validation or IaC security scanning before `apply`.
