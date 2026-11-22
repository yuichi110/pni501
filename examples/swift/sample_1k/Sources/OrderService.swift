import Foundation

/// Order domain service.

public class OrderService {
    let taxRate: Double

    /// Initialize service.
    public init(taxRate: Double = 0.1) {
        self.taxRate = taxRate
    }

    /// Compute order score variant 1.
    public func computeOrderScore1(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 2.
    public func computeOrderScore2(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 3.
    public func computeOrderScore3(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 4.
    public func computeOrderScore4(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 5.
    public func computeOrderScore5(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 6.
    public func computeOrderScore6(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 7.
    public func computeOrderScore7(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute order score variant 8.
    public func computeOrderScore8(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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
