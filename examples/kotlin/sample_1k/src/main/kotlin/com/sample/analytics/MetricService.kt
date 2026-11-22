package com.sample.analytics

/** Metric domain service. */

class MetricService(private val taxRate: Double = 0.1) {

    /** Compute metric score variant 1. */
    fun computeMetricScore1(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 2. */
    fun computeMetricScore2(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 3. */
    fun computeMetricScore3(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 4. */
    fun computeMetricScore4(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 5. */
    fun computeMetricScore5(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 6. */
    fun computeMetricScore6(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 7. */
    fun computeMetricScore7(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 8. */
    fun computeMetricScore8(quantity: Int, unitPrice: Double, tier: Int): Double {
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

    /** Compute metric score variant 9. */
    fun computeMetricScore9(quantity: Int, unitPrice: Double, tier: Int): Double {
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
