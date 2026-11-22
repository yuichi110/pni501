# Modern Protobuf (Proto3 / Editions 2023) & Buf v2 Idioms (`protobuf/modern_stack`)

## Core Principles
1. **Migrate Legacy `proto2` to `proto3` / Editions 2023**: Replace legacy `syntax = "proto2";` (especially `required` fields and `group` syntax, which cause permanent evolution hazards; `AstFacts.bug_risk_idioms`, `AstFacts.modernization_hints`) with `syntax = "proto3";` or `edition = "2023";`.
2. **Buf v2 & `protovalidate`**: Prefer `buf` CLI + `buf.validate` CEL validation rules over hand-coded per-language validation boilerplate and legacy `protoc-gen-validate`.
3. **Avoid Hardcoded Language Options When `buf.gen.yaml` Managed Mode Applies**: Prefer Buf managed mode for `go_package` / `java_package` consistency across multi-language monorepos.
4. **Security & Payload Boundaries**: Document max message size / pagination limits (`page_size`, `page_token`) on list RPCs to prevent unbounded response OOM/DoS.
