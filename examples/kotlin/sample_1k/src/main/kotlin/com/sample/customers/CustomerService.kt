package com.sample.customers

/** Customer domain service. */

class CustomerService(private val taxRate: Double = 0.1) {

    /** Compute customer score variant 1. */
    fun computeCustomerScore1(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 2. */
    fun computeCustomerScore2(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 3. */
    fun computeCustomerScore3(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 4. */
    fun computeCustomerScore4(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 5. */
    fun computeCustomerScore5(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 6. */
    fun computeCustomerScore6(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 7. */
    fun computeCustomerScore7(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 8. */
    fun computeCustomerScore8(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute customer score variant 9. */
    fun computeCustomerScore9(quantity: Int, unitPrice: Double, tier: Int): Double {
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
