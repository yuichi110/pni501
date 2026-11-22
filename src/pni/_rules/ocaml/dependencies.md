# Dependency & Dune / Opam Management Standards (OCaml)

## Core Principles
1. **Modern Dune (`dune-project`) & Generated `*.opam`**: Use `dune` (`(lang dune 3.x)`) with `(generate_opam_files true)` and declare explicit OCaml compiler bounds (`(ocaml (>= 5.1))` or `>= 4.14`; `ProjectFacts.language_version_constraint`).
2. **Reproducible Opam Locking**: Commit `*.opam.locked` (via `opam lock`) for deployed applications/services (`ProjectFacts.lockfiles_found`). Published opam library packages legitimately omit `.opam.locked` and must **NOT** be penalized.
3. **Bounded Constraints & `:with-test` Separation**: Bound external opam dependencies (`ProjectFacts.unpinned_dependencies`) and mark test/doc packages (`alcotest`, `qcheck`, `bisect_ppx`, `odoc`) strictly with `:with-test` / `:with-doc`.
4. **Security & C-Stub Auditing**: Track vendored C stubs and opam packages via Trivy and CI builds.

## Evaluation Thresholds
- **`PASS`**: Modern `dune 3.x` + OCaml `>= 4.14` (`5.x` preferred), `:with-test` separation, bounded dependencies, and `.opam.locked` for apps.
- **`WARN`**: Missing `.ocamlformat` version pin or unpinned test-only deps.
- **`FAIL`**: Legacy `ocamlbuild`/`oasis` without migration plan, EOL OCaml `< 4.12`, or missing lockfile on production services.
