// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract LegacyVault {
    address public owner;
    function dangerousWithdraw(address target, bytes calldata data) external {
        require(tx.origin == owner);
        (bool ok, ) = target.delegatecall(data);
        require(ok);
    }
}
