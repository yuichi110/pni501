# Buf Module & Schema Dependency Standards (Protocol Buffers)

## Core Principles
1. **Declarative `buf.yaml` + Committed `buf.lock`**: Manage external Protobuf schema imports (`googleapis`, `protovalidate`) via `buf.yaml` (`version: v2`) and commit `buf.lock` pinning exact BSR commit digests (`ProjectFacts.lockfiles_found`, `ProjectFacts.unpinned_dependencies`). Standalone zero-import `.proto` directories legitimately omit `buf.lock`.
2. **Explicit `buf.gen.yaml` Codegen Pinning**: Pin `protoc` / remote Buf plugin versions (`buf.build/protocolbuffers/go:v1.36.x`, etc.) explicitly in `buf.gen.yaml` — never generate code with unpinned floating plugin versions.
3. **Zero Unmanaged Vendored `google/` Copies**: Avoid copying raw `google/api/*.proto` files by hand into repositories when Buf Schema Registry dependencies track them cleanly.
4. **Clean Package-to-Directory Alignment**: Match directory paths (`proto/acme/billing/v1/billing.proto`) strictly to `package acme.billing.v1;` so imports remain deterministic across languages.

## Evaluation Thresholds
- **`PASS`**: `buf.yaml` v2 + `buf.lock` (when using external imports), pinned `buf.gen.yaml` plugins, and package-aligned directory layout.
- **`WARN`**: Legacy `buf.yaml` v1 or manual `protoc` scripts without pinned plugin versions.
- **`FAIL`**: Unpinned floating codegen plugins, broken cross-file imports, or stale diverging copies of shared `.proto` contracts.
