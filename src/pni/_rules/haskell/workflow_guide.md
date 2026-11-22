# Haskell Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Haskell (`*.cabal`, `cabal.project`, `stack.yaml`) repositories.

---

## 1. Mapping `targets` by Haskell Package Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard Cabal / Stack Package** | `src/**/*.hs`, `app/Main.hs`, `test/*Spec.hs` | `source: ["src", "app"]`<br>`tests: ["test"]`<br>`docs: ["README.md"]` |
| **Multi-Package `cabal.project` / Stack Workspace** | `packages/core/src`, `packages/api/src` | List explicit package `src` dirs or create per-package `scope: component` workflows + one `category: rollup` workflow |

---

## 2. Selecting Haskell Actions & Rules

1. **Core Built-in Haskell Actions**:
   - `repo_structure_audit` (`haskell` scope): Auto-runs `project_inspect` for `*.cabal`, `stack.yaml`, `cabal.project`, GHC/PVP bounds, and supply-chain hygiene.
   - `haskell_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="haskell"`) to extract Haddock coverage, partial functions (`head`/`fromJust`/`error`), `unsafePerformIO`/`unsafeCoerce`, `Debug.Trace`, complexity, and Servant/Yesod/Scotty routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records pure core vs IO shell boundaries, entry points (`app/Main.hs`, Servant APIs), module layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `haskell_test_audit` (`needs: [ast_and_quality]`): Evaluates Hspec/Tasty/QuickCheck suites and HPC coverage against `haskell/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated GHC/Cabal harness image via `.pni/dockerfiles/haskell/cabal.dockerfile`, runs tests offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Haskell

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Haskell)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Haskell AST/Cabal analysis, container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "app"
  tests:
    - "test"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: haskell_ast_audit
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
    uses: haskell_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
