module ShipmentService where

-- | Compute shipment score variant 1
computeShipmentScore1 :: Int -> Double -> Int -> Double
computeShipmentScore1 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 1.5

-- | Compute shipment score variant 2
computeShipmentScore2 :: Int -> Double -> Int -> Double
computeShipmentScore2 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 2.5

-- | Compute shipment score variant 3
computeShipmentScore3 :: Int -> Double -> Int -> Double
computeShipmentScore3 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 3.5

-- | Compute shipment score variant 4
computeShipmentScore4 :: Int -> Double -> Int -> Double
computeShipmentScore4 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 4.5

-- | Compute shipment score variant 5
computeShipmentScore5 :: Int -> Double -> Int -> Double
computeShipmentScore5 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 5.5

-- | Compute shipment score variant 6
computeShipmentScore6 :: Int -> Double -> Int -> Double
computeShipmentScore6 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 6.5

-- | Compute shipment score variant 7
computeShipmentScore7 :: Int -> Double -> Int -> Double
computeShipmentScore7 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 7.5

-- | Compute shipment score variant 8
computeShipmentScore8 :: Int -> Double -> Int -> Double
computeShipmentScore8 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 8.5

-- | Compute shipment score variant 9
computeShipmentScore9 :: Int -> Double -> Int -> Double
computeShipmentScore9 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 9.5

-- | Compute shipment score variant 10
computeShipmentScore10 :: Int -> Double -> Int -> Double
computeShipmentScore10 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 10.5

-- | Compute shipment score variant 11
computeShipmentScore11 :: Int -> Double -> Int -> Double
computeShipmentScore11 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 11.5

-- | Compute shipment score variant 12
computeShipmentScore12 :: Int -> Double -> Int -> Double
computeShipmentScore12 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 12.5

-- | Compute shipment score variant 13
computeShipmentScore13 :: Int -> Double -> Int -> Double
computeShipmentScore13 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 13.5

-- | Compute shipment score variant 14
computeShipmentScore14 :: Int -> Double -> Int -> Double
computeShipmentScore14 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 14.5

-- | Compute shipment score variant 15
computeShipmentScore15 :: Int -> Double -> Int -> Double
computeShipmentScore15 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 15.5
