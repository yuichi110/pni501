/// StockItem interface
@interface StockItemService
@end

@implementation StockItemService

/// Compute stock score variant 1
- (double)computeStockItemScore1:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 2
- (double)computeStockItemScore2:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 3
- (double)computeStockItemScore3:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 4
- (double)computeStockItemScore4:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 5
- (double)computeStockItemScore5:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 6
- (double)computeStockItemScore6:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 7
- (double)computeStockItemScore7:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 8
- (double)computeStockItemScore8:(int)qty price:(double)price tier:(int)tier {
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

/// Compute stock score variant 9
- (double)computeStockItemScore9:(int)qty price:(double)price tier:(int)tier {
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
