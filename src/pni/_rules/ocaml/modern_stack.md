# Modern OCaml 5 & Production Stack Idioms (`ocaml/modern_stack`)

## Core Principles
1. **OCaml 5 Syntax & Safe Stdlib**: Prefer `let*` / `let+` binding operators (`Result.bind`, `Option.bind`), `Fun.protect` for deterministic resource cleanup, `Seq` / `In_channel.with_open_text`, and structured concurrency (`Eio` on OCaml 5 or `Lwt`/`Async` with explicit cancellation; `AstFacts.modernization_hints`).
2. **Safe Strings & Serialization**: Never rely on legacy mutable `Bytes` aliasing strings (`-safe-string` default in modern OCaml), forbid `Marshal.from_string` / `Marshal.from_channel` on untrusted network bytes (CWE-502 / segfault; `AstFacts.dangerous_sinks`), and use `Yojson`/`Atdgen`/`Ppx_yojson_conv`.
3. **Hardened Networking**: Configure explicit timeouts on `Cohttp`/`Piaf`/`Eio` HTTP clients (`AstFacts.missing_io_timeouts`) and keep TLS verification enabled.
4. **Structured Logging**: Prefer `Logs` (`Logs.info`, `Logs.err` with tags) over `Printf.printf` / `print_endline` in services (`AstFacts.unstructured_logging`).
