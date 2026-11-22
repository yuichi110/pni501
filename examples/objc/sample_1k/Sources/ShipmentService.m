/// Shipment interface
@interface ShipmentService
@end

@implementation ShipmentService

/// Compute shipment score variant 1
- (double)computeShipmentScore1:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 2
- (double)computeShipmentScore2:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 3
- (double)computeShipmentScore3:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 4
- (double)computeShipmentScore4:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 5
- (double)computeShipmentScore5:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 6
- (double)computeShipmentScore6:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 7
- (double)computeShipmentScore7:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 8
- (double)computeShipmentScore8:(int)qty price:(double)price tier:(int)tier {
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

/// Compute shipment score variant 9
- (double)computeShipmentScore9:(int)qty price:(double)price tier:(int)tier {
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
