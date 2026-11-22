# Dependency & Pub Package Standards (Dart)

## Core Principles
1. **Supported Dart 3 / Flutter SDK Constraint**: Declare an explicit Dart 3 constraint (`sdk: '^3.4.0'` or `>=3.3.0 <4.0.0`) in `pubspec.yaml` (`ProjectFacts.language_version_constraint`).
2. **Lockfile Policy (`pubspec.lock` — App vs. Package Distinction)**:
   - **Applications (Flutter apps, CLI binaries, backend Dart servers)**: Commit `pubspec.lock` for deterministic builds (`ProjectFacts.lockfiles_found`).
   - **Published `pub.dev` Library Packages**: Omitting `pubspec.lock` is official Dart/Pub convention and must **NOT** be penalized.
3. **Pinned SemVer & Clean Dev Separation**: Avoid `any` or mutable git branch dependencies (`ProjectFacts.unpinned_dependencies`), keep test/linter/codegen packages (`test`, `lints`, `build_runner`, `mocktail`) in `dev_dependencies`, and avoid `dependency_overrides` in release builds.
4. **Vulnerability Auditing**: Check outdated/discontinued packages via `dart pub outdated` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Dart `>= 3.0`, zero `any`/mutable git dependencies (`unpinned_dependencies == 0`), `pubspec.lock` committed for apps (exempt for pure pub packages), and clean `dev_dependencies`.
- **`WARN`**: Missing `analysis_options.yaml` or temporary `dependency_overrides`.
- **`FAIL`**: Legacy Dart 2 (pre-null-safety), `any` dependencies, or missing `pubspec.lock` in production applications.
