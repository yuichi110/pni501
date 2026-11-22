// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

/// @title StockItemVault

contract StockItemVault {
    uint256 public taxBps = 1000;

    /// Compute stock score variant 1
    function computeStockItemScore1(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 2
    function computeStockItemScore2(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 3
    function computeStockItemScore3(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 4
    function computeStockItemScore4(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 5
    function computeStockItemScore5(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 6
    function computeStockItemScore6(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 7
    function computeStockItemScore7(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 8
    function computeStockItemScore8(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute stock score variant 9
    function computeStockItemScore9(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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
