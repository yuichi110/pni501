package billing

Invoice_Record :: struct {
    qty: int,
    price: f64,
    tier: int,
}

// Compute invoice score variant 1
compute_invoice_score_1 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 2
compute_invoice_score_2 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 3
compute_invoice_score_3 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 4
compute_invoice_score_4 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 5
compute_invoice_score_5 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 6
compute_invoice_score_6 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 7
compute_invoice_score_7 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 8
compute_invoice_score_8 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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

// Compute invoice score variant 9
compute_invoice_score_9 :: proc(rec: Invoice_Record, tax_rate: f64) -> f64 {
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
