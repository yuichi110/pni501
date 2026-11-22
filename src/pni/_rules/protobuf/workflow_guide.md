# Protocol Buffers Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing standalone API/IDL repositories (`*.proto`, `buf.yaml`). In polyglot microservice monorepos, PNI also scans `.proto` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by Protobuf Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Dedicated API / IDL Repo** | `proto/<org>/<svc>/v1/*.proto`, `buf.yaml`, `buf.lock` | `source: ["proto", "api"]`<br>`docs: ["README.md"]` |
| **Polyglot gRPC Monorepo** | `proto/` + `services/go/` + `services/python/` | Create per-service `scope: component` workflows + `category: rollup` (automatically scans `.proto` as Companion DSL) |

---

## 2. Selecting Protobuf Actions & Rules

1. **Core Built-in Protobuf Actions**:
   - `repo_structure_audit` (`protobuf` scope): Auto-runs `project_inspect` for `buf.yaml`, `buf.lock`, `buf.gen.yaml`, and governance.
   - `protobuf_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="protobuf"`) to detect `proto2` legacy syntax, missing `package`, duplicate field numbers, enum/naming issues, and schema docs.
   - `protobuf_test_audit` (`needs: [ast_and_quality]`): Evaluates `buf lint`, `buf breaking`, and codegen sync gates against `protobuf/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for Protocol Buffers

```yaml
id: full_audit
category: audit
name: Full Protobuf Schema Audit & Report (Protocol Buffers)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Protobuf AST & security analysis, grounded API contract map, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "proto"
    - "protos"
    - "api"
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: protobuf_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: protobuf_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
