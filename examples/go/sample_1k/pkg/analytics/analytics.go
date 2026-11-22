package analytics

// MetricRecord holds immutable domain values.

type MetricRecord struct {
    ID        string
    Quantity  int
    UnitPrice float64
    Tier      int
}

// MetricService handles metric domain logic.

type MetricService struct {
    TaxRate float64
}

// ComputeMetricScore1 computes weighted score variant 1.
func (s *MetricService) ComputeMetricScore1(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore2 computes weighted score variant 2.
func (s *MetricService) ComputeMetricScore2(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore3 computes weighted score variant 3.
func (s *MetricService) ComputeMetricScore3(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore4 computes weighted score variant 4.
func (s *MetricService) ComputeMetricScore4(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore5 computes weighted score variant 5.
func (s *MetricService) ComputeMetricScore5(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore6 computes weighted score variant 6.
func (s *MetricService) ComputeMetricScore6(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore7 computes weighted score variant 7.
func (s *MetricService) ComputeMetricScore7(rec MetricRecord, bonus float64) float64 {
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

// ComputeMetricScore8 computes weighted score variant 8.
func (s *MetricService) ComputeMetricScore8(rec MetricRecord, bonus float64) float64 {
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
