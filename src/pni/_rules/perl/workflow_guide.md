# Perl Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Perl (`cpanfile`, `Makefile.PL`, `Build.PL`, `*.pm`/`*.pl`) repositories.

---

## 1. Mapping `targets` by Perl Repository Layout

Inspect `cpanfile`, `Makefile.PL`, `Build.PL`, and `lib/`/`t/` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard CPAN Distribution / App** | `lib/**/*.pm`, `bin/`, `t/*.t`, `cpanfile` | `source: ["lib", "bin"]`<br>`tests: ["t"]`<br>`docs: ["README.md"]` |
| **Legacy Perl Scripts / CGI App** | `*.pl`, `*.pm`, `cgi-bin/`, `t/` | `source: ["."]` *(exclude `local/` Carton dir via `targets.exclude`)*<br>`tests: ["t", "tests"]` |
| **Polyglot Monorepo (e.g. Legacy Perl + Python/Go)** | `legacy-perl/`, `services/api/` | Create a `scope: component` workflow (`targets.root: "legacy-perl"`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Perl Actions & Rules

1. **Core Built-in Perl Actions**:
   - `repo_structure_audit` (`perl` scope): Auto-runs `project_inspect` for `cpanfile`, `cpanfile.snapshot`, `Makefile.PL`/`Build.PL`, Perl version floor, and supply-chain hygiene.
   - `perl_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="perl"`) to detect missing `use strict`/`use warnings`, 2-arg `open` pipe injection, string `eval` CWE-94, shell injection, mutable globals, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records entry points (`bin/`, Mojolicious/Dancer2/PSGI apps, cron scripts), module layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `perl_test_audit` (`needs: [ast_and_quality]`): Evaluates `t/*.t` (`Test2::V0`/`Test::More`/`prove`) suites and coverage against `perl/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Perl harness image via `.pni/dockerfiles/perl/cpan.dockerfile`, runs `perl -c` syntax checks and `prove` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Perl

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Perl)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Perl AST/CPAN analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "lib"
    - "bin"
  tests:
    - "t"
    - "tests"
  docs:
    - "README.md"
  exclude:
    - "local/**"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: perl_ast_audit
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
    uses: perl_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
