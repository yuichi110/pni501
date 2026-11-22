package com.sample.pricing;

/** PriceRule Groovy service. */

class PriceRuleService {
    double taxRate = 0.1;

    /** Compute pricing score variant 1. */
    double computePriceRuleScore1(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 2. */
    double computePriceRuleScore2(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 3. */
    double computePriceRuleScore3(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 4. */
    double computePriceRuleScore4(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 5. */
    double computePriceRuleScore5(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 6. */
    double computePriceRuleScore6(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 7. */
    double computePriceRuleScore7(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 8. */
    double computePriceRuleScore8(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 9. */
    double computePriceRuleScore9(int quantity, double unitPrice, int tier) {
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
