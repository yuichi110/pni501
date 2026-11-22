# Dependency & Pod/SwiftPM Management Standards (Objective-C)

## Core Principles
1. **CocoaPods (`Podfile` + `Podfile.lock`) or SwiftPM (`Package.swift`)**: Declare explicit platform minimums (e.g. `platform :ios, '15.0'`) and pinned dependency versions in `Podfile` / `*.podspec` / `Package.swift` (`ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
2. **Committed Lockfile for Apps**: Commit `Podfile.lock` / `Package.resolved` for application targets (`ProjectFacts.lockfiles_found`); pure SDK podspecs/SwiftPM libraries may omit lockfiles.
3. **Clang Warnings & Static Analyzer**: Enable `-Wall -Wextra -Wobjc-missing-super-calls -Wimplicit-retain-self` and Clang Static Analyzer in Xcode/CI builds.
4. **Supply-Chain & Interop Auditing**: Audit third-party pods/XCFrameworks for maintenance status and CVEs (Trivy), and plan incremental Swift migration for legacy Apple-platform codebases.

## Evaluation Thresholds
- **`PASS`**: Supported platform deployment target, pinned pod/SPM versions (`unpinned_dependencies == 0`), and `Podfile.lock` committed on apps.
- **`WARN`**: Deprecated CocoaPods specs nearing SwiftPM migration or minor unpinned test pods.
- **`FAIL`**: Unpinned git branch pods in release apps, missing `Podfile.lock` on shipped apps, or abandoned vulnerable native frameworks.
