# Modern Perl (5.36+ / 5.40+) Stack Idioms (`perl/modern_stack`)

## Core Principles
1. **Modern Perl 5.36+ Baseline**: Use `use v5.36;` (auto-enabling `strict`, `warnings`, `signatures`, `say`, `state`, and disabling `indirect`/`multidimensional`), `try`/`catch` (`Feature::Compat::Try` or Perl 5.40 built-in) over `eval { ... }; if ($@)`, and `Path::Tiny` over raw `File::Spec` + manual `open` (`AstFacts.modernization_hints`).
2. **Modern Web & Database Access**: Prefer `Mojolicious` / `Dancer2` / `Plack` over legacy `CGI.pm` (removed from core in 5.22), and always use DBI bound placeholders (`$dbh->prepare("SELECT ... WHERE id = ?")`) instead of interpolated SQL (`AstFacts.dangerous_sinks`).
3. **Hardened HTTP & UTF-8 Hygiene**: Configure explicit timeouts on `HTTP::Tiny` / `Mojo::UserAgent` / `LWP::UserAgent` (`AstFacts.missing_io_timeouts`) and enforce explicit `:encoding(UTF-8)` layers on I/O.
4. **Structured Logging**: Prefer `Log::Any` / `Log::Log4perl` / `Mojo::Log` over scattered `print STDERR` / `warn` calls in services (`AstFacts.unstructured_logging`).
