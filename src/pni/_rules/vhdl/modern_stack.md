# Modern VHDL-2008 / VHDL-2019 RTL Idioms (`vhdl/modern_stack`)

## Core Principles
1. **VHDL-2008 Synthesizable Ergonomics**: Adopt `process(all)`, reading `out` ports directly (without dummy `_i` internal shadow signals), direct entity instantiation (`entity work.my_mod port map (...)` eliminating duplicate `component` declarations), `std.env.finish`, and `numeric_std_unsigned` only when appropriate (`AstFacts.modernization_hints`).
2. **Parameterized Generic Packages & Record Interfaces**: Use VHDL-2008 unconstrained array fields in `record` types and generic packages to eliminate copy-pasted bus wrappers.
3. **Explicit `std_ulogic` / Single-Driver Discipline**: Prefer `std_ulogic` / `std_ulogic_vector` internally so multi-driver conflicts fail at compile/elaboration time rather than producing `'X'` in simulation (`AstFacts.bug_risk_idioms`).
4. **Reproducible Open-Source Verification**: Combine GHDL / NVC simulation with VUnit or `cocotb` and Yosys + `ghdl-yosys-plugin` synthesis checks.
