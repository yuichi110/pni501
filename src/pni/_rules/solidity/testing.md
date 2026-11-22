# Testing, Fuzzing & Invariant Standards (Solidity)

## Core Principles
1. **Foundry (`forge test`) Unit, Fuzz & Invariant Suites**: Organize tests under `test/*.t.sol` (or Hardhat `test/*.test.ts`), combining deterministic unit tests (`test_*`, `testRevert_*`), stateless fuzz tests (`testFuzz_*`), and stateful invariant tests (`invariant_*`; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain branch & line coverage of 90%+ on value-handling contracts (`forge coverage`; `RuntimeFacts.coverage.line_coverage_pct`) — smart contracts are immutable once deployed and require stricter branch coverage than typical web apps.
3. **Adversarial & Economic Edge-Case Testing**: Explicitly test reentrancy attacker contracts, unauthorized callers (`vm.prank`), zero-amount/max-uint256 boundaries, fee-on-transfer/rebasing ERC-20 quirks, and front-running/slippage limits offline (no flaky mainnet RPC dependencies in unit tests).
4. **Meaningful Assertions**: Every test must verify state changes, balances, emitted events (`vm.expectEmit`), and exact custom-error reverts (`vm.expectRevert(MyError.selector)`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated unit + fuzz/invariant tests exist, `assertion_free_tests == 0`, adversarial/revert paths verified, and coverage `>= 85%`.
- **`WARN`**: Unit tests only (no fuzz/invariant tests) or coverage between `70%` and `84.9%`.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 70%`, or missing unauthorized-caller / reentrancy tests on asset-holding contracts.
