# Modern Solidity (0.8.20+) & On-Chain Security Idioms (`solidity/modern_stack`)

## Core Principles
1. **Modern Solidity 0.8.20+ & OpenZeppelin v5**: Use custom errors (`revert Err()`), `Ownable2Step` (two-step ownership transfer preventing irreversible typos), `SafeERC20` (`safeTransfer`/`forceApprove`), transient storage (`tstore`/`tload` / `ReentrancyGuardTransient` on Cancun+ EVM), and EIP-712 typed signatures with nonce + chainId + deadline replay protection (`AstFacts.modernization_hints`).
2. **Oracle & Flash-Loan Resistance**: Never rely on manipulable spot AMM reserves (`getReserves()`) as a price oracle; validate Chainlink `latestRoundData()` staleness (`updatedAt`), `answer > 0`, and sequencer uptime feeds (`AstFacts.dangerous_sinks`).
3. **Avoid Weak On-Chain Randomness**: Never derive lottery/game randomness from `block.timestamp`, `block.prevrandao`, or `blockhash` for high-value outcomes (CWE-330; use VRF).
4. **Pull-Over-Push & Pausable Emergency Controls**: Prefer withdrawal pull patterns over pushing ETH in loops and pair emergency admin controls with a `TimelockController` + multisig.
