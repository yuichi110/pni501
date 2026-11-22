package inventory

// StockItemRecord holds immutable domain values.

type StockItemRecord struct {
    ID        string
    Quantity  int
    UnitPrice float64
    Tier      int
}

// StockItemService handles stock domain logic.

type StockItemService struct {
    TaxRate float64
}

// ComputeStockItemScore1 computes weighted score variant 1.
func (s *StockItemService) ComputeStockItemScore1(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore2 computes weighted score variant 2.
func (s *StockItemService) ComputeStockItemScore2(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore3 computes weighted score variant 3.
func (s *StockItemService) ComputeStockItemScore3(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore4 computes weighted score variant 4.
func (s *StockItemService) ComputeStockItemScore4(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore5 computes weighted score variant 5.
func (s *StockItemService) ComputeStockItemScore5(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore6 computes weighted score variant 6.
func (s *StockItemService) ComputeStockItemScore6(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore7 computes weighted score variant 7.
func (s *StockItemService) ComputeStockItemScore7(rec StockItemRecord, bonus float64) float64 {
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

// ComputeStockItemScore8 computes weighted score variant 8.
func (s *StockItemService) ComputeStockItemScore8(rec StockItemRecord, bonus float64) float64 {
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
