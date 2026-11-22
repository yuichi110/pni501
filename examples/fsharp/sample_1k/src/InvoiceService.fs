module Sample.InvoiceService

/// Compute invoice score variant 1
let computeInvoiceScore1 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 1.5

/// Compute invoice score variant 2
let computeInvoiceScore2 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 2.5

/// Compute invoice score variant 3
let computeInvoiceScore3 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 3.5

/// Compute invoice score variant 4
let computeInvoiceScore4 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 4.5

/// Compute invoice score variant 5
let computeInvoiceScore5 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 5.5

/// Compute invoice score variant 6
let computeInvoiceScore6 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 6.5

/// Compute invoice score variant 7
let computeInvoiceScore7 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 7.5

/// Compute invoice score variant 8
let computeInvoiceScore8 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 8.5

/// Compute invoice score variant 9
let computeInvoiceScore9 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 9.5

/// Compute invoice score variant 10
let computeInvoiceScore10 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 10.5

/// Compute invoice score variant 11
let computeInvoiceScore11 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 11.5

/// Compute invoice score variant 12
let computeInvoiceScore12 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 12.5

/// Compute invoice score variant 13
let computeInvoiceScore13 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 13.5
