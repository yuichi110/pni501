# Modern Haskell (GHC2021 / GHC2024) & Production Idioms (`haskell/modern_stack`)

## Core Principles
1. **Strict `Text` / `ByteString` Over Lazy `String`**: Replace linked-list `String` (`[Char]`) and lazy I/O (`readFile`, `hGetContents` causing fd leaks) with strict `Data.Text` / `Data.ByteString` and streaming (`conduit`/`pipes`; `AstFacts.modernization_hints`).
2. **GHC2021 / Modern Resource & Async Safety**: Prefer `Control.Concurrent.Async` (`withAsync`, `race`, `concurrently`) over raw `forkIO`, `bracket` / `ResourceT` for deterministic cleanup, and `GHC2021` default language mode.
3. **Hardened Web & DB Access**: Configure explicit manager timeouts on `http-client` / `req` (`AstFacts.missing_io_timeouts`), use parameterized SQL (`postgresql-simple`/`persistent`/`esqueleto`/`opaleye`) instead of raw string interpolation (`AstFacts.dangerous_sinks`), and avoid `read` on untrusted strings (`readMaybe`).
4. **Structured Logging**: Prefer `katip` / `co-log` / `monad-logger` over `putStrLn` / `Debug.Trace.trace` (never ship `Debug.Trace` in production; `AstFacts.unstructured_logging`).
