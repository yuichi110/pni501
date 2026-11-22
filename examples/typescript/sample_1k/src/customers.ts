/** Customer record interface. */

export interface CustomerRecord {
  readonly id: string;
  readonly quantity: number;
  readonly unitPrice: number;
  readonly tier: number;
}

/** Customer domain service. */

export class CustomerService {
  private readonly taxRate: number;

  constructor(taxRate: number = 0.1) {
    this.taxRate = taxRate;
  }

  /** Compute customer score variant 1. */
  public computeCustomerScore1(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 2. */
  public computeCustomerScore2(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 3. */
  public computeCustomerScore3(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 4. */
  public computeCustomerScore4(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 5. */
  public computeCustomerScore5(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 6. */
  public computeCustomerScore6(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 7. */
  public computeCustomerScore7(rec: CustomerRecord, bonus: number = 0): number {
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

  /** Compute customer score variant 8. */
  public computeCustomerScore8(rec: CustomerRecord, bonus: number = 0): number {
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
