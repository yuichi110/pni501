# Code Quality & Hermetic Purity Standards (Nix)

## Core Principles
1. **Pure Hermetic Evaluation (Zero `<nixpkgs>` / Unhashed Fetchers)**: Eliminate impure `<nixpkgs>` channel lookups (`NIX_PATH` host dependence), `builtins.getEnv` inside derivations, and unhashed `builtins.fetchTarball` / `builtins.fetchGit` without fixed `sha256`/`hash` (`AstFacts.bug_risk_idioms`, `AstFacts.dangerous_sinks`).
2. **Zero World-Readable Secrets in `/nix/store`**: NEVER put plaintext secrets, private keys, or API tokens into Nix expressions, `writeText`, or `environment.etc` (everything in `/nix/store` is world-readable `0444` to every local user! CWE-732; `AstFacts.hardcoded_secrets`) — use `agenix` or `sops-nix` referencing runtime-decrypted paths.
3. **Avoid `with pkgs;` Shadowing & Use `statix`/`deadnix`/`nixfmt`**: Minimize `with` scopes (especially nested `with` blocks, which hide variable provenance and cause silent shadowing), prefer `inherit (pkgs) ...`, format with `nixfmt-rfc-style` / `alejandra`, and lint with `statix` and `deadnix`.
4. **Avoid `rec { ... }` Recursion Traps & Document Modules**: Prefer `let ... in` or `finalAttrs: { ... }` over `rec { ... }` (prevents infinite recursion on `overrideAttrs`), and document NixOS/Home-Manager `options` with explicit `description` (`AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Pure Flake evaluation (zero `<nixpkgs>`/unhashed fetches), zero secrets in `/nix/store`, clean `inherit` over nested `with`, and `statix`/`deadnix` hygiene.
- **`WARN`**: Nested `with pkgs;` scopes or missing `description` on custom NixOS module options.
- **`FAIL`**: Secrets written into `/nix/store`, unhashed remote `fetchTarball`, or impure host-path leaks breaking reproducibility.
