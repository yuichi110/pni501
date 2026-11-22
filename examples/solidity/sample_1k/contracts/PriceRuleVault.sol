// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

/// @title PriceRuleVault

contract PriceRuleVault {
    uint256 public taxBps = 1000;

    /// Compute pricing score variant 1
    function computePriceRuleScore1(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 2
    function computePriceRuleScore2(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 3
    function computePriceRuleScore3(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 4
    function computePriceRuleScore4(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 5
    function computePriceRuleScore5(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 6
    function computePriceRuleScore6(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 7
    function computePriceRuleScore7(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 8
    function computePriceRuleScore8(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute pricing score variant 9
    function computePriceRuleScore9(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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
