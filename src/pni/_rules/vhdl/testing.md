# Verification & Testbench Standards (VHDL)

## Core Principles
1. **Self-Checking Testbenches (`tb_*.vhd` / VUnit / OSVVM / cocotb)**: Organize self-checking VHDL testbenches under `tb/` or `sim/` using VUnit (`check_equal`), OSVVM, or standard `assert ... report "..." severity failure;` so mismatches terminate simulation with non-zero exit code (`AstFacts.test_functions_count`).
2. **Reset, Boundary & FSM Coverage**: Test synchronous/asynchronous reset behavior, counter wrap/overflow edges, handshake backpressure, and invalid inputs; track code/functional coverage via GHDL/OSVVM (`RuntimeFacts.coverage.line_coverage_pct`).
3. **Deterministic Termination & Offline Execution**: Stop the clock cleanly (`std.env.stop` / `std.env.finish` in VHDL-2008) with a watchdog cycle timeout so simulations never hang indefinitely.
4. **Meaningful Assertions**: Never rely solely on waveform dumps (`.ghw`/`.vcd`) without programmatic `assert ... severity failure` checks (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Self-checking testbenches with `severity failure` / VUnit assertions, clean `std.env.finish` termination, and reset/boundary coverage.
- **`WARN`**: Directed happy-path tests only (missing backpressure/overflow cases).
- **`FAIL`**: Zero testbenches (`test_files_count == 0`) or waveform-only simulations lacking programmatic assertions.
