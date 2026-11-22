/// Compute metric score variant 1.
pub fn computeMetricScore1(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 2.
pub fn computeMetricScore2(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 3.
pub fn computeMetricScore3(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 4.
pub fn computeMetricScore4(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 5.
pub fn computeMetricScore5(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 6.
pub fn computeMetricScore6(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 7.
pub fn computeMetricScore7(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 8.
pub fn computeMetricScore8(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute metric score variant 9.
pub fn computeMetricScore9(qty: i32, unit_price: f64, tier: u8) f64 {
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
