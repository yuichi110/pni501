/// Compute invoice score variant 1.
pub fn computeInvoiceScore1(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 2.
pub fn computeInvoiceScore2(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 3.
pub fn computeInvoiceScore3(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 4.
pub fn computeInvoiceScore4(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 5.
pub fn computeInvoiceScore5(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 6.
pub fn computeInvoiceScore6(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 7.
pub fn computeInvoiceScore7(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 8.
pub fn computeInvoiceScore8(qty: i32, unit_price: f64, tier: u8) f64 {
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

/// Compute invoice score variant 9.
pub fn computeInvoiceScore9(qty: i32, unit_price: f64, tier: u8) f64 {
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
