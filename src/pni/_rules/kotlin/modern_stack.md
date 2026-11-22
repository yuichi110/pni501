# Modern Kotlin Stack & Coroutines Idioms (`kotlin/modern_stack`)

## Core Principles
1. **Kotlin 2.0 (K2) & Idiomatic Stdlib**: Prefer `kotlinx.serialization` over reflection-heavy JSON parsers, `enum entries` over `values()`, `sealed interface` ADTs, and `java.time` / `kotlinx.datetime` over legacy `java.util.Date` (`AstFacts.modernization_hints`).
2. **Coroutine & Flow Safety**: Inject dispatchers, avoid `runBlocking` inside suspending functions or request threads, and use `Flow` / `StateFlow` / `Channel` with explicit backpressure and cancellation propagation.
3. **Hardened Web Services (Ktor / Spring Boot)**: Configure explicit HTTP client timeouts (`HttpTimeout` / `WebClient` timeouts; `AstFacts.missing_io_timeouts`), prefer parameterized Exposed/jOOQ/Spring Data queries over string-interpolated SQL (`AstFacts.dangerous_sinks`), and use constructor injection in Spring Boot.
4. **Structured Logging**: Use `kotlin-logging` / SLF4J structured key-value logging instead of `println(...)` (`AstFacts.unstructured_logging`).
