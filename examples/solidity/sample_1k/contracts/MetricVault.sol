// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

/// @title MetricVault

contract MetricVault {
    uint256 public taxBps = 1000;

    /// Compute metric score variant 1
    function computeMetricScore1(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 2
    function computeMetricScore2(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 3
    function computeMetricScore3(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 4
    function computeMetricScore4(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 5
    function computeMetricScore5(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 6
    function computeMetricScore6(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 7
    function computeMetricScore7(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 8
    function computeMetricScore8(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute metric score variant 9
    function computeMetricScore9(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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
