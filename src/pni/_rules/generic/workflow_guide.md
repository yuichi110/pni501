# Generic Multi-Language Audit Workflow Guide (Workflow v2)

Use this Workflow v2 DAG for any PNI-supported language (Rust, C#, Ruby, Kotlin, Swift, C/C++, Scala, Dart, Elixir, Perl, COBOL, R, Zig, Solidity, etc.) outside the 6 bespoke rule directories:

1. **Phase 0/1 — `confirm_plan` (Auto-Prepended Human Alignment Gate)**: Preview recon, discovered components, companion DSLs, and the validated Mermaid DAG (`pni workflows plan full_audit`), then confirm scope, focus areas, and disabled steps with the user.
2. **Wave 1 — `repo_structure_audit`**: Auto-runs `project_inspect` to inspect manifests, lockfiles, governance hygiene, and companion IaC/config files (`Dockerfile`, Terraform/HCL, CI YAML, Protobuf, SQL).
3. **Wave 2 (Parallel DAG Fan-Out after `repo_structure_audit`)**:
   - **`generic_ast_audit`**: Auto-runs deterministic Tree-sitter AST analysis (`ast_analyze`) to extract LOC, symbol inventory, cognitive complexity, parameter counts, bug idioms, operational signals, and CWE dangerous sinks.
   - **`container_runtime_audit`** (`when: "has_runtime_harness"`): Automatically runs containerized build/test/coverage verification when a built-in harness exists for the language (e.g., Rust, C#, Ruby, Kotlin, Swift, C/C++, Scala, Dart, Elixir), and cleanly auto-skips otherwise.
   - **`security_vulnerability_audit`**: Auto-runs Trivy (`security_scan`) and correlates CVEs, IaC misconfigs, and secrets with AST CWE sinks.
4. **Wave 3 — `architecture_analysis`** (`needs: [ast_and_quality]`): Ground the 3-aspect architectural model in `module_inventory` and `internal_import_graph`.
5. **Fan-In — `emit_score`**: Submit compact `ScoreSubmissionInput` (with `det-*` FP triage and `±10pt` anchored baseline deltas); PNI outputs `*_score.json` (v2.0), `*_summary.json`, and `*_findings.sarif` (SARIF 2.1.0).
6. **Final — `write_drawlib_report`**: Generate the visual A4 PDF executive and technical health report (or omit on `scope: component` sub-audits when aggregated via a `category: rollup` monorepo workflow).

Verify with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
