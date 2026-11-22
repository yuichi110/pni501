package com.sample.shipping

/** Shipment domain service. */

class ShipmentService(private val taxRate: Double = 0.1) {

    /** Compute shipment score variant 1. */
    fun computeShipmentScore1(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 1.5
    }

    /** Compute shipment score variant 2. */
    fun computeShipmentScore2(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 2.5
    }

    /** Compute shipment score variant 3. */
    fun computeShipmentScore3(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 3.5
    }

    /** Compute shipment score variant 4. */
    fun computeShipmentScore4(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 4.5
    }

    /** Compute shipment score variant 5. */
    fun computeShipmentScore5(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 5.5
    }

    /** Compute shipment score variant 6. */
    fun computeShipmentScore6(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 6.5
    }

    /** Compute shipment score variant 7. */
    fun computeShipmentScore7(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 7.5
    }

    /** Compute shipment score variant 8. */
    fun computeShipmentScore8(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 8.5
    }

    /** Compute shipment score variant 9. */
    fun computeShipmentScore9(quantity: Int, unitPrice: Double, tier: Int): Double {
        if (quantity <= 0) {
            return 0.0
        }
        var base = quantity * unitPrice
        if (tier >= 3) {
            base *= 0.90
        } else if (tier == 2) {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 9.5
    }

}
