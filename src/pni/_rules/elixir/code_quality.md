# Code Quality Standards (Elixir)

## Core Principles
1. **`mix format`, Credo & Compiler Warnings**: Enforce `mix format --check-formatted`, `mix compile --warnings-as-errors`, and `mix credo --strict`, avoiding blanket Credo disable comments (`AstFacts.unscoped_type_ignores == 0`).
2. **ExDoc Documentation (`@moduledoc` & `@doc`)**: Document every public module with `@moduledoc` and public function with `@doc` (including doctest examples where appropriate; mark internal modules explicitly with `@moduledoc false`; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **BEAM / OTP Safety & Pattern Matching**: Never call `String.to_atom/1` or `:erlang.binary_to_term/1` (without `[:safe]`) on untrusted input (atom-table DoS exhaustion & RCE; `AstFacts.dangerous_sinks`, `AstFacts.bug_risk_idioms`). Prefer pattern matching, `with` pipelines, and tagged tuples `{:ok, val} | {:error, reason}` over deep nested `if`/`try/rescue`.
4. **Supervised Processes & Zero Global ETS/Process-Dict Abuse**: Start stateful processes (`GenServer`, `Task.Supervisor`, `Agent`) inside OTP `Supervisor` trees rather than naked `spawn`/`Task.start`, avoid process dictionary (`Process.put`) or unowned `:ets` global mutable state (`AstFacts.global_state_usages`), and keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero untrusted `String.to_atom`/unsafe `binary_to_term`/naked process leaks, clean OTP supervision, and concise pattern-matched functions.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated deep nesting / Credo style warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, atom-table exhaustion (`String.to_atom` on user input), unsafe `Code.eval_string`/`binary_to_term`, or unmanaged global mutable state.
