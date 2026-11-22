module PriceRuleService where

-- | Compute pricing score variant 1
computePriceRuleScore1 :: Int -> Double -> Int -> Double
computePriceRuleScore1 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 1.5

-- | Compute pricing score variant 2
computePriceRuleScore2 :: Int -> Double -> Int -> Double
computePriceRuleScore2 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 2.5

-- | Compute pricing score variant 3
computePriceRuleScore3 :: Int -> Double -> Int -> Double
computePriceRuleScore3 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 3.5

-- | Compute pricing score variant 4
computePriceRuleScore4 :: Int -> Double -> Int -> Double
computePriceRuleScore4 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 4.5

-- | Compute pricing score variant 5
computePriceRuleScore5 :: Int -> Double -> Int -> Double
computePriceRuleScore5 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 5.5

-- | Compute pricing score variant 6
computePriceRuleScore6 :: Int -> Double -> Int -> Double
computePriceRuleScore6 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 6.5

-- | Compute pricing score variant 7
computePriceRuleScore7 :: Int -> Double -> Int -> Double
computePriceRuleScore7 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 7.5

-- | Compute pricing score variant 8
computePriceRuleScore8 :: Int -> Double -> Int -> Double
computePriceRuleScore8 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 8.5

-- | Compute pricing score variant 9
computePriceRuleScore9 :: Int -> Double -> Int -> Double
computePriceRuleScore9 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 9.5

-- | Compute pricing score variant 10
computePriceRuleScore10 :: Int -> Double -> Int -> Double
computePriceRuleScore10 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 10.5

-- | Compute pricing score variant 11
computePriceRuleScore11 :: Int -> Double -> Int -> Double
computePriceRuleScore11 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 11.5

-- | Compute pricing score variant 12
computePriceRuleScore12 :: Int -> Double -> Int -> Double
computePriceRuleScore12 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 12.5

-- | Compute pricing score variant 13
computePriceRuleScore13 :: Int -> Double -> Int -> Double
computePriceRuleScore13 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 13.5

-- | Compute pricing score variant 14
computePriceRuleScore14 :: Int -> Double -> Int -> Double
computePriceRuleScore14 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 14.5

-- | Compute pricing score variant 15
computePriceRuleScore15 :: Int -> Double -> Int -> Double
computePriceRuleScore15 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 15.5
