# Modern C# / .NET Stack & Standard Library Idioms (`csharp/modern_stack`)

## Core Principles
1. **Modern .NET 8+ Standard Libraries**: Prefer `System.Text.Json` (with source generation) over `Newtonsoft.Json` for new code, `IHttpClientFactory` (with resilience/timeouts via `Microsoft.Extensions.Http.Resilience`) over `new HttpClient()` socket exhaustion (`AstFacts.missing_io_timeouts`), and `PeriodicTimer` over legacy `System.Timers.Timer` (`AstFacts.modernization_hints`).
2. **C# 12/13 Language Ergonomics**: Adopt `record` / `record struct` immutable DTOs, primary constructors, file-scoped namespaces, pattern matching, and `using` declarations to cut boilerplate cleanly.
3. **Security Hardening**: Never use `BinaryFormatter` (CWE-502, banned in .NET 8+), raw string-interpolated SQL (`FromSqlRaw($"...")` -> use `FromSqlInterpolated` / parameterized Dapper), or `ServerCertificateCustomValidationCallback = (_, _, _, _) => true` (`AstFacts.dangerous_sinks`).
4. **Structured Observability**: Use `ILogger<T>` with `[LoggerMessage]` source-generated structured templates instead of `Console.WriteLine` (`AstFacts.unstructured_logging`).
