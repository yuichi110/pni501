# Dependency & Module Management Standards (Go)

## Core Principles
1. **Standard Go Modules**: Declare the module path, an actively supported Go toolchain version (`go 1.23+` / `1.24+`), and dependencies cleanly in `go.mod` (`ProjectFacts.language_version_constraint`).
2. **Cryptographic Checksums (`go.sum`)**: Always commit an up-to-date `go.sum` lockfile (`ProjectFacts.lockfiles_found`) when external dependencies are declared and keep `go.mod` tidy (`go mod tidy`) with zero unused or undeclared requirements (`AstFacts.unused_dependencies`, `AstFacts.undeclared_dependencies`).
3. **Direct vs Indirect Hygiene**: Keep direct `require` dependencies minimal, avoid local `replace` directives pointing outside the repository in release branches, and pin semantic versions rather than mutable branch pseudo-versions (`ProjectFacts.unpinned_dependencies`).
4. **Vulnerability Auditing**: Regularly audit module dependencies with `govulncheck` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Supported Go version in `go.mod`, `go.sum` committed (when dependencies exist), `unpinned_dependencies == 0`, and zero external local `replace` directives.
- **`WARN`**: Minor unused/indirect tidiness gaps or Go version nearing EOL.
- **`FAIL`**: Missing `go.mod` / `go.sum` for modules with dependencies, EOL Go toolchain target, or mutable/unpinned module directives.
