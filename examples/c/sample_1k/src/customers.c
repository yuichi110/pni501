#include <stddef.h>

/** Customer record struct. */

struct customer_record {
    int quantity;
    double unit_price;
    int tier;
};

/** Compute customer score variant 1. */
double compute_customer_score_1(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 1.5;
}

/** Compute customer score variant 2. */
double compute_customer_score_2(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 2.5;
}

/** Compute customer score variant 3. */
double compute_customer_score_3(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 3.5;
}

/** Compute customer score variant 4. */
double compute_customer_score_4(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 4.5;
}

/** Compute customer score variant 5. */
double compute_customer_score_5(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 5.5;
}

/** Compute customer score variant 6. */
double compute_customer_score_6(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 6.5;
}

/** Compute customer score variant 7. */
double compute_customer_score_7(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 7.5;
}

/** Compute customer score variant 8. */
double compute_customer_score_8(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 8.5;
}

/** Compute customer score variant 9. */
double compute_customer_score_9(struct customer_record rec, double tax_rate) {
    if (rec.quantity <= 0) {
        return 0.0;
    }
    double base = (double)rec.quantity * rec.unit_price;
    if (rec.tier >= 3) {
        base *= 0.90;
    } else if (rec.tier == 2) {
        base *= 0.95;
    }
    return base * (1.0 + tax_rate) + 9.5;
}
