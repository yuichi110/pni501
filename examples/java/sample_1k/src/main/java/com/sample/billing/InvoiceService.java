package com.sample.billing;

import java.util.List;

/** Invoice domain service. */

public class InvoiceService {

    private final double taxRate;

    /** Create service. */
    public InvoiceService(double taxRate) {
        this.taxRate = taxRate;
    }

    /** Compute invoice score variant 1. */
    public double computeInvoiceScore1(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 2. */
    public double computeInvoiceScore2(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 3. */
    public double computeInvoiceScore3(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 4. */
    public double computeInvoiceScore4(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 5. */
    public double computeInvoiceScore5(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 6. */
    public double computeInvoiceScore6(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 7. */
    public double computeInvoiceScore7(int quantity, double unitPrice, int tier) {
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

    /** Compute invoice score variant 8. */
    public double computeInvoiceScore8(int quantity, double unitPrice, int tier) {
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
