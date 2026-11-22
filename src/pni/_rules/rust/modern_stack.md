# Modern Rust Stack & Standard Library Idioms (`rust/modern_stack`)

## Core Principles
1. **Rust 2021 / 2024 Edition & Stdlib Modernization**: Replace legacy crates (`lazy_static`, `once_cell` for simple statics, `failure`, `error-chain`) with `std::sync::OnceLock` / `LazyLock`, `thiserror`, and `anyhow` (`AstFacts.modernization_hints`).
2. **Hardened Async & Network Clients**: Never disable TLS verification (`danger_accept_invalid_certs(true)`; CWE-295) or construct `reqwest::Client` without explicit `.timeout(...)` / `.connect_timeout(...)` (`AstFacts.dangerous_sinks`, `AstFacts.missing_io_timeouts`). Always await or track `tokio::spawn` `JoinHandle`s and prefer structured `tracing` over `println!`/`eprintln!` (`AstFacts.unstructured_logging`).
3. **Memory-Safe Web & CLI Frameworks**: Prefer `axum`/`actix-web` with typed extractors, `sqlx` compile-time checked queries over `format!()` SQL concatenation, and `clap` derive macros for CLI tools.
4. **Workspace & Build Hygiene**: Share crate versions via `[workspace.dependencies]` and configure release profiles (`lto`, `strip`, `panic`) intentionally.
