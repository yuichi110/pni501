# Typing, Sound Null Safety & Pattern Standards (Dart)

## Core Principles
1. **Dart 3 Sound Null Safety**: Target SDK `>=3.0.0` (sound null safety guaranteed) and avoid unsafe bang assertions (`value!`) and unnecessary `late` variables that defer `LateInitializationError` to runtime (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Eliminate `dynamic` & Implicit Casts**: Enable `strict-casts`, `strict-inference`, and `strict-raw-types` in `analysis_options.yaml`; replace `dynamic` and raw `Map`/`List` with explicit generics (`Map<String, Object?>`, `List<Item>`) and `sealed class` ADTs (`AstFacts.weak_type_usages`).
3. **Typed Serialization & Models**: Use typed DTO classes (`freezed` / `json_serializable` / Dart 3 `extension type` / records) instead of passing untyped `Map<String, dynamic>` through domain layers.
4. **Scoped Analyzer Ignores**: Never use `// ignore_for_file: type=lint` or blanket ignore lists (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 95%`, `unscoped_type_ignores == 0`, strict analyzer mode, and minimal `dynamic`/`!` usage outside JSON boundary decoders.
- **`WARN`**: `type_safety_coverage_pct` between `80%` and `94.9%`, or isolated `dynamic`/`late` usages.
- **`FAIL`**: Pervasive `dynamic` domain models, unchecked `!` null-dereference hazards, or file-wide lint disablements.
