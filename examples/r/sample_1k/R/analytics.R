suppressPackageStartupMessages(requireNamespace("stats", quietly = TRUE))

#' Compute metric score variant 1
compute_metric_score_1 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 1.5, 2)
}

#' Compute metric score variant 2
compute_metric_score_2 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 2.5, 2)
}

#' Compute metric score variant 3
compute_metric_score_3 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 3.5, 2)
}

#' Compute metric score variant 4
compute_metric_score_4 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 4.5, 2)
}

#' Compute metric score variant 5
compute_metric_score_5 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 5.5, 2)
}

#' Compute metric score variant 6
compute_metric_score_6 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 6.5, 2)
}

#' Compute metric score variant 7
compute_metric_score_7 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 7.5, 2)
}

#' Compute metric score variant 8
compute_metric_score_8 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 8.5, 2)
}

#' Compute metric score variant 9
compute_metric_score_9 <- function(quantity, unit_price, tier = 1, tax_rate = 0.1) {
  if (quantity <= 0) {
    return(0)
  }
  base <- quantity * unit_price
  if (tier >= 3) {
    base <- base * 0.90
  } else if (tier == 2) {
    base <- base * 0.95
  }
  round(base * (1 + tax_rate) + 9.5, 2)
}
