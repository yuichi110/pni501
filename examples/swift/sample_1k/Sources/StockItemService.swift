import Foundation

/// StockItem domain service.

public class StockItemService {
    let taxRate: Double

    /// Initialize service.
    public init(taxRate: Double = 0.1) {
        self.taxRate = taxRate
    }

    /// Compute stock score variant 1.
    public func computeStockItemScore1(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 2.
    public func computeStockItemScore2(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 3.
    public func computeStockItemScore3(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 4.
    public func computeStockItemScore4(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 5.
    public func computeStockItemScore5(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 6.
    public func computeStockItemScore6(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 7.
    public func computeStockItemScore7(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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

    /// Compute stock score variant 8.
    public func computeStockItemScore8(quantity: Int, unitPrice: Double, tier: Int) -> Double {
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
