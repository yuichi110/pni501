package com.sample.pricing

/** PriceRule domain service. */

class PriceRuleService(private val taxRate: Double = 0.1) {

    /** Compute pricing score variant 1. */
    fun computePriceRuleScore1(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 2. */
    fun computePriceRuleScore2(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 3. */
    fun computePriceRuleScore3(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 4. */
    fun computePriceRuleScore4(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 5. */
    fun computePriceRuleScore5(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 6. */
    fun computePriceRuleScore6(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 7. */
    fun computePriceRuleScore7(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 8. */
    fun computePriceRuleScore8(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute pricing score variant 9. */
    fun computePriceRuleScore9(quantity: Int, unitPrice: Double, tier: Int): Double {
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
