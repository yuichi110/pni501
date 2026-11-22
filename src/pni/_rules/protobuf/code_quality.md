# Code Quality & Wire-Compatibility Standards (Protocol Buffers)

## Core Principles
1. **Explicit Versioned `package` & Standard Naming (`buf lint`)**: Declare a versioned package (`package acme.orders.v1;`) in every `.proto` file (`AstFacts.bug_risk_idioms`), enforce Google/Buf naming (`PascalCase` messages/services/RPCs, `snake_case` fields, `PREFIX_UNSPECIFIED = 0` zero-value enum entries), and format with `buf format`.
2. **Strict Wire-Number Integrity (Zero Duplicate or Reused Field Numbers)**: NEVER duplicate field tag numbers within a message (`AstFacts.bug_risk_idioms`), and whenever removing a field or enum value, **ALWAYS** add `reserved <tag>;` and `reserved "<name>";` so wire-incompatible tag reuse can never corrupt serialized payloads.
3. **Request/Response Envelope Pattern**: Give every gRPC method dedicated `FooRequest` and `FooResponse` message wrappers (never reuse domain entities directly or `google.protobuf.Empty` when future evolution is likely) so APIs evolve backward-compatibly.
4. **Schema Documentation**: Document services, RPCs, messages, and non-obvious fields with leading `//` comments (`AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Versioned `package`, `buf lint` clean, zero duplicate/reused field tags, `*_UNSPECIFIED = 0` enums, dedicated RPC request/response messages, and schema comments `>= 80%`.
- **`WARN`**: Missing comments on internal fields or missing `buf.yaml` config.
- **`FAIL`**: Duplicate field numbers, missing `package`, reused wire tags without `reserved`, or breaking wire changes on versioned `v1` APIs.
