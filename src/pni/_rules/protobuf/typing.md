# Schema Typing, Well-Known Types & Presence Standards (Protocol Buffers)

## Core Principles
1. **Standard Well-Known Types (WKTs) Over Primitive Hacks**: Use `google.protobuf.Timestamp`, `google.protobuf.Duration`, `google.protobuf.FieldMask`, and structured `Money` messages instead of raw `int64` epoch numbers, ISO strings, or floating-point `float`/`double` for currency (`AstFacts.type_safety_coverage_pct`).
2. **Explicit Field Presence (`optional`) & `oneof` Modeling**: Use `optional` on `proto3` scalar fields where "unset" differs from `0`/`false`/`""` (or Protobuf Editions 2023 explicit presence), and model mutually exclusive payload variants with `oneof` instead of loosely correlated nullable fields.
3. **Avoid `google.protobuf.Struct` / `Any` Overuse**: Prefer concrete typed messages over untyped `google.protobuf.Struct` or opaque `bytes` JSON blobs in core RPC contracts (`AstFacts.weak_type_usages`).
4. **Validated Numeric & String Bounds**: Document or enforce constraints declaratively via `buf.validate` (`protovalidate`) annotations on external API schemas.

## Evaluation Thresholds
- **`PASS`**: Standard WKTs (`Timestamp`/`Duration`), explicit presence/`oneof`, concrete typed messages, and zero `float`/`double` currency fields.
- **`WARN`**: Isolated `google.protobuf.Struct` metadata bags or missing `optional` where zero vs unset matters.
- **`FAIL`**: Floating-point monetary fields, untyped string/bytes JSON blobs defeating Protobuf typing, or inconsistent enum zero-values.
