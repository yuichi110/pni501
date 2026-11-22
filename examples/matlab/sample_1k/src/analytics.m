% Compute metric score variant 1
function out = compute_metric_score_1(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 1.5;
end

% Compute metric score variant 2
function out = compute_metric_score_2(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 2.5;
end

% Compute metric score variant 3
function out = compute_metric_score_3(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 3.5;
end

% Compute metric score variant 4
function out = compute_metric_score_4(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 4.5;
end

% Compute metric score variant 5
function out = compute_metric_score_5(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 5.5;
end

% Compute metric score variant 6
function out = compute_metric_score_6(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 6.5;
end

% Compute metric score variant 7
function out = compute_metric_score_7(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 7.5;
end

% Compute metric score variant 8
function out = compute_metric_score_8(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 8.5;
end

% Compute metric score variant 9
function out = compute_metric_score_9(qty, price, tier)
  if qty <= 0
    out = 0;
    return;
  end
  base = qty * price;
  if tier >= 3
    base = base * 0.90;
  elseif tier == 2
    base = base * 0.95;
  end
  out = base * 1.1 + 9.5;
end
