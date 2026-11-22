package ledger

// LedgerEntryRecord holds immutable domain values.

type LedgerEntryRecord struct {
    ID        string
    Quantity  int
    UnitPrice float64
    Tier      int
}

// LedgerEntryService handles ledger domain logic.

type LedgerEntryService struct {
    TaxRate float64
}

// ComputeLedgerEntryScore1 computes weighted score variant 1.
func (s *LedgerEntryService) ComputeLedgerEntryScore1(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore2 computes weighted score variant 2.
func (s *LedgerEntryService) ComputeLedgerEntryScore2(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore3 computes weighted score variant 3.
func (s *LedgerEntryService) ComputeLedgerEntryScore3(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore4 computes weighted score variant 4.
func (s *LedgerEntryService) ComputeLedgerEntryScore4(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore5 computes weighted score variant 5.
func (s *LedgerEntryService) ComputeLedgerEntryScore5(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore6 computes weighted score variant 6.
func (s *LedgerEntryService) ComputeLedgerEntryScore6(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore7 computes weighted score variant 7.
func (s *LedgerEntryService) ComputeLedgerEntryScore7(rec LedgerEntryRecord, bonus float64) float64 {
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

// ComputeLedgerEntryScore8 computes weighted score variant 8.
func (s *LedgerEntryService) ComputeLedgerEntryScore8(rec LedgerEntryRecord, bonus float64) float64 {
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
