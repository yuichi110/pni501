# Dependency & Module Management Standards (Go)

## Core Principles
1. **Standard Go Modules**: Declare the module path, minimum Go toolchain version (`go 1.22+`), and dependencies cleanly in `go.mod`.
2. **Cryptographic Checksums (`go.sum`)**: Always commit an up-to-date `go.sum` lockfile and keep `go.mod` tidy (`go mod tidy`) with no unused or unverified requirements.
3. **Direct vs Indirect Hygiene**: Keep direct `require` dependencies minimal, avoid local `replace` directives pointing outside the repository in release branches, and pin semantic versions rather than mutable branch pseudo-versions.
4. **Vulnerability Auditing**: Regularly audit module dependencies with `govulncheck` and Trivy.
