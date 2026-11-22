package com.sample.orders

/** Order domain service. */

class OrderService(private val taxRate: Double = 0.1) {

    /** Compute order score variant 1. */
    fun computeOrderScore1(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 2. */
    fun computeOrderScore2(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 3. */
    fun computeOrderScore3(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 4. */
    fun computeOrderScore4(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 5. */
    fun computeOrderScore5(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 6. */
    fun computeOrderScore6(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 7. */
    fun computeOrderScore7(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 8. */
    fun computeOrderScore8(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute order score variant 9. */
    fun computeOrderScore9(quantity: Int, unitPrice: Double, tier: Int): Double {
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
