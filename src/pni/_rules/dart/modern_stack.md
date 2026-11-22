# Modern Dart 3 & Flutter Stack Idioms (`dart/modern_stack`)

## Core Principles
1. **Dart 3 Language Features**: Adopt `sealed class` hierarchies with exhaustive `switch` expressions, records `(A, B)`, pattern matching, and `final class` / `interface class` modifiers (`AstFacts.modernization_hints`).
2. **Hardened Networking & Security**: Configure explicit timeouts on `http.Client` / `Dio` requests (`AstFacts.missing_io_timeouts`), never override `badCertificateCallback = (_, _, _) => true` in production (`AstFacts.dangerous_sinks`), and store tokens in secure platform storage rather than plaintext `SharedPreferences`.
3. **Structured Logging**: Replace `print(...)` with `package:logging` / `logger` or `debugPrint` in Flutter (`AstFacts.unstructured_logging`).
4. **Flutter Performance & State**: Prefer `const` widgets, extract deep widget subtrees into focused stateless widgets, and avoid expensive work inside `build()`.
