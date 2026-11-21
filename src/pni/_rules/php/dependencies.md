# Dependency & Packaging Standards (PHP)

## Core Principles
1. **Composer & Deterministic Lockfile**: Manage all runtime and development dependencies in `composer.json` and commit `composer.lock` (`ProjectFacts.lockfiles_found`) for deployed applications (for reusable Composer libraries, declare SemVer-compatible bounds in `composer.json` per `common/library_guidelines`); avoid Composer-less manual `.php` vendoring.
2. **PSR-4 Autoloading**: Configure `autoload.psr-4` and `autoload-dev.psr-4` in `composer.json` instead of manual `require_once` file includes or excessive `autoload.files` bootstrap scripts.
3. **Supported PHP Runtime Bounds**: Specify an actively supported PHP constraint (`^8.3` or `^8.4`, minimum `^8.2`) in `require.php` and prohibit EOL PHP 5.x / 7.x / 8.0 / 8.1 targets and unpinned `*` or `dev-master` package constraints (`ProjectFacts.unpinned_dependencies`).
4. **Acyclic Namespace Layering**: Keep internal namespace dependencies (`Controller -> Service -> Repository/Domain`) unidirectional with zero circular imports (`AstFacts.circular_dependencies == 0`) or unused/undeclared Composer packages (`AstFacts.unused_dependencies`, `AstFacts.undeclared_dependencies`).

## Evaluation Thresholds
- **`PASS`**: Composer PSR-4 project with active PHP `>= 8.2` (`8.3+` recommended), `unpinned_dependencies == 0`, `circular_dependencies == 0`, and `composer.lock` committed (for apps).
- **`WARN`**: PHP `8.2` constraint nearing EOL or minor unused dependencies.
- **`FAIL`**: Composer-less raw PHP with manual includes, EOL PHP `<= 8.1` target, or unpinned `*` / `dev-master` specs.
