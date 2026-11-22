# Typing, Solidity 0.8+ Arithmetic, Visibility & Storage Standards (Solidity)

## Core Principles
1. **Pinned Solidity `0.8.20+` Checked Arithmetic & Explicit `unchecked`**: Use Solidity `>= 0.8.20` (built-in overflow/underflow revert protection) with locked pragma on deployable contracts (`pragma solidity 0.8.26;` — floating `^` acceptable only on libraries) and justify every `unchecked { ... }` block with an inline proof (`AstFacts.type_safety_issues`).
2. **Explicit Visibility, Mutability & Data Location**: Declare explicit visibility (`external`, `public`, `internal`, `private`), state mutability (`view`, `pure`, `payable`), and data location (`calldata` over `memory` for read-only external params) on every function and state variable; guard integer downcasts (`uint256 -> uint128`) with OpenZeppelin `SafeCast`.
3. **Upgradeable Proxy Storage Discipline**: For UUPS/Transparent proxies, preserve storage slot order (use ERC-7201 namespaced storage or `__gap` slots), call `_disableInitializers()` in implementation constructors, and never initialize state variables inline on proxy implementations.
4. **Custom Errors & Typed Interfaces**: Prefer gas-efficient `error Unauthorized(address caller);` over string `require(..., "...")`, and type external contracts with strict `IERC20` / interface types rather than raw `address` + `abi.encodeWithSignature`.

## Evaluation Thresholds
- **`PASS`**: Solidity `0.8.20+`, locked deploy pragma, `SafeCast` on narrowing casts, explicit visibility/mutability, and safe proxy storage discipline.
- **`WARN`**: Floating pragma on deployable contract or string `require` messages instead of custom errors.
- **`FAIL`**: Solidity `< 0.8.0` without `SafeMath`, unsafe downcasts / precision loss (division before multiplication), or uninitialized proxy / storage-slot collisions.
