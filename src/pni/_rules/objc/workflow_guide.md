# Objective-C Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Objective-C (`*.m`, `*.mm`, `*.h`, `Podfile`) repositories.

---

## 1. Mapping `targets` by Objective-C Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard iOS / macOS Framework or App** | `Sources/` or `Classes/`, `Tests/`, `Podfile` | `source: ["Sources", "Classes"]`<br>`tests: ["Tests"]`<br>`docs: ["README.md"]` |
| **Mixed Swift + Objective-C App** | `Sources/ObjC/`, `Sources/Swift/` | Create separate `scope: component` workflows (`objc` + `swift`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Objective-C Actions & Rules

1. **Core Built-in Objective-C Actions**:
   - `repo_structure_audit` (`objc` scope): Auto-runs `project_inspect` for `Podfile`/`Podfile.lock`/`*.podspec`, platform constraints, and supply-chain hygiene.
   - `objc_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="objc"`) to extract HeaderDoc coverage, ARC/retain-cycle risks, format-string & `NSKeyedUnarchiver` CWE sinks, complexity, and nullability/generics hygiene.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records `AppDelegate`/public framework classes, delegate/protocol boundaries, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `objc_test_audit` (`needs: [ast_and_quality]`): Evaluates XCTest `*Tests.m` suites and isolation against `objc/testing`.
   - `container_runtime_audit` (`when: "has_runtime_harness"`): Automatically skipped cleanly on Linux hosts (Objective-C Apple SDKs have `has_runtime_harness=False`).
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `Podfile.lock` / workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Objective-C

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Objective-C)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Objective-C AST analysis, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "Sources"
    - "Classes"
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
    uses: objc_ast_audit
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

  - id: test_health
    uses: objc_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
