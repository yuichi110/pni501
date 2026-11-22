package com.sample.customers;

/** Customer Groovy service. */

class CustomerService {
    double taxRate = 0.1;

    /** Compute customer score variant 1. */
    double computeCustomerScore1(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 2. */
    double computeCustomerScore2(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 3. */
    double computeCustomerScore3(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 4. */
    double computeCustomerScore4(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 5. */
    double computeCustomerScore5(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 6. */
    double computeCustomerScore6(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 7. */
    double computeCustomerScore7(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 8. */
    double computeCustomerScore8(int quantity, double unitPrice, int tier) {
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

    /** Compute customer score variant 9. */
    double computeCustomerScore9(int quantity, double unitPrice, int tier) {
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
