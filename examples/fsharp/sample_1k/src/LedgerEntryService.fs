module Sample.LedgerEntryService

/// Compute ledger score variant 1
let computeLedgerEntryScore1 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 1.5

/// Compute ledger score variant 2
let computeLedgerEntryScore2 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 2.5

/// Compute ledger score variant 3
let computeLedgerEntryScore3 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 3.5

/// Compute ledger score variant 4
let computeLedgerEntryScore4 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 4.5

/// Compute ledger score variant 5
let computeLedgerEntryScore5 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 5.5

/// Compute ledger score variant 6
let computeLedgerEntryScore6 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 6.5

/// Compute ledger score variant 7
let computeLedgerEntryScore7 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 7.5

/// Compute ledger score variant 8
let computeLedgerEntryScore8 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 8.5

/// Compute ledger score variant 9
let computeLedgerEntryScore9 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 9.5

/// Compute ledger score variant 10
let computeLedgerEntryScore10 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 10.5

/// Compute ledger score variant 11
let computeLedgerEntryScore11 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 11.5

/// Compute ledger score variant 12
let computeLedgerEntryScore12 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 12.5

/// Compute ledger score variant 13
let computeLedgerEntryScore13 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 13.5
