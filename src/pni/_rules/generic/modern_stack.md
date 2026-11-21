# Generic Modern Stack & Toolchain Standards

## Evaluation Criteria
- **Supported Runtime / Compiler**: Target an actively supported compiler/runtime release (non-EOL LTS or current stable edition).
- **Formatting & Static Analysis**: Enforce an automated formatter and linter in CI (e.g., `rustfmt`/`clippy`, `dotnet format`/Roslyn analyzers, `rubocop`, `ktlint`/`detekt`, `swiftlint`, `clang-format`/`clang-tidy`, `dart analyze`, `mix format`/`credo`, `shellcheck`, `tflint`, `hadolint`, `buf lint`).
- **Declarative Packaging**: Prefer modern declarative manifests (`Cargo.toml`, `Directory.Packages.props`, `Package.swift`, `mix.exs`, `pubspec.yaml`, `buf.yaml`, `flake.nix`) over imperative ad-hoc build scripts.
