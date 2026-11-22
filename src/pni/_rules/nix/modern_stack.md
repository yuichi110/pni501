# Modern Nix Flakes & RFC-166 Idioms (`nix/modern_stack`)

## Core Principles
1. **Flakes, `nixfmt-rfc-style` & `lib.fileset`**: Prefer `flake.nix` + `devShells` + `formatter` + `checks`, `lib.fileset.toSource` (minimal source closure preventing rebuilds on `README.md` edits), and `finalAttrs: { ... }` derivation pattern over legacy `default.nix`/`shell.nix` + `rec {}` (`AstFacts.modernization_hints`).
2. **Hardened NixOS Systemd Services**: Enable systemd sandboxing (`DynamicUser = true`, `ProtectSystem = "strict"`, `ProtectHome = true`, `PrivateTmp = true`, `NoNewPrivileges = true`) on custom `systemd.services.<name>.serviceConfig`.
3. **Secret Management (`sops-nix` / `agenix`)**: Load secrets via `LoadCredential` / `EnvironmentFile` from runtime-decrypted paths rather than Nix store literals (`AstFacts.hardcoded_secrets`).
4. **Multi-System Cleanliness**: Use `lib.genAttrs` or `flake-parts` cleanly without breaking `nix flake show` schema expectations.
