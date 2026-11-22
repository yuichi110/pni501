# Modern Bash & Safe Automation Idioms (`bash/modern_stack`)

## Core Principles
1. **Modern Command Substitution & Parameter Expansion**: Replace backticks `` `cmd` `` with `$(cmd)`, legacy `[ ... ]` with `[[ ... ]]` in Bash, and external `sed`/`awk` subprocess forks with built-in parameter expansion (`${var##*/}`, `${var//a/b}`) where clearer (`AstFacts.modernization_hints`).
2. **Safe File & Line Iteration**: Use `while IFS= read -r line; do ... done < "$file"` and `find ... -print0 | while IFS= read -r -d '' f; do ...` instead of `for f in $(find ...)` or `for l in $(cat ...)` (handles whitespace/newlines safely).
3. **Hardened Network Calls**: Always pass `--fail --show-error --silent --max-time <sec>` (`-fsSL --max-time`) to `curl` (`AstFacts.missing_io_timeouts`), never use `curl -k` / `wget --no-check-certificate` (CWE-295; `AstFacts.dangerous_sinks`), and never pass secrets on command lines visible in `ps`.
4. **Know When to Graduate from Shell**: Flag multi-hundred-line scripts performing complex JSON/API/concurrency logic as candidates for Python/Go/Rust migration.
