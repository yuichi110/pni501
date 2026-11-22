# Code Quality & Smart-Contract Security Standards (Solidity)

## Core Principles
1. **Checks-Effects-Interactions (CEI) & Reentrancy Protection**: Mutate all internal contract state BEFORE external `.call` / token transfers and guard state-changing entrypoints with OpenZeppelin `ReentrancyGuard` (`nonReentrant`) to prevent Reentrancy exploits (CWE-841; `AstFacts.dangerous_sinks`, `AstFacts.bug_risk_idioms`).
2. **Zero `tx.origin` Auth, Unsafe `delegatecall` or `selfdestruct`**: Strictly forbid `tx.origin` for authorization (phishing bypass; CWE-287 — always use `msg.sender`), forbid `delegatecall` to untrusted/mutable addresses (storage takeover; CWE-829), forbid deprecated `selfdestruct`, and always check return values of low-level `.call{value: ...}` / ERC-20 transfers (`SafeERC20`).
3. **Explicit Access Control, Events & NatSpec**: Protect every privileged `external`/`public` function with explicit modifiers (`onlyOwner`, `AccessControl` `onlyRole`, zero-address checks), emit indexed events on all state mutations, and document contracts/functions with NatSpec (`/// @notice`, `@dev`, `@param`, `@return`; `AstFacts.docstring_coverage_pct`).
4. **Gas-Bounded Loops & Slither/Solhint Hygiene**: Never iterate over unbounded user-growable arrays in on-chain transactions (DoS out-of-gas; use pull-over-push), format with `forge fmt`, and verify with `slither` / `solhint`.

## Evaluation Thresholds
- **`PASS`**: CEI + `ReentrancyGuard`, zero `tx.origin`/untrusted `delegatecall`/unchecked low-level `.call`, explicit access control + events, and NatSpec `>= 80%`.
- **`WARN`**: Missing NatSpec on internal helpers, non-indexed event params, or minor gas-optimization findings.
- **`FAIL`**: Reentrancy vulnerability, `tx.origin` auth, untrusted `delegatecall`, missing access control on privileged functions, or unchecked ERC-20 / low-level call returns.
