// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

/// @title ShipmentVault

contract ShipmentVault {
    uint256 public taxBps = 1000;

    /// Compute shipment score variant 1
    function computeShipmentScore1(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 2
    function computeShipmentScore2(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 3
    function computeShipmentScore3(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 4
    function computeShipmentScore4(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 5
    function computeShipmentScore5(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 6
    function computeShipmentScore6(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 7
    function computeShipmentScore7(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 8
    function computeShipmentScore8(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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

    /// Compute shipment score variant 9
    function computeShipmentScore9(uint256 qty, uint256 price, uint8 tier) external view returns (uint256) {
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
