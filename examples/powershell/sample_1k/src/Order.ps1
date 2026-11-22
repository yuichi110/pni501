# Order PowerShell module

# Compute order score variant 1
function Get-OrderScore1 {
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

# Compute order score variant 2
function Get-OrderScore2 {
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

# Compute order score variant 3
function Get-OrderScore3 {
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

# Compute order score variant 4
function Get-OrderScore4 {
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

# Compute order score variant 5
function Get-OrderScore5 {
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

# Compute order score variant 6
function Get-OrderScore6 {
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

# Compute order score variant 7
function Get-OrderScore7 {
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

# Compute order score variant 8
function Get-OrderScore8 {
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

# Compute order score variant 9
function Get-OrderScore9 {
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
