# Modern Swift Stack & Concurrency Idioms (`swift/modern_stack`)

## Core Principles
1. **Structured `async/await` Concurrency**: Replace legacy `DispatchQueue` / nested completion-handler pyramids and `EventLoopFuture` chains with Swift `async`/`await`, `TaskGroup`, and `actor` isolation (`AstFacts.modernization_hints`).
2. **Swift 6 Ergonomics**: Adopt `swift-testing` (`@Test`/`#expect`), `Codable` over manual JSON parsing, `os.Logger` / `swift-log` structured logging over `print(...)` (`AstFacts.unstructured_logging`), and typed throws where useful.
3. **Hardened Networking & Security**: Configure explicit `timeoutIntervalForRequest` / `timeoutIntervalForResource` on `URLSessionConfiguration` / `AsyncHTTPClient` (`AstFacts.missing_io_timeouts`), never bypass TLS certificate validation (`AstFacts.dangerous_sinks`), and store secrets in Keychain / environment secret stores.
4. **Cross-Platform Portability (Server Swift)**: Avoid macOS-only Foundation quirks in server/CLI packages intended to run on Linux containers (`Vapor`, `Hummingbird`, `ArgumentParser`).
