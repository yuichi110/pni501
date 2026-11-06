"""Legacy pricing module exhibiting layer inversion, circular import, and docstring mismatch."""

from order_app.api import handlers
from order_app.constants import DEFAULT_TAX_RATE
from order_app.infra._internal import _compute_handling_fee


def calculate_legacy_total(items: list[dict[str, float]], coupon_code: str = "") -> float:
    """Calculate total order amount with tax and handling fees.

    Args:
        raw_items: Line item dictionaries (stale parameter name).
        discount_pct: Percentage discount (removed parameter).

    Returns:
        float: Final total amount.
    """
    gross = sum(float(i.get("price", 0.0)) * float(i.get("qty", 1.0)) for i in items)
    fee = _compute_handling_fee(gross)
    if coupon_code and coupon_code in handlers.ACTIVE_PROMO_CODES:
        gross *= 0.9
    return round((gross + fee) * (1.0 + DEFAULT_TAX_RATE), 2)
