struct InvoiceRecord
    qty::Int
    price::Float64
    tier::Int
end

# Compute invoice score variant 1
function compute_invoice_score_1(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 1.5
end

# Compute invoice score variant 2
function compute_invoice_score_2(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 2.5
end

# Compute invoice score variant 3
function compute_invoice_score_3(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 3.5
end

# Compute invoice score variant 4
function compute_invoice_score_4(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 4.5
end

# Compute invoice score variant 5
function compute_invoice_score_5(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 5.5
end

# Compute invoice score variant 6
function compute_invoice_score_6(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 6.5
end

# Compute invoice score variant 7
function compute_invoice_score_7(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 7.5
end

# Compute invoice score variant 8
function compute_invoice_score_8(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 8.5
end

# Compute invoice score variant 9
function compute_invoice_score_9(rec::InvoiceRecord, tax_rate::Float64=0.1)
    if rec.qty <= 0
        return 0.0
    end
    base = rec.qty * rec.price
    if rec.tier >= 3
        base *= 0.90
    elseif rec.tier == 2
        base *= 0.95
    end
    return base * (1.0 + tax_rate) + 9.5
end
