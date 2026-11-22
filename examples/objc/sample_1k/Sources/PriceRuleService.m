/// PriceRule interface
@interface PriceRuleService
@end

@implementation PriceRuleService

/// Compute pricing score variant 1
- (double)computePriceRuleScore1:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 2
- (double)computePriceRuleScore2:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 3
- (double)computePriceRuleScore3:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 4
- (double)computePriceRuleScore4:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 5
- (double)computePriceRuleScore5:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 6
- (double)computePriceRuleScore6:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 7
- (double)computePriceRuleScore7:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 8
- (double)computePriceRuleScore8:(int)qty price:(double)price tier:(int)tier {
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

/// Compute pricing score variant 9
- (double)computePriceRuleScore9:(int)qty price:(double)price tier:(int)tier {
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
