# HTML Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing static web sites or HTML template directories (`*.html`, `*.htm`). In web-app repos, PNI also scans `.html` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by HTML Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Static Site / Templates Repo** | `templates/*.html`, `public/*.html`, `README.md` | `source: ["templates", "public", "src", "."]`<br>`docs: ["README.md"]` |
| **Web App with Server Templates** | `src/` (Python/Go/PHP/Java) + `templates/` | Audit the primary app language (`scope: repo`) so `templates/` is scanned automatically as a Companion DSL |

---

## 2. Selecting HTML Actions & Rules

1. **Core Built-in HTML Actions**:
   - `repo_structure_audit` (`html` scope): Auto-runs `project_inspect` for site layout, CDN/asset references, and governance.
   - `html_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="html"`) to detect inline `onclick`/`javascript:` XSS sinks (CWE-79), missing `rel="noopener"`, missing SRI on CDN scripts, and semantic/accessibility issues.
   - `html_test_audit` (`needs: [ast_and_quality]`): Evaluates `html-validate`, `axe-core`/Lighthouse, and broken-link CI gates against `html/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for HTML

```yaml
id: full_audit
category: audit
name: Full Markup, Security & Accessibility Audit & Report (HTML)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic HTML AST & security analysis, grounded template structure review, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "templates"
    - "public"
    - "src"
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: html_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: html_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
