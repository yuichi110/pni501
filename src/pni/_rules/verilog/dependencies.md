# IP Packaging, Filelists & Toolchain Standards (Verilog / SystemVerilog)

## Core Principles
1. **Declarative Filelists & Build Metadata**: Provide reproducible RTL/simulation filelists (`*.f`, FuseSoC `*.core`, Bender `Bender.yml`, or clean `Makefile`) specifying the exact SystemVerilog standard (`-g2012` / `IEEE 1800-2017`) and include directories (`ProjectFacts.language_version_constraint`).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: HDL repositories rarely use npm-style lockfiles — do **NOT** penalize RTL projects for lacking one; instead verify that third-party IP cores (`Bender.lock`, git submodules) are pinned to exact commits/tags (`ProjectFacts.unpinned_dependencies`).
3. **Strict RTL vs Simulation Separation**: Keep synthesizable RTL (`rtl/` / `src/`) cleanly separated from testbenches (`tb/` / `sim/`) and vendor black-box stubs.
4. **Open-Source Lint/Sim Reproducibility**: Support reproducible lint/simulation via Verilator, Icarus Verilog (`iverilog`), or Yosys synthesis checks in CI.

## Evaluation Thresholds
- **`PASS`**: Clean `rtl/` vs `tb/` separation, deterministic filelist / FuseSoC / Makefile, and pinned external IP submodules.
- **`WARN`**: Missing `verilator --lint-only` CI target or undocumented simulator version.
- **`FAIL`**: Unpinned external IP branches, tangled RTL+testbench source lists, or missing build/sim instructions.
