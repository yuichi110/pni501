# Variable Semantics, Tab Indentation & Portability Standards (Makefile)

## Core Principles
1. **Explicit Assignment Semantics (`:=`, `?=`, `+=`, `=`)**: Distinguish immediate assignment (`:=`), overridable defaults (`?=`), and deferred expansion (`=`) intentionally, and avoid undefined variable typos (`MAKEFLAGS += --warn-undefined-variables` where appropriate).
2. **DSL Exemption (Avoid False Positives)**: Make is a build-automation DSL — do **NOT** apply software type-annotation or OOP rules. Evaluate structural clarity via strict TAB recipe indentation, explicit `$(VAR)` parentheses (consistent over `$V`), and safe automatic variables (`$@`, `$<`, `$^`).
3. **Avoid Fragile Sub-Shell State (`cd dir` Across Lines)**: Remember each recipe line executes in a separate subshell (unless `.ONESHELL:` is set) — chain directory changes on a single logical line (`cd subdir && cmd`) or pass `-C subdir` (`$(MAKE) -C subdir`).
4. **Parameter Validation**: Guard required override variables (`ifndef ENV` -> `$(error ENV is required)`) before destructive deploy/clean recipes.

## Evaluation Thresholds
- **`PASS`**: Consistent `$(VAR)` syntax, guarded required variables, clean `:=`/`?=` semantics, and safe subshell handling.
- **`WARN`**: Missing `ifndef` guards on optional deploy variables or mixed `$V`/`$(V)` notation.
- **`FAIL`**: Broken multi-line `cd` subshell bugs, space-vs-tab syntax traps, or unguarded destructive target variables.
