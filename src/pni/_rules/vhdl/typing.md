# Signal Typing, Range Constraints & CDC Standards (VHDL)

## Core Principles
1. **Strong Range-Constrained Types & Explicit `unsigned`/`signed`**: Constrain `integer` / `natural` / `positive` signals with explicit bounds (`natural range 0 to MAX_DEPTH - 1`) so synthesis infers exact bit widths and simulation catches out-of-range faults immediately (`AstFacts.type_safety_coverage_pct`). Use `unsigned`/`signed` for arithmetic and `std_logic_vector` strictly for untyped bus ports.
2. **Typed FSM Enumerations & Record Ports**: Model FSM states as custom `type state_t is (ST_IDLE, ST_RUN, ...);` enumerations and group bus signals into `record` types inside shared `package`s.
3. **Explicit `resize()` & Bit-Width Alignment**: Resize `unsigned`/`signed` operands explicitly via `resize(x, target'length)` and use `'range` / `'length` attributes instead of hardcoded magic bit indices (`AstFacts.type_safety_issues`).
4. **Clock Domain Crossing (CDC) Synchronization**: Isolate CDC paths in dedicated 2-FF synchronizer or async-FIFO entities with explicit timing-constraint attributes (`ASYNC_REG`).

## Evaluation Thresholds
- **`PASS`**: Bounded `integer`/`natural` ranges, `unsigned`/`signed` arithmetic with `resize()`, typed FSM enumerations, and isolated CDC synchronizers.
- **`WARN`**: Unbounded `integer` counters or magic bit-slice indices instead of `'range`.
- **`FAIL`**: Unconstrained integer bit-width bloat, raw `std_logic_vector` arithmetic via non-standard packages, or unsynchronized CDC crossings.
