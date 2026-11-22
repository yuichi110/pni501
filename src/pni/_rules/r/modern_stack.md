# Modern R (4.2+ / 4.4+) & Tidyverse / Production Idioms (`r/modern_stack`)

## Core Principles
1. **Modern R 4.2+ Syntax & Tooling**: Prefer the native pipe `|>` (with `_` placeholder) over `magrittr` `%>%` where R >= 4.2 is required, `httr2` (with `req_timeout()` and retries; `AstFacts.missing_io_timeouts`) over superseded `httr`/`RCurl`, and `cli`/`rlang::abort` structured errors over bare `stop()` (`AstFacts.modernization_hints`).
2. **Parameterized Database Queries & Shiny Security**: Use `DBI::dbGetQuery(..., params = list(...))` / `glue::glue_sql()` instead of `paste0("SELECT ... ", user_input)` (CWE-89; `AstFacts.dangerous_sinks`), and sanitize untrusted HTML in Shiny (`htmltools::HTML()` XSS; CWE-79).
3. **Structured Logging**: Prefer `logger` / `lgr` / `cli` messaging over scattered `print()` / `cat()` calls in production Plumber APIs or Shiny apps (`AstFacts.unstructured_logging`).
4. **Vectorized & Memory-Safe Data Processing**: Avoid growing vectors inside `for` loops (`x <- c(x, val)` -> pre-allocate or vectorize), and use `data.table` / `dplyr` / `arrow` for large datasets.
