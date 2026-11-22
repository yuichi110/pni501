# CSS Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing CSS design systems or stylesheet libraries (`*.css`). In frontend repos, PNI also scans `.css` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by CSS Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Design System / Stylesheet Library** | `styles/*.css`, `src/*.css`, `.stylelintrc.json` | `source: ["styles", "src", "public", "."]`<br>`docs: ["README.md"]` |
| **Web App with CSS** | `src/` (TS/Vue/Svelte) + `styles/` | Audit the primary frontend language (`scope: repo`) so `.css` is scanned automatically as a Companion DSL |

---

## 2. Selecting CSS Actions & Rules

1. **Core Built-in CSS Actions**:
   - `repo_structure_audit` (`css` scope): Auto-runs `project_inspect` for `.stylelintrc*`, `.browserslistrc`, asset config, and governance.
   - `css_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="css"`) to inspect selector complexity, `!important` abuse, `outline: none` a11y gaps, remote `@import`, and design-token hygiene.
   - `css_test_audit` (`needs: [ast_and_quality]`): Evaluates `stylelint`, contrast, and visual-regression CI checks against `css/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/dependencies.

---

## 3. Recommended `full_audit.yaml` DAG Template for CSS

```yaml
id: full_audit
category: audit
name: Full Stylesheet Quality & Accessibility Audit & Report (CSS)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic CSS AST & security analysis, grounded token/layer architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "styles"
    - "src"
    - "public"
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: css_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: css_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
