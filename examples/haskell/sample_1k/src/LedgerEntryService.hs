module LedgerEntryService where

-- | Compute ledger score variant 1
computeLedgerEntryScore1 :: Int -> Double -> Int -> Double
computeLedgerEntryScore1 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 1.5

-- | Compute ledger score variant 2
computeLedgerEntryScore2 :: Int -> Double -> Int -> Double
computeLedgerEntryScore2 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 2.5

-- | Compute ledger score variant 3
computeLedgerEntryScore3 :: Int -> Double -> Int -> Double
computeLedgerEntryScore3 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 3.5

-- | Compute ledger score variant 4
computeLedgerEntryScore4 :: Int -> Double -> Int -> Double
computeLedgerEntryScore4 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 4.5

-- | Compute ledger score variant 5
computeLedgerEntryScore5 :: Int -> Double -> Int -> Double
computeLedgerEntryScore5 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 5.5

-- | Compute ledger score variant 6
computeLedgerEntryScore6 :: Int -> Double -> Int -> Double
computeLedgerEntryScore6 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 6.5

-- | Compute ledger score variant 7
computeLedgerEntryScore7 :: Int -> Double -> Int -> Double
computeLedgerEntryScore7 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 7.5

-- | Compute ledger score variant 8
computeLedgerEntryScore8 :: Int -> Double -> Int -> Double
computeLedgerEntryScore8 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 8.5

-- | Compute ledger score variant 9
computeLedgerEntryScore9 :: Int -> Double -> Int -> Double
computeLedgerEntryScore9 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 9.5

-- | Compute ledger score variant 10
computeLedgerEntryScore10 :: Int -> Double -> Int -> Double
computeLedgerEntryScore10 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 10.5

-- | Compute ledger score variant 11
computeLedgerEntryScore11 :: Int -> Double -> Int -> Double
computeLedgerEntryScore11 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 11.5

-- | Compute ledger score variant 12
computeLedgerEntryScore12 :: Int -> Double -> Int -> Double
computeLedgerEntryScore12 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 12.5

-- | Compute ledger score variant 13
computeLedgerEntryScore13 :: Int -> Double -> Int -> Double
computeLedgerEntryScore13 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 13.5

-- | Compute ledger score variant 14
computeLedgerEntryScore14 :: Int -> Double -> Int -> Double
computeLedgerEntryScore14 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 14.5

-- | Compute ledger score variant 15
computeLedgerEntryScore15 :: Int -> Double -> Int -> Double
computeLedgerEntryScore15 qty price tier =
  if qty <= 0
    then 0.0
    else
      let base = fromIntegral qty * price
          disc = if tier >= 3 then 0.90 else if tier == 2 then 0.95 else 1.00
      in base * disc * 1.1 + 15.5
