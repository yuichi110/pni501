# Modern Go Stack & Standard Library Idioms (`go/modern_stack`)

## Core Principles
1. **Eliminate Deprecated Standard Library Packages**: Replace `io/ioutil` (deprecated since Go 1.16) with `io` and `os` functions directly (`AstFacts.modernization_hints`).
2. **Modern Go 1.18+ / 1.21+ Idioms**: Prefer `any` and type parameters (`[T any]`) over legacy `interface{}`, `slices`/`maps` standard packages, and `log/slog` structured logging over `fmt.Println`/`log.Printf` (`AstFacts.modernization_hints`, `AstFacts.unstructured_logging`).
3. **Hardened HTTP Servers & Clients**: Never use bare `http.ListenAndServe(...)` or `http.DefaultClient` in production services (`AstFacts.framework_issues`, `AstFacts.missing_io_timeouts`); configure `&http.Server{ReadHeaderTimeout: ..., IdleTimeout: ...}` and `&http.Client{Timeout: ...}` with `context.Context` cancellation.
4. **Loop & Resource Safety**: Avoid `defer` inside loops (`AstFacts.bug_risk_idioms`) and ensure every `http.Response.Body`, `*sql.Rows`, and file handle is closed deterministically.
