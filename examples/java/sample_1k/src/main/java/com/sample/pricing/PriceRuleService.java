package com.sample.pricing;

import java.util.List;

/** PriceRule domain service. */

public class PriceRuleService {

    private final double taxRate;

    /** Create service. */
    public PriceRuleService(double taxRate) {
        this.taxRate = taxRate;
    }

    /** Compute pricing score variant 1. */
    public double computePriceRuleScore1(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 2. */
    public double computePriceRuleScore2(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 3. */
    public double computePriceRuleScore3(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 4. */
    public double computePriceRuleScore4(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 5. */
    public double computePriceRuleScore5(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 6. */
    public double computePriceRuleScore6(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 7. */
    public double computePriceRuleScore7(int quantity, double unitPrice, int tier) {
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

    /** Compute pricing score variant 8. */
    public double computePriceRuleScore8(int quantity, double unitPrice, int tier) {
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
