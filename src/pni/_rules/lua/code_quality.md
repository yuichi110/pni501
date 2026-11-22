# Code Quality Standards (Lua)

## Core Principles
1. **Strict `local` Scoping & Zero Accidental Globals**: Declare every variable and helper function `local` (Lua defaults unassigned identifiers to global `_G`; `AstFacts.global_state_usages`). Lint with `luacheck` / `selene` and format with `StyLua`.
2. **Eliminate Dynamic Execution & Shell Injection Sinks**: Never pass untrusted strings to `load()`/`loadstring()`/`dofile()` (CWE-94) or `os.execute()`/`io.popen()` (CWE-78; `AstFacts.dangerous_sinks`), and never leave `debug` library hooks accessible in sandboxed environments.
3. **LuaCATS / EmmyLua Documentation**: Document public module tables and exported functions with LuaLS annotations (`--- description`, `---@param`, `---@return`; `AstFacts.docstring_coverage_pct`).
4. **Explicit Error Propagation & Bounded Complexity**: Return idiomatic `value, err` tuples (or check `pcall`/`xpcall` results explicitly — never discard `pcall` failure flags; `AstFacts.bug_risk_idioms`) and keep functions modular (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: Consistent `local` declarations (zero accidental `_G` mutations), zero `load`/`os.execute` injection sinks, checked `pcall` returns, and LuaCATS/doc comments on public APIs.
- **`WARN`**: Missing LuaCATS docs on helper modules or isolated `luacheck` complexity/unused-variable warnings.
- **`FAIL`**: Pervasive accidental global leaks, `loadstring`/`os.execute` on untrusted input, or silently discarded `pcall` errors.
