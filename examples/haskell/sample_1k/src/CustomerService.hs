module CustomerService where

-- | Compute customer score variant 1
computeCustomerScore1 :: Int -> Double -> Int -> Double
computeCustomerScore1 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 1.5

-- | Compute customer score variant 2
computeCustomerScore2 :: Int -> Double -> Int -> Double
computeCustomerScore2 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 2.5

-- | Compute customer score variant 3
computeCustomerScore3 :: Int -> Double -> Int -> Double
computeCustomerScore3 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 3.5

-- | Compute customer score variant 4
computeCustomerScore4 :: Int -> Double -> Int -> Double
computeCustomerScore4 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 4.5

-- | Compute customer score variant 5
computeCustomerScore5 :: Int -> Double -> Int -> Double
computeCustomerScore5 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 5.5

-- | Compute customer score variant 6
computeCustomerScore6 :: Int -> Double -> Int -> Double
computeCustomerScore6 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 6.5

-- | Compute customer score variant 7
computeCustomerScore7 :: Int -> Double -> Int -> Double
computeCustomerScore7 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 7.5

-- | Compute customer score variant 8
computeCustomerScore8 :: Int -> Double -> Int -> Double
computeCustomerScore8 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 8.5

-- | Compute customer score variant 9
computeCustomerScore9 :: Int -> Double -> Int -> Double
computeCustomerScore9 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 9.5

-- | Compute customer score variant 10
computeCustomerScore10 :: Int -> Double -> Int -> Double
computeCustomerScore10 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 10.5

-- | Compute customer score variant 11
computeCustomerScore11 :: Int -> Double -> Int -> Double
computeCustomerScore11 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 11.5

-- | Compute customer score variant 12
computeCustomerScore12 :: Int -> Double -> Int -> Double
computeCustomerScore12 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 12.5

-- | Compute customer score variant 13
computeCustomerScore13 :: Int -> Double -> Int -> Double
computeCustomerScore13 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 13.5

-- | Compute customer score variant 14
computeCustomerScore14 :: Int -> Double -> Int -> Double
computeCustomerScore14 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 14.5

-- | Compute customer score variant 15
computeCustomerScore15 :: Int -> Double -> Int -> Double
computeCustomerScore15 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 15.5
