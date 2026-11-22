# Code Quality & Synthesizable RTL Standards (Verilog / SystemVerilog)

## Core Principles
1. **Strict Blocking (`=`) vs. Non-Blocking (`<=`) Discipline**: Use **non-blocking (`<=`)** exclusively inside sequential clocked blocks (`always_ff @(posedge clk)`) and **blocking (`=`)** exclusively inside combinational blocks (`always_comb` / `always @*`) — never mix both on the same signal (`AstFacts.bug_risk_idioms`).
2. **Zero Unintentional Latches & Zero Synthesizable `#delay`s**: Assign defaults to every output at the top of `always_comb` and include `default:` branches in `case` statements to prevent inferred latches; never place `#delay`, `initial` reset assumptions (outside FPGA-documented ROM/init), or `$display` in synthesizable RTL (keep them strictly inside `tb/` testbenches).
3. **Verilator / Verible Lint & Named Port Connections**: Lint RTL cleanly with `verilator --lint-only -Wall` and `verible-verilog-lint`, always connect module instances by explicit named ports (`.clk(clk)` — never fragile positional connections), and avoid multi-driven nets.
4. **Module Documentation & Hardware Domain Exemption**: Document module ports, parameters, clock/reset polarity, and handshake protocols (`valid`/`ready`) in header comments (`AstFacts.docstring_coverage_pct`). Do **NOT** apply software OOP or exception-handling rules to RTL modules.

## Evaluation Thresholds
- **`PASS`**: Clean `always_ff` (`<=`) / `always_comb` (`=`) separation, zero inferred latches or `#delay` in RTL, named port bindings, and `verilator --lint-only` cleanliness.
- **`WARN`**: Missing port/reset header comments or positional port connections on minor internal primitives.
- **`FAIL`**: Mixed `=`/`<=` in sequential blocks, unintentional latch inference, multi-driven signals, or non-synthesizable delays embedded in RTL.
