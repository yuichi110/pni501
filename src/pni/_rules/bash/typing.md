# Argument Validation, Quoting & Contract Standards (Bash / Shell)

## Core Principles
1. **Untyped Shell Exemption & Explicit Argument Contracts**: Bash/POSIX Shell is string-oriented — do **NOT** penalize shell scripts for lacking static type annotations. Evaluate contract safety via explicit argument-count checks (`${1:?Usage: ...}`), `getopts` flag parsing, and input format validation (`[[ "$val" =~ ^[0-9]+$ ]]`).
2. **Array & Arithmetic Discipline**: Use indexed/associative Bash arrays (`declare -a`, `declare -A`) rather than space-delimited strings for filenames/argument lists, use `(( ... ))` for integer arithmetic, and pass `--` before user-supplied operands (`rm -- "$file"`).
3. **Safe Conditionals**: Prefer `[[ ... ]]` in Bash (or quoted `[ "$a" = "$b" ]` in POSIX `sh`) and explicitly handle unset defaults (`"${VAR:-default}"`).
4. **Read-Only Constants & Scoped Exports**: Declare constants with `readonly` and avoid leaking temporary variables via unnecessary `export`.

## Evaluation Thresholds
- **`PASS`**: Explicit CLI argument validation (`getopts` / `${1:?}`), proper array quoting (`"${arr[@]}"`), `--` option terminators, and `readonly` constants.
- **`WARN`**: Implicit positional arguments (`$1`, `$2`) without validation on internal helper scripts.
- **`FAIL`**: Space-delimited string lists causing word-splitting bugs or unvalidated user arguments passed into command flags.
