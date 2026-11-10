# Go Workflow Authoring Best Practices

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Go (`go.mod`) repositories.

---

## 1. Mapping `targets` by Go Module Layout

Inspect `go.mod` and package directories to configure `targets` accurately. Note that PNI automatically separates production `*.go` files from co-located `*_test.go` files even when `source` and `tests` point to the same directories:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Root Package / Flat Module** | `*.go`, `*_test.go`, `go.mod` | `source: ["."]`<br>`tests: ["."]`<br>`docs: ["README.md"]` |
| **Standard `cmd/` + `internal/` + `pkg/`** | `cmd/app`, `internal/...`, `pkg/...` | `source: ["cmd", "internal", "pkg"]`<br>`tests: ["cmd", "internal", "pkg"]`<br>`docs: ["README.md"]` |
| **Multi-Module / `go.work` Monorepo** | `services/auth/go.mod`, `pkg/sdk/go.mod` | Create per-module workflows (`auth_audit.yaml` with `root: "services/auth"`) or list explicit module directories in `source` and `tests` |

---

## 2. Selecting Go Actions & Rules

1. **Core Built-in Go Actions**:
   - `repo_structure_audit` (`go` scope): Inspects `go.mod`, `go.sum`, Go version directives, direct vs `// indirect` dependencies, and local `replace` directives.
   - `architecture_analysis`: Records system archetype, entry points (`cmd/*/main.go`, HTTP routers, gRPC servers, Cobra CLIs), internal package layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `go_ast_audit`: Parses `*.go` files once via `ast-grep-py` (`lang="go"`) to extract import grouping/dot-imports, `any`/`interface{}` & `unsafe.Pointer` usage, GoDoc comment coverage on exported symbols, cognitive complexity, ignored errors (`_ = ...`), `panic(...)` in library packages, `defer` inside loops, package-level `var` state, HTTP/SQL/exec CWE sinks, and Gin/Echo/Fiber/Chi/net-http routes.
   - `go_test_audit`: Evaluates co-located `*_test.go` suites (`TestXxx`, `BenchmarkXxx`, `FuzzXxx`), assertion/helper coverage, and package test alignment.
   - `container_runtime_audit`: Builds an isolated Go harness image via `.pni/dockerfiles/.../Dockerfile`, runs `go test -v -coverprofile=/out/coverage.out ./...` and `go vet ./...` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit`: Runs Trivy (`security_scan`) against `go.mod`/`go.sum` and the resolved container image, evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints`.

---

## 3. Recommended `full_audit.yaml` Template for Go

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Go)
description: Deterministic Go AST/module analysis, 3-aspect grounded architecture recording, AI rule interpretation, score emission, and drawlib report creation.

targets:
  root: "."
  source:
    - "."
  tests:
    - "."
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: go_ast_audit

  - id: arch_recording
    uses: architecture_analysis

  - id: test_health
    uses: go_test_audit

  - id: runtime_verification
    uses: container_runtime_audit

  - id: security_audit
    uses: security_vulnerability_audit

  - id: output_score
    uses: emit_score

  - id: create_report
    uses: write_drawlib_report
```
