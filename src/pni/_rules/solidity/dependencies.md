# Dependency & Foundry/Hardhat Management Standards (Solidity)

## Core Principles
1. **Audited Standard Libraries & Locked Commits**: Use audited, pinned versions of OpenZeppelin Contracts (`@openzeppelin/contracts` v5+) or Solady — never fork/hand-roll cryptographic signature verification (`ECDSA`), EIP-712, or Merkle proofs.
2. **Reproducible Pinning (`foundry.toml` / `remappings.txt` / Lockfiles)**:
   - **Foundry**: Pin exact `solc_version`, `evm_version`, and git submodules (`.gitmodules` exact commit SHAs) or `soldeer.lock` (`ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
   - **Hardhat**: Commit `package-lock.json` / `pnpm-lock.yaml` with exact compiler settings (`ProjectFacts.lockfiles_found`).
3. **Strict Compiler Settings**: Document optimizer runs (`optimizer = true`, `optimizer_runs = ...`) and `via_ir` settings reproducibly for Etherscan/Sourcify verification.
4. **Static Security Tooling**: Integrate `slither`, `aderyn`, or `mythril` alongside Trivy in CI.

## Evaluation Thresholds
- **`PASS`**: Pinned Solidity `0.8.20+` compiler, pinned OpenZeppelin/audited libraries (`unpinned_dependencies == 0`), and reproducible Foundry/Hardhat config.
- **`WARN`**: Floating OpenZeppelin minor range or missing Slither CI step.
- **`FAIL`**: Unpinned / unverified third-party contract imports, EOL Solidity `< 0.8.0`, or known-vulnerable OpenZeppelin release.
