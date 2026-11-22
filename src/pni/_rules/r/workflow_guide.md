# R Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for R (`DESCRIPTION`, `renv.lock`, `*.R`) repositories.

---

## 1. Mapping `targets` by R Project Layout

Inspect `DESCRIPTION`, `NAMESPACE`, `renv.lock`, and `R/`/`tests/` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard CRAN / R Package** | `R/*.R`, `tests/testthat/test-*.R`, `DESCRIPTION` | `source: ["R"]`<br>`tests: ["tests/testthat", "tests"]`<br>`docs: ["README.md", "DESCRIPTION"]` |
| **Shiny App / Plumber API / Pipeline** | `R/`, `app.R` or `plumber.R`, `renv.lock`, `tests/` | `source: ["R", "."]` *(exclude `renv/` via `targets.exclude`)*<br>`tests: ["tests"]` |
| **Polyglot Data Monorepo (e.g. R + Python)** | `r-analytics/`, `python-api/` | Create a `scope: component` workflow (`targets.root: "r-analytics"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting R Actions & Rules

1. **Core Built-in R Actions**:
   - `repo_structure_audit` (`r` scope): Auto-runs `project_inspect` for `DESCRIPTION`, `NAMESPACE`, `renv.lock` (exempting CRAN packages), R version bounds, and supply-chain hygiene.
   - `r_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="r"`) to extract `roxygen2` coverage, `<<-` super-assignment / `attach()` global state, `eval(parse())` / `system()` CWE sinks, complexity, and Plumber routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records entry points (`NAMESPACE` exports, `app.R`, `plumber.R`, batch scripts), module layering, and data flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `r_test_audit` (`needs: [ast_and_quality]`): Evaluates `testthat` suites, deterministic seed isolation, assertion quality, and `covr` coverage against `r/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated R harness image via `.pni/dockerfiles/r/r.dockerfile`, runs `testthat` / `R CMD check` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for R

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (R)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic R AST/DESCRIPTION analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "R"
    - "src"
  tests:
    - "tests/testthat"
    - "tests"
  docs:
    - "README.md"
  exclude:
    - "renv/**"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: r_ast_audit
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
    uses: r_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
