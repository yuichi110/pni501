// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

/// @title OrderVault

contract OrderVault {
    uint256 public taxBps = 1000;

    /// Compute order score variant 1
    function computeOrderScore1(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 1;
    }

    /// Compute order score variant 2
    function computeOrderScore2(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 2;
    }

    /// Compute order score variant 3
    function computeOrderScore3(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 3;
    }

    /// Compute order score variant 4
    function computeOrderScore4(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 4;
    }

    /// Compute order score variant 5
    function computeOrderScore5(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 5;
    }

    /// Compute order score variant 6
    function computeOrderScore6(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 6;
    }

    /// Compute order score variant 7
    function computeOrderScore7(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 7;
    }

    /// Compute order score variant 8
    function computeOrderScore8(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 8;
    }

    /// Compute order score variant 9
    function computeOrderScore9(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
        if (qty == 0) {
            return 0;
        }
        uint256 baseVal = qty * price;
        if (tier >= 3) {
            baseVal = (baseVal * 90) / 100;
        } else if (tier == 2) {
            baseVal = (baseVal * 95) / 100;
        }
        return baseVal + (baseVal * taxBps) / 10000 + 9;
    }

}
