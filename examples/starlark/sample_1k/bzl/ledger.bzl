# Bazel macro helpers for LedgerEntry

def compute_ledger_score_1(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 1

def compute_ledger_score_2(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 2

def compute_ledger_score_3(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 3

def compute_ledger_score_4(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 4

def compute_ledger_score_5(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 5

def compute_ledger_score_6(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 6

def compute_ledger_score_7(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 7

def compute_ledger_score_8(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 8

def compute_ledger_score_9(qty, price, tier = 1):
    if qty <= 0:
        return 0
    base = qty * price
    if tier >= 3:
        base = base * 90
    elif tier == 2:
        base = base * 95
    else:
        base = base * 100
    return base + 9
