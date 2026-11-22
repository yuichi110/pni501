module Sample.ShipmentService

/// Compute shipment score variant 1
let computeShipmentScore1 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 1.5

/// Compute shipment score variant 2
let computeShipmentScore2 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 2.5

/// Compute shipment score variant 3
let computeShipmentScore3 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 3.5

/// Compute shipment score variant 4
let computeShipmentScore4 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 4.5

/// Compute shipment score variant 5
let computeShipmentScore5 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 5.5

/// Compute shipment score variant 6
let computeShipmentScore6 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 6.5

/// Compute shipment score variant 7
let computeShipmentScore7 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 7.5

/// Compute shipment score variant 8
let computeShipmentScore8 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 8.5

/// Compute shipment score variant 9
let computeShipmentScore9 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 9.5

/// Compute shipment score variant 10
let computeShipmentScore10 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 10.5

/// Compute shipment score variant 11
let computeShipmentScore11 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 11.5

/// Compute shipment score variant 12
let computeShipmentScore12 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 12.5

/// Compute shipment score variant 13
let computeShipmentScore13 (qty: int) (price: float) (tier: int) : float =
    if qty <= 0 then
        0.0
    else
        let baseVal = float qty * price
        let disc =
            if tier >= 3 then 0.90
            elif tier = 2 then 0.95
            else 1.00
        baseVal * disc * 1.1 + 13.5
