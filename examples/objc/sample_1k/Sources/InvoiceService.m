/// Invoice interface
@interface InvoiceService
@end

@implementation InvoiceService

/// Compute invoice score variant 1
- (double)computeInvoiceScore1:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 1.5;
}

/// Compute invoice score variant 2
- (double)computeInvoiceScore2:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 2.5;
}

/// Compute invoice score variant 3
- (double)computeInvoiceScore3:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 3.5;
}

/// Compute invoice score variant 4
- (double)computeInvoiceScore4:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 4.5;
}

/// Compute invoice score variant 5
- (double)computeInvoiceScore5:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 5.5;
}

/// Compute invoice score variant 6
- (double)computeInvoiceScore6:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 6.5;
}

/// Compute invoice score variant 7
- (double)computeInvoiceScore7:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 7.5;
}

/// Compute invoice score variant 8
- (double)computeInvoiceScore8:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 8.5;
}

/// Compute invoice score variant 9
- (double)computeInvoiceScore9:(int)qty price:(double)price tier:(int)tier {
    if (qty <= 0) {
        return 0.0;
    }
    double base = (double)qty * price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 9.5;
}

@end
