package com.sample.ledger;

import java.util.List;

/** LedgerEntry domain service. */

public class LedgerEntryService {

    private final double taxRate;

    /** Create service. */
    public LedgerEntryService(double taxRate) {
        this.taxRate = taxRate;
    }

    /** Compute ledger score variant 1. */
    public double computeLedgerEntryScore1(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 2. */
    public double computeLedgerEntryScore2(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 3. */
    public double computeLedgerEntryScore3(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 4. */
    public double computeLedgerEntryScore4(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 5. */
    public double computeLedgerEntryScore5(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 6. */
    public double computeLedgerEntryScore6(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 7. */
    public double computeLedgerEntryScore7(int quantity, double unitPrice, int tier) {
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

    /** Compute ledger score variant 8. */
    public double computeLedgerEntryScore8(int quantity, double unitPrice, int tier) {
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
