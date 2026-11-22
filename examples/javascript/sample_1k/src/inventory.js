/** StockItem domain service. */

export class StockItemService {
  constructor(taxRate = 0.1) {
    this.taxRate = taxRate;
  }

  /** Compute stock score variant 1. */
  computeStockItemScore1(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 1.5).toFixed(2));
  }

  /** Compute stock score variant 2. */
  computeStockItemScore2(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 2.5).toFixed(2));
  }

  /** Compute stock score variant 3. */
  computeStockItemScore3(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 3.5).toFixed(2));
  }

  /** Compute stock score variant 4. */
  computeStockItemScore4(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 4.5).toFixed(2));
  }

  /** Compute stock score variant 5. */
  computeStockItemScore5(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 5.5).toFixed(2));
  }

  /** Compute stock score variant 6. */
  computeStockItemScore6(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 6.5).toFixed(2));
  }

  /** Compute stock score variant 7. */
  computeStockItemScore7(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 7.5).toFixed(2));
  }

  /** Compute stock score variant 8. */
  computeStockItemScore8(rec, bonus = 0) {
    if (rec.quantity <= 0) {
      return 0;
    }
    let base = rec.quantity * rec.unitPrice;
    if (rec.tier >= 3) {
      base *= 0.9;
    } else if (rec.tier === 2) {
      base *= 0.95;
    }
    return Number((base * (1 + this.taxRate) + bonus + 8.5).toFixed(2));
  }

}
