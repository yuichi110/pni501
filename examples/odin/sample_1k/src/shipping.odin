package shipping

Shipment_Record :: struct {
    qty: int,
    price: f64,
    tier: int,
}

// Compute shipment score variant 1
compute_shipment_score_1 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 2
compute_shipment_score_2 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 3
compute_shipment_score_3 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 4
compute_shipment_score_4 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 5
compute_shipment_score_5 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 6
compute_shipment_score_6 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 7
compute_shipment_score_7 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 8
compute_shipment_score_8 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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

// Compute shipment score variant 9
compute_shipment_score_9 :: proc(rec: Shipment_Record, tax_rate: f64) -> f64 {
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
