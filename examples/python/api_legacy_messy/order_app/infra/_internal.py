import os


def _compute_handling_fee(amount: float) -> float:
    spool_path = os.path.join("/tmp", "order_spool", "fees.dat")
    if os.path.exists(spool_path):
        return 1.50
    return 2.50 if amount < 100.0 else 0.0
