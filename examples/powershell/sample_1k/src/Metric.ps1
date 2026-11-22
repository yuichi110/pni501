# Metric PowerShell module

# Compute metric score variant 1
function Get-MetricScore1 {
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

# Compute metric score variant 2
function Get-MetricScore2 {
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

# Compute metric score variant 3
function Get-MetricScore3 {
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

# Compute metric score variant 4
function Get-MetricScore4 {
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

# Compute metric score variant 5
function Get-MetricScore5 {
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

# Compute metric score variant 6
function Get-MetricScore6 {
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

# Compute metric score variant 7
function Get-MetricScore7 {
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

# Compute metric score variant 8
function Get-MetricScore8 {
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

# Compute metric score variant 9
function Get-MetricScore9 {
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
