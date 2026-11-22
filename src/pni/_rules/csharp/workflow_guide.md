# C# / .NET Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for C# / .NET (`*.csproj`, `*.sln`) repositories.

---

## 1. Mapping `targets` by .NET Solution Layout

Inspect `*.sln`, `*.csproj`, `Directory.Build.props`, and `Directory.Packages.props` to configure `targets` accurately (note PNI automatically excludes `*.designer.cs` and `*.g.cs`):

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Solution (`src/` + `tests/`)** | `src/App/*.cs`, `tests/App.Tests/*.cs` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Single Project Root** | `Program.cs`, `Services/`, `App.csproj` | `source: ["."]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Multi-Service / Polyglot Monorepo** | `services/billing/*.csproj`, `frontend/` | Create per-service `scope: component` workflows (`root: "services/billing"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting C# Actions & Rules

1. **Core Built-in C# Actions**:
   - `repo_structure_audit` (`csharp` scope): Auto-runs `project_inspect` for `*.csproj`/`*.sln`, `Directory.Packages.props`, `packages.lock.json`, TFM (`net8.0`/`net9.0`), NuGet pinning, and supply-chain hygiene.
   - `csharp_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="csharp"`) to extract XML doc coverage, `dynamic`/nullability issues, `async void`/`.Result`/`.Wait()` deadlocks, empty `catch` blocks, cognitive complexity, `BinaryFormatter`/SQLi/XSS/TLS-bypass CWE sinks, and ASP.NET Core endpoints.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (`Program.cs`, ASP.NET controllers/minimal APIs, `BackgroundService`), namespace layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `csharp_test_audit` (`needs: [ast_and_quality]`): Evaluates xUnit/NUnit/MSTest suites, assertion coverage, and isolation against `csharp/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated .NET SDK harness image via `.pni/dockerfiles/csharp/dotnet.dockerfile`, runs `dotnet test` + Cobertura coverage offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against NuGet packages / container images and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for C#

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (C#)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic C# AST/.NET analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
  tests:
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: csharp_ast_audit
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
    uses: csharp_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
