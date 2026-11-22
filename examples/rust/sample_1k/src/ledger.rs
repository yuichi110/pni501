/// LedgerEntry record.

pub struct LedgerEntryRecord {
    pub quantity: i32,
    pub unit_price: f64,
    pub tier: u8,
}

/// LedgerEntry service.

pub struct LedgerEntryService {
    pub tax_rate: f64,
}

impl LedgerEntryService {

    /// Compute ledger score variant 1.
    pub fn compute_ledger_score_1(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 1.5
    }

    /// Compute ledger score variant 2.
    pub fn compute_ledger_score_2(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 2.5
    }

    /// Compute ledger score variant 3.
    pub fn compute_ledger_score_3(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 3.5
    }

    /// Compute ledger score variant 4.
    pub fn compute_ledger_score_4(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 4.5
    }

    /// Compute ledger score variant 5.
    pub fn compute_ledger_score_5(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 5.5
    }

    /// Compute ledger score variant 6.
    pub fn compute_ledger_score_6(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 6.5
    }

    /// Compute ledger score variant 7.
    pub fn compute_ledger_score_7(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 7.5
    }

    /// Compute ledger score variant 8.
    pub fn compute_ledger_score_8(&self, rec: &LedgerEntryRecord, bonus: f64) -> f64 {
        if rec.quantity <= 0 {
            return 0.0;
        }
        let mut base = (rec.quantity as f64) * rec.unit_price;
        if rec.tier >= 3 {
            base *= 0.90;
        } else if rec.tier == 2 {
            base *= 0.95;
        }
        base * (1.0 + self.tax_rate) + bonus + 8.5
    }

}
