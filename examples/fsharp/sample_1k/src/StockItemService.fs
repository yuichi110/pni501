module Sample.StockItemService

/// Compute stock score variant 1
let computeStockItemScore1 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 1.5

/// Compute stock score variant 2
let computeStockItemScore2 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 2.5

/// Compute stock score variant 3
let computeStockItemScore3 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 3.5

/// Compute stock score variant 4
let computeStockItemScore4 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 4.5

/// Compute stock score variant 5
let computeStockItemScore5 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 5.5

/// Compute stock score variant 6
let computeStockItemScore6 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 6.5

/// Compute stock score variant 7
let computeStockItemScore7 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 7.5

/// Compute stock score variant 8
let computeStockItemScore8 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 8.5

/// Compute stock score variant 9
let computeStockItemScore9 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 9.5

/// Compute stock score variant 10
let computeStockItemScore10 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 10.5

/// Compute stock score variant 11
let computeStockItemScore11 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 11.5

/// Compute stock score variant 12
let computeStockItemScore12 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 12.5

/// Compute stock score variant 13
let computeStockItemScore13 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 13.5
