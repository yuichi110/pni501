/** Invoice record interface. */

export interface InvoiceRecord {
  readonly id: string;
  readonly quantity: number;
  readonly unitPrice: number;
  readonly tier: number;
}

/** Invoice domain service. */

export class InvoiceService {
  private readonly taxRate: number;

  constructor(taxRate: number = 0.1) {
    this.taxRate = taxRate;
  }

  /** Compute invoice score variant 1. */
  public computeInvoiceScore1(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 2. */
  public computeInvoiceScore2(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 3. */
  public computeInvoiceScore3(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 4. */
  public computeInvoiceScore4(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 5. */
  public computeInvoiceScore5(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 6. */
  public computeInvoiceScore6(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 7. */
  public computeInvoiceScore7(rec: InvoiceRecord, bonus: number = 0): number {
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

  /** Compute invoice score variant 8. */
  public computeInvoiceScore8(rec: InvoiceRecord, bonus: number = 0): number {
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
