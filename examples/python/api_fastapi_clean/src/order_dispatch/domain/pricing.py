"""Pure integer-cents pricing and loyalty discount calculations."""

from __future__ import annotations

from collections.abc import Sequence

from order_dispatch.domain.models import CustomerTier, OrderLine


class PricingError(ValueError):
    """Raised when order lines or discount rates violate domain invariants."""


def calculate_subtotal_cents(lines: Sequence[OrderLine]) -> int:
    """Sum line-item quantities multiplied by unit prices in integer cents.

    Args:
        lines: Non-empty sequence of order line items.

    Returns:
        int: Gross order subtotal in cents.
    """
    if not lines:
        raise PricingError("Order must contain at least one OrderLine.")
    subtotal = 0
    for line in lines:
        if line.quantity <= 0 or line.unit_price_cents < 0:
            raise PricingError(f"Invalid quantity or unit price for SKU '{line.sku}'.")
        subtotal += line.quantity * line.unit_price_cents
    return subtotal


def compute_order_total_cents(
    lines: Sequence[OrderLine],
    tier: CustomerTier,
    vip_discount_rate: float = 0.10,
) -> tuple[int, int]:
    """Compute gross subtotal and net discounted total in integer cents.

    Args:
        lines: Sequence of order line items.
        tier: Customer loyalty tier.
        vip_discount_rate: Fractional discount applied to VIP orders in [0.0, 0.5].

    Returns:
        tuple[int, int]: Pair of (subtotal_cents, net_total_cents).
    """
    if vip_discount_rate < 0.0 or vip_discount_rate > 0.5:
        raise PricingError(f"vip_discount_rate must be within [0.0, 0.5], got {vip_discount_rate}.")
    subtotal = calculate_subtotal_cents(lines)
    if tier == CustomerTier.VIP:
        discount = round(subtotal * vip_discount_rate)
        return subtotal, max(0, subtotal - discount)
    return subtotal, subtotal
