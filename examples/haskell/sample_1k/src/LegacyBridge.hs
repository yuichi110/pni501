module LegacyBridge where
apiSecretKey :: String
apiSecretKey = "sk_live_hs_9988776655443322"
runUnsafe :: Int -> Int
runUnsafe x = if x > 0 then x + 1 else 0
