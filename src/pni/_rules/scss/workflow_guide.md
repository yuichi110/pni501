# SCSS Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing SCSS design-system libraries (`*.scss`). In frontend repos, PNI also scans `.scss` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by SCSS Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **SCSS Design System / Token Library** | `styles/**/*.scss`, `src/**/*.scss`, `package.json` | `source: ["styles", "src", "."]`<br>`docs: ["README.md"]` |
| **Frontend App with SCSS** | `src/` (TS/Vue/Svelte) + `styles/` | Audit the primary frontend language (`scope: repo`) so `.scss` is scanned automatically as a Companion DSL |

---

## 2. Selecting SCSS Actions & Rules

1. **Core Built-in SCSS Actions**:
   - `repo_structure_audit` (`scss` scope): Auto-runs `project_inspect` for `package.json` (`sass` vs EOL `node-sass`), `.stylelintrc*`, and governance.
   - `scss_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="scss"`) to inspect legacy `@import`, deep nesting, `!important` abuse, deprecated global functions, and SassDoc coverage.
   - `scss_test_audit` (`needs: [ast_and_quality]`): Evaluates `sass` compilation, `stylelint`, and `sass-true` CI gates against `scss/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against dependencies/workspace files.

---

## 3. Recommended `full_audit.yaml` DAG Template for SCSS

```yaml
id: full_audit
category: audit
name: Full Stylesheet Architecture Audit & Report (SCSS)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic SCSS AST & security analysis, grounded module/token topology, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "styles"
    - "src"
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: scss_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: scss_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
