# Ruby Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Ruby / Rails (`Gemfile`, `*.gemspec`) repositories.

---

## 1. Mapping `targets` by Ruby Repository Layout

Inspect `Gemfile`, `*.gemspec`, and `config/application.rb` to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Ruby on Rails Application** | `app/`, `lib/`, `spec/` or `test/`, `README.md` | `source: ["app", "lib"]`<br>`tests: ["spec", "test"]`<br>`docs: ["README.md"]` |
| **RubyGem Library** | `lib/`, `exe/` or `bin/`, `spec/`, `*.gemspec` | `source: ["lib"]`<br>`tests: ["spec", "test"]`<br>`docs: ["README.md"]` |
| **Rails + JS/TS Monorepo** | `backend/` (Rails) + `frontend/` (TypeScript) | Create per-component `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Ruby Actions & Rules

1. **Core Built-in Ruby Actions**:
   - `repo_structure_audit` (`ruby` scope): Auto-runs `project_inspect` for `Gemfile`, `Gemfile.lock` (exempting pure gems), `*.gemspec`, Ruby version constraints, dependency pinning, and supply-chain hygiene.
   - `ruby_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="ruby"`) to extract YARD/RDoc coverage, complexity, bare `rescue`/`eval`/`YAML.load`/`Marshal.load` idioms, global/class-var state, SQLi/XSS/command-injection CWE sinks, and Rails/Sinatra routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records system archetype, entry points (`config/routes.rb`, Rack/Sinatra apps, Sidekiq workers, CLI `exe/`), service/model layering, and flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `ruby_test_audit` (`needs: [ast_and_quality]`): Evaluates RSpec/Minitest coverage, assertion density, and deterministic isolation against `ruby/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Ruby harness image via `.pni/dockerfiles/ruby/bundler.dockerfile`, runs RSpec/Minitest offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `Gemfile.lock` and container images, correlating findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Ruby

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Ruby)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Ruby AST/Bundler analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "lib"
    - "app"
  tests:
    - "spec"
    - "test"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: ruby_ast_audit
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
    uses: ruby_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
