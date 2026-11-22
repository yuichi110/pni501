package pricing

// PriceRuleRecord holds immutable domain values.

type PriceRuleRecord struct {
    ID        string
    Quantity  int
    UnitPrice float64
    Tier      int
}

// PriceRuleService handles pricing domain logic.

type PriceRuleService struct {
    TaxRate float64
}

// ComputePriceRuleScore1 computes weighted score variant 1.
func (s *PriceRuleService) ComputePriceRuleScore1(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore2 computes weighted score variant 2.
func (s *PriceRuleService) ComputePriceRuleScore2(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore3 computes weighted score variant 3.
func (s *PriceRuleService) ComputePriceRuleScore3(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore4 computes weighted score variant 4.
func (s *PriceRuleService) ComputePriceRuleScore4(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore5 computes weighted score variant 5.
func (s *PriceRuleService) ComputePriceRuleScore5(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore6 computes weighted score variant 6.
func (s *PriceRuleService) ComputePriceRuleScore6(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore7 computes weighted score variant 7.
func (s *PriceRuleService) ComputePriceRuleScore7(rec PriceRuleRecord, bonus float64) float64 {
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

// ComputePriceRuleScore8 computes weighted score variant 8.
func (s *PriceRuleService) ComputePriceRuleScore8(rec PriceRuleRecord, bonus float64) float64 {
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
