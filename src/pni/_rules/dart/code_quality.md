# Code Quality Standards (Dart)

## Core Principles
1. **Effective Dart, `dart format` & `analysis_options.yaml`**: Enforce `dart format`, `dart analyze --fatal-infos`, and `lints/recommended.yaml` or `flutter_lints` / `very_good_analysis`, scoping `// ignore:` comments narrowly with inline rationale (`AstFacts.unscoped_type_ignores == 0`).
2. **Dartdoc Documentation**: Document public libraries, classes, mixins, extensions, and functions with `///` dartdoc comments (`AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Async Safety & Resource Lifecycle**: Always `await` futures (or explicitly mark intentional fire-and-forget via `unawaited(...)`), guard `BuildContext` after `await` with `context.mounted` in Flutter, and deterministically `close()`/`dispose()` every `StreamSubscription`, `StreamController`, `TextEditingController`, and `http.Client` (`AstFacts.bug_risk_idioms`).
4. **Immutable State & Bounded Complexity**: Prefer `final` fields and `const` constructors, avoid mutable top-level global variables (`AstFacts.global_state_usages`), never swallow errors in empty `catch (e) {}` blocks, and keep widget `build()` methods and functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero unawaited/empty-catch/resource-leak idioms, zero unguarded mutable top-level globals, and scoped analyzer ignores.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated widget/function complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, undisposed controllers/streams, empty `catch` error swallowing, or unguarded mutable global state.
