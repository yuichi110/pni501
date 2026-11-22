/** LedgerEntry record interface. */

export interface LedgerEntryRecord {
  readonly id: string;
  readonly quantity: number;
  readonly unitPrice: number;
  readonly tier: number;
}

/** LedgerEntry domain service. */

export class LedgerEntryService {
  private readonly taxRate: number;

  constructor(taxRate: number = 0.1) {
    this.taxRate = taxRate;
  }

  /** Compute ledger score variant 1. */
  public computeLedgerEntryScore1(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 2. */
  public computeLedgerEntryScore2(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 3. */
  public computeLedgerEntryScore3(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 4. */
  public computeLedgerEntryScore4(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 5. */
  public computeLedgerEntryScore5(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 6. */
  public computeLedgerEntryScore6(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 7. */
  public computeLedgerEntryScore7(rec: LedgerEntryRecord, bonus: number = 0): number {
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

  /** Compute ledger score variant 8. */
  public computeLedgerEntryScore8(rec: LedgerEntryRecord, bonus: number = 0): number {
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
