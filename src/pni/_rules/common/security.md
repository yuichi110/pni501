# Security Standards (Common — OWASP ASVS Baseline)

Design-level secure-by-default engineering principles applied across all languages. Evaluate concrete CVE, IaC, secret, CWE sink, API surface, and DAST gates (`SEC-01` – `SEC-06`) under `common/security_vulnerability`.

## Core Principles
1. **Zero Hardcoded or Committed Secrets**: Never hardcode passwords, API keys, or tokens in source literals (`AstFacts.hardcoded_secrets`) or commit `.env`, `*.pem`, `*.key`, or credential JSON files to version control (`ProjectFacts.committed_secret_files`).
2. **Safe Execution, Deserialization & Parameterized Queries**: Eliminate dynamic code evaluation (`eval`/`exec`/`new Function`), shell-interpolated subprocess calls (`shell=True`, `sh -c`, `child_process.exec`), unsafe deserializers (`pickle`, unguarded `yaml.load`, `unserialize`, `ObjectInputStream`), and unparameterized SQL/command string concatenation (`AstFacts.bug_risk_idioms`, `AstFacts.dangerous_sinks`).
3. **Boundary Input Validation**: Validate and parse all untrusted external inputs (CLI arguments, HTTP payloads, file/YAML/JSON inputs, environment variables) through strict schema types at system boundaries (Pydantic, Bean Validation, FormRequest, Zod/Valibot, Go struct validation).
4. **Principle of Least Privilege & Secure Defaults**: Operate processes, CI workflows, containers, CORS policies, and TLS/storage clients with minimal required permissions and fail-closed defaults.
