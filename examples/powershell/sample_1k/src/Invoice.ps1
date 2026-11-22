# Invoice PowerShell module

# Compute invoice score variant 1
function Get-InvoiceScore1 {
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

# Compute invoice score variant 2
function Get-InvoiceScore2 {
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

# Compute invoice score variant 3
function Get-InvoiceScore3 {
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

# Compute invoice score variant 4
function Get-InvoiceScore4 {
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

# Compute invoice score variant 5
function Get-InvoiceScore5 {
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

# Compute invoice score variant 6
function Get-InvoiceScore6 {
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

# Compute invoice score variant 7
function Get-InvoiceScore7 {
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

# Compute invoice score variant 8
function Get-InvoiceScore8 {
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

# Compute invoice score variant 9
function Get-InvoiceScore9 {
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
