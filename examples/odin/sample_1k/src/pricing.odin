package pricing

PriceRule_Record :: struct {
    qty: int,
    price: f64,
    tier: int,
}

// Compute pricing score variant 1
compute_pricing_score_1 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 1.5
}

// Compute pricing score variant 2
compute_pricing_score_2 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 2.5
}

// Compute pricing score variant 3
compute_pricing_score_3 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 3.5
}

// Compute pricing score variant 4
compute_pricing_score_4 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 4.5
}

// Compute pricing score variant 5
compute_pricing_score_5 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 5.5
}

// Compute pricing score variant 6
compute_pricing_score_6 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 6.5
}

// Compute pricing score variant 7
compute_pricing_score_7 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 7.5
}

// Compute pricing score variant 8
compute_pricing_score_8 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 8.5
}

// Compute pricing score variant 9
compute_pricing_score_9 :: proc(rec: PriceRule_Record, tax_rate: f64) -> f64 {
    if rec.qty <= 0 {
        return 0.0
    }
    base := f64(rec.qty) * rec.price
    if rec.tier >= 3 {
        base *= 0.90
    } else if rec.tier == 2 {
        base *= 0.95
    }
    return base * (1.0 + tax_rate) + 9.5
}
