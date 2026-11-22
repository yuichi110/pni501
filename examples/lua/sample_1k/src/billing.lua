local M = {}

--- Compute invoice score variant 1
function M.compute_invoice_score_1(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 1.5
end

--- Compute invoice score variant 2
function M.compute_invoice_score_2(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 2.5
end

--- Compute invoice score variant 3
function M.compute_invoice_score_3(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 3.5
end

--- Compute invoice score variant 4
function M.compute_invoice_score_4(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 4.5
end

--- Compute invoice score variant 5
function M.compute_invoice_score_5(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 5.5
end

--- Compute invoice score variant 6
function M.compute_invoice_score_6(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 6.5
end

--- Compute invoice score variant 7
function M.compute_invoice_score_7(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 7.5
end

--- Compute invoice score variant 8
function M.compute_invoice_score_8(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 8.5
end

--- Compute invoice score variant 9
function M.compute_invoice_score_9(qty, price, tier)
  if qty <= 0 then
    return 0
  end
  local base = qty * price
  if tier >= 3 then
    base = base * 0.90
  elseif tier == 2 then
    base = base * 0.95
  end
  return base * 1.1 + 9.5
end

return M
