# Flake Inputs & Lockfile Management Standards (Nix)

## Core Principles
1. **Committed `flake.lock` & Deduplicated `.follows`**: Commit `flake.lock` alongside `flake.nix` (`ProjectFacts.lockfiles_found`) and wire shared `nixpkgs` inputs via `inputs.<dep>.inputs.nixpkgs.follows = "nixpkgs";` to prevent evaluation bloat and duplicate conflicting `nixpkgs` revisions.
2. **Supported Nixpkgs Channels**: Track an active `nixos-24.11` / `nixos-25.05` / `nixpkgs-unstable` branch rather than EOL NixOS releases (`ProjectFacts.language_version_constraint`).
3. **SRI `hash` Over Legacy `sha256` & Zero `allowUnfree` Leaks**: Use SRI hashes (`hash = "sha256-..."`) in `fetchFromGitHub`/`fetchurl`, avoid disabling `allowBroken`/`allowInsecure` globally, and keep `permittedInsecurePackages` empty or strictly justified.
4. **Automated Flake Updates & Auditing**: Automate lockfile updates (GitHub Actions `update-flake-lock` / Renovate) and scan built container/system closures with Trivy / `vulnix`.

## Evaluation Thresholds
- **`PASS`**: `flake.nix` + committed `flake.lock`, `.follows` deduplication, SRI hashes, and active `nixpkgs` branch.
- **`WARN`**: Missing `.follows` causing duplicate `nixpkgs` trees or legacy base32 `sha256`.
- **`FAIL`**: Missing `flake.lock`, EOL `nixos-22.11`/`23.05` channel, unhashed fetches, or blanket `allowInsecure = true`.
