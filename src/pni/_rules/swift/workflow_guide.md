# Swift Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Swift (`Package.swift`) repositories.

---

## 1. Mapping `targets` by Swift Package Layout

Inspect `Package.swift` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard SwiftPM Package** | `Sources/<Target>/*.swift`, `Tests/<Target>Tests/*.swift` | `source: ["Sources"]`<br>`tests: ["Tests"]`<br>`docs: ["README.md"]` |
| **Multi-Target Server / CLI Repo** | `Sources/Core/`, `Sources/App/`, `Tests/` | `source: ["Sources"]`<br>`tests: ["Tests"]`<br>`docs: ["README.md"]` |
| **Polyglot Monorepo** | `ios/` or `swift-sdk/` + `backend/` | Create a `scope: component` workflow (`targets.root: "swift-sdk"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Swift Actions & Rules

1. **Core Built-in Swift Actions**:
   - `repo_structure_audit` (`swift` scope): Auto-runs `project_inspect` for `Package.swift`, `Package.resolved`, `swift-tools-version`, dependency pinning, and supply-chain hygiene.
   - `swift_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="swift"`) to extract DocC coverage, `!`/`try!`/`as!`/`fatalError` force-unwrap idioms, mutable `static var` globals, complexity, CWE sinks, and Vapor/Hummingbird routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records target boundaries, entry points (`@main`, Vapor routes, CLI commands), actor/service layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `swift_test_audit` (`needs: [ast_and_quality]`): Evaluates Swift Testing / XCTest suites, assertion quality, and isolation against `swift/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Swift harness image via `.pni/dockerfiles/swift/swiftpm.dockerfile`, runs `swift test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against project files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Swift

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Swift)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Swift AST/SwiftPM analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "Sources"
    - "src"
  tests:
    - "Tests"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: swift_ast_audit
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
    uses: swift_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
