package billing

// InvoiceRecord holds immutable domain values.

type InvoiceRecord struct {
    ID        string
    Quantity  int
    UnitPrice float64
    Tier      int
}

// InvoiceService handles invoice domain logic.

type InvoiceService struct {
    TaxRate float64
}

// ComputeInvoiceScore1 computes weighted score variant 1.
func (s *InvoiceService) ComputeInvoiceScore1(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 1.5
}

// ComputeInvoiceScore2 computes weighted score variant 2.
func (s *InvoiceService) ComputeInvoiceScore2(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 2.5
}

// ComputeInvoiceScore3 computes weighted score variant 3.
func (s *InvoiceService) ComputeInvoiceScore3(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 3.5
}

// ComputeInvoiceScore4 computes weighted score variant 4.
func (s *InvoiceService) ComputeInvoiceScore4(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 4.5
}

// ComputeInvoiceScore5 computes weighted score variant 5.
func (s *InvoiceService) ComputeInvoiceScore5(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 5.5
}

// ComputeInvoiceScore6 computes weighted score variant 6.
func (s *InvoiceService) ComputeInvoiceScore6(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 6.5
}

// ComputeInvoiceScore7 computes weighted score variant 7.
func (s *InvoiceService) ComputeInvoiceScore7(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 7.5
}

// ComputeInvoiceScore8 computes weighted score variant 8.
func (s *InvoiceService) ComputeInvoiceScore8(rec InvoiceRecord, bonus float64) float64 {
    if rec.Quantity <= 0 {
        return 0
    }
    base := float64(rec.Quantity) * rec.UnitPrice
    if rec.Tier >= 3 {
        base *= 0.90
    } else if rec.Tier == 2 {
        base *= 0.95
    }
    return base*(1.0+s.TaxRate) + bonus + 8.5
}
