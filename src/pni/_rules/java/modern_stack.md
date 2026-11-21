# Modern Java Stack & JDK Idioms (`java/modern_stack`)

## Core Principles
1. **Supported LTS Runtime & Compiler Alignment**: Target Java 21 LTS (or Java 17 LTS minimum) cleanly in `pom.xml` / `build.gradle(.kts)` and avoid using APIs newer than the declared toolchain target (`AstFacts.language_version_mismatches == 0`).
2. **Modern Java 17–21 Idioms**: Prefer `record` value objects/DTOs, `sealed` interfaces/classes, pattern matching (`instanceof` / `switch`), and `List.of()` / `Map.of()` immutable factories over verbose mutable POJO boilerplate (`AstFacts.modernization_hints`).
3. **Jakarta EE Namespace & Modern Stdlib**: Use `jakarta.*` packages instead of legacy `javax.*` (Servlet, Persistence, Validation, Inject), `java.time` (`Instant`, `LocalDate`, `DateTimeFormatter`) instead of `java.util.Date`/`Calendar`/`SimpleDateFormat`, and `java.net.http.HttpClient` (with explicit timeouts) instead of legacy `HttpURLConnection`.
4. **Clean Collection & Concurrency Primitives**: Eliminate legacy synchronized containers (`Vector`, `Hashtable`, `Stack`) in favor of `ArrayList`, `HashMap`, `ArrayDeque`, or `ConcurrentHashMap`.
