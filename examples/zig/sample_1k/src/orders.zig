/// Compute order score variant 1.
pub fn computeOrderScore1(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 2.
pub fn computeOrderScore2(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 3.
pub fn computeOrderScore3(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 4.
pub fn computeOrderScore4(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 5.
pub fn computeOrderScore5(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 6.
pub fn computeOrderScore6(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 7.
pub fn computeOrderScore7(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 8.
pub fn computeOrderScore8(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute order score variant 9.
pub fn computeOrderScore9(qty: i32, unit_price: f64, tier: u8) f64 {
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
