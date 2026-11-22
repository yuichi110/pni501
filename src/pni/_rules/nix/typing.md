# Module Option Typing & Schema Standards (Nix)

## Core Principles
1. **Dynamic Language Exemption & NixOS Module `lib.types`**: The Nix expression language is dynamically typed — do **NOT** penalize pure Nix expressions for lacking static type syntax. For NixOS / Home-Manager / flake-parts modules, evaluate schema rigor via `lib.mkOption { type = lib.types.* ; default = ...; description = "..."; }` using strict types (`types.str`, `types.port`, `types.enum [...]`, `types.submodule`, `types.package`) instead of `types.anything` or `types.attrs` (`AstFacts.weak_type_usages`).
2. **Explicit `lib.assertMsg` & Derivation `meta` Attributes**: Guard invalid configurations with `assertions = [{ assertion = ...; message = "..."; }]` and populate `meta = { description = ...; license = ...; mainProgram = ...; }` on custom packages.
3. **Avoid `builtins.toString` Path-Copy Traps**: Be careful with path interpolation (`"${./foo}"` copies the entire directory into `/nix/store`; prefer `lib.fileset` to filter build sources cleanly).
4. **Clean Function Argument Sets**: Destructure expected inputs explicitly (`{ lib, stdenv, fetchFromGitHub }:`) rather than relying on unchecked `args: ...` attribute bags.

## Evaluation Thresholds
- **`PASS`**: Strict `lib.types.*` + `description` on NixOS/flake module options, explicit argument destructuring, and `lib.fileset` source filtering.
- **`WARN`**: Occasional `types.attrs` / `types.anything` or missing `meta.mainProgram`.
- **`FAIL`**: Unvalidated module options silently accepting wrong types or accidental full-repo `.git` copies into `/nix/store`.
