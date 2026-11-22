# Code Quality & Synthesizable RTL Standards (VHDL)

## Core Principles
1. **Standard IEEE `numeric_std` Only (Zero Non-Standard Synopsys Packages)**: Use `ieee.std_logic_1164.all` and `ieee.numeric_std.all` exclusively — forbid legacy non-standard `ieee.std_logic_arith`, `ieee.std_logic_unsigned`, and `ieee.std_logic_signed` (`AstFacts.bug_risk_idioms`).
2. **Clean Clocked vs. Combinational Processes & Zero Inferred Latches**: Use `rising_edge(clk)` (not `clk'event and clk = '1'`) in synchronous processes, use `process(all)` (VHDL-2008) for combinational processes, assign explicit default values before `if`/`case` statements, and include `when others =>` in every `case` statement to eliminate unintentional latches.
3. **Zero Shared Mutable Variables & Named Port Maps**: Avoid `shared variable` globals outside protected simulation monitors (`AstFacts.global_state_usages`), connect entity instantiations via explicit named `port map` / `generic map` associations (`clk => clk`), and keep `wait for <time>` strictly inside `tb/` testbenches.
4. **Entity Documentation & Hardware Domain Exemption**: Document every `entity` port/generic contract, clock/reset polarity, and latency in header comments (`AstFacts.docstring_coverage_pct`). Do **NOT** apply software OOP or exception rules to RTL entities.

## Evaluation Thresholds
- **`PASS`**: Standard `ieee.numeric_std`, `rising_edge(clk)` + `process(all)` discipline, zero inferred latches or `std_logic_arith`, named port maps, and documented entities.
- **`WARN`**: Missing header docs on minor internal entities or legacy `clk'event` syntax.
- **`FAIL`**: Non-standard `std_logic_arith`/`std_logic_unsigned`, unintentional latch inference, incomplete sensitivity lists, or `wait for` embedded in synthesizable RTL.
