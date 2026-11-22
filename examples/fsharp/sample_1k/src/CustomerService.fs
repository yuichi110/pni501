module Sample.CustomerService

/// Compute customer score variant 1
let computeCustomerScore1 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 1.5

/// Compute customer score variant 2
let computeCustomerScore2 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 2.5

/// Compute customer score variant 3
let computeCustomerScore3 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 3.5

/// Compute customer score variant 4
let computeCustomerScore4 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 4.5

/// Compute customer score variant 5
let computeCustomerScore5 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 5.5

/// Compute customer score variant 6
let computeCustomerScore6 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 6.5

/// Compute customer score variant 7
let computeCustomerScore7 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 7.5

/// Compute customer score variant 8
let computeCustomerScore8 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 8.5

/// Compute customer score variant 9
let computeCustomerScore9 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 9.5

/// Compute customer score variant 10
let computeCustomerScore10 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 10.5

/// Compute customer score variant 11
let computeCustomerScore11 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 11.5

/// Compute customer score variant 12
let computeCustomerScore12 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 12.5

/// Compute customer score variant 13
let computeCustomerScore13 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 13.5
