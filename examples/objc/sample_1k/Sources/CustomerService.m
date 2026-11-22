/// Customer interface
@interface CustomerService
@end

@implementation CustomerService

/// Compute customer score variant 1
- (double)computeCustomerScore1:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 2
- (double)computeCustomerScore2:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 3
- (double)computeCustomerScore3:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 4
- (double)computeCustomerScore4:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 5
- (double)computeCustomerScore5:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 6
- (double)computeCustomerScore6:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 7
- (double)computeCustomerScore7:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 8
- (double)computeCustomerScore8:(int)qty price:(double)price tier:(int)tier {
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

/// Compute customer score variant 9
- (double)computeCustomerScore9:(int)qty price:(double)price tier:(int)tier {
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
