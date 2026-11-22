# Modern SystemVerilog (IEEE 1800-2017) RTL Idioms (`verilog/modern_stack`)

## Core Principles
1. **SystemVerilog-2012/2017 Over Legacy Verilog-1995/2001**: Prefer ANSI-style port declarations, `always_ff` / `always_comb` / `always_latch`, `logic`, `package` + `typedef`, and `unique case` / `priority case` over legacy `always @(*)`, `reg`/`wire`, and non-ANSI port lists (`AstFacts.modernization_hints`).
2. **SystemVerilog Assertions (SVA) & Synthesis Guards**: Embed lightweight `assert` / `assume` invariants guarded by `` `ifndef SYNTHESIS `` so formal tools and simulators verify protocol contracts continuously.
3. **Clean Reset & Clocking**: Use consistent synchronous or active-low asynchronous reset strategy across the design (avoid mixing reset styles haphazardly) and avoid gated clocks in RTL (`AstFacts.bug_risk_idioms`).
4. **Modern Verification Flows**: Combine Verilator fast C++/Python (`cocotb`) verification with Yosys synthesis sanity checks.
