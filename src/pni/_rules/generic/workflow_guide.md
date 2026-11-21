# Generic Multi-Language Audit Workflow Guide

Use this 6-step workflow for any PNI-supported language outside the 6 bespoke legacy/core rule directories:

1. **`repo_structure_audit`**: Inspect project manifests, lockfiles, governance hygiene, and companion IaC/config files (`Dockerfile`, Terraform/HCL, CI YAML, Protobuf, SQL).
2. **`generic_ast_audit`**: Run deterministic Tree-sitter AST analysis (`ast_analyze`) to extract LOC, symbol inventory, cognitive complexity, parameter counts, bug idioms, operational signals, and CWE dangerous sinks.
3. **`architecture_analysis`**: Ground the 3-aspect architectural model in `module_inventory` and `internal_import_graph`.
4. **`security_vulnerability_audit`**: Correlate AST CWE sinks and hardcoded secrets with dependency vulnerability scans (`security_scan`).
5. **`emit_score`**: Emit the structured PNI score JSON grounded in deterministic facts.
6. **`write_drawlib_report`**: Generate the visual executive and technical health report.
