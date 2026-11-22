# Dart / Flutter Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Dart / Flutter (`pubspec.yaml`) repositories.

---

## 1. Mapping `targets` by Dart / Flutter Project Layout

Inspect `pubspec.yaml` to configure `targets` accurately (exclude generated `*.g.dart` / `*.freezed.dart` files via `targets.exclude`):

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Dart Package / CLI** | `lib/`, `bin/`, `test/`, `pubspec.yaml` | `source: ["lib", "bin"]`<br>`tests: ["test"]`<br>`exclude: ["**/*.g.dart", "**/*.freezed.dart"]` |
| **Flutter Application** | `lib/`, `test/`, `integration_test/` | `source: ["lib"]`<br>`tests: ["test"]`<br>`exclude: ["**/*.g.dart", "**/*.freezed.dart"]` |
| **Melos / Polyglot Monorepo** | `packages/*/lib`, `backend/` | Create per-package `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Dart Actions & Rules

1. **Core Built-in Dart Actions**:
   - `repo_structure_audit` (`dart` scope): Auto-runs `project_inspect` for `pubspec.yaml`, `pubspec.lock` (exempting published `pub.dev` libraries), Dart SDK bounds, dependency pinning, and supply-chain hygiene.
   - `dart_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="dart"`) to extract dartdoc coverage, `dynamic`/`!` nullability issues, empty catches, mutable top-level globals, complexity, and CWE sinks.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records entry points (`bin/`, `lib/main.dart`, Shelf/Dart Frog routes), state/repository layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `dart_test_audit` (`needs: [ast_and_quality]`): Evaluates `*_test.dart` unit/widget suites, assertion quality, and coverage against `dart/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Dart harness image via `.pni/dockerfiles/dart/pub.dockerfile`, runs `dart test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `pubspec.lock` / workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Dart

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Dart)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Dart AST/Pub analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "lib"
    - "bin"
  tests:
    - "test"
  docs:
    - "README.md"
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: dart_ast_audit
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
    uses: dart_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
