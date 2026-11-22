# Dependency & Gem Management Standards (Ruby)

## Core Principles
1. **Bundler & Supported Ruby Runtime**: Declare a supported Ruby version (`>= 3.2`, ideally `3.3` / `3.4`) in `Gemfile`, `.ruby-version`, or `*.gemspec` (`ProjectFacts.language_version_constraint`).
2. **Lockfile Policy (App vs. Gem Distinction)**:
   - **Applications / Services (Rails, Sinatra, CLI apps)**: Commit `Gemfile.lock` for deterministic deploys (`ProjectFacts.lockfiles_found`).
   - **Published RubyGems (`*.gemspec` library repos)**: Omitting `Gemfile.lock` is standard RubyGems practice and must **NOT** be penalized.
3. **Group Separation & Version Constraints**: Isolate test/development gems (`rspec`, `rubocop`, `pry`, `factory_bot`) inside `group :development, :test`, use pessimistic version constraints (`~>`), and avoid unpinned git branch sources (`ProjectFacts.unpinned_dependencies`).
4. **Security Auditing**: Regularly run `bundle-audit` (`bundler-audit`) and Trivy against `Gemfile.lock`.

## Evaluation Thresholds
- **`PASS`**: Supported Ruby `>= 3.2`, pinned/pessimistic gem constraints (`unpinned_dependencies == 0`), `Gemfile.lock` committed on applications (exempt on pure gems), and clean `:development, :test` separation.
- **`WARN`**: Missing `.ruby-version` or minor ungrouped development gems.
- **`FAIL`**: EOL Ruby (`< 3.1`), missing `Gemfile.lock` in production applications, or mutable git branch gem references.
