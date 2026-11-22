# Modern TOML v1.0.0 & Project Configuration Idioms (`toml/modern_stack`)

## Core Principles
1. **TOML v1.0.0 Standardization**: Use PEP 621 `[project]` + PEP 735 `[dependency-groups]` in Python `pyproject.toml`, `[workspace.dependencies]` in Rust `Cargo.toml`, and `mise.toml` for polyglot toolchain version pinning (`AstFacts.modernization_hints`).
2. **Dotted Keys for Concise Flat Config**: Use dotted keys (`lint.select = [...]`) cleanly without mixing table headers and dotted paths ambiguously for the same parent table.
3. **Taplo Schema Ecosystem**: Pair `.toml` files with `taplo.toml` / SchemaStore bindings for zero-drift IDE autocompletion and CI schema verification.
4. **UTF-8 Cleanliness**: Keep all `.toml` files UTF-8 encoded with LF line endings.
