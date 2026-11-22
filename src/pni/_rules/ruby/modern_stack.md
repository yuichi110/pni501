# Modern Ruby & Rails Stack Idioms (`ruby/modern_stack`)

## Core Principles
1. **Modern Ruby 3.2+ / 3.3+ Features**: Adopt immutable value objects (`Data.define`), pattern matching (`case ... in`), YJIT-friendly frozen string literals, and `YAML.safe_load` over unsafe `YAML.load` (`AstFacts.modernization_hints`, `AstFacts.dangerous_sinks`).
2. **Rails Security & Query Hygiene**: Enforce Strong Parameters (never `params.permit!`), avoid raw SQL string interpolation in `where("name = '#{x}'")` (use bound placeholders `?` / `:name`), prevent N+1 queries with `includes`/`preload`/`strict_loading`, and avoid `html_safe` / `raw` on user input (CWE-79 / CWE-89).
3. **Hardened HTTP & Timeouts**: Always configure explicit `open_timeout` and `read_timeout` on `Net::HTTP`, `Faraday`, or `HTTParty` clients (`AstFacts.missing_io_timeouts`).
4. **Structured Logging**: Prefer `Rails.logger` / `SemanticLogger` / JSON `Logger` over raw `puts` / `p` in production services (`AstFacts.unstructured_logging`).
