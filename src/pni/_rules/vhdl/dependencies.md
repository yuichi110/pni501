# IP Packaging, Libraries & Toolchain Standards (VHDL)

## Core Principles
1. **Explicit VHDL Standard (`--std=08` / VHDL-2008) & Compile Order**: Declare the VHDL standard (`VHDL-2008` or `VHDL-2019`) and deterministic library compile order in `run.py` (VUnit), FuseSoC `*.core`, `hdl-prj`, or `Makefile` (`ProjectFacts.language_version_constraint`).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: VHDL repositories do **not** use npm-style lockfiles — do **NOT** penalize RTL repos for lacking one; instead verify pinned external IP submodules/commits (`ProjectFacts.unpinned_dependencies`).
3. **Clean `rtl/` vs `tb/` Library Separation**: Keep synthesizable entities under `rtl/`/`src/` and verification harnesses under `tb/`/`sim/` cleanly separated with explicit VHDL library namespaces.
4. **Open-Source Lint & Simulation**: Support reproducible analysis/simulation with `ghdl` (`--std=08 -Wall`), `vsg` (VHDL Style Guide), or `nvc` in CI.

## Evaluation Thresholds
- **`PASS`**: Explicit VHDL-2008+ standard, deterministic compile order (`VUnit`/FuseSoC/`Makefile`), clean `rtl/` vs `tb/` split, and pinned IP submodules.
- **`WARN`**: Legacy VHDL-1993 flags or missing automated `ghdl` lint step.
- **`FAIL`**: Unpinned external IP branches, missing compile order causing broken builds, or mixed RTL/testbench synthesis lists.
