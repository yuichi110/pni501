# Modern F# 8/9 & .NET Stack Idioms (`fsharp/modern_stack`)

## Core Principles
1. **Modern F# `task { ... }` & `System.Text.Json`**: Prefer native `task { ... }` computation expressions for .NET `Task` interop (reducing `Async.AwaitTask`/`Async.StartAsTask` overhead), F# 9 nullable interop checking, and `System.Text.Json` / `FSharp.SystemTextJson` over legacy `Newtonsoft.Json` (`AstFacts.modernization_hints`).
2. **Hardened Web & Data Access**: In Giraffe/Saturn/Falco/ASP.NET services, configure explicit `IHttpClientFactory` timeouts (`AstFacts.missing_io_timeouts`), use parameterized SQL (`Dapper`/`Npgsql.FSharp`/SQLProvider — never interpolated SQL; `AstFacts.dangerous_sinks`), and ban `BinaryFormatter`.
3. **Structured Observability**: Prefer `ILogger` / `Serilog` structured logging over `printfn` in production services (`AstFacts.unstructured_logging`).
4. **Clean Functional Error Pipelines**: Adopt `FsToolkit.ErrorHandling` (`result { ... }`, `taskResult { ... }`) or lightweight computation expressions instead of nested `match` pyramids.
