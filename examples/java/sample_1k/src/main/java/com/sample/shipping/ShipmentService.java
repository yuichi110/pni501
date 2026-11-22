package com.sample.shipping;

import java.util.List;

/** Shipment domain service. */

public class ShipmentService {

    private final double taxRate;

    /** Create service. */
    public ShipmentService(double taxRate) {
        this.taxRate = taxRate;
    }

    /** Compute shipment score variant 1. */
    public double computeShipmentScore1(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 1.5;
    }

    /** Compute shipment score variant 2. */
    public double computeShipmentScore2(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 2.5;
    }

    /** Compute shipment score variant 3. */
    public double computeShipmentScore3(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 3.5;
    }

    /** Compute shipment score variant 4. */
    public double computeShipmentScore4(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 4.5;
    }

    /** Compute shipment score variant 5. */
    public double computeShipmentScore5(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 5.5;
    }

    /** Compute shipment score variant 6. */
    public double computeShipmentScore6(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 6.5;
    }

    /** Compute shipment score variant 7. */
    public double computeShipmentScore7(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 7.5;
    }

    /** Compute shipment score variant 8. */
    public double computeShipmentScore8(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + this.taxRate) + 8.5;
    }

}
