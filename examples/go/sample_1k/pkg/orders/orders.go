package orders

// OrderRecord holds immutable domain values.

type OrderRecord struct {
    ID        string
    Quantity  int
    UnitPrice float64
    Tier      int
}

// OrderService handles order domain logic.

type OrderService struct {
    TaxRate float64
}

// ComputeOrderScore1 computes weighted score variant 1.
func (s *OrderService) ComputeOrderScore1(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore2 computes weighted score variant 2.
func (s *OrderService) ComputeOrderScore2(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore3 computes weighted score variant 3.
func (s *OrderService) ComputeOrderScore3(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore4 computes weighted score variant 4.
func (s *OrderService) ComputeOrderScore4(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore5 computes weighted score variant 5.
func (s *OrderService) ComputeOrderScore5(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore6 computes weighted score variant 6.
func (s *OrderService) ComputeOrderScore6(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore7 computes weighted score variant 7.
func (s *OrderService) ComputeOrderScore7(rec OrderRecord, bonus float64) float64 {
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

// ComputeOrderScore8 computes weighted score variant 8.
func (s *OrderService) ComputeOrderScore8(rec OrderRecord, bonus float64) float64 {
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
