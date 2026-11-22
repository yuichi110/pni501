# Makefile Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing standalone Makefile build systems (`Makefile`, `GNUmakefile`, `*.mk`). In polyglot repos, PNI automatically scans Makefiles as a Companion DSL during `scope: repo` and `category: rollup` audits.

---

## 1. Mapping `targets` by Makefile Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Build Orchestration / Make Library Repo** | `Makefile`, `mk/*.mk`, `README.md` | `source: ["."]`<br>`docs: ["README.md"]` |
| **Application Repo with Makefile** | `src/` (C/Go/Python) + `Makefile` | Audit the primary app language (`scope: repo`) so `Makefile` is scanned automatically as a Companion DSL |

---

## 2. Selecting Make Actions & Rules

1. **Core Built-in Make Actions**:
   - `repo_structure_audit` (`make` scope): Auto-runs `project_inspect` for build layout, toolchain config, and governance.
   - `make_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="make"`) to check `.PHONY`, `.DELETE_ON_ERROR`, `rm -rf $(VAR)/` & `curl | sh` sinks, recursive `=$(shell ...)` traps, and recipe complexity.
   - `make_test_audit` (`needs: [ast_and_quality]`): Evaluates `checkmake`, `make -n`, and parallel-safety (`make -j`) against `make/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets.

---

## 3. Recommended `full_audit.yaml` DAG Template for Makefile

```yaml
id: full_audit
category: audit
name: Full Build Definition Audit & Report (Makefile)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Makefile AST & security analysis, grounded build graph review, score+SARIF emission, and Drawlib report.

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
    uses: make_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: make_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
