# Breaking-Change & Schema Verification Standards (Protocol Buffers)

## Core Principles
1. **Mandatory `buf lint` & `buf breaking` CI Gates**: Run `buf lint` and `buf breaking --against '.git#branch=main'` on every pull request so accidental wire-breaking or JSON-breaking contract changes are blocked automatically.
2. **Codegen Freshness Check**: Verify generated stubs (`buf generate` + `git diff --exit-code` when committed) stay 100% synchronized with `.proto` definitions.
3. **Contract Serialization & Golden Round-Trip Tests**: Test backward/forward wire compatibility and `protovalidate` constraint rules in consumer/provider test suites (`AstFacts.test_functions_count`).
4. **DSL Exemption**: Evaluate `.proto` verification via `buf lint`, `buf breaking`, and contract round-trip checks rather than line-coverage metrics on `.proto` files.

## Evaluation Thresholds
- **`PASS`**: Automated `buf lint` + `buf breaking` CI gates and verified codegen sync.
- **`WARN`**: `buf lint` configured without `buf breaking` backward-compatibility checks.
- **`FAIL`**: Zero schema linting/breaking-change checks on shared cross-service RPC contracts.
