# Dependency & Mix Management Standards (Elixir)

## Core Principles
1. **Supported Elixir & Erlang/OTP Versions**: Declare an actively supported Elixir constraint (`~> 1.16` / `~> 1.17` / `~> 1.18`) in `mix.exs` (`ProjectFacts.language_version_constraint`) and pin OTP/Elixir versions in `.tool-versions` or `mise.toml`.
2. **Lockfile Policy (`mix.lock` — App vs. Hex Library Distinction)**:
   - **Applications (Phoenix apps, OTP releases, Umbrella apps)**: Commit `mix.lock` for deterministic releases (`ProjectFacts.lockfiles_found`).
   - **Published Hex Library Packages**: Omitting `mix.lock` is standard Hex convention and must **NOT** be penalized.
3. **Environment Scoping & Pinned Hex Constraints**: Scope dev/test tooling (`credo`, `dialyxir`, `ex_doc`, `mox`, `sobelow`) with `only: [:dev, :test], runtime: false`, use `~>` constraints, and avoid mutable git branch dependencies (`ProjectFacts.unpinned_dependencies`).
4. **Security Auditing**: Run `mix hex.audit`, `mix deps.audit`, `mix sobelow` (for Phoenix apps), and Trivy.

## Evaluation Thresholds
- **`PASS`**: Elixir `>= 1.15`, clean `only: [:dev, :test], runtime: false` scoping, zero mutable branch deps (`unpinned_dependencies == 0`), and `mix.lock` committed for applications (exempt for Hex libs).
- **`WARN`**: Missing `.tool-versions` or minor ungrouped dev tooling deps.
- **`FAIL`**: EOL Elixir (`< 1.14`), missing `mix.lock` on production apps, or mutable git branch dependencies.
