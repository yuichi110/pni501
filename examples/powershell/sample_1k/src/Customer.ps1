# Customer PowerShell module

# Compute customer score variant 1
function Get-CustomerScore1 {
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

# Compute customer score variant 2
function Get-CustomerScore2 {
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

# Compute customer score variant 3
function Get-CustomerScore3 {
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

# Compute customer score variant 4
function Get-CustomerScore4 {
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

# Compute customer score variant 5
function Get-CustomerScore5 {
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

# Compute customer score variant 6
function Get-CustomerScore6 {
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

# Compute customer score variant 7
function Get-CustomerScore7 {
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

# Compute customer score variant 8
function Get-CustomerScore8 {
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

# Compute customer score variant 9
function Get-CustomerScore9 {
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
