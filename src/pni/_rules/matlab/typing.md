# Typing, `arguments` Validation & Matrix Contract Standards (MATLAB)

## Core Principles
1. **Dynamic Typing Exemption & Modern `arguments` Blocks**: MATLAB is dynamically typed — do **NOT** penalize MATLAB code for lacking C/Java-style static type declarations. Evaluate contract rigor via MATLAB R2019b+ `arguments ... end` validation blocks (size, class, and validator functions like `(1,:) double {mustBeFinite, mustBeNonempty}`) or `inputParser` / `validateattributes` on public functions.
2. **Typed Class Properties & Enumerations**: Annotate `classdef` properties with explicit size/class validators and use `enumeration` classes instead of magic string/numeric mode codes.
3. **Explicit `string` vs `char`, `table` vs `cell` & `NaN` Guards**: Prefer `string` scalars (`"text"`) over legacy `char` cell arrays (`{'text'}`) in R2016b+ code, check `isnan`/`isfinite`/`isempty` explicitly, and use `numel` / `size(x, dim)` over ambiguous `length(x)` on 2D matrices.
4. **Element-Wise vs Matrix Operator Discipline**: Use `&&`/`||` (short-circuit scalar logicals) in `if`/`while` conditions rather than `&`/`|`, and verify `.` element-wise operators (`.*`, `./`, `.^`) carefully.

## Evaluation Thresholds
- **`PASS`**: `arguments` / `validateattributes` contracts on public functions, `size`/`numel` matrix dimension safety, and explicit `NaN`/empty guards.
- **`WARN`**: Missing `arguments` validation on internal helpers or legacy `char` cell arrays.
- **`FAIL`**: Unvalidated public matrix dimensions causing silent broadcasting bugs or `&`/`|` misuse in scalar conditionals.
