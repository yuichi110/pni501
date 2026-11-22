import Foundation

/// Metric domain service.

public class MetricService {
    let taxRate: Double

    /// Initialize service.
    public init(taxRate: Double = 0.1) {
        self.taxRate = taxRate
    }

    /// Compute metric score variant 1.
    public func computeMetricScore1(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 1.5
    }

    /// Compute metric score variant 2.
    public func computeMetricScore2(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 2.5
    }

    /// Compute metric score variant 3.
    public func computeMetricScore3(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 3.5
    }

    /// Compute metric score variant 4.
    public func computeMetricScore4(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 4.5
    }

    /// Compute metric score variant 5.
    public func computeMetricScore5(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 5.5
    }

    /// Compute metric score variant 6.
    public func computeMetricScore6(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 6.5
    }

    /// Compute metric score variant 7.
    public func computeMetricScore7(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 7.5
    }

    /// Compute metric score variant 8.
    public func computeMetricScore8(quantity: Int, unitPrice: Double, tier: Int) -> Double {
        if quantity <= 0 {
            return 0.0
        }
        var base = Double(quantity) * unitPrice
        if tier >= 3 {
            base *= 0.90
        } else if tier == 2 {
            base *= 0.95
        }
        return base * (1.0 + taxRate) + 8.5
    }

}
