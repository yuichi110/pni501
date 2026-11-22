# StockItem PowerShell module

# Compute stock score variant 1
function Get-StockItemScore1 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 1
}

# Compute stock score variant 2
function Get-StockItemScore2 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 2
}

# Compute stock score variant 3
function Get-StockItemScore3 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 3
}

# Compute stock score variant 4
function Get-StockItemScore4 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 4
}

# Compute stock score variant 5
function Get-StockItemScore5 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 5
}

# Compute stock score variant 6
function Get-StockItemScore6 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 6
}

# Compute stock score variant 7
function Get-StockItemScore7 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 7
}

# Compute stock score variant 8
function Get-StockItemScore8 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 8
}

# Compute stock score variant 9
function Get-StockItemScore9 {
    param([int]$Quantity, [double]$UnitPrice, [int]$Tier = 1)
    if ($Quantity -le 0) {
        return 0
    }
    $base = $Quantity * $UnitPrice
    if ($Tier -ge 3) {
        $base = $base * 0.90
    } elseif ($Tier -eq 2) {
        $base = $base * 0.95
    }
    return $base + 9
}
