# Modern Elixir / OTP & Phoenix Stack Idioms (`elixir/modern_stack`)

## Core Principles
1. **Modern Elixir & Runtime Config**: Use `config/runtime.exs` for runtime environment configuration (avoid compile-time `Application.get_env` in module attributes for secrets/URLs; `AstFacts.scattered_env_access`), `Req` / `Finch` with explicit timeouts over legacy `HTTPoison`/`Tesla` without timeouts (`AstFacts.missing_io_timeouts`), and `Jason` / built-in `JSON` (Elixir 1.18+).
2. **Phoenix & Ecto Security**: Use parameterized Ecto queries (never interpolate user strings into `Ecto.Adapters.SQL.query` or `fragment`), avoid `Phoenix.HTML.raw/1` on untrusted HTML (CWE-79), and enforce `Plug.CSRFProtection` + `Sobelow` security scanning (`AstFacts.dangerous_sinks`).
3. **Structured Telemetry & Logging**: Use Elixir `Logger` with structured metadata (`Logger.info("...", user_id: id)`) and `:telemetry` events instead of `IO.puts` / `IO.inspect` in production (`AstFacts.unstructured_logging`).
4. **OTP Release Readiness**: Favor `mix release` with explicit supervision trees, graceful shutdown timeouts, and bounded `Task.Supervisor.async_stream` concurrency.
