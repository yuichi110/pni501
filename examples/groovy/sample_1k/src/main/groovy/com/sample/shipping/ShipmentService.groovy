package com.sample.shipping;

/** Shipment Groovy service. */

class ShipmentService {
    double taxRate = 0.1;

    /** Compute shipment score variant 1. */
    double computeShipmentScore1(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 1.5;
    }

    /** Compute shipment score variant 2. */
    double computeShipmentScore2(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 2.5;
    }

    /** Compute shipment score variant 3. */
    double computeShipmentScore3(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 3.5;
    }

    /** Compute shipment score variant 4. */
    double computeShipmentScore4(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 4.5;
    }

    /** Compute shipment score variant 5. */
    double computeShipmentScore5(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 5.5;
    }

    /** Compute shipment score variant 6. */
    double computeShipmentScore6(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 6.5;
    }

    /** Compute shipment score variant 7. */
    double computeShipmentScore7(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 7.5;
    }

    /** Compute shipment score variant 8. */
    double computeShipmentScore8(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 8.5;
    }

    /** Compute shipment score variant 9. */
    double computeShipmentScore9(int quantity, double unitPrice, int tier) {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = quantity * unitPrice;
        if (tier >= 3) {
            base = base * 0.90;
        } else if (tier == 2) {
            base = base * 0.95;
        }
        return base * (1.0 + taxRate) + 9.5;
    }

}
