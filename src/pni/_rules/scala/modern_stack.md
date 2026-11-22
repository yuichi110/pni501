# Modern Scala 3 Stack & Effect Idioms (`scala/modern_stack`)

## Core Principles
1. **Scala 3 Idioms**: Prefer `enum`, `opaque type`, `given`/`using`, `extension`, and `export` over Scala 2 `sealed trait` boilerplate, `implicit class`, and `package object` (`AstFacts.modernization_hints`).
2. **Structured Concurrency & Resource Safety**: Use `cats.effect.Resource` / `ZIO.acquireRelease` or `scala.util.Using` for deterministic resource teardown, and avoid global `ExecutionContext.Implicits.global` for blocking I/O (isolate blocking calls on dedicated pools).
3. **Hardened Web & Database Access**: Prefer parameterized Doobie/Skunk/Slick queries over string-interpolated SQL (`AstFacts.dangerous_sinks`), configure explicit timeouts on http4s/sttp/Play WS clients (`AstFacts.missing_io_timeouts`), and avoid Java native deserialization (`ObjectInputStream`).
4. **Structured Logging**: Use `log4cats` / SLF4J / `zio-logging` rather than `println(...)` (`AstFacts.unstructured_logging`).
