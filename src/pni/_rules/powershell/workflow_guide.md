# PowerShell Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for PowerShell (`*.ps1`, `*.psm1`, `*.psd1`) repositories.

---

## 1. Mapping `targets` by PowerShell Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **PowerShell Module** | `src/Public/*.ps1`, `src/Private/*.ps1`, `*.psd1`, `Tests/*.Tests.ps1` | `source: ["src"]`<br>`tests: ["Tests", "tests"]`<br>`docs: ["README.md"]` |
| **Automation Scripts Repo** | `scripts/*.ps1`, `tests/*.Tests.ps1` | `source: ["scripts", "."]`<br>`tests: ["tests", "Tests"]` |
| **Polyglot Monorepo (e.g. C# + PowerShell Ops)** | `src/`, `ops-pwsh/` | Create a `scope: component` workflow (`targets.root: "ops-pwsh"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting PowerShell Actions & Rules

1. **Core Built-in PowerShell Actions**:
   - `repo_structure_audit` (`powershell` scope): Auto-runs `project_inspect` for `.psd1` manifests, `#Requires` pins, and supply-chain hygiene.
   - `powershell_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="powershell"`) to extract `Invoke-Expression` CWE-94 sinks, plaintext credentials, `$global:` state, complexity, and Comment-Based Help coverage.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records exported cmdlets (`Public/` vs `Private/`), external API/cloud boundaries, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `powershell_test_audit` (`needs: [ast_and_quality]`): Evaluates Pester v5 `*.Tests.ps1` suites, mocking, and coverage against `powershell/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated `pwsh` + Pester harness image via `.pni/dockerfiles/powershell/pester.dockerfile`, runs Pester offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for PowerShell

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (PowerShell)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic PowerShell AST analysis, Pester container runtime verification, security scan, grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
    - "scripts"
    - "."
  tests:
    - "tests"
    - "Tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: powershell_ast_audit
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
    uses: powershell_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
