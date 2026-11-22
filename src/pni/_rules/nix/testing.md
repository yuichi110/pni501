# Flake Check, NixOS VM & Evaluation Testing Standards (Nix)

## Core Principles
1. **Declarative `checks.<system>.*` & `nix flake check`**: Wire formatting (`nixfmt --check`), static lint (`statix check`, `deadnix --fail`), package builds, and unit/integration checks into `outputs.checks` so `nix flake check` validates everything reproducibly (`AstFacts.test_functions_count`).
2. **NixOS Integration Tests (`pkgs.testers.runNixOSTest`)**: Verify multi-service NixOS module configurations using declarative QEMU VM tests (`nodes` + Python `testScript`) where applicable.
3. **Pure Expression Unit Tests**: Test complex Nix library functions (`lib/*.nix`) via `lib.debug.runTests` or `nix-unit` completely offline.
4. **DSL Exemption**: Evaluate verification via `nix flake check` / `statix` / `deadnix` / `runNixOSTest` rather than line-coverage tools.

## Evaluation Thresholds
- **`PASS`**: `checks` outputs wired cleanly (`nix flake check`, `statix`/`deadnix`/formatter, package builds, or VM tests).
- **`WARN`**: Packages build in CI without `statix`/`deadnix`/format checks.
- **`FAIL`**: Broken `nix flake check` evaluation or unverified NixOS configurations deployed blindly.
