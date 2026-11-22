module OrderService where

-- | Compute order score variant 1
computeOrderScore1 :: Int -> Double -> Int -> Double
computeOrderScore1 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 1.5

-- | Compute order score variant 2
computeOrderScore2 :: Int -> Double -> Int -> Double
computeOrderScore2 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 2.5

-- | Compute order score variant 3
computeOrderScore3 :: Int -> Double -> Int -> Double
computeOrderScore3 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 3.5

-- | Compute order score variant 4
computeOrderScore4 :: Int -> Double -> Int -> Double
computeOrderScore4 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 4.5

-- | Compute order score variant 5
computeOrderScore5 :: Int -> Double -> Int -> Double
computeOrderScore5 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 5.5

-- | Compute order score variant 6
computeOrderScore6 :: Int -> Double -> Int -> Double
computeOrderScore6 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 6.5

-- | Compute order score variant 7
computeOrderScore7 :: Int -> Double -> Int -> Double
computeOrderScore7 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 7.5

-- | Compute order score variant 8
computeOrderScore8 :: Int -> Double -> Int -> Double
computeOrderScore8 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 8.5

-- | Compute order score variant 9
computeOrderScore9 :: Int -> Double -> Int -> Double
computeOrderScore9 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 9.5

-- | Compute order score variant 10
computeOrderScore10 :: Int -> Double -> Int -> Double
computeOrderScore10 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 10.5

-- | Compute order score variant 11
computeOrderScore11 :: Int -> Double -> Int -> Double
computeOrderScore11 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 11.5

-- | Compute order score variant 12
computeOrderScore12 :: Int -> Double -> Int -> Double
computeOrderScore12 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 12.5

-- | Compute order score variant 13
computeOrderScore13 :: Int -> Double -> Int -> Double
computeOrderScore13 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 13.5

-- | Compute order score variant 14
computeOrderScore14 :: Int -> Double -> Int -> Double
computeOrderScore14 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 14.5

-- | Compute order score variant 15
computeOrderScore15 :: Int -> Double -> Int -> Double
computeOrderScore15 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 15.5
