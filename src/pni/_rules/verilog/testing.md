# Verification & Testbench Standards (Verilog / SystemVerilog)

## Core Principles
1. **Self-Checking Testbenches (`tb_*.sv` / `*_tb.v` / cocotb / UVM)**: Organize self-checking testbenches under `tb/` or `sim/` that compare DUT outputs against a golden reference model and exit non-zero (`$fatal(1, ...)` / Python `assert`) on any mismatch (`AstFacts.test_functions_count`).
2. **Reset, Backpressure & Protocol Coverage**: Verify asynchronous/synchronous reset recovery, boundary widths (`0`, all-ones, overflow), `valid`/`ready` backpressure stalls, and FSM illegal-state transitions; track toggle/branch coverage via Verilator `--coverage` (`RuntimeFacts.coverage.line_coverage_pct`).
3. **Deterministic Simulation & Watchdog Timeouts**: Seed constrained-random stimuli deterministically and include a cycle-limit watchdog timeout in every testbench so hung handshakes fail fast instead of stalling CI forever.
4. **Meaningful Assertions**: Never rely solely on visual waveform inspection (`$dumpfile`) — every testbench must contain programmatic self-checking assertions (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Self-checking testbenches with `$fatal`/assertions, reset/backpressure edge cases, watchdog timeouts, and simulator-clean runs.
- **`WARN`**: Happy-path directed tests only (missing backpressure/reset edge cases or random seeds).
- **`FAIL`**: Zero testbenches (`test_files_count == 0`) or waveform-only dumps with zero self-checking assertions.
