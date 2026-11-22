# Bit-Width, Signal Typing & CDC Standards (Verilog / SystemVerilog)

## Core Principles
1. **Disable Implicit Nets & Prefer `logic` / `typedef enum`**: Put `` `default_nettype none `` in Verilog-2001 files (prevents silent 1-bit typos!) or use SystemVerilog `logic`, `typedef enum logic [...]` for FSM states, and `typedef struct packed` for bus payloads (`AstFacts.type_safety_coverage_pct`).
2. **Explicit Bit-Width & Signedness Hygiene**: Match LHS and RHS bit widths explicitly (avoid silent truncation or zero-extension bugs; parameterize widths with `localparam int WIDTH = ...` and `WIDTH'(expr)`), and never mix `signed` and `unsigned` operands unintentionally (`AstFacts.type_safety_issues`).
3. **Clock Domain Crossing (CDC) Discipline**: Synchronize every single-bit async signal crossing clock domains with a dedicated 2-FF synchronizer (and multi-bit crossings via Gray-coded async FIFOs or handshake protocols) — never sample raw async signals directly.
4. **Scoped Lint Waivers**: Scope `/* verilator lint_off WIDTH */` waivers to single lines with matching `lint_on` and rationale (`AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `logic`/`default_nettype none`, clean bit-width matching, typed FSM `enum`s, explicit CDC synchronizers, and scoped Verilator waivers.
- **`WARN`**: Isolated width-cast warnings or raw `reg`/`wire` in SystemVerilog files.
- **`FAIL`**: Unchecked bit-width truncation on datapaths, missing `default_nettype none` causing implicit 1-bit nets, or unsynchronized CDC paths.
