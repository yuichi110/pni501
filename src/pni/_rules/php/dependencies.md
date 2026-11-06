# Dependency & Packaging Standards (PHP)

## Core Principles
1. **Composer & Deterministic Lockfile**: Manage all runtime and development dependencies in `composer.json` and commit `composer.lock` for deterministic, auditable builds (avoid Composer-less manual `.php` vendoring).
2. **PSR-4 Autoloading**: Configure `autoload.psr-4` and `autoload-dev.psr-4` in `composer.json` instead of manual `require_once` file includes or excessive `autoload.files` bootstrap scripts.
3. **Supported PHP Runtime Bounds**: Specify an active PHP constraint (`^8.2` or `^8.3`) in `require.php` and prohibit EOL PHP 5.x / 7.x / 8.0 targets and unpinned `*` or `dev-master` package constraints.
4. **Acyclic Namespace Layering**: Keep internal namespace dependencies (`Controller -> Service -> Repository/Domain`) unidirectional with zero circular imports or unused Composer packages.
