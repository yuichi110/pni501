/** Customer domain service. */

export class CustomerService {
  constructor(taxRate = 0.1) {
    this.taxRate = taxRate;
  }

  /** Compute customer score variant 1. */
  computeCustomerScore1(rec, bonus = 0) {
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
  computeCustomerScore2(rec, bonus = 0) {
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
  computeCustomerScore3(rec, bonus = 0) {
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
  computeCustomerScore4(rec, bonus = 0) {
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
  computeCustomerScore5(rec, bonus = 0) {
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
  computeCustomerScore6(rec, bonus = 0) {
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
  computeCustomerScore7(rec, bonus = 0) {
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
  computeCustomerScore8(rec, bonus = 0) {
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
