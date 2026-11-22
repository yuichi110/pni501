/// Compute shipment score variant 1.
pub fn computeShipmentScore1(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 1.5;
}

/// Compute shipment score variant 2.
pub fn computeShipmentScore2(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 2.5;
}

/// Compute shipment score variant 3.
pub fn computeShipmentScore3(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 3.5;
}

/// Compute shipment score variant 4.
pub fn computeShipmentScore4(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 4.5;
}

/// Compute shipment score variant 5.
pub fn computeShipmentScore5(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 5.5;
}

/// Compute shipment score variant 6.
pub fn computeShipmentScore6(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 6.5;
}

/// Compute shipment score variant 7.
pub fn computeShipmentScore7(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 7.5;
}

/// Compute shipment score variant 8.
pub fn computeShipmentScore8(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 8.5;
}

/// Compute shipment score variant 9.
pub fn computeShipmentScore9(qty: i32, unit_price: f64, tier: u8) f64 {
    if (qty <= 0) {
        return 0.0;
    }
    var base: f64 = @as(f64, @floatFromInt(qty)) * unit_price;
    if (tier >= 3) {
        base *= 0.90;
    } else if (tier == 2) {
        base *= 0.95;
    }
    return base * 1.1 + 9.5;
}
