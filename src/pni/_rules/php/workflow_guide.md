# PHP Workflow Authoring Best Practices

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for PHP repositories (both modern Composer / Laravel / Symfony applications and legacy Composer-less raw PHP / WordPress projects).

---

## 1. Mapping `targets` by PHP Repository Layout

Inspect `composer.json`, `artisan`, `wp-config.php`, or root `*.php` scripts to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Laravel Application** | `app/`, `routes/`, `config/`, `tests/`, `README.md` | `source: ["app", "routes"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Modern Composer / Symfony / PSR-4 Library** | `src/`, `tests/`, `composer.json`, `README.md` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Legacy Raw PHP ("素PHP") Web App** | `index.php`, `login.php`, `includes/`, `public/` (often no `composer.json` or `tests/`) | `source: ["."]` (automatically excludes `vendor/` and `tests/`)<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **WordPress Plugin or Theme** | `my-plugin.php` (`Plugin Name:` header), `includes/`, `admin/` | `source: ["."]`<br>`tests: ["tests"]`<br>`docs: ["README.md", "readme.txt"]` |

---

## 2. Selecting PHP Actions & Rules

1. **Core Built-in PHP Actions**:
   - `repo_structure_audit` (`php` scope): Inspects `composer.json` / `composer.lock` (or flags Composer-less `raw_php`), PHP version constraints (`< 8.1` EOL), PSR-4 autoloading, WordPress headers, and supply-chain hygiene.
   - `php_ast_audit`: Parses PHP & mixed HTML+PHP files once via `ast-grep-py` (`lang="php"`) to extract namespace/`use` vs `include`/`require` hygiene, `declare(strict_types=1)` & type-hint coverage, PHPDoc `@param` alignment, superglobal coupling (`$_GET`/`$_POST`), `@` error suppression, CWE dangerous sinks (SQLi, XSS, LFI, Command Injection, `unserialize`, `md5` + `==` type juggling), API endpoints, and Laravel / WordPress framework violations.
   - `architecture_analysis`: Records system archetype, HTTP/CLI/WordPress hook entry points, namespace or include layering, and execution flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `php_test_audit`: Evaluates PHPUnit / Pest test suite completeness, assertion density, and test isolation.
   - `container_runtime_audit`: Builds an isolated PHP container via `.pni/dockerfiles/.../Dockerfile` (`composer.dockerfile` or `raw.dockerfile`), runs `php -l` syntax checks across all `.php` files, executes PHPUnit + `pcov` Clover coverage offline (`--network=none`), and runs archetype smoke checks (`artisan`, `php -S`, PSR-4 autoload, or WordPress plugin bootstrap stub).
   - `security_vulnerability_audit`: Runs Trivy (`security_scan`) against `composer.lock`, `Dockerfile` (e.g., aging `php:7.4-apache` root images), secrets, and resolved container OS packages, synthesizing findings with AST `dangerous_sinks` and `api_endpoints`.

---

## 3. Recommended `full_audit.yaml` Template for PHP

```yaml
id: full_audit
name: Full PHP Project Health Audit & Report
description: Deterministic PHP AST/Composer/Raw-PHP analysis, 3-aspect architecture recording, container syntax/test/Trivy verification, and Drawlib PDF report.

targets:
  root: "."
  source:
    - "app"
    - "src"
    - "routes"
  tests:
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: php_ast_audit

  - id: arch_recording
    uses: architecture_analysis

  - id: test_health
    uses: php_test_audit

  - id: runtime_verification
    uses: container_runtime_audit

  - id: security_audit
    uses: security_vulnerability_audit

  - id: output_score
    uses: emit_score

  - id: create_report
    uses: write_drawlib_report
```

Verify with `pni workflows show full_audit` before running `pni workflows start full_audit`.
