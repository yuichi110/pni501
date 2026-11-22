# Dependency & CPAN Management Standards (Perl)

## Core Principles
1. **Declarative CPAN Manifests**: Declare runtime and test dependencies explicitly in `cpanfile` (`requires`, `on 'test' => sub { ... }`), `Makefile.PL`, `Build.PL`, or `dist.ini` alongside a supported minimum Perl version (`requires 'perl', '5.036';`; `ProjectFacts.language_version_constraint`).
2. **Reproducible Locking (`cpanfile.snapshot`)**: For production applications and services using Carton (`carton install`), commit `cpanfile.snapshot` (`ProjectFacts.lockfiles_found`). Note that standalone zero-dependency core-module scripts or CPAN distributions legitimately omit `cpanfile.snapshot` and must **NOT** be penalized.
3. **Pinned Version Floors & Clean Test Scoping**: Specify minimum versions for CPAN modules (`ProjectFacts.unpinned_dependencies`), isolate `Test2::V0` / `Test::More` / `Perl::Critic` inside test/develop phases, and avoid installing unverified modules via raw `curl | perl`.
4. **Security Auditing**: Audit CPAN dependencies via `CPAN::Audit` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Explicit `cpanfile`/`Makefile.PL`/`Build.PL` with supported Perl version (`>= 5.32`), clean test-phase scoping, and `cpanfile.snapshot` committed for deployed Carton services.
- **`WARN`**: Missing minimum Perl version or unpinned CPAN floors on non-core scripts.
- **`FAIL`**: Implicit undocumented host-CPAN dependencies for production apps, EOL Perl `< 5.20` idioms without migration plan, or vulnerable CPAN modules (`CPAN::Audit` findings).
