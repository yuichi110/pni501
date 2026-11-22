# Go Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Go (`go.mod`) repositories.

---

## 1. Mapping `targets` by Go Module Layout

Inspect `go.mod` and package directories to configure `targets` accurately. Note that PNI automatically separates production `*.go` files from co-located `*_test.go` files even when `source` and `tests` point to the same directories:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Root Package / Flat Module** | `*.go`, `*_test.go`, `go.mod` | `source: ["."]`<br>`tests: ["."]`<br>`docs: ["README.md"]` |
| **Standard `cmd/` + `internal/` + `pkg/`** | `cmd/app`, `internal/...`, `pkg/...` | `source: ["cmd", "internal", "pkg"]`<br>`tests: ["cmd", "internal", "pkg"]`<br>`docs: ["README.md"]` |
| **Multi-Module / `go.work` Monorepo** | `services/auth/go.mod`, `pkg/sdk/go.mod` | Create per-module `scope: component` workflows (`auth_audit.yaml` with `root: "services/auth"`) + one `category: rollup` workflow (`includes:`), or list explicit module directories in `source` and `tests` |

---

## 2. Selecting Go Actions & Rules

1. **Core Built-in Go Actions**:
   - `repo_structure_audit` (`go` scope): Auto-runs `project_inspect` for `go.mod`, `go.sum`, Go version directives, direct vs `// indirect` dependencies, and local `replace` directives.
   - `go_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="go"`) to extract import grouping/dot-imports, `any`/`interface{}` & `unsafe.Pointer` usage, GoDoc comment coverage on exported symbols, cognitive complexity, partially ignored errors (`val, _ := ...`), `panic(...)` in library packages, `defer` inside loops, package-level `var` state, HTTP/SQL/exec CWE sinks, and Gin/Echo/Fiber/Chi/net-http routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (`cmd/*/main.go`, HTTP routers, gRPC servers, Cobra CLIs), internal package layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `go_test_audit` (`needs: [ast_and_quality]`): Evaluates co-located `*_test.go` suites (`TestXxx`, `BenchmarkXxx`, `FuzzXxx`), assertion/helper coverage, and package test alignment.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Go harness image via `.pni/dockerfiles/.../Dockerfile`, runs `go test -v -coverprofile=/out/coverage.out ./...` and `go vet ./...` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `go.mod`/`go.sum` and the resolved container image, evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Go

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Go)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Go AST/module analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

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
    needs: [repo_and_deps]

  - id: runtime_verification
    uses: container_runtime_audit
    needs: [repo_and_deps]
    when: "has_runtime_harness"

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  # Optional archetype audit: service_readiness_audit | cli_guidelines_audit | library_hygiene_audit
  - id: test_health
    uses: go_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
