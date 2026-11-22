# XML Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing XML schema libraries, XSLT transforms, or XML manifest repositories (`*.xml`, `*.xsd`, `*.xsl`). In application repos, PNI also scans `.xml` files automatically via `companion_ast_facts`.

---

## 1. Mapping `targets` by XML Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **XSD / XSLT / XML Config Repo** | `schemas/*.xsd`, `transforms/*.xsl`, `config/*.xml` | `source: ["."]`<br>`docs: ["README.md"]` |
| **App Repo with XML Manifests (`pom.xml`, `AndroidManifest.xml`)** | `src/` (Java/Kotlin/C#) + `*.xml` | Audit the primary app language (`scope: repo`) so `.xml` is scanned automatically as a Companion DSL |

---

## 2. Selecting XML Actions & Rules

1. **Core Built-in XML Actions**:
   - `repo_structure_audit` (`xml` scope): Auto-runs `project_inspect` for XML layout, schema catalog hygiene, secret files, and governance.
   - `xml_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="xml"`) to detect XXE/DTD entity declarations (CWE-611), hardcoded credentials, insecure manifest flags, and namespace/schema hygiene.
   - `xml_test_audit` (`needs: [ast_and_quality]`): Evaluates `xmllint --noout --nonet`, XSD/RNG fixtures, and XSpec tests against `xml/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for XML

```yaml
id: full_audit
category: audit
name: Full XML Schema & Manifest Audit & Report (XML)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic XML AST & security analysis, grounded schema/manifest map, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: xml_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: xml_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
